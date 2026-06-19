import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve("hermes_cli/web_dist");
const brandsRoot = path.resolve("skills/social-media/brands");
const port = Number(process.env.PORT || 8088);
const host = process.env.HOST || "127.0.0.1";
const categories = ["logos", "fonts", "templates", "settings", "assets"];
const imageExts = new Set([".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]);
const previewMaxBytes = 1_500_000;
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".woff2": "font/woff2",
  ".json": "application/json; charset=utf-8",
};

function send(res, status, body, contentType = "application/json; charset=utf-8") {
  res.writeHead(status, { "Content-Type": contentType, "Cache-Control": "no-store" });
  res.end(Buffer.isBuffer(body) || typeof body === "string" ? body : JSON.stringify(body));
}

function slug(value) {
  const out = String(value || "").trim().toLowerCase().replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^[.-]+|[.-]+$/g, "");
  if (!out) throw new Error("Brand name is required");
  return out;
}

function safeName(value) {
  const out = path.basename(String(value || "").replaceAll("\0", "")).trim();
  if (!out || out === "." || out === "..") throw new Error("Invalid file name");
  return out;
}

function brandDir(name) {
  const target = path.resolve(brandsRoot, slug(name));
  if (target !== brandsRoot && !target.startsWith(`${brandsRoot}${path.sep}`)) {
    throw new Error("Invalid brand path");
  }
  return target;
}

function mime(file) {
  return types[path.extname(file).toLowerCase()] || "application/octet-stream";
}

function fileInfo(file, brand, category) {
  const stat = fs.statSync(file);
  let preview_data_url = null;
  if (imageExts.has(path.extname(file).toLowerCase()) && stat.size <= previewMaxBytes) {
    preview_data_url = `data:${mime(file)};base64,${fs.readFileSync(file).toString("base64")}`;
  }
  return {
    brand,
    category,
    name: path.basename(file),
    size: stat.size,
    modified_at: stat.mtimeMs / 1000,
    media_type: mime(file),
    preview_data_url,
  };
}

function listBrand(dir) {
  const brand = path.basename(dir);
  const byCategory = {};
  for (const category of categories) {
    const categoryDir = path.join(dir, category);
    byCategory[category] = fs.existsSync(categoryDir)
      ? fs.readdirSync(categoryDir)
          .filter((name) => !name.startsWith("."))
          .map((name) => path.join(categoryDir, name))
          .filter((file) => fs.statSync(file).isFile())
          .sort((a, b) => path.basename(a).localeCompare(path.basename(b)))
          .map((file) => fileInfo(file, brand, category))
      : [];
  }
  return { name: brand, path: dir, categories: byCategory };
}

function listBrands() {
  fs.mkdirSync(brandsRoot, { recursive: true });
  return {
    root: brandsRoot,
    categories,
    brands: fs.readdirSync(brandsRoot)
      .map((name) => path.join(brandsRoot, name))
      .filter((dir) => fs.statSync(dir).isDirectory())
      .sort((a, b) => path.basename(a).localeCompare(path.basename(b)))
      .map(listBrand),
  };
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  return Buffer.concat(chunks);
}

function parseMultipart(buffer, boundary) {
  const marker = Buffer.from(`--${boundary}`);
  const fileKey = Buffer.from('name="file"');
  const filenameRe = /filename="([^"]+)"/;
  let offset = 0;
  while (offset < buffer.length) {
    const partStart = buffer.indexOf(marker, offset);
    if (partStart === -1) break;
    const headerStart = partStart + marker.length;
    const headerEnd = buffer.indexOf(Buffer.from("\r\n\r\n"), headerStart);
    if (headerEnd === -1) break;
    const headers = buffer.slice(headerStart, headerEnd).toString("utf8");
    const dataStart = headerEnd + 4;
    const nextPart = buffer.indexOf(marker, dataStart);
    if (nextPart === -1) break;
    if (headers.includes(fileKey.toString())) {
      const match = headers.match(filenameRe);
      const filename = safeName(match?.[1] || "upload");
      let dataEnd = nextPart;
      if (buffer[dataEnd - 2] === 13 && buffer[dataEnd - 1] === 10) dataEnd -= 2;
      return { filename, data: buffer.slice(dataStart, dataEnd) };
    }
    offset = nextPart;
  }
  throw new Error("No file field found");
}

async function handleApi(req, res, url) {
  try {
    if (req.method === "GET" && url.pathname === "/api/social-content/brands") {
      send(res, 200, listBrands());
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/social-content/brands") {
      const body = JSON.parse((await readBody(req)).toString("utf8") || "{}");
      const dir = brandDir(body.name);
      for (const category of categories) fs.mkdirSync(path.join(dir, category), { recursive: true });
      send(res, 200, { ok: true, brand: listBrand(dir) });
      return;
    }

    const uploadMatch = url.pathname.match(/^\/api\/social-content\/brands\/([^/]+)\/upload$/);
    if (req.method === "POST" && uploadMatch) {
      const brand = slug(decodeURIComponent(uploadMatch[1]));
      const category = categories.includes(url.searchParams.get("category") || "")
        ? url.searchParams.get("category")
        : "assets";
      const boundary = req.headers["content-type"]?.match(/boundary=(.+)$/)?.[1];
      if (!boundary) throw new Error("Missing multipart boundary");
      const upload = parseMultipart(await readBody(req), boundary);
      const dir = path.join(brandDir(brand), category);
      fs.mkdirSync(dir, { recursive: true });
      const target = path.join(dir, upload.filename);
      fs.writeFileSync(target, upload.data);
      send(res, 200, { ok: true, file: fileInfo(target, brand, category) });
      return;
    }

    const deleteMatch = url.pathname.match(/^\/api\/social-content\/brands\/([^/]+)\/files\/([^/]+)\/([^/]+)$/);
    if (req.method === "DELETE" && deleteMatch) {
      const brand = slug(decodeURIComponent(deleteMatch[1]));
      const category = decodeURIComponent(deleteMatch[2]);
      if (!categories.includes(category)) throw new Error("Invalid category");
      const target = path.resolve(brandDir(brand), category, safeName(decodeURIComponent(deleteMatch[3])));
      if (!target.startsWith(`${brandDir(brand)}${path.sep}`)) throw new Error("Invalid path");
      if (fs.existsSync(target)) fs.unlinkSync(target);
      send(res, 200, { ok: true });
      return;
    }
  } catch (error) {
    send(res, 400, { detail: error.message || "Bad request" });
    return;
  }

  send(res, 404, { detail: "Not found" });
}

function serveSpa(req, res, url) {
  let file = path.resolve(root, url.pathname === "/" ? "index.html" : `.${url.pathname}`);
  if (!file.startsWith(root)) {
    send(res, 403, "Forbidden", "text/plain; charset=utf-8");
    return;
  }
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) file = path.join(root, "index.html");
  fs.readFile(file, (error, data) => {
    if (error) {
      send(res, 404, "Not found", "text/plain; charset=utf-8");
      return;
    }
    send(res, 200, data, mime(file));
  });
}

http.createServer((req, res) => {
  const url = new URL(req.url || "/", "http://localhost");
  if (url.pathname.startsWith("/api/social-content/")) {
    void handleApi(req, res, url);
    return;
  }
  serveSpa(req, res, url);
}).listen(port, host, () => {
  console.log(`Social brand preview http://${host}:${port}/social-brands`);
});
