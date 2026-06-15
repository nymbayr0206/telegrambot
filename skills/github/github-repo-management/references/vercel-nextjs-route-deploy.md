# Vercel Next.js route deployment from a local repo

Use this when the user asks to place a new page at a specific Vercel-hosted URL such as `https://site.vercel.app/dashboard/agents` and the repository is available locally.

## Workflow

1. Locate the app repository and confirm it is the Vercel project repo:
   - Inspect `package.json`, remotes, branch, and app structure (`src/app`, `app`, or `pages`).
   - Prefer the deployment branch Vercel watches, usually `main`.
2. Sync the deployment branch before editing:
   - `git checkout main`
   - `git pull --ff-only origin main`
3. Add the route in the correct router shape:
   - App Router: `src/app/<route>/page.tsx` or `app/<route>/page.tsx`
   - Pages Router: `pages/<route>.tsx` or nested directories.
4. Keep the page self-contained unless the app already has a data API. For operational dashboards, embedding a safe snapshot is acceptable when no public API exists yet. Never embed secrets or raw credentials.
5. Build locally before pushing:
   - Use the project package manager from `package.json` / `packageManager`.
   - For Yarn 4 repos without a `yarn` binary, use `corepack yarn build`.
   - If dependencies changed upstream and local modules are stale, run `corepack yarn install` first.
6. Commit and push to the Vercel deployment branch:
   - `git add <files>`
   - `git commit -m "Add <feature>"`
   - `git push origin main`
7. Verify the public URL after Vercel deploys:
   - It may return `404` immediately after push while deployment is pending; wait and retry a few times.
   - A `200` response alone can be insufficient for client-rendered pages; verify expected text from the new page appears in the HTML.

## Pitfalls

- Do not assume a local static server URL like `127.0.0.1:<port>` is public. For a user-facing Vercel URL, integrate the route into the app repo and push.
- Avoid treating transient post-push 404 as failure. Vercel often needs a short delay before the new route is live.
- If browser automation is unavailable, use a lightweight HTTP check and search for route-specific content in the returned HTML.
- Do not commit ignored install artifacts (`node_modules`, `.next`, `.yarn`, `yarn.lock` if intentionally ignored) unless the repository convention requires it.
