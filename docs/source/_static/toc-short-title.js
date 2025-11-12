document.addEventListener("DOMContentLoaded", () => {
  // Build a map from "#id" -> short title pulled from the span in the heading
  const shortMap = {};
  document.querySelectorAll("h2,h3,h4,h5,h6").forEach(h => {
    const span = h.querySelector(".toc-short");
    if (!span) return;
    const id = h.getAttribute("id");
    const label = span.dataset.shortTitle || span.textContent.trim();
    if (id && label) shortMap["#" + id] = label;
  });

  // Update link text in the right-hand Page TOC (covers theme variants)
  document.querySelectorAll(
    ".bd-sidebar-secondary .bd-toc-nav a[href^='#'], .bd-toc a[href^='#']"
  ).forEach(a => {
    const key = a.getAttribute("href");
    if (shortMap[key]) a.textContent = shortMap[key];
  });
});
