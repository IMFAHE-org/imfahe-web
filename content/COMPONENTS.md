# Page building blocks

Every page is a list of `<section class="section">` blocks inside `content/<page>.html`. Alternate plain sections with `section--tint`. Styles live in `docs/assets/site.css`; do not add inline styles. [imfahe-international-mentor-program.html](imfahe-international-mentor-program.html) uses most blocks and is the reference page. [home.html](home.html) shows the rest.

Rules that apply everywhere:

- Text is real text, never a picture of text.
- One `<h1>` per page. Heading levels never skip (h1, h2, h3).
- Icons: write `@icon:name@` and the build inlines `docs/assets/icons/name.svg` (Lucide). Social logos: `@brand:name@`.
- Links to pages: `@site@/page-slug/`. Files: `@site@/assets/...`.
- Network map: `@network@` becomes the world map on IMFAHE Connects, drawn from `content/network.json`. To add an organization, add one entry with its `name`, its place as `at: [longitude, latitude]`, and, when there is a logo file, `logo` (a path under `docs/assets/`, ideally an SVG with a transparent background) and `ratio` (the logo's width divided by its height). The build places it near its city without overlapping the others; an entry without a logo shows its name. `hubs`, `links` and `community` are the places the lines start from, the lines between hubs, and places that get a dot and a line but no logo.
- Public calls: `@calls@` becomes the list of calls and `@calls-pdf@` the address of the PDF poster, both from `content/calls.json`. To change a deadline, link or organization, edit that file only; the three languages follow. A call is shown as closed from the day after its `date`.
- Images: local WebP, `width` and `height` set, `loading="lazy"` below the first screen, meaningful `alt` (empty `alt=""` for decoration).
- The row of sibling programs at the foot of a program page is added by the build. Do not write a sub-menu.
- Layout habits from the home page review: sections that pair text with a picture swap sides from one to the next (`split--flip`); a heading shares its row with an intro, or runs wide when it is alone; links in a row of columns sit on one line; a short statement with one link is a quiet band, not a full section.
- A page can write its own "How to join": `<section class="section join">` with a `join-head` (title and button) and `<ul class="join-list join-list--4">` of icon, title, text and arrow link; see imfahe-connects-program.html. Add the page to `join.skip` in navigation.json so the shared one is not added too.
- The numbers block of the home page (`stats-block` inside `wrap hero-extras`) can close any page top; see the same page.
- Every page ends with one closing call. If a page has its own (a `cta` block, or a red `band` as its last section) it keeps it; otherwise the build adds the shared "How to join IMFAHE" section. Contact and Financial Disclosure get none (`join.skip` in `content/navigation.json`).
- In a row of actions use at most two button styles: one `button`, alternatives as `button button--outline`. Keep `link-arrow` for the link inside a card or list item; a call to action on its own is a button.

## Program page hero

```html
<section class="section section--hero">
<div class="wrap hero hero--banner">
<h1>Title</h1>
<p class="lead">One-line tagline (optional).</p>
<figure class="media hero-photo"><img ... 3:1 picture, fetchpriority="high"></figure>   <!-- add hero-photo--natural to show the whole picture uncropped -->
<div class="prose prose--cols"><p>Intro paragraphs flow in two columns.</p></div>
</div>
</section>
```

## Section heading with an intro line

```html
<section class="section"><div class="wrap section-layout">
<div class="section-intro"><h2>Heading</h2>
<p class="section-summary">One or two sentences.</p></div>
...blocks...
</div></section>
```

## Benefits (icon, title, tagline, text)

```html
<ul class="benefits">            <!-- add class benefits--3 for three columns -->
<li>@icon:target@<h3>Title</h3><p class="benefit-tag">Short red tagline (optional).</p><p>Description.</p></li>
</ul>
```

## Steps (numbered automatically)

```html
<ol class="steps">
<li><h3>Title</h3><p>Text.</p></li>
</ol>
<p class="steps-note">@icon:calendar@ Closing note (optional).</p>
<a class="button" href="...">The action the steps lead to (optional)</a>
```

## Numbers

```html
<ul class="stats">
<li>@icon:globe@<strong>3,000+</strong> <span>Global talents</span></li>
</ul>
```

## Two columns

```html
<div class="split">              <!-- split--media centers a picture beside text; add split--flip to show the picture on the left while the text still comes first for phones and screen readers -->
<div class="prose">...</div>
<div class="prose">...</div>
</div>
```

## Tabs (one block shown at a time)

```html
<div class="tabs">
<div class="tab-list" role="radiogroup" aria-labelledby="id-of-the-section-heading">
<input type="radio" name="group" id="tab-1" checked><label for="tab-1">@icon:globe@ First</label>
<input type="radio" name="group" id="tab-2"><label for="tab-2">@icon:lightbulb@ Second</label>
</div>
<div class="tab-panels">
<article class="tab-panel"><figure class="media"><img ...></figure><h3>Title</h3><div class="prose"><p>Text.</p></div><a class="button" href="...">Learn More<span class="sr-only"> about First</span></a></article>
<article class="tab-panel">...</article>
</div>
</div>
```

Blocks must be in the same order as their tabs, with the same four parts (picture, title, text, one button), so they line up. The hidden words after "Learn More" tell screen readers and search engines where each button goes. Up to four tabs.

## Small cards (a title and a short list or line)

```html
<ul class="cards">
<li class="card">@icon:map-pin@<h3>United States</h3><ul><li>Harvard University</li></ul></li>
</ul>
```

## Expandable rows (long bullet lists)

```html
<div class="accordion">
<details name="group-name" open><summary>Title</summary><p>Text.</p></details>
<details name="group-name"><summary>Title</summary><p>Text.</p></details>
</div>
```

## Quotes

```html
<div class="quotes">
<figure class="quote"><blockquote><p>Quote without quotation marks.</p></blockquote>
<figcaption><img alt="" ...portrait...><h3>Name</h3><p>Role, organization (country)</p></figcaption></figure>
</div>
```

## Videos (YouTube loads on click)

```html
<div class="video-grid">
<div class="video-card">
<button class="video-trigger" data-title="Title" data-youtube="VIDEO_ID" type="button">
<img alt="" height="540" loading="lazy" src="@site@/assets/images/video/VIDEO_ID.webp" width="960"/>
<span class="play-button">@icon:play@</span>
<span class="play-label">Title</span>
</button>
<noscript><a href="https://www.youtube.com/watch?v=VIDEO_ID">Title</a></noscript>
<p>Caption.</p>
</div>
</div>
```

## Events

```html
<ol class="timeline">
<li class="event"><p class="event-date">October 2026</p>
<div class="event-body"><h3>Event | City, Country</h3><p class="meta">Topic</p><div class="prose"><p>Text.</p></div></div>
<figure class="media"><img ...></figure></li>
</ol>
```

## Table

```html
<div class="table-scroll"><table class="table">
<caption>Title</caption>
<thead><tr><th>Team</th><th class="num">Award ($)</th></tr></thead>
<tbody><tr><th scope="row">Name</th><td class="num">2,000</td></tr></tbody>
</table></div>
```

## Red call band and closing call to action

```html
<section class="band"><div class="wrap"><h2><a href="...">Call text</a></h2><a class="button" href="...">Label</a></div></section>

<section class="section section--tint"><div class="wrap"><div class="cta">   <!-- cta--plain when there is no picture; cta--flip puts the picture on the right -->
<figure class="media"><img ...4:5 picture...></figure>
<div class="stack"><h2>Heading</h2><div class="prose"><p>Text.</p></div>
<div class="actions"><a class="button" href="...">Main action</a><a class="button button--outline" href="...">Second action</a></div></div>
</div></div></section>
```

A quiet band is the same row on grey and thinner. Use it for a short statement with one link that is not the page's main call (the nonprofit line at the foot of the home page). It does not count as a closing call, so the build still adds "How to join" after it.

```html
<section class="band band--quiet"><div class="wrap"><div><h2>Statement</h2><p>One sentence.</p></div><a class="button button--outline" href="...">Label</a></div></section>
```

## Other pieces

- Buttons: `button`, `button button--outline`. Text link with arrow: `link-arrow`. Row of buttons: `<div class="actions">`.
- Picture that must not be cropped (a flyer, a chart): `<figure class="media media--contain">`.
- Partner logos: `<ul class="logos">`, see home.html. Team cards: `<div class="team">` with `<article class="photo-card">`, see who-is-imfahe.html. Press cards: `<ul class="press">`, same page. A page top with a title, text and a photo is a `split split--media` inside `section--hero`, also on that page.
