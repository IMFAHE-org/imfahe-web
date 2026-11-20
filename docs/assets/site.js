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
