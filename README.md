# IMFAHE website

The institutional website is built from plain HTML and CSS and published from `main:/docs` on GitHub Pages.

- Edit page copy and sections in `content/<page>.html`.
- Edit navigation and page metadata in `content/navigation.json` and `content/pages.json`.
- Edit the shared page template in `templates/page.html` and styles in `docs/assets/site.css`.
- The `@site@/` prefix in fragments resolves to the site's root, including when GitHub Pages serves the site from a repository subpath.
- Use local, compressed WebP images with a `srcset`, intrinsic dimensions, meaningful alt text where applicable and lazy loading below the first screen. Keep images in their original colors. Use only Lucide SVGs for icons.

After editing, rebuild and preview with Python 3.10 or newer:

```sh
python3 scripts/build.py --origin https://imfahe.github.io/imfahe-web/
python3 -m http.server 8080 --bind 127.0.0.1 --directory docs
```

Preview at http://127.0.0.1:8080/. Commit the edited source and the regenerated files under `docs` together. A merge to `main` publishes the updated site. Python is used only to assemble common HTML and does not run on the server.

`archive/images/` is the original public image archive. See `archive/inventory.json` for each captured URL and source page. The archive is excluded from Pages deployment; only the web renditions under `docs/assets/images/` are requested by visitors. Public PDFs and other downloadable resources are under `docs/assets/resources/`. Noto Sans and Lucide are stored locally with their licenses.

The page slugs match the original WordPress site. The contact page uses the foundation's published email address because GitHub Pages cannot process the former WordPress form. YouTube players load when selected. The Pages URL is the deployment target. The live imfahe.org domain is still served by its current hosting.
