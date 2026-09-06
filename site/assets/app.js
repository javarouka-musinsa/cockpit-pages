(() => {
  const menuButton = document.querySelector("[data-menu]");
  const navigation = document.querySelector("[data-nav]");

  if (menuButton && navigation) {
    menuButton.addEventListener("click", () => {
      const expanded = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!expanded));
      navigation.classList.toggle("open", !expanded);
    });

    navigation.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        menuButton.setAttribute("aria-expanded", "false");
        navigation.classList.remove("open");
      }
    });
  }

  const tour = document.querySelector("[data-tour]");
  if (tour) {
    const tabs = [...tour.querySelectorAll("[role='tab']")];
    const panels = [...tour.querySelectorAll("[role='tabpanel']")];

    const activate = (tab) => {
      const name = tab.dataset.tab;
      tabs.forEach((item) => {
        const selected = item === tab;
        item.setAttribute("aria-selected", String(selected));
        item.tabIndex = selected ? 0 : -1;
      });
      panels.forEach((panel) => {
        const selected = panel.dataset.panel === name;
        panel.hidden = !selected;
        panel.classList.toggle("active", selected);
      });
    };

    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => activate(tab));
      tab.addEventListener("keydown", (event) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        let targetIndex = index;
        if (event.key === "ArrowLeft") targetIndex = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "ArrowRight") targetIndex = (index + 1) % tabs.length;
        if (event.key === "Home") targetIndex = 0;
        if (event.key === "End") targetIndex = tabs.length - 1;
        activate(tabs[targetIndex]);
        tabs[targetIndex].focus();
      });
    });
  }

  const guideNavigation = document.querySelector("[data-guide-nav]");
  if (guideNavigation && "IntersectionObserver" in window) {
    const links = [...guideNavigation.querySelectorAll("a[href^='#']")];
    const sections = links
      .map((link) => document.querySelector(link.getAttribute("href")))
      .filter(Boolean);
    const activateGuideLink = (id) => {
      links.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${id}`));
    };
    const observer = new IntersectionObserver((entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];
      if (visible) activateGuideLink(visible.target.id);
    }, { rootMargin: "-18% 0px -68% 0px", threshold: [0, 0.15, 0.4] });
    sections.forEach((section) => observer.observe(section));
  }
})();
