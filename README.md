# IMFAHE website

The institutional website is built from plain HTML and CSS and published from `main:/docs` on GitHub Pages.

- Edit page copy and sections in `content/<page>.html`. The building blocks (hero, benefits, steps, quotes, cards and so on) are listed with their markup in [content/COMPONENTS.md](content/COMPONENTS.md).
- Edit navigation, menu taglines, the footer email and social links in `content/navigation.json`, and page titles and descriptions in `content/pages.json`.
- Edit the shared page template in `templates/page.html` and styles in `docs/assets/site.css`. Brand colors (`#E6122C` red, `#F39220` orange) and Noto Sans match the imfahe.org theme. The design rules are written down in [DESIGN.md](DESIGN.md).
- In fragments, `@site@/page-slug/` links to a page in the current language (`/`, `/es/` or `/pt/`), and `@site@/assets/...` always points at the shared assets folder. Both work when GitHub Pages serves the site from a repository subpath. A page that has no translation is linked in English.
- Use local, compressed WebP images with a `srcset`, intrinsic dimensions, meaningful alt text where applicable and lazy loading below the first screen. Keep images in their original colors. Text is real text, never a picture of text.
- Public calls: `content/calls.json` holds each organization's logo, deadline (`date` as YYYY-MM-DD, optional `time`) and links (`for` is `students`, `professors` or left out), plus the path of the PDF poster. The Public Calls page and every link to the poster are built from it. The page marks a call as closed in the browser from the day after its date, so no rebuild is needed when a deadline passes.
- Icons: write `@icon:name@` in a fragment and the build inlines `docs/assets/icons/name.svg`. Use only Lucide SVGs for interface icons. The four social logos in `docs/assets/brands/` come from Simple Icons and are written `@brand:name@`.

## Languages

English lives in `content/` and is served from the site root. Spanish and Portuguese live in `content/es/` and `content/pt/` and are served from `/es/` and `/pt/`. Menu labels, interface words and translated page titles are in `content/i18n.json`. A page without a translated fragment is not built in that language: the language switch hides that option and menus link to the English page instead. When you change an English fragment, make the same change in the other two.

## Build and preview

After editing, rebuild and preview with Python 3.10 or newer (the error page, `404.html`, only shows its styles on the published site because its links are absolute):

```sh
python3 scripts/build.py --origin https://imfahe.github.io/imfahe-web/
python3 -m http.server 8080 --bind 127.0.0.1 --directory docs
```

Preview at http://127.0.0.1:8080/. Commit the edited source and the regenerated files under `docs` together. A merge to `main` publishes the updated site. Python is used only to assemble common HTML and does not run on the server.

## Assets and sources

`archive/images/` is the original public image archive. See `archive/inventory.json` for each captured URL and source page. The archive is excluded from Pages deployment; only the web renditions under `docs/assets/images/` are requested by visitors. Public PDFs and other downloadable resources are under `docs/assets/resources/`. Noto Sans, Lucide and Simple Icons are stored locally with their licenses. Stock photos and their sources are listed in [docs/assets/images/CREDITS.md](docs/assets/images/CREDITS.md).

The page slugs match the original WordPress site. The contact page uses the address the WordPress contact form delivers to (`contact@imfahe.org`) because GitHub Pages cannot process the form itself. YouTube players load when selected. Google Analytics uses the same property as imfahe.org. It loads only after a visitor accepts the cookie question (the answer is kept in their browser and can be changed from "Cookie settings" in the footer), and never on `localhost`. A security header in `templates/page.html` lists the only outside hosts the pages may load from: Google Analytics and YouTube. The Pages URL is the deployment target. The live imfahe.org domain is still served by its current hosting.
