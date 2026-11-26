#!/usr/bin/env python3
"""Build the Two Farm Cottages static site into _site/.

Content lives in content/*.html (page body only). Page settings (URL, title,
description) are in PAGES below. Every page is written as <slug>/index.html so
URLs keep the trailing slash used by the old WordPress site.

Run:  python3 build.py
"""
import json
import os
import re
import pathlib
import shutil
from datetime import date

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "_site"
SITE = "https://www.twofarmcottages.co.uk"
UP = "/wp-content/uploads"
# Path prefix for the github.io preview (e.g. "/twofarmcottages"). Empty once the real domain is live.
BASE = os.environ.get("BASE_PATH", "").rstrip("/")

BUSINESS = {
    "name": "Two Farm Cottages",
    "people": "Janet & Mike Wright",
    "street": "Rackham Road",
    "locality": "Amberley",
    "region": "West Sussex",
    "postcode": "BN18 9NT",
    "tel": "+44 (0)1798 831266",
    "tel_link": "+441798831266",
    "mob": "07379 100061",
    "mob_link": "+447379100061",
    "email": "mikewright45@icloud.com",
}

# slug -> settings. Slug "" is the homepage. Titles match the old site.
PAGES = [
    {"slug": "", "file": "home", "nav": "Home",
     "title": "Bed and Breakfast on the South Downs Way - Amberley, West Sussex",
     "h1": "Bed and Breakfast on the South Downs Way",
     "desc": "Luxury B&B in Amberley, West Sussex, on the South Downs Way. Two private rooms in a 1890s farm cottage with views of the Downs and the Wildbrooks, and award-nominated breakfasts.",
     "image": f"{UP}/2016/05/IMG_0401-1.jpg"},
    {"slug": "double-bedroom", "file": "double-bedroom", "nav": "Double Room",
     "title": "Double Bedroom - Two Farm Cottages",
     "h1": "Double Bedroom",
     "desc": "The south-facing double room at Two Farm Cottages, Amberley, with panoramic views of the South Downs, hospitality tray, TV and free WiFi.",
     "image": f"{UP}/2016/05/IMG_0347.jpg"},
    {"slug": "twin-bedroom", "file": "twin-bedroom", "nav": "Twin Room",
     "title": "Twin Bedroom - Two Farm Cottages",
     "h1": "Twin-Bedded Room",
     "desc": "The north-facing twin room at Two Farm Cottages, Amberley, overlooking the Amberley Wildbrooks, with hospitality tray, TV and free WiFi.",
     "image": f"{UP}/2016/05/IMG_0370.jpg"},
    {"slug": "about-us", "file": "about-us", "nav": "About Us",
     "title": "About Us - Two Farm Cottages",
     "h1": "About Us",
     "desc": "Meet Janet and Mike Wright, B&B hosts in Amberley since 2002, plus Connie the Great Dane and Mack and Mabel the cats.",
     "image": f"{UP}/2011/06/Janet-mike-150x150.jpg"},
    {"slug": "sample-menu", "file": "sample-menu", "nav": "Breakfast Menu",
     "title": "Sample Menu - Two Farm Cottages",
     "h1": "Sample Breakfast Menu",
     "desc": "A typical breakfast at Two Farm Cottages, Amberley: compote, Irish porridge, apple pancakes, the Amberley Monty and home-baked bread.",
     "image": f"{UP}/2016/05/IMG_0410-3.jpg"},
    {"slug": "tariff", "file": "tariff", "nav": "Tariff",
     "title": "Tariff - Two Farm Cottages",
     "h1": "Tariff",
     "desc": "Room rates at Two Farm Cottages B&B, Amberley: prices per person per night, children's rates and a 10% discount for stays of 3 nights or more.",
     "image": None},
    {"slug": "places-to-visit", "file": "places-to-visit", "nav": "Places to Visit",
     "title": "Places to Visit - Two Farm Cottages",
     "h1": "Places to Visit",
     "desc": "Places to visit near Amberley: Arundel Castle, Chichester Cathedral and Festival Theatre, Parham, Petworth, Bignor and Fishbourne Roman sites, and Goodwood.",
     "image": f"{UP}/2016/05/arundel_castle-1.jpg", "post": True},
    {"slug": "about-amberley", "file": "about-amberley", "nav": "About Amberley",
     "title": "About Amberley - Two Farm Cottages",
     "h1": "About Amberley",
     "desc": "Amberley, the 'Pearl of Sussex': St Michael's Church, Amberley Castle, the Wildbrooks and a village at the foot of the South Downs.",
     "image": f"{UP}/2016/05/amberley.jpg", "post": True},
    {"slug": "new-site-new-location", "file": "new-site-new-location", "nav": None,
     "title": "New Site and New Location! - Two Farm Cottages",
     "h1": "New Site and New Location!",
     "desc": "Janet and Mike have moved their Amberley B&B from Stream Cottage to Two Farm Cottages, at the foot of the South Downs.",
     "image": f"{UP}/2016/05/IMG_0351.jpg", "post": True},
    {"slug": "contact", "file": "contact", "nav": "Contact & Booking",
     "title": "Contact - Two Farm Cottages",
     "h1": "Contact & Booking",
     "desc": "Book or enquire at Two Farm Cottages B&B, Rackham Road, Amberley, West Sussex BN18 9NT. Call 01798 831266 or email Janet and Mike.",
     "image": None},
]

# Old WordPress URLs with no equivalent page: send to the closest page.
REDIRECTS = {
    "category/the-area": "/places-to-visit/",
    "author/mikewr": "/about-us/",
    "author/admin": "/about-us/",
    "feed": "/",
    "comments/feed": "/",
    "sitemap_index.xml": None,  # handled by sitemap.xml
}


def esc(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def url(slug):
    return "/" if not slug else f"/{slug}/"


def schema():
    b = BUSINESS
    data = {
        "@context": "https://schema.org",
        "@type": "BedAndBreakfast",
        "@id": SITE + "/#business",
        "name": b["name"],
        "url": SITE + "/",
        "description": PAGES[0]["desc"],
        "image": SITE + PAGES[0]["image"],
        "logo": SITE + f"{UP}/2016/05/Farm-logo.jpg",
        "telephone": "+44 1798 831266",
        "email": b["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": b["street"],
            "addressLocality": b["locality"],
            "addressRegion": b["region"],
            "postalCode": b["postcode"],
            "addressCountry": "GB",
        },
        "hasMap": "https://www.google.com/maps/search/?api=1&query=Two+Farm+Cottages+Rackham+Road+Amberley+BN18+9NT",
        "checkinTime": "16:00",
        "checkoutTime": "10:30",
        "numberOfRooms": 2,
        "petsAllowed": False,
        "priceRange": "£££",
        "paymentAccepted": "Bank transfer (BACS), cheque, cash",
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True}
            for n in ["Free WiFi", "TV in room", "Tea and coffee making facilities",
                      "Private guest bathroom", "Private guest lounge", "Breakfast included"]
        ],
        "containedInPlace": {"@type": "Place", "name": "South Downs National Park"},
        "founder": [{"@type": "Person", "name": "Janet Wright"},
                    {"@type": "Person", "name": "Mike Wright"}],
    }
    return json.dumps(data, ensure_ascii=False, indent=1)


def breadcrumb(p):
    if not p["slug"]:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": p["h1"], "item": SITE + url(p["slug"])},
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def nav(active):
    items = []
    for p in PAGES:
        if not p["nav"]:
            continue
        cur = ' aria-current="page"' if p["slug"] == active else ""
        cls = ' class="nav-cta"' if p["slug"] == "contact" else ""
        items.append(f'<li{cls}><a href="{url(p["slug"])}"{cur}>{p["nav"]}</a></li>')
    return "\n".join(items)


def layout(p, body):
    b = BUSINESS
    canonical = SITE + url(p["slug"])
    og_img = SITE + (p["image"] or PAGES[0]["image"])
    home_schema = f'<script type="application/ld+json">{schema()}</script>' if not p["slug"] else ""
    hero = ""
    if not p["slug"]:
        hero = f'''<section class="hero" style="background-image:url('/assets/hero.jpg')">
  <div class="hero-inner">
    <p class="eyebrow">Amberley · South Downs National Park</p>
    <h1>{esc(p["h1"])}</h1>
    <p class="lede">Two private rooms in an 1890s farm cottage, with views of the Downs and the Wildbrooks, and a breakfast table that overflows.</p>
    <p><a class="btn" href="/contact/">Check availability</a> <a class="btn btn-ghost" href="/tariff/">See tariff</a></p>
  </div>
</section>'''
    else:
        hero = f'<header class="page-head"><div class="wrap"><h1>{esc(p["h1"])}</h1></div></header>'
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["desc"])}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Two Farm Cottages">
<meta property="og:title" content="{esc(p["title"])}">
<meta property="og:description" content="{esc(p["desc"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{UP}/2016/05/cropped-Farm-logo-32x32.jpg" sizes="32x32">
<link rel="apple-touch-icon" href="{UP}/2016/05/cropped-Farm-logo-180x180.jpg">
<link rel="stylesheet" href="/assets/style.css">
{home_schema}
{breadcrumb(p)}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="/">
      <img src="{UP}/2016/05/Farm-logo-266x300.jpg" alt="" width="40" height="45">
      <span><strong>Two Farm Cottages</strong><small>Bed &amp; Breakfast · Amberley</small></span>
    </a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav id="nav" aria-label="Main"><ul>
{nav(p["slug"])}
    </ul></nav>
  </div>
</header>
{hero}
<main id="main" class="wrap content">
{body}
</main>
<footer class="site-footer">
  <div class="wrap cols">
    <div>
      <h2>Two Farm Cottages</h2>
      <address>{b["people"]}<br>{b["street"]}<br>{b["locality"]}, {b["region"]}<br>{b["postcode"]}</address>
    </div>
    <div>
      <h2>Get in touch</h2>
      <p>Tel: <a href="tel:{b["tel_link"]}">{b["tel"]}</a><br>
      Mob: <a href="tel:{b["mob_link"]}">{b["mob"]}</a><br>
      Email: <a href="mailto:{b["email"]}">{b["email"]}</a></p>
    </div>
    <div>
      <h2>Useful info</h2>
      <ul class="plain">
        <li><a href="/places-to-visit/">Places to Visit</a></li>
        <li><a href="/about-amberley/">About Amberley</a></li>
        <li><a href="/new-site-new-location/">New Site and New Location</a></li>
      </ul>
    </div>
  </div>
  <p class="wrap legal">© {date.today().year} Two Farm Cottages, Amberley, West Sussex.</p>
</footer>
<script>
const b=document.querySelector('.menu-btn'),n=document.getElementById('nav');
b.addEventListener('click',()=>{{const o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)}});
</script>
</body>
</html>
'''


def redirect_page(target):
    t = SITE + target
    return f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8">
<title>Moved - Two Farm Cottages</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{t}">
<meta http-equiv="refresh" content="0; url={target}">
</head><body><p>This page has moved to <a href="{target}">{t}</a>.</p>
<script>location.replace("{target}")</script></body></html>
'''


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if (ROOT / "wp-content").exists():
        shutil.copytree(ROOT / "wp-content", OUT / "wp-content")
    for f in ["CNAME", "robots.txt", "llms.txt"]:
        if (ROOT / f).exists():
            shutil.copy(ROOT / f, OUT / f)
    (OUT / ".nojekyll").write_text("")

    for p in PAGES:
        body = (ROOT / "content" / f'{p["file"]}.html').read_text(encoding="utf-8")
        d = OUT / p["slug"] if p["slug"] else OUT
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(layout(p, body), encoding="utf-8")

    for src, target in REDIRECTS.items():
        if not target:
            continue
        d = OUT / src
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(redirect_page(target), encoding="utf-8")

    nf = {"slug": "404", "nav": None, "title": "Page not found - Two Farm Cottages",
          "h1": "Page not found", "desc": "This page could not be found.", "image": None}
    (OUT / "404.html").write_text(
        layout(nf, '<p>Sorry, that page isn\'t here. Try the <a href="/">homepage</a> or <a href="/contact/">get in touch</a>.</p>')
        .replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"'),
        encoding="utf-8")

    today = date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{SITE}{url(p['slug'])}</loc><lastmod>{today}</lastmod></url>" for p in PAGES)
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    (OUT / "sitemap.xml").write_text(xml)
    # Old Yoast sitemap address, so Search Console's saved sitemap keeps working.
    (OUT / "sitemap_index.xml").write_text(xml)
    if BASE:
        for f in OUT.rglob("*.html"):
            h = f.read_text(encoding="utf-8")
            h = re.sub(r'(href|src|content)="/(?!/)', rf'\1="{BASE}/', h)
            h = h.replace("url('/", f"url('{BASE}/").replace('location.replace("/', f'location.replace("{BASE}/')
            f.write_text(h, encoding="utf-8")
    print(f"Built {len(PAGES)} pages into {OUT}" + (f" with base path {BASE}" if BASE else ""))


if __name__ == "__main__":
    main()
