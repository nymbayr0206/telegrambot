import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  FileArchive,
  FileText,
  Image,
  Plus,
  RefreshCw,
  Settings,
  Trash2,
  Type,
  Upload,
} from "lucide-react";
import { Badge } from "@nous-research/ui/ui/components/badge";
import { Button } from "@nous-research/ui/ui/components/button";
import { Spinner } from "@nous-research/ui/ui/components/spinner";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Toast } from "@/components/Toast";
import { usePageHeader } from "@/contexts/usePageHeader";
import { useToast } from "@/hooks/useToast";
import { api, type SocialBrand, type SocialBrandFile } from "@/lib/api";
import { cn } from "@/lib/utils";
import { PluginSlot } from "@/plugins";

const CATEGORY_LABELS: Record<string, string> = {
  logos: "Лого",
  fonts: "Фонт",
  templates: "Постер template",
  settings: "Тохиргоо",
  assets: "Нэмэлт asset",
};

const CATEGORY_ICONS = {
  logos: Image,
  fonts: Type,
  templates: FileArchive,
  settings: Settings,
  assets: FileText,
};

export default function SocialBrandsPage() {
  const [brands, setBrands] = useState<SocialBrand[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [root, setRoot] = useState("");
  const [activeBrand, setActiveBrand] = useState("");
  const [newBrand, setNewBrand] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [uploadTarget, setUploadTarget] = useState<{
    brand: string;
    category: string;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { setAfterTitle, setEnd, setTitle } = usePageHeader();
  const { toast, showToast } = useToast();

  const load = async () => {
    setLoading(true);
    try {
      const res = await api.getSocialBrands();
      setBrands(res.brands);
      setCategories(res.categories);
      setRoot(res.root);
      setActiveBrand((current) => {
        if (current && res.brands.some((b) => b.name === current)) return current;
        return res.brands[0]?.name ?? "";
      });
    } catch {
      showToast("Брэнд asset мэдээлэл уншиж чадсангүй", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  useLayoutEffect(() => {
    setTitle("Social brand assets");
    setAfterTitle(
      <Badge tone="secondary" className="text-[10px]">
        {brands.length} брэнд
      </Badge>,
    );
    setEnd(
      <Button size="sm" className="gap-2 whitespace-nowrap" onClick={() => void load()}>
        <RefreshCw className="size-3.5" />
        Шинэчлэх
      </Button>,
    );
    return () => {
      setTitle(null);
      setAfterTitle(null);
      setEnd(null);
    };
  }, [brands.length, setAfterTitle, setEnd, setTitle]);

  const selectedBrand = useMemo(
    () => brands.find((brand) => brand.name === activeBrand) ?? null,
    [activeBrand, brands],
  );

  const createBrand = async () => {
    const name = newBrand.trim();
    if (!name) return;
    setBusy(true);
    try {
      const res = await api.createSocialBrand(name);
      await load();
      setActiveBrand(res.brand.name);
      setNewBrand("");
      showToast(`${res.brand.name} брэнд үүсгэлээ`, "success");
    } catch {
      showToast("Брэнд үүсгэж чадсангүй", "error");
    } finally {
      setBusy(false);
    }
  };

  const requestUpload = (brand: string, category: string) => {
    setUploadTarget({ brand, category });
    fileInputRef.current?.click();
  };

  const uploadFile = async (file: File | null | undefined) => {
    if (!file || !uploadTarget) return;
    setBusy(true);
    try {
      await api.uploadSocialBrandAsset(
        uploadTarget.brand,
        uploadTarget.category,
        file,
      );
      await load();
      showToast(`${file.name} upload хийлээ`, "success");
    } catch {
      showToast("Файл upload хийж чадсангүй", "error");
    } finally {
      setBusy(false);
      setUploadTarget(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const deleteFile = async (file: SocialBrandFile) => {
    setBusy(true);
    try {
      await api.deleteSocialBrandAsset(file.brand, file.category, file.name);
      await load();
      showToast(`${file.name} устгалаа`, "success");
    } catch {
      showToast("Файл устгаж чадсангүй", "error");
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner className="text-2xl text-primary" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <PluginSlot name="social-brands:top" />
      <Toast toast={toast} />
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={(event) => void uploadFile(event.target.files?.[0])}
      />

      <section className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="grid content-start gap-3">
          <Card>
            <CardHeader>
              <CardTitle>Брэндүүд</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2">
              <div className="flex gap-2">
                <Input
                  value={newBrand}
                  placeholder="brand-name"
                  onChange={(event) => setNewBrand(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") void createBrand();
                  }}
                />
                <Button
                  size="icon"
                  aria-label="Брэнд нэмэх"
                  disabled={busy || !newBrand.trim()}
                  onClick={() => void createBrand()}
                >
                  <Plus className="size-4" />
                </Button>
              </div>

              <div className="grid gap-1">
                {brands.length === 0 ? (
                  <p className="py-8 text-center text-sm text-muted-foreground">
                    Одоогоор brand байхгүй байна.
                  </p>
                ) : (
                  brands.map((brand) => (
                    <button
                      key={brand.name}
                      type="button"
                      onClick={() => setActiveBrand(brand.name)}
                      className={cn(
                        "flex min-w-0 items-center justify-between border border-border px-3 py-2 text-left text-sm",
                        activeBrand === brand.name
                          ? "bg-muted text-foreground"
                          : "bg-muted/15 text-muted-foreground hover:text-foreground",
                      )}
                    >
                      <span className="truncate">{brand.name}</span>
                      <Badge tone="secondary" className="text-[10px]">
                        {countFiles(brand)}
                      </Badge>
                    </button>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Хадгалах зам</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="break-all font-mono-ui text-xs leading-5 text-muted-foreground">
                {root}
              </p>
            </CardContent>
          </Card>
        </aside>

        <main className="min-w-0">
          {!selectedBrand ? (
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                Эхлээд brand үүсгэнэ үү.
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              <Card>
                <CardContent className="flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <h2 className="truncate text-lg font-semibold text-foreground">
                      {selectedBrand.name}
                    </h2>
                    <p className="mt-1 break-all font-mono-ui text-xs text-muted-foreground">
                      {selectedBrand.path}
                    </p>
                  </div>
                  <Badge tone="success" className="w-fit text-[10px]">
                    {countFiles(selectedBrand)} файл
                  </Badge>
                </CardContent>
              </Card>

              <div className="grid gap-4 xl:grid-cols-2">
                {categories.map((category) => (
                  <AssetCategory
                    key={category}
                    brand={selectedBrand}
                    category={category}
                    busy={busy}
                    onUpload={() => requestUpload(selectedBrand.name, category)}
                    onDelete={(file) => void deleteFile(file)}
                  />
                ))}
              </div>
            </div>
          )}
        </main>
      </section>

      <PluginSlot name="social-brands:bottom" />
    </div>
  );
}

function AssetCategory({
  brand,
  category,
  busy,
  onUpload,
  onDelete,
}: {
  brand: SocialBrand;
  category: string;
  busy: boolean;
  onUpload: () => void;
  onDelete: (file: SocialBrandFile) => void;
}) {
  const files = brand.categories[category] ?? [];
  const Icon = CATEGORY_ICONS[category as keyof typeof CATEGORY_ICONS] ?? FileText;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex min-w-0 items-center gap-2">
            <Icon className="size-4 shrink-0" />
            <span className="truncate">
              {CATEGORY_LABELS[category] ?? category}
            </span>
          </CardTitle>
          <Button size="sm" className="gap-2 whitespace-nowrap" disabled={busy} onClick={onUpload}>
            <Upload className="size-3.5" />
            Upload
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {files.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            Энэ ангилалд файл байхгүй.
          </p>
        ) : (
          <div className="grid gap-2">
            {files.map((file) => (
              <div
                key={`${file.category}:${file.name}`}
                className="grid gap-3 border border-border bg-muted/15 p-3 sm:grid-cols-[64px_minmax(0,1fr)_auto]"
              >
                <div className="grid size-16 place-items-center overflow-hidden border border-border bg-card">
                  {file.preview_data_url ? (
                    <img
                      src={file.preview_data_url}
                      alt={file.name}
                      className="h-full w-full object-contain"
                    />
                  ) : (
                    <Icon className="size-5 text-muted-foreground" />
                  )}
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-foreground">
                    {file.name}
                  </p>
                  <p className="mt-1 truncate text-xs text-muted-foreground">
                    {file.media_type}
                  </p>
                  <p className="mt-1 font-mono-ui text-xs text-muted-foreground">
                    {formatBytes(file.size)}
                  </p>
                </div>
                <Button
                  ghost
                  size="icon"
                  aria-label={`${file.name} устгах`}
                  disabled={busy}
                  onClick={() => onDelete(file)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function countFiles(brand: SocialBrand): number {
  return Object.values(brand.categories).reduce((sum, files) => sum + files.length, 0);
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
