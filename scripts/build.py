#!/usr/bin/env python3
"""Render editable HTML fragments with the shared IMFAHE page template."""
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
from string import Template
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
CONTENT = ROOT / "content"
TEMPLATE = Template((ROOT / "templates/page.html").read_text())
PAGES = json.loads((CONTENT / "pages.json").read_text())
MENU = json.loads((CONTENT / "navigation.json").read_text())
I18N = json.loads((CONTENT / "i18n.json").read_text())
LANGS = list(I18N)  # first language is the default and lives at the site root
CSS_VERSION = sha256((SITE / "assets/site.css").read_bytes()).hexdigest()[:10]
JS_VERSION = sha256((SITE / "assets/site.js").read_bytes()).hexdigest()[:10]
ICON_TOKEN = re.compile(r"@(icon|brand):([a-z0-9-]+)@")


def prefix(lang):
    return "" if lang == LANGS[0] else f"{lang}/"


def ui(lang, key):
    return I18N[lang]["ui"].get(key) or I18N[LANGS[0]]["ui"][key]


def label(lang, text):
    """Translate a navigation label or tagline; English text is the key."""
    return I18N[lang].get("nav", {}).get(text, text)


def fragment(page, lang):
    folder = CONTENT if lang == LANGS[0] else CONTENT / lang
    return folder / f'{page["slug"]}.html'


def meta(page, lang, field):
    return I18N[lang].get("pages", {}).get(page["slug"], {}).get(field) or page[field]


def icon(kind, name):
    """Inline an SVG so it takes the text color. Lucide icons are stroked, brand logos are filled."""
    folder = "icons" if kind == "icon" else "brands"
    svg = (SITE / "assets" / folder / f"{name}.svg").read_text()
    svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    fill = "" if kind == "icon" else ' fill="currentColor"'
    start = f'<svg class="icon" aria-hidden="true" focusable="false" width="24" height="24"{fill}'
    # Only the root tag loses its own size and class; shapes inside keep their width and height.
    svg = re.sub(r"<svg\b[^>]*>", lambda tag: re.sub(r'\s(class|width|height|role)="[^"]*"', "", tag[0]).replace("<svg", start, 1), svg, count=1)
    return re.sub(r"\s*\n\s*", " ", svg).strip()


def icons(html):
    return ICON_TOKEN.sub(lambda match: icon(match[1], match[2]), html)


def home_logo():
    return (
        '<a href="@site@/" class="logo" aria-label="IMFAHE">'
        '<img src="@site@/assets/images/imfahe-logo.png" width="325" height="155" alt="IMFAHE">'
        '</a>'
    )


def menu_link(item, route, lang, button=False, tagline=False):
    current = ' aria-current="page"' if item["path"] == route else ""
    style = ' class="button"' if button else ""
    text = f'<span class="nav-label">{escape(label(lang, item["label"]))}</span>' if tagline else escape(label(lang, item["label"]))
    if tagline and item.get("tagline"):
        text += f'<span class="nav-tagline">{escape(label(lang, item["tagline"]))}</span>'
    return f'<a href="@site@/{escape(item["path"], quote=True)}"{style}{current}>{text}</a>'


def navigation_items(route, lang):
    items = []
    for item in MENU["pages"]:
        if "children" in item:
            links = "".join(
                f'<li>{menu_link(child, route, lang, tagline=True)}</li>' for child in item["children"]
            )
            active = ' data-active' if any(child["path"] == route for child in item["children"]) else ""
            items.append(
                f'<details class="nav-group" name="nav"{active}><summary>{escape(label(lang, item["label"]))} @icon:chevron-down@</summary>'
                f'<ul>{links}</ul></details>'
            )
        else:
            items.append(menu_link(item, route, lang, item["path"] == "contact/"))
    return "\n      ".join(items)


def language_switch(page, route, lang):
    links = []
    for other in LANGS:
        if not fragment(page, other).exists():
            continue
        current = ' aria-current="true"' if other == lang else ""
        links.append(
            f'<li><a href="@root@/{prefix(other)}{route}" lang="{I18N[other]["htmlLang"]}" hreflang="{I18N[other]["htmlLang"]}"'
            f' title="{escape(I18N[other]["name"], quote=True)}"{current}>{other.upper()}</a></li>'
        )
    if len(links) < 2:
        return ""
    return f'<ul class="lang-switch" aria-label="{escape(ui(lang, "language"), quote=True)}">{"".join(links)}</ul>'


def header(page, route, lang):
    items = navigation_items(route, lang)
    switch = language_switch(page, route, lang)
    nav_name = escape(ui(lang, "mainNavigation"), quote=True)
    return f'''  <header class="site-header">
    <div class="wrap header-inner">
      {home_logo()}
      <nav class="main-nav" aria-label="{nav_name}">
      {items}
      </nav>
      {switch}
      <details class="mobile-nav">
        <summary>@icon:menu@ {escape(ui(lang, "menu"))}</summary>
        <nav aria-label="{nav_name}">
      {items}
      {switch}
        </nav>
      </details>
    </div>
  </header>'''


def related(route, lang):
    """Sibling programs, shown at the foot of a program page instead of a second menu."""
    for item in MENU["pages"]:
        children = item.get("children", [])
        if not any(child["path"] == route for child in children):
            continue
        cards = "".join(
            f'<li><a class="related-card" href="@site@/{escape(child["path"], quote=True)}">'
            f'<span class="nav-label">{escape(label(lang, child["label"]))}</span>'
            f'<span class="nav-tagline">{escape(label(lang, child.get("tagline", "")))}</span>@icon:arrow-right@</a></li>'
            for child in children if child["path"] != route
        )
        title = ui(lang, "moreIn").format(group=label(lang, item["label"]))
        return f'''
<section class="section related"><div class="wrap section-layout">
<h2>{escape(title)}</h2>
<ul class="related-list">{cards}</ul>
</div></section>'''
    return ""


def footer(lang):
    social_links = "".join(
        f'<a href="{escape(item["url"], quote=True)}" aria-label="{escape(item["label"], quote=True)}" title="{escape(item["label"], quote=True)}">@brand:{item["label"].lower()}@</a>'
        for item in MENU["socials"]
    )
    email = MENU["email"]
    return f'''  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-brand">
        {home_logo()}
        <p>{escape(ui(lang, "nonprofit"))}</p>
      </div>
      <ul class="footer-links">
        <li><a href="mailto:{email}">@icon:mail@ {email}</a></li>
        <li><a href="@site@/economical-disclosure/">{escape(ui(lang, "nonprofitInfo"))}</a></li>
        <li><a href="#top">{escape(ui(lang, "backToTop"))} @icon:arrow-up@</a></li>
      </ul>
      <nav class="socials" aria-label="{escape(ui(lang, "socialMedia"), quote=True)}">{social_links}</nav>
      <p class="footer-legal">Copyright © 2026 <a href="@site@/">imfahe.org</a>. {escape(ui(lang, "rights"))}</p>
    </div>
  </footer>'''


def head_links(page, route, lang, origin):
    if not origin:
        return ""
    url = escape(origin + prefix(lang) + route, quote=True)
    lines = [f'  <link rel="canonical" href="{url}">', f'  <meta property="og:url" content="{url}">']
    for other in LANGS:
        if fragment(page, other).exists():
            lines.append(
                f'  <link rel="alternate" hreflang="{I18N[other]["htmlLang"]}" href="{escape(origin + prefix(other) + route, quote=True)}">'
            )
    image = page.get("image") or MENU["shareImage"]
    lines.append(f'  <meta property="og:image" content="{escape(origin + "assets/images/" + image, quote=True)}">')
    return "\n".join(lines)


def render(page, lang, origin):
    route = page["route"]
    depth = (prefix(lang) + route).count("/")
    base = "/".join([".."] * depth) if depth else "."
    html = TEMPLATE.substitute(
        lang=I18N[lang]["htmlLang"],
        title=escape(meta(page, lang, "title")),
        description=escape(meta(page, lang, "description"), quote=True),
        skip=escape(ui(lang, "skip")),
        base=base,
        css_version=CSS_VERSION,
        js_version=JS_VERSION,
        head_links=head_links(page, route, lang, origin),
        header=header(page, route, lang),
        content=fragment(page, lang).read_text().rstrip() + related(route, lang),
        footer=footer(lang),
    )
    # Assets are shared by every language; page links stay inside the current language.
    html = html.replace("@root@", base).replace("@site@/assets/", f"{base}/assets/").replace("@site@/", f"{base}/{prefix(lang)}")
    return icons(html)


def write_sitemap(origin, routes):
    sitemap_path = SITE / "sitemap.xml"
    if not origin:
        sitemap_path.unlink(missing_ok=True)
        (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\n")
        return

    sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for route in routes:
        ET.SubElement(ET.SubElement(sitemap, "url"), "loc").text = origin + route
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
    routes = []
    for lang in LANGS:
        for page in PAGES:
            if not fragment(page, lang).exists():
                continue
            target = SITE / prefix(lang) / page["route"] / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render(page, lang, origin))
            routes.append(prefix(lang) + page["route"])
    write_sitemap(origin, routes)
    home = escape(origin or "./", quote=True)
    (SITE / "404.html").write_text(f'''<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | IMFAHE</title>
<style>body{{font:1rem/1.6 system-ui,sans-serif;margin:clamp(1.25rem,10vw,6rem);color:#3a3a3a}}a{{color:#c20e24}}</style></head>
<body><main><h1>Page not found</h1><p><a href="{home}">Return to IMFAHE</a></p></main></body>
</html>
''')
    print(f"Built {len(routes)} IMFAHE pages in {len(LANGS)} languages.")


if __name__ == "__main__":
    main()
