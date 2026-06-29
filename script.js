function toggleMenu() {
  const menu = document.querySelector(".menu-links");
  const icon = document.querySelector(".hamburger-icon");
  const isOpen = menu.classList.toggle("open");
  icon.classList.toggle("open", isOpen);
  icon.setAttribute("aria-expanded", String(isOpen));
}

const yearElement = document.getElementById("current-year");
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}

window.addEventListener("resize", () => {
  if (window.innerWidth > 1200) {
    const menu = document.querySelector(".menu-links");
    const icon = document.querySelector(".hamburger-icon");
    menu?.classList.remove("open");
    icon?.classList.remove("open");
    icon?.setAttribute("aria-expanded", "false");
  }
});
