---
name: IMFAHE website
description: Static site of a US nonprofit that connects students and professors with international mentors.
colors:
  brand: "#e6122c"
  brand-strong: "#c20e24"
  accent: "#f39220"
  ink: "#1d1d1f"
  text: "#3a3a3a"
  muted: "#5e6066"
  line: "#e2e2e2"
  tint: "#f5f5f7"
  rose: "#fdecee"
  white: "#ffffff"
typography:
  title-xl:
    fontFamily: "Noto Sans, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(2.25rem, 1.45rem + 3.4vw, 3.75rem)"
    fontWeight: 800
    lineHeight: 1.04
    letterSpacing: "-0.028em"
  title-lg:
    fontSize: "clamp(1.75rem, 1.35rem + 1.7vw, 2.625rem)"
    fontWeight: 750
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  title-md:
    fontSize: "clamp(1.1875rem, 1.1rem + .4vw, 1.375rem)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title-sm:
    fontSize: "1.0625rem"
    fontWeight: 700
  intro:
    fontSize: "clamp(1.0625rem, 1rem + .35vw, 1.25rem)"
    lineHeight: 1.45
  body:
    fontSize: "clamp(1rem, .96rem + .2vw, 1.125rem)"
    fontWeight: 400
    lineHeight: 1.6
  small:
    fontSize: ".875rem"
rounded:
  radius: ".75rem"
  radius-lg: "1.25rem"
  pill: "62rem"
spacing:
  gutter: "clamp(1.25rem, 4vw, 2.5rem)"
  section: "clamp(3.5rem, 2rem + 6vw, 7rem)"
  gap: "clamp(1.5rem, 1rem + 2vw, 2.5rem)"
  panel: "clamp(1.25rem, 1rem + 1.2vw, 2rem)"
components:
  button:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.white}"
    rounded: "{rounded.pill}"
    padding: ".7rem 1.4rem"
    height: "2.875rem"
  button-hover:
    backgroundColor: "{colors.brand-strong}"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.brand-strong}"
    rounded: "{rounded.pill}"
  card:
    backgroundColor: "{colors.white}"
    rounded: "{rounded.radius}"
    padding: "{spacing.panel}"
  quote:
    backgroundColor: "{colors.tint}"
    rounded: "{rounded.radius-lg}"
    padding: "{spacing.panel}"
---

# Design System: IMFAHE website

## Overview

This is the website of IMFAHE, a US nonprofit that connects students and professors at partner universities with international mentors. Visitors are students, professors, mentors and partner organizations, reading in English, Spanish or Portuguese. This file is for the people and AI assistants who edit page content once or twice a year: it describes what the site already does so new content looks the same.

The site is plain HTML and one stylesheet, `docs/assets/site.css`. Pages are white, text is dark grey, and red is used for actions and small marks. Sections alternate white and light grey. Everything here was read from that stylesheet; if this file and the CSS disagree, the CSS is right.

**Fixed by the organization. These are constraints, not choices:**

- The logo (`docs/assets/images/imfahe-logo.png`), unaltered.
- Brand red `#E6122C` and orange accent `#F39220`.
- Noto Sans as the only typeface.
- Photos keep their original colors. No filters, tints or overlays.
- Icons come from Lucide. The four social logos (Instagram, LinkedIn, X, YouTube) come from Simple Icons.
- The organization's own wording. Do not rewrite, shorten or "improve" its text unless asked.

## Colors

All colors are CSS variables in `:root`. Use the variable, never a new hex value.

| Token | Value | Where it is used |
|---|---|---|
| `--brand` | `#e6122c` | Buttons, the red call band, step number circles, big numbers, icons, list bullets, the focus outline, the text selection, "IMFAHE" in the home title |
| `--brand-strong` | `#c20e24` | Text links, button hover, outline-button text, the current menu item, event dates, benefit taglines. Darker so red text stays readable on white and on grey |
| `--accent` | `#f39220` | Defined but not used by any rule today. Do not introduce it without a decision from the organization |
| `--ink` | `#1d1d1f` | Headings, menu text, quote text, the active language pill, link hover |
| `--text` | `#3a3a3a` | Body text, footer links |
| `--muted` | `#5e6066` | Intro lines, captions, roles, descriptions under a title, footer text |
| `--line` | `#e2e2e2` | Borders and divider lines on white |
| `--tint` | `#f5f5f7` | Background of `section--tint`, the footer, quote cards, hover rows |
| `--rose` | `#fdecee` | Round background behind benefit icons, social icon hover |
| `--white` | `#fff` | Page background, cards, text on red |

Divider lines inside a grey section use a slightly darker grey, `#d9d9de`, written directly in the CSS (no token).

**The Red Is For Action Rule.** Large red areas are the button and the call band only. Red text for reading uses `--brand-strong`, not `--brand`.

## Typography

One family: Noto Sans, a single local variable font file (`docs/assets/fonts/noto-sans.woff2`, weights 400 to 800), with Helvetica Neue and Arial as fallbacks.

| Token | Size | Used for |
|---|---|---|
| `--title-xl` | 2.25rem to 3.75rem | `h1`, weight 800, at most 20 characters wide (24 in a banner hero) |
| `--title-lg` | 1.75rem to 2.625rem | `h2`, weight 750, at most 26 characters wide |
| `--title-md` | 1.1875rem to 1.375rem | `h3`, weight 700; also headings inside `.prose`, the footer and the related row |
| `--title-sm` | 1.0625rem | `h4`, weight 700 |
| `--intro` | 1.0625rem to 1.25rem | `.lead` (dark, weight 600) and `.section-summary` (grey), at most 58 characters wide |
| `--body` | 1rem to 1.125rem | Body text, weight 400, line height 1.6 |
| `--small` | .875rem | `.meta` lines and the footer |

Sizes grow smoothly with the screen; nobody sets a size by hand. Secondary text in cards, steps, benefits and menus is `.9375rem`; roles and menu taglines are `.8125rem` (both written directly, no token). Headings are balanced over their lines automatically. Text lines stop at `--measure` (68 characters). The home page title has its own smaller size (`.hero-title--home`) and puts each phrase on its own line.

## Layout

- **Page width.** Content sits in `.wrap`: at most `--container` (76rem) wide, with a side margin of `--gutter` on small screens.
- **Sections.** Each block is a `<section class="section">` with top and bottom space `--section`. Alternate plain sections with `section--tint`. `section--slim` is a shorter strip (used for the numbers row); `section--hero` is the page top.
- **Inside a section.** `.section-layout` stacks its parts with `--gap` between them. `.stack` is a tighter stack (1rem). `.section-layout--narrow` limits parts to 48rem. Card and panel padding is `--panel`.
- **Two columns.** `.split` makes two equal columns; `split--media` centers a picture beside text.

**Wide screens (1025px and up) fill the row instead of leaving the right half empty.** This happens automatically from the markup:

- Heading beside intro: a `.section-intro` holding an `h2` and an intro line puts the heading on the left and the intro on the right.
- Heading beside text: a section that is only an `h2` followed by `.prose` puts the heading in a narrow left column (one third) and the text beside it. The same applies to a `cta--plain` with body text.
- Centered short calls: a `cta--plain` with no body text, or a `section-layout--center`, is centered with centered text.
- Two-column page tops: `hero--single` puts the `h1` on the left and everything else on the right. `hero--banner` with a `.lead` puts the title on the left, the tagline and button on the right, and the picture across the full width below. The banner intro text (`prose--cols`) flows in two columns.
- Team groups: the group name sits in a narrow left column with three people per row beside it.

**Small screens.** Below 960px the menu becomes a single "Menu" button that opens a full-width panel. At 1024px and below the footer blocks stack; the three home pillars stack, each with its picture beside its text; three-column benefits become two; an event moves its date above the text.

**Phones (720px and below).** Everything becomes one column: hero, `.split`, `.cta`, pillars, benefits, events, the footer lists. Steps stack vertically with the dashed line running down between the numbers. Partner logos go two per row. The banner picture changes from 3:1 to 2:1, the closing picture from 4:5 to 3:2, and the logo gets slightly smaller.

## Elevation & Depth

The site is flat. Blocks are separated by a grey background or a 1px line, not by shadows. One soft shadow exists (`--shadow`) and it is used only on things that float or lift: the open menu, the mobile menu panel, the video thumbnail, and a related-program card on hover. The sticky header is slightly see-through white with a blur and a bottom line.

## Shapes

- `--radius` (.75rem): cards, the partner logo grid, the menu panel, event pictures.
- `--radius-lg` (1.25rem): photos, video thumbnails, quote cards.
- Fully round: buttons, the language switch, step numbers, benefit icon backgrounds, portraits, social buttons.
- Lines are 1px solid. The only dashed line is the connector between steps.

## Components

Markup for every block is in [content/COMPONENTS.md](content/COMPONENTS.md). Copy from there or from the two reference pages, `content/imfahe-international-mentor-program.html` and `content/home.html`. Do not write inline styles or new classes.

**Added by the build on every page (do not write these in a page):**

- Header: logo, menu with drop-downs (program names only; they open on hover or click), the red "contact" button (an outline on the Contact page) and one small language menu. Sticks to the top.
- Footer: logo, one-line description and social links beside four link columns (the three pillars plus "IMFAHE"), then one thin legal line with the copyright and "Cookie settings".
- Closing call: every page ends with one. A page keeps its own (`cta`, or a red `band` as its last section); otherwise the build adds the shared "How to join IMFAHE" section on the rose background. Contact and Financial Disclosure have none.
- Rows of actions: at most two button styles in a row. Text links with an arrow stay inside cards and list items.
- Related programs row: sibling programs at the foot of each program page.
- Skip link, icons, new-tab links.

**Blocks you place in a page:**

- **Program page hero** (`hero hero--banner`): title, optional one-line tagline, 3:1 photo, intro text. Use at the top of a program page. Add `hero-photo--natural` when the picture must show whole (a map).
- **Plain page top** (`hero hero--single`): title and text with no photo.
- **Home hero** (`hero`): title, text and the three entry links (`entry-links`) beside the video. Home only.
- **Section heading with intro** (`section-intro` + `section-summary`): start of most sections.
- **Benefits** (`benefits`, `benefits--3`): reasons to join; icon in a round rose background, title, optional red tagline, description.
- **Steps** (`steps`, `steps-note`): a process in order. Numbers are added automatically. Five or six steps form two rows of three.
- **Numbers** (`stats`): a few big figures with a short label.
- **Two columns** (`split`, `split--media`): two text blocks, or text beside a picture.
- **Small cards** (`cards` / `card`): a title with a short list or line, such as universities per country.
- **Expandable rows** (`accordion`): long lists or questions; one row open at a time when the rows share a `name`.
- **Quotes** (`quotes` / `quote`): testimonials with a round portrait, name and role. The opening quotation mark is added automatically; do not type quotation marks.
- **Videos** (`video-grid`, `video-card`, `video-trigger`): a thumbnail with a red play button. YouTube loads only when clicked.
- **Events** (`timeline` / `event`): date, title, topic, text and one picture per event.
- **Table** (`table-scroll` + `table`): real data. Numbers use `class="num"`.
- **Red call band** (`band`): one line and one button on red, for the single most important call on a page.
- **Quiet band** (`band band--quiet`): the same row on grey, thinner, with an outline button, for a short statement that is not a call (the nonprofit line on the home page).
- **Closing call to action** (`cta`, `cta--plain`): heading, text and buttons at the end of a page, with a 4:5 picture or without one.
- **Home program tabs** (`tabs` / `tab-list` / `tab-panel`): the three program areas on the home page, one open at a time, each ending in one Learn More button. `pillars` / `pillar` remain for the three audience columns on Contact.
- **Partner logos** (`logos`): a grid of linked logos. Add `data-shape="square"` to square logos so they show a little taller.
- **Team** (`team`, `photo-card`, `card-role`, `socials`): one grid of portrait cards, the square photo filling the top of each, then name, role and links.
- **Press** (`press`, `press-source`, `press-title`): one card per piece of coverage: icon, source, headline, arrow. The whole card is the link.
- **Buttons and links** (`button`, `button button--outline`, `link-arrow`, `actions`): a solid button for the main action of a section, outline buttons for the other actions beside it. A text link with an arrow is only for the link inside a card or list item (How to join, the Contact columns). A call to action that stands on its own is always a button, wherever it leads. `actions` holds a row of them.
- **Uncropped picture** (`media media--contain`): a flyer or chart that must not be cropped.

Buttons are at least 2.875rem tall. On hover a button darkens; arrows in links slide slightly right.

## Imagery

- Local WebP files in `docs/assets/images/`. No images loaded from other sites.
- Provide several widths with `srcset` and `sizes` (the site uses 400, 800 and 1500 pixels wide for photos) and always set `width` and `height`.
- The first picture on a page gets `fetchpriority="high"`. Every picture below the first screen gets `loading="lazy"`.
- Shapes are set by the block: banner 3:1, thumbnails 3:2, closing picture 4:5, video thumbnails 16:9, portraits round.
- `alt` describes the picture when it carries meaning ("Graduates in caps and gowns celebrating together"; "University of Seville logo"). Use `alt=""` for decoration and for portraits whose name is written beside them.
- No text inside pictures. Old infographics were rebuilt as Benefits and Steps blocks.
- Original colors only. Every new stock photo is added to `docs/assets/images/CREDITS.md` with its source.

## Icons

- Write `@icon:name@`; the build inlines `docs/assets/icons/name.svg` (Lucide). Write `@brand:name@` for the four social logos in `docs/assets/brands/`.
- Icons take the color of the text around them and are 1.25 times the text size. They are hidden from screen readers, so an icon never replaces a word.
- To use a new icon, add its Lucide SVG file to `docs/assets/icons/` first. Do not use emoji, icon fonts or icons from another set.
- The build adds a small up-right arrow after text links that open a new tab.

## Motion

- Hover changes take 0.2 to 0.3 seconds: colors fade, arrows slide 0.25rem, a related card lifts slightly, a button shrinks a touch when pressed. The menu panel fades in; accordion arrows rotate.
- The hero parts fade up once when a page opens. In browsers that support it, each section fades up as it scrolls into view. Content is visible by default if neither runs.
- People who ask their device for reduced motion get none of this, and no smooth scrolling.
- Nothing moves on its own: no carousels, no autoplay, no looping animation.

## Accessibility

Already true on every page; keep it true:

- One `h1` per page; heading levels never skip.
- A "skip to content" link is the first thing a keyboard reaches.
- Every focused element shows a red outline. Do not remove it.
- Menus and expandable rows are native `<details>` elements, so they work without JavaScript; Escape and a click outside close a menu.
- The current page is marked in the menu (`aria-current`), and each page declares its language.
- Buttons and main links are at least 44px tall.
- Links to other sites and to PDFs open in a new tab (the build does this) and show the arrow.
- Videos have a plain link fallback; tables have a caption and header cells, and scroll sideways on phones instead of breaking the page.
- Text is real text and wraps on any screen; nothing scrolls sideways except tables.

## Languages

English lives in `content/` and is the source. Spanish is in `content/es/`, Portuguese in `content/pt/`. **Any change to an English page must be made in the same place in the other two files**, with the same blocks and classes and translated text. Menu labels, footer wording and page titles are translated in `content/i18n.json`, not in the pages. Link to pages with `@site@/page-slug/` so each language stays inside itself.

## Do's and Don'ts

### Do:
- **Do** build pages only from the blocks in `content/COMPONENTS.md`, alternating white and `section--tint` sections.
- **Do** use the color and size variables; let the layout rules place headings and text on wide screens.
- **Do** keep one main action per section: one solid `button`, with `button--outline` for the rest.
- **Do** mirror every English change in `content/es` and `content/pt`.
- **Do** rebuild after editing (see README.md) and check the page on a phone-width window.

### Don't:
- **Don't** change the logo, the red, the typeface, or the organization's wording.
- **Don't** add inline styles, new classes, new colors, new font sizes or a second typeface.
- **Don't** put text inside pictures, or apply filters, tints or overlays to photos.
- **Don't** use emoji or icons from outside Lucide and Simple Icons.
- **Don't** add shadows, gradients or colored backgrounds to make a block stand out; use the red band once per page instead.
- **Don't** add carousels, pop-ups, autoplay video or anything that moves by itself.
- **Don't** write a header, footer, sub-menu or related-programs row inside a page; the build adds them.
- **Don't** skip heading levels or add a second `h1`.
- **Don't** embed YouTube directly; use the video block so nothing loads until clicked.
