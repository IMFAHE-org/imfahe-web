#!/usr/bin/env python3
"""Render editable HTML fragments with the shared IMFAHE page template."""
import argparse
from html import escape
import json
from pathlib import Path
from string import Template
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
CONTENT = ROOT / "content"
TEMPLATE = Template((ROOT / "templates/page.html").read_text())
PAGES = json.loads((CONTENT / "pages.json").read_text())
MENU = json.loads((CONTENT / "navigation.json").read_text())


def icon(name):
    return f'<img class="icon" src="@site@/assets/icons/{name}.svg" width="20" height="20" alt="">'


def home_logo():
    return (
        '<a href="@site@/" class="logo" aria-label="IMFAHE home">'
        '<img src="@site@/assets/images/imfahe-logo.png" width="325" height="155" alt="IMFAHE">'
        '</a>'
    )


def navigation_items(route):
    items = []
    for item in MENU["pages"]:
        label = escape(item["label"])
        if "children" in item:
            links = "".join(
                f'<li>{menu_link(child, route)}</li>' for child in item["children"]
            )
            items.append(
                f'<details class="nav-group"><summary>{label} {icon("chevron-down")}</summary>'
                f'<ul>{links}</ul></details>'
            )
        else:
            items.append(menu_link(item, route, item["path"] == "contact/"))
    return "\n      ".join(items)


def menu_link(item, route, button=False):
    current = ' aria-current="page"' if item["path"] == route else ""
    style = ' class="button button--outline"' if button else ""
    return f'<a href="@site@/{escape(item["path"], quote=True)}"{style}{current}>{escape(item["label"])}</a>'


def header(route):
    items = navigation_items(route)
    return f'''  <header class="site-header">
    <div class="wrap header-inner">
      {home_logo()}
      <nav class="main-nav" aria-label="Main navigation">
      {items}
      </nav>
      <details class="mobile-nav">
        <summary>{icon("menu")} Menu</summary>
        <nav aria-label="Main navigation">
      {items}
        </nav>
      </details>
    </div>
  </header>'''


def footer():
    social_links = "\n".join(
        f'<a href="{escape(item["url"], quote=True)}">{escape(item["label"])}</a>'
        for item in MENU["socials"]
    )
    return f'''  <footer class="site-footer">
    <div class="wrap footer-inner">
      {home_logo()}
      <div><p>Copyright © 2026</p><a href="@site@/">imfahe.org</a><p>All rights reserved.</p></div>
      <div><a href="#top">Back to Top {icon("arrow-up")}</a><br><a href="@site@/economical-disclosure/">Non-Profit Information</a></div>
      <nav class="socials" aria-label="Social media">{social_links}</nav>
    </div>
  </footer>'''


def render(page, origin):
    route = page["route"]
    base = "/".join([".."] * route.count("/")) if route else "."
    canonical = ""
    if origin:
        url = escape(origin + route, quote=True)
        canonical = f'  <link rel="canonical" href="{url}">\n  <meta property="og:url" content="{url}">'
    return TEMPLATE.substitute(
        title=escape(page["title"]),
        description=escape(page["description"], quote=True),
        base=base,
        canonical=canonical,
        header=header(route),
        content=(CONTENT / f'{page["slug"]}.html').read_text().rstrip(),
        footer=footer(),
    ).replace("@site@", base)


def write_sitemap(origin):
    sitemap_path = SITE / "sitemap.xml"
    if not origin:
        sitemap_path.unlink(missing_ok=True)
        (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\n")
        return

    sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for page in PAGES:
        ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = origin + page["route"]
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(sitemap_path, encoding="utf-8", xml_declaration=True)
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {origin}sitemap.xml\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default="", help="Published URL of the homepage, including the GitHub project path.")
    args = parser.parse_args()
    origin = args.origin.rstrip("/") + "/" if args.origin else ""
    if origin:
        url = urlsplit(origin)
        if url.scheme != "https" or not url.netloc or url.query or url.fragment:
            parser.error("--origin must be an absolute HTTPS homepage URL")
    for page in PAGES:
        target = SITE / page["route"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page, origin))
    write_sitemap(origin)
    home = escape(origin or "./", quote=True)
    (SITE / "404.html").write_text(f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | IMFAHE</title>
<style>body{{font:1rem/1.6 system-ui,sans-serif;margin:clamp(1.25rem,10vw,6rem);color:#212529}}a{{color:#c1272d}}</style></head>
<body><main><h1>Page not found</h1><p><a href="{home}">Return to IMFAHE</a></p></main></body>
</html>
''')
    print(f"Built {len(PAGES)} IMFAHE pages.")


if __name__ == "__main__":
    main()
