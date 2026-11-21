document.querySelectorAll(".video-trigger").forEach((button) => {
  button.addEventListener("click", () => {
    const videoId = button.dataset.youtube;
    if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return;

    const player = document.createElement("iframe");
    player.className = "player";
    player.title = button.dataset.title || "YouTube video";
    player.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`;
    player.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
    player.allowFullscreen = true;
    button.replaceWith(player);
    player.focus();
  });
});

// With a mouse, the header dropdowns open on hover as well as on click. A short delay keeps
// them open while the pointer crosses the gap between the label and its list.
if (matchMedia("(hover: hover) and (pointer: fine)").matches) {
  document.querySelectorAll(".main-nav details").forEach((menu) => {
    let closing;
    menu.addEventListener("mouseenter", () => { clearTimeout(closing); menu.open = true; });
    menu.addEventListener("mouseleave", () => { closing = setTimeout(() => { menu.open = false; }, 180); });
    // A mouse click on a label that hover already opened should not close it again (keyboard Enter still toggles).
    menu.querySelector("summary").addEventListener("click", (event) => { if (menu.open && event.detail > 0) event.preventDefault(); });
  });
}

const menus = Array.from(document.querySelectorAll(".main-nav details, .mobile-nav details, .mobile-nav"));
document.addEventListener("click", (event) => {
  menus.forEach((menu) => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const openMenu = menus.find((menu) => menu.open && menu.contains(document.activeElement));
  if (!openMenu) return;
  openMenu.open = false;
  openMenu.querySelector("summary")?.focus();
});

// Numbers count up once when they scroll into view. Skipped for people who ask their device for less motion.
// shortcut: treats "." and "," as thousands separators, never decimals; revisit if a figure like "1.5" is ever shown.
if (!matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) {
  const counter = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    counter.unobserve(entry.target);
    const el = entry.target, final = el.textContent;
    const parts = final.match(/^(\D*)(\d[\d.,\u00a0 ]*\d|\d)(\D*)$/);
    if (!parts) return;
    const target = Number(parts[2].replace(/\D/g, "")), separator = (parts[2].match(/\D/) || [""])[0], start = performance.now();
    const tick = (now) => {
      const progress = Math.min(1, (now - start) / 1200), eased = 1 - (1 - progress) ** 4;
      const shown = String(Math.round(target * eased)).replace(/\B(?=(\d{3})+$)/g, separator);
      el.textContent = progress < 1 ? parts[1] + shown + parts[3] : final; // always ends on the exact original text
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }), { threshold: 0.6 });
  document.querySelectorAll(".stats strong").forEach((el) => counter.observe(el));
}

// Partner logos appear one after another the first time the wall scrolls into view.
// Without this script, or with reduced motion, the wall is simply visible.
const wall = document.querySelector(".logos--cards");
if (wall && !matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) {
  wall.classList.add("is-waiting");
  [...wall.children].forEach((logo, index) => logo.style.setProperty("--i", index));
  new IntersectionObserver((entries, observer) => {
    if (!entries[0].isIntersecting) return;
    wall.classList.replace("is-waiting", "is-in");
    observer.disconnect();
  }, { threshold: 0.2 }).observe(wall);
}

// Google Analytics (same property as imfahe.org) loads only after the visitor accepts cookies.
// It is also skipped on a developer's machine so previews stay out of the reports.
// Public calls: the day after its deadline a call is marked closed and moves below the open ones.
// Dates are compared as plain days in the visitor's own time, so a call stays open through its deadline day.
const today = new Date().toLocaleDateString("sv"); // "sv" formats as YYYY-MM-DD
document.querySelectorAll(".calls").forEach((list) => {
  list.querySelectorAll("li[data-deadline]").forEach((item) => {
    if (item.dataset.deadline >= today) return;
    item.classList.add("is-closed");
    const status = item.querySelector(".call-status");
    status.textContent = status.dataset.closed;
    list.append(item);
  });
});

function loadAnalytics() {
  if (window.gtag || /^(localhost|127\.|\[::1\])/.test(location.hostname)) return;
  const tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=G-8Q9PR9CWSB";
  document.head.append(tag);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  window.gtag("config", "G-8Q9PR9CWSB");
}

const consent = document.getElementById("consent");
const CONSENT_KEY = "imfahe-analytics";
// Private windows can block storage: treat that as "no answer yet" and never load analytics.
const stored = () => { try { return localStorage.getItem(CONSENT_KEY); } catch { return null; } };
if (stored() === "yes") loadAnalytics();
else if (!stored() && consent) consent.hidden = false;
consent?.addEventListener("click", (event) => {
  const answer = event.target.closest("[data-consent]")?.dataset.consent;
  if (!answer) return;
  try { localStorage.setItem(CONSENT_KEY, answer); } catch { /* the banner will ask again next visit */ }
  consent.hidden = true;
  if (answer === "yes") loadAnalytics();
});
document.querySelector("[data-consent-open]")?.addEventListener("click", () => {
  if (!consent) return;
  consent.hidden = false;
  consent.querySelector("button")?.focus();
});
