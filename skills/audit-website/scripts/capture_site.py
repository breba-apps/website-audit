#!/usr/bin/env python3
"""
Playwright script to capture screenshots and SEO data for a list of URLs.

No dynamic discovery — it visits only the URLs it is given.

Usage:
    python3 capture_site.py <output_dir> <url> [<url> ...]
    python3 capture_site.py <output_dir>            # reads <output_dir>/urls.json

urls.json format: {"urls": ["https://example.com", "https://example.com/pricing"]}
"""

import sys
import json
import time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


def scroll_to_trigger_lazy_loads(page):
    """Scroll down the page in steps to trigger lazy-loaded content, then scroll back to top."""
    scroll_height = page.evaluate("document.body.scrollHeight")
    viewport_height = page.evaluate("window.innerHeight")
    position = 0
    step = viewport_height
    while position < scroll_height:
        page.evaluate(f"window.scrollTo(0, {position})")
        page.wait_for_timeout(150)
        position += step
        scroll_height = page.evaluate("document.body.scrollHeight")
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)


def extract_seo(page, url):
    """Extract SEO-relevant data from the current page via JS evaluation."""
    return page.evaluate(r"""
        (url) => {
            const get = (sel, attr) => {
                const el = document.querySelector(sel);
                return el ? (attr ? el.getAttribute(attr) : el.innerText.trim()) : null;
            };
            const getAll = (sel, attr) =>
                Array.from(document.querySelectorAll(sel)).map(el =>
                    attr ? el.getAttribute(attr) : el.innerText.trim()
                ).filter(Boolean);

            const headings = {};
            ['h1','h2','h3'].forEach(tag => {
                headings[tag] = getAll(tag);
            });

            const imagesNoAlt = Array.from(document.querySelectorAll('img')).filter(
                img => !img.getAttribute('alt') || img.getAttribute('alt').trim() === ''
            ).map(img => img.getAttribute('src') || '(no src)');

            const images = Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.getAttribute('src'),
                alt: img.getAttribute('alt') || null,
            }));

            const jsonLd = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                .map(s => { try { return JSON.parse(s.innerText); } catch(e) { return null; } })
                .filter(Boolean);

            const parsed = new URL(url);
            const allLinks = Array.from(document.querySelectorAll('a[href]'));
            const internalLinks = allLinks
                .filter(a => !a.href.startsWith('http') || a.href.includes(parsed.hostname))
                .map(a => ({ text: a.innerText.trim(), href: a.getAttribute('href') }));
            const externalLinks = allLinks
                .filter(a => a.href.startsWith('http') && !a.href.includes(parsed.hostname))
                .map(a => ({ text: a.innerText.trim(), href: a.href }));

            return {
                url,
                title: document.title,
                metaDescription: get('meta[name="description"]', 'content'),
                metaRobots: get('meta[name="robots"]', 'content'),
                canonical: get('link[rel="canonical"]', 'href'),
                og: {
                    title:       get('meta[property="og:title"]',       'content'),
                    description: get('meta[property="og:description"]', 'content'),
                    image:       get('meta[property="og:image"]',       'content'),
                    type:        get('meta[property="og:type"]',        'content'),
                    url:         get('meta[property="og:url"]',         'content'),
                },
                twitter: {
                    card:        get('meta[name="twitter:card"]',        'content'),
                    title:       get('meta[name="twitter:title"]',       'content'),
                    description: get('meta[name="twitter:description"]', 'content'),
                    image:       get('meta[name="twitter:image"]',       'content'),
                },
                headings,
                imagesTotal: images.length,
                imagesMissingAlt: imagesNoAlt,
                jsonLd,
                internalLinkCount: internalLinks.length,
                externalLinkCount: externalLinks.length,
                externalLinks,
                wordCount: (document.body.innerText.match(/[^\s]+/g) || []).length,
            };
        }
    """, url)


def url_to_slug(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "home"
    return "page_" + path.replace("/", "_").replace("-", "_")[:30]


def capture_page(page, url, slug, out, captured, seo_pages):
    print(f"  Visiting: {url}")
    page.goto(url, wait_until="networkidle", timeout=25000)
    page.wait_for_timeout(1500)

    print(f"    Scrolling to trigger lazy loads...")
    scroll_to_trigger_lazy_loads(page)

    full_path = out / f"{slug}_full.png"
    page.screenshot(path=str(full_path), full_page=True)
    captured.append((f"{slug} (full page)", str(full_path)))
    print(f"    Saved: {full_path}")

    vp_path = out / f"{slug}_viewport.png"
    page.screenshot(path=str(vp_path), full_page=False)
    captured.append((f"{slug} (viewport)", str(vp_path)))
    print(f"    Saved: {vp_path}")

    seo = extract_seo(page, url)
    seo_pages[slug] = seo
    print(f"    SEO: title='{seo.get('title', '')}' h1s={seo.get('headings', {}).get('h1', [])}")


def take_screenshots(output_dir: str, urls=None):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if urls:
        print(f"Loaded {len(urls)} URL(s) from the command line")
    else:
        urls_file = out / "urls.json"
        if not urls_file.exists():
            raise SystemExit(
                f"No URLs given and no {urls_file}.\n"
                f"Usage: python3 capture_site.py <output_dir> <url> [<url> ...]"
            )
        with open(urls_file) as f:
            data = json.load(f)
        urls = data.get("urls", [])
        if not urls:
            raise SystemExit(f"No URLs found in {urls_file}")
        print(f"Loaded {len(urls)} URL(s) from {urls_file}")

    captured = []
    seo_pages = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for url in urls:
            slug = url_to_slug(url)
            try:
                capture_page(page, url, slug, out, captured, seo_pages)
            except Exception as e:
                print(f"    Warning: could not capture {url}: {e}")

        browser.close()

    # Write screenshot manifest
    manifest_path = out / "manifest.txt"
    with open(manifest_path, "w") as f:
        f.write(f"Screenshots — {len(captured)} captured\n\n")
        for label, path in captured:
            f.write(f"{label}\n  {path}\n")

    # Write SEO JSON
    seo_path = out / "seo.json"
    with open(seo_path, "w") as f:
        json.dump(seo_pages, f, indent=2)

    # Write human-readable SEO summary
    seo_summary_path = out / "seo_summary.txt"
    with open(seo_summary_path, "w") as f:
        f.write(f"SEO Summary\nCaptured: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        for slug, seo in seo_pages.items():
            f.write(f"{'='*60}\n")
            f.write(f"PAGE: {slug}  ({seo.get('url', '')})\n")
            f.write(f"{'='*60}\n")
            f.write(f"  Title:            {seo.get('title') or '(missing)'}\n")
            f.write(f"  Meta description: {seo.get('metaDescription') or '(missing)'}\n")
            f.write(f"  Canonical:        {seo.get('canonical') or '(missing)'}\n")
            f.write(f"  Meta robots:      {seo.get('metaRobots') or '(not set)'}\n")
            f.write(f"  Word count:       {seo.get('wordCount', 0)}\n")
            og = seo.get('og', {})
            f.write(f"  OG title:         {og.get('title') or '(missing)'}\n")
            f.write(f"  OG description:   {og.get('description') or '(missing)'}\n")
            f.write(f"  OG image:         {og.get('image') or '(missing)'}\n")
            tw = seo.get('twitter', {})
            f.write(f"  Twitter card:     {tw.get('card') or '(missing)'}\n")
            headings = seo.get('headings', {})
            f.write(f"  H1s:              {headings.get('h1') or '(none)'}\n")
            f.write(f"  H2s:              {headings.get('h2') or '(none)'}\n")
            f.write(f"  H3s:              {headings.get('h3') or '(none)'}\n")
            missing_alt = seo.get('imagesMissingAlt', [])
            f.write(f"  Images total:     {seo.get('imagesTotal', 0)}\n")
            f.write(f"  Images no alt:    {len(missing_alt)}")
            if missing_alt:
                f.write(f"\n    {chr(10).join('    ' + s for s in missing_alt[:5])}")
                if len(missing_alt) > 5:
                    f.write(f"\n    ... and {len(missing_alt)-5} more")
            f.write(f"\n")
            json_ld = seo.get('jsonLd', [])
            if json_ld:
                types = [item.get('@type', '?') for item in json_ld]
                f.write(f"  JSON-LD types:    {types}\n")
            else:
                f.write(f"  JSON-LD:          (none)\n")
            ext_links = seo.get('externalLinks', [])
            f.write(f"  External links:   {len(ext_links)}\n")
            f.write("\n")

    print(f"\nDone.")
    print(f"  {len(captured)} screenshots → {out}")
    print(f"  SEO data      → {seo_path}")
    print(f"  SEO summary   → {seo_summary_path}")
    return captured, seo_pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python3 capture_site.py <output_dir> <url> [<url> ...]\n"
            "       python3 capture_site.py <output_dir>   # reads <output_dir>/urls.json"
        )
    take_screenshots(sys.argv[1], sys.argv[2:])
