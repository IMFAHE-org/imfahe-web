#!/usr/bin/env python3
"""Render editable HTML fragments with the shared IMFAHE page template."""
import argparse
from hashlib import sha256
from html import escape
from functools import cache
import json
from math import cos, hypot, sin, sqrt
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
CALLS = json.loads((CONTENT / "calls.json").read_text())
NETWORK = json.loads((CONTENT / "network.json").read_text())
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
                f'<li>{menu_link(child, route, lang)}</li>' for child in item["children"]
            )
            active = ' data-active' if any(child["path"] == route for child in item["children"]) else ""
            items.append(
                f'<details class="nav-group" name="nav"{active}><summary>{escape(label(lang, item["label"]))} @icon:chevron-down@</summary>'
                f'<ul>{links}</ul></details>'
            )
        else:
            items.append(menu_link(item, route, lang, item["path"] == "contact/"))
    return "\n      ".join(items)


def language_switch(page, route, lang, menu=False):
    """The header bar gets one small dropdown; the phone panel gets a row of pills."""
    links = []
    for other in LANGS:
        if page["slug"] == "404" or not fragment(page, other).exists():
            continue
        current = ' aria-current="true"' if other == lang else ""
        code = escape(I18N[other]["htmlLang"], quote=True)
        text = escape(I18N[other]["name"]) if menu else other.upper()
        title = "" if menu else f' title="{escape(I18N[other]["name"], quote=True)}"'
        links.append(f'<li><a href="@root@/{prefix(other)}{escape(route, quote=True)}" lang="{code}" hreflang="{code}"{title}{current}>{text}</a></li>')
    if len(links) < 2:
        return ""
    name = escape(ui(lang, "language"), quote=True)
    if menu:
        return (
            f'<details class="nav-group lang-menu" name="nav"><summary aria-label="{name}: {escape(I18N[lang]["name"], quote=True)}">'
            f'@icon:globe@ {lang.upper()} @icon:chevron-down@</summary><ul>{"".join(links)}</ul></details>'
        )
    return f'<ul class="lang-switch" aria-label="{name}">{"".join(links)}</ul>'


def header(page, route, lang):
    items = navigation_items(route, lang)
    switch = language_switch(page, route, lang)
    lang_menu = language_switch(page, route, lang, menu=True)
    nav_name = escape(ui(lang, "mainNavigation"), quote=True)
    return f'''  <header class="site-header">
    <div class="wrap header-inner">
      {home_logo()}
      <nav class="main-nav" aria-label="{nav_name}">
      {items}
      {lang_menu}
      </nav>
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


def calls_list(lang):
    """The public calls, one row per organization, from content/calls.json. site.js marks the ones whose date has passed."""
    rows = []
    for call in CALLS["calls"]:
        logo = call["logo"]
        links = "".join(
            f'<a class="button button--outline" href="{escape(link["url"], quote=True)}">{escape(ui(lang, "calls" + link.get("for", "see").capitalize()))} @icon:arrow-up-right@</a>'
            for link in call["links"]
        )
        if "date" in call:
            year, month, day = (int(part) for part in call["date"].split("-"))
            text = ui(lang, "dateFormat").format(day=day, month=ui(lang, "months")[month - 1], year=year)
            time = call.get("time")
            when = (
                f'{escape(ui(lang, "callsDeadline"))}: <time datetime="{call["date"]}{"T" + time if time else ""}">{escape(text)}{", " + time if time else ""}</time>'
                f' <span class="call-status" data-closed="{escape(ui(lang, "callsClosed"), quote=True)}"></span>'
            )
            deadline = f' data-deadline="{call["date"]}"'
        else:
            when, deadline = escape(ui(lang, "callsSoon")), ""
        rows.append(
            f'<li{deadline}><span class="call-logo"><img alt="" decoding="async" loading="lazy" src="@site@/assets/images/{logo["file"]}" width="{logo["width"]}" height="{logo["height"]}"></span>'
            f'<div><h3>{escape(call["name"])}</h3><p class="call-deadline">{when}</p></div>'
            + (f'<div class="actions">{links}</div>' if links else "") + "</li>"
        )
    return f'<ul class="calls">{"".join(rows)}</ul>'


@cache
def network_parts():
    """The Connects map as SVG pieces: lines, dots and one plate per organization, from content/network.json.

    Every organization gets the same area, shaped by its logo's proportions. Each starts on its city; overlapping
    ones are pushed apart while a weak pull keeps them near home. The result is the same on every build.
    """
    m = NETWORK["map"]
    k = m["width"] / (m["lon"][1] - m["lon"][0])
    width, height = m["width"], round((m["lat"][0] - m["lat"][1]) * k, 1)

    def xy(point):
        lon, lat = point
        return ((lon + 360 if lon < m["lon"][0] else lon) - m["lon"][0]) * k, (m["lat"][0] - lat) * k

    area, gap, tiles = 1050, 1.5, []
    for index, org in enumerate(NETWORK["orgs"]):
        x, y = xy(org["at"])
        ratio = min(4.2, max(1.15, org.get("ratio") or len(org["name"]) * .33))
        tiles.append({"org": org, "hx": x, "hy": y, "w": sqrt(area * ratio), "h": sqrt(area / ratio), "x": x + sin(index * 2.4) * 4, "y": y + cos(index * 1.7) * 4})
    for step in range(1500):
        pull = .006 if step < 1250 else 0
        for a, first in enumerate(tiles):
            for second in tiles[a + 1:]:
                dx, dy = second["x"] - first["x"], second["y"] - first["y"]
                over_x = (first["w"] + second["w"]) / 2 + gap - abs(dx)
                if over_x <= 0:
                    continue
                over_y = (first["h"] + second["h"]) / 2 + gap - abs(dy)
                if over_y <= 0:
                    continue
                if over_x / (first["w"] + second["w"]) < over_y / (first["h"] + second["h"]):
                    move = (over_x / 2) * (1 if dx >= 0 else -1)
                    first["x"] -= move
                    second["x"] += move
                else:
                    move = (over_y / 2) * (1 if dy >= 0 else -1)
                    first["y"] -= move
                    second["y"] += move
        for tile in tiles:
            tile["x"] = min(width - tile["w"] / 2 - 2, max(tile["w"] / 2 + 2, tile["x"] + (tile["hx"] - tile["x"]) * pull))
            tile["y"] = min(height - tile["h"] / 2 - 2, max(tile["h"] / 2 + 2, tile["y"] + (tile["hy"] - tile["y"]) * pull))

    hubs = {name: xy(point) for name, point in NETWORK["hubs"].items()}
    lines, drawn = [], set()

    def arc(a, b):
        key = tuple(sorted((round(p[0] / 5), round(p[1] / 5)) for p in (a, b)))
        length = hypot(b[0] - a[0], b[1] - a[1])
        if key in drawn or length < 6:
            return
        drawn.add(key)
        lines.append(f'<path pathLength="1" d="M{a[0]:.1f} {a[1]:.1f}Q{(a[0] + b[0]) / 2:.1f} {(a[1] + b[1]) / 2 - length * .3:.1f} {b[0]:.1f} {b[1]:.1f}"/>')

    for a, b in NETWORK["links"]:
        arc(hubs[a], hubs[b])
    cities = [(tile["hx"], tile["hy"]) for tile in tiles] + [xy(point) for point in NETWORK["community"]]
    for city in cities:  # every place to Madrid; the Americas to Boston too; far places to their regional hub
        arc(hubs["madrid"], city)
        if city[0] < 420:
            arc(hubs["boston"], city)
        if city[0] > 640 and city[1] > 150:
            arc(hubs["singapore"], city)
        elif city[0] > 600:
            arc(hubs["doha"], city)
        if city[0] < 420 and city[1] > 200:
            arc(hubs["saopaulo"], city)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.9"/>' for x, y in cities) + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>' for x, y in hubs.values())
    return width, height, "".join(lines), dots, tiles


def collage(match):
    """@collage:photo-a,photo-b,photo-c,photo-d|Description@ -> the dotted world map with the IMFAHE logo in the middle
    and four photos (docs/assets/images/<name>-480.webp, 3:2) joined to it by lines that draw themselves."""
    names, label = match.group(1).split(","), match.group(2)
    spots = list(zip(names, [(0, 0), (410, 0), (0, 334), (410, 334)]))
    clips = "".join(f'<clipPath id="collage-{n}"><rect x="{x}" y="{y}" width="190" height="126" rx="12"/></clipPath>' for n, (x, y) in spots)
    photos = "".join(f'<g class="netmap-org"><image href="@site@/assets/images/{n}-480.webp" x="{x}" y="{y}" width="190" height="126" preserveAspectRatio="xMidYMid slice" clip-path="url(#collage-{n})"/></g>' for n, (x, y) in spots)
    lines = '<path pathLength="1" d="M120 126 Q135 205 215 215"/><path pathLength="1" d="M480 126 Q465 205 385 215"/><path pathLength="1" d="M120 334 Q135 255 215 245"/><path pathLength="1" d="M480 334 Q465 255 385 245"/>'
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4"/>' for x, y in [(120, 126), (480, 126), (120, 334), (480, 334), (215, 215), (385, 215), (215, 245), (385, 245)])
    return (f'<figure class="media netmap netmap--collage"><svg viewBox="0 0 600 460" role="img" aria-label="{label}"><defs>{clips}</defs>'
            '<image class="netmap-world" href="@site@/assets/world-dots.svg" x="0" y="118" width="600" height="223"/>'
            f'<g class="netmap-lines">{lines}</g><g class="netmap-dots">{dots}</g>{photos}'
            '<g class="collage-logo"><rect x="215" y="188" width="170" height="84" rx="14"/><image href="@site@/assets/images/imfahe-logo.png" x="232" y="198" width="136" height="64"/></g></svg></figure>')


def network_map(lang):
    """The map itself. On a phone the logos are too small to read, so they are also listed in a grid below it."""
    width, height, lines, dots, tiles = network_parts()
    plates, items = [], []
    for tile in tiles:
        org, w, h = tile["org"], tile["w"], tile["h"]
        x, y, name = tile["x"] - w / 2, tile["y"] - h / 2, escape(org["name"], quote=True)
        plate = f'<rect class="netmap-plate" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2"/>'
        if org.get("logo"):
            src = f'@site@/assets/{org["logo"]}'
            flat = " netmap-flat" if org["logo"].startswith("images/") else ""  # a file with a white background, not a transparent one
            plates.append(f'<g class="netmap-org{flat}">{plate}<image href="{src}" x="{x + 1.5:.1f}" y="{y + 1.5:.1f}" width="{w - 3:.1f}" height="{h - 3:.1f}"><title>{name}</title></image></g>')
            items.append(f'<li{" class=" + chr(34) + "netmap-flat" + chr(34) if flat else ""}><img alt="{name}" loading="lazy" decoding="async" src="{src}" width="{round(org["ratio"] * 40)}" height="40"></li>')
        else:  # no logo file yet: the name stands in
            size = min(7, (w - 2) / (len(org["name"]) * .56))
            plates.append(f'<g class="netmap-org">{plate}<text x="{tile["x"]:.1f}" y="{tile["y"]:.1f}" font-size="{size:.1f}" text-anchor="middle" dominant-baseline="central">{name}</text></g>')
            items.append(f'<li>{name}</li>')
    return (
        f'<figure class="netmap"><svg viewBox="0 0 {width} {height}" role="img" aria-label="{escape(ui(lang, "networkMap"), quote=True)}">'
        f'<image class="netmap-world" href="@site@/assets/world-dots.svg" width="{width}" height="{height}"/>'
        f'<g class="netmap-lines">{lines}</g><g class="netmap-dots">{dots}</g>{"".join(plates)}</svg>'
        f'<ul class="netmap-list">{"".join(items)}</ul></figure>'
    )


def join_section(page, html, lang):
    """Every page ends with one closing call: its own, or this shared one."""
    last = html.rstrip().rsplit("<section", 1)[-1]
    if page["slug"] in MENU["join"]["skip"] or 'class="cta' in html or last.lstrip().startswith('class="band"'):
        return ""
    join = MENU["join"]
    ways = [
        ("joinStudent", "graduation-cap", f'@site@/{join["calls"]}'),
        ("joinMentor", "handshake", join["mentorForm"]),
        ("joinOrg", "landmark", f'mailto:{MENU["email"]}'),
    ]
    items = "".join(
        f'<li>@icon:{icon_name}@<h3>{escape(ui(lang, key))}</h3><p>{escape(ui(lang, key + "Text"))}</p>'
        f'<a class="link-arrow" href="{escape(href, quote=True)}">{escape(ui(lang, key + "Action"))} @icon:arrow-right@</a></li>'
        for key, icon_name, href in ways
    )
    return f'''
<section class="section join" aria-labelledby="join-title"><div class="wrap join-inner">
<h2 id="join-title">{escape(ui(lang, "joinTitle"))}</h2>
<ul class="join-list">{items}</ul>
</div></section>'''


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
    about = "".join(f'<li>{menu_link(item, route, lang)}</li>' for item in MENU["pages"] if "children" not in item)
    support = escape(ui(lang, "support"))
    return f'''  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-main">
        <div class="footer-brand">
          {home_logo()}
          <p>{escape(ui(lang, "nonprofit"))}</p>
          <nav class="socials" aria-label="{escape(ui(lang, "socialMedia"), quote=True)}">{social_links}</nav>
        </div>
        <nav class="footer-nav" aria-label="{escape(ui(lang, "programs"), quote=True)}">{columns}<div><h3>IMFAHE</h3><ul>
          {about}
          <li><a href="mailto:{email}?subject={support.replace(" ", "%20")}">{support}</a></li>
          <li><a href="@site@/public-calls/">{escape(ui(lang, "calls"))}</a></li>
          <li><a href="@site@/economical-disclosure/">{escape(ui(lang, "financial"))}</a></li>
        </ul></div></nav>
      </div>
      <div class="footer-legal">
        <p>Copyright © 2026 {escape(MENU["legalName"])} (<a href="@site@/">imfahe.org</a>). {escape(ui(lang, "rights"))}</p>
        <button class="link-button" type="button" data-consent-open>{escape(ui(lang, "cookieSettings"))}</button>
      </div>
    </div>
  </footer>'''


def consent(lang):
    """Analytics only loads after the visitor accepts. The choice is kept in the browser."""
    return f'''  <div class="consent" id="consent" role="region" aria-label="{escape(ui(lang, "cookieSettings"), quote=True)}" hidden>
    <p>{escape(ui(lang, "consentText"))}</p>
    <div class="actions"><button class="button" type="button" data-consent="yes">{escape(ui(lang, "consentAccept"))}</button><button class="button button--outline" type="button" data-consent="no">{escape(ui(lang, "consentDecline"))}</button></div>
  </div>'''


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
        content=(text := re.sub(r"@collage:([\w,-]+)\|([^@]+)@", collage, fragment(page, lang).read_text().rstrip().replace("@calls@", calls_list(lang)).replace("@network@", network_map(lang)))) + join_section(page, text, lang) + related(route, lang),
        footer=footer(page, route, lang),
        consent=consent(lang),
    )
    # Assets are shared by every language; page links stay inside the current language.
    html = html.replace("@calls-pdf@", f'@site@/{CALLS["pdf"]}').replace("@root@", base).replace("@site@/assets/", f"{base}/assets/").replace("@site@/", f"{base}/{prefix(lang)}")
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
        footer=footer(page, "404", first), consent=consent(first),
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
