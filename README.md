# Photo portfolio — setup notes

## 1. Get the base site + this scaffold

```bash
hugo new site photo-portfolio
cd photo-portfolio
# copy hugo.toml, .github/, and content/ from this scaffold in, overwriting the defaults
```

## 2. Install the Gallery theme as a Hugo Module

The theme's docs recommend Hugo Modules over a git submodule:

```bash
hugo mod init github.com/<your-username>/photo-portfolio
```

Then add this to `hugo.toml` (replace the `theme = "gallery"` line):

```toml
[module]
  [[module.imports]]
    path = "github.com/nicokaiser/hugo-theme-gallery"
```

Run `hugo mod get -u` to fetch it, then `hugo server` to preview locally.

(If you'd rather use a submodule instead of Modules, that also works:
`git submodule add https://github.com/nicokaiser/hugo-theme-gallery.git themes/gallery`
and keep `theme = "gallery"` in the config as-is.)

## 3. Add your photos

- Replace `content/night-architecture/cover.jpg` and `content/wildlife/cover.jpg`
  with real cover images (same folder as each album's `_index.md`).
- For each shoot/series, make a new `.md` file like `ri-campus.md` inside the
  album folder, with your images sitting alongside it in the same directory.
- List each image under `resources:` in the front matter, same pattern as
  the `ri-campus.md` example.

## 4. Export settings from Darktable

- **Do not export as WebP** — Hugo's WebP resize implementation has a known
  bug that dulls image color/levels on this theme. Export as high-quality
  JPEG instead.
- Set the EXIF `ImageDescription` tag on export (or via `exiftool`) if you
  want captions to populate automatically instead of setting `title:` by hand
  in front matter.

## 5. Hide full-resolution originals from visitors (optional)

To stop visitors downloading full-res files, add this to an album's
`_index.md` front matter (applies to everything under it via cascade):

```yaml
cascade:
  build:
    publishResources: false
```

## 6. Push to GitHub

```bash
git init
git add .
git commit -m "Initial portfolio scaffold"
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

- If this is your main GitHub Pages user site, name the repo
  `<your-username>.github.io`. Otherwise any repo name works — the site
  serves at `https://<your-username>.github.io/<repo-name>/` and you should
  set `baseURL` in `hugo.toml` accordingly (already parameterized above).

## 7. Enable GitHub Pages

In the repo: **Settings → Pages → Build and deployment → Source → GitHub
Actions**. The included workflow (`.github/workflows/hugo.yml`) builds and
deploys automatically on every push to `main`.

## 8. Verify

Push, check the **Actions** tab for the build/deploy run, then visit your
site URL once it's green.