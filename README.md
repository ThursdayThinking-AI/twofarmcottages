# Two Farm Cottages – website

Static rebuild of www.twofarmcottages.co.uk (previously WordPress on TTD hosting).

## How it works
- `content/*.html` – the body text of each page. Edit these for copy changes.
- `build.py` – page titles, meta descriptions, URLs, business details and the shared layout. Builds everything into `_site/`.
- `assets/style.css` – styling.
- `wp-content/uploads/` – photos, kept at the same paths as the old site so image URLs (and Google Images) don't change.
- Pushing to `main` builds and deploys to GitHub Pages automatically.

Preview locally: `python3 build.py && python3 -m http.server -d _site 8000`

## SEO carried over
- Every page keeps its old URL, including the trailing slash, and its old `<title>`.
- New: meta descriptions, unique H1s, BedAndBreakfast + breadcrumb structured data, Open Graph tags, `sitemap.xml` (also served at the old Yoast address `sitemap_index.xml`), `robots.txt`, `llms.txt`.
- Old WordPress archive URLs (`/category/the-area/`, `/author/...`, `/feed/`) redirect to the nearest page.

## Go-live checklist
1. Run **Actions → Import images from old site** (while the old site is still up) and check the photos on the preview.
2. In `.github/workflows/deploy.yml` remove the `BASE_PATH` lines. Rename `CNAME.golive` to `CNAME`, and set the custom domain `www.twofarmcottages.co.uk` under Settings → Pages (tick Enforce HTTPS once the certificate is issued).
3. DNS: point `www` with a CNAME record to `thursdaythinking-ai.github.io`; point the apex `twofarmcottages.co.uk` A records to 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 so it redirects to www.
4. Google Search Console: submit `https://www.twofarmcottages.co.uk/sitemap.xml`, then URL-inspect the homepage and room pages.
5. Keep the old hosting for about a week, then cancel it.
