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


def home_of(path, lang):
    """Where links to a page start: its own language, or the default language when it has no translation."""
    page = next((item for item in PAGES if item["route"] == path), None)
    return "@site@" if page is None or fragment(page, lang).exists() else "@root@"


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
    return f'<a href="{home_of(item["path"], lang)}/{escape(item["path"], quote=True)}"{style}{current}>{text}</a>'


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
        if page["slug"] == "404" or not fragment(page, other).exists():
            continue
        current = ' aria-current="true"' if other == lang else ""
        links.append(
            f'<li><a href="@root@/{prefix(other)}{escape(route, quote=True)}" lang="{escape(I18N[other]["htmlLang"], quote=True)}" hreflang="{escape(I18N[other]["htmlLang"], quote=True)}"'
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
            f'<li><a class="related-card" href="{home_of(child["path"], lang)}/{escape(child["path"], quote=True)}">'
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


def join_block(lang):
    """Three ways into IMFAHE, shown at the top of the footer on every page."""
    join = MENU["join"]
    ways = [
        ("joinStudent", f'@site@/{join["calls"]}'),
        ("joinMentor", join["mentorForm"]),
        ("joinOrg", f'mailto:{MENU["email"]}'),  # escaped below with the other links
    ]
    items = "".join(
        f'<li><h3>{escape(ui(lang, key))}</h3><p>{escape(ui(lang, key + "Text"))}</p>'
        f'<a class="link-arrow" href="{escape(href, quote=True)}">{escape(ui(lang, key + "Action"))} @icon:arrow-right@</a></li>'
        for key, href in ways
    )
    return f'''<section class="footer-join" aria-labelledby="join-title">
        <h2 id="join-title">{escape(ui(lang, "joinTitle"))}</h2>
        <ul class="join-list">{items}</ul>
      </section>'''


def footer(page, route, lang):
    social_links = "".join(
        f'<a href="{escape(item["url"], quote=True)}" aria-label="{escape(item["label"], quote=True)}" title="{escape(item["label"], quote=True)}">@brand:{item["label"].lower()}@</a>'
        for item in MENU["socials"]
    )
    columns = "".join(
        f'<div><h3>{escape(label(lang, item["label"]))}</h3><ul>'
        + "".join(f'<li>{menu_link(child, route, lang)}</li>' for child in item["children"])
        + '</ul></div>'
        for item in MENU["pages"] if "children" in item
    )
    email = escape(MENU["email"], quote=True)
    links = "".join(f'<li>{menu_link(item, route, lang)}</li>' for item in MENU["pages"] if "children" not in item)
    return f'''  <footer class="site-footer">
    <div class="wrap">
      {join_block(lang)}
      <div class="footer-main">
        <div class="footer-brand">
          {home_logo()}
          <p>{escape(ui(lang, "nonprofit"))}</p>
          <nav class="socials" aria-label="{escape(ui(lang, "socialMedia"), quote=True)}">{social_links}</nav>
        </div>
        <nav class="footer-nav" aria-label="{escape(ui(lang, "programs"), quote=True)}">{columns}</nav>
      </div>
      <div class="footer-legal">
        <ul class="footer-links">
          {links}
          <li><a href="@site@/economical-disclosure/">{escape(ui(lang, "financial"))}</a></li>
          <li><a href="mailto:{email}?subject={escape(ui(lang, "support"), quote=True).replace(" ", "%20")}">{escape(ui(lang, "support"))}</a></li>
        </ul>
        {language_switch(page, route, lang)}
        <p>Copyright © 2026 {escape(MENU["legalName"])} (<a href="@site@/">imfahe.org</a>). {escape(ui(lang, "rights"))}</p>
      </div>
    </div>
  </footer>'''


def new_tab_links(html):
    """Links that leave the site, and PDF files, open in a new tab. One rule for every page."""
    def fix(match):
        tag = match[0]
        href = re.search(r'href="([^"]*)"', tag)
        if not href or not (href[1].startswith(("http://", "https://")) or href[1].lower().endswith(".pdf")):
            return tag
        rel = re.search(r'\srel="([^"]*)"', tag)
        tokens = dict.fromkeys((rel[1].split() if rel else []) + ["noopener"])  # keep nofollow, noreferrer and the like
        tag = re.sub(r'\s(target|rel)="[^"]*"', "", tag)
        return tag[:-1] + f' target="_blank" rel="{" ".join(tokens)}">'
    return re.sub(r"<a\b[^>]*>", fix, html)


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
        lang=escape(I18N[lang]["htmlLang"], quote=True),
        title=escape(meta(page, lang, "title")),
        description=escape(meta(page, lang, "description"), quote=True),
        skip=escape(ui(lang, "skip")),
        base=base,
        css_version=CSS_VERSION,
        js_version=JS_VERSION,
        head_links=head_links(page, route, lang, origin),
        header=header(page, route, lang),
        content=fragment(page, lang).read_text().rstrip() + related(route, lang),
        footer=footer(page, route, lang),
    )
    # Assets are shared by every language; page links stay inside the current language.
    html = html.replace("@root@", base).replace("@site@/assets/", f"{base}/assets/").replace("@site@/", f"{base}/{prefix(lang)}")
    return new_tab_links(icons(html))


def not_found(origin):
    """GitHub Pages serves this file for any missing address, so its links must not be relative."""
    root = urlsplit(origin).path.rstrip("/") if origin else "."
    page = {"slug": "404", "route": "", "title": "Page not found - imfahe.org", "description": "Page not found."}
    first = LANGS[0]
    blocks = "".join(
        f'<div class="stack" lang="{I18N[lang]["htmlLang"]}"><h2>{escape(ui(lang, "notFoundTitle"))}</h2>'
        f'<p>{escape(ui(lang, "notFoundText"))}</p>'
        f'<a class="link-arrow" href="@root@/{prefix(lang)}">{escape(ui(lang, "notFoundHome"))} @icon:arrow-right@</a></div>'
        for lang in LANGS[1:]
    )
    content = f'''<section class="section section--hero">
<div class="wrap hero hero--single">
<h1>{escape(ui(first, "notFoundTitle"))}</h1>
<p class="lead">{escape(ui(first, "notFoundText"))}</p>
<a class="button" href="@root@/">{escape(ui(first, "notFoundHome"))}</a>
</div>
</section>
<section class="section section--slim section--tint"><div class="wrap"><div class="split">{blocks}</div></div></section>'''
    html = TEMPLATE.substitute(
        lang=I18N[first]["htmlLang"], title=escape(page["title"]), description=escape(page["description"], quote=True),
        skip=escape(ui(first, "skip")), base=root, css_version=CSS_VERSION, js_version=JS_VERSION,
        head_links='  <meta name="robots" content="noindex">', header=header(page, "404", first), content=content,
        footer=footer(page, "404", first),
    )
    html = html.replace("@root@", root).replace("@site@/assets/", f"{root}/assets/").replace("@site@/", f"{root}/")
    return new_tab_links(icons(html))


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
    (SITE / "404.html").write_text(not_found(origin))
    print(f"Built {len(routes)} IMFAHE pages in {len(LANGS)} languages.")


if __name__ == "__main__":
    main()
