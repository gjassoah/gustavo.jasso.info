const navigation = document.getElementById("site-navigation");

if (navigation) {
    const button = document.getElementById("menu-toggle");
    const menu = document.getElementById("main-menu");
    const narrowScreen = window.matchMedia("(max-width: 48em)");
    let previousScroll = Math.max(0, window.scrollY);

    const measureNavigation = () => {
        document.documentElement.style.setProperty(
            "--navigation-height", `${navigation.offsetHeight}px`
        );
    };

    const setExpanded = (expanded) => {
        button.setAttribute("aria-expanded", String(expanded));
        menu.hidden = narrowScreen.matches && !expanded;
        measureNavigation();
    };

    const updateLayout = () => {
        const menuHadFocus = menu.contains(document.activeElement);
        const buttonHadFocus = document.activeElement === button;
        button.hidden = !narrowScreen.matches;
        setExpanded(false);
        navigation.classList.remove("is-hidden");
        if (narrowScreen.matches && menuHadFocus) button.focus();
        if (!narrowScreen.matches && buttonHadFocus) menu.querySelector("a").focus();
    };

    button.addEventListener("click", () => {
        setExpanded(button.getAttribute("aria-expanded") !== "true");
    });

    navigation.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && narrowScreen.matches && !menu.hidden) {
            setExpanded(false);
            button.focus();
        }
    });

    menu.addEventListener("click", (event) => {
        if (narrowScreen.matches && event.target.closest("a")) setExpanded(false);
    });

    narrowScreen.addEventListener("change", updateLayout);
    updateLayout();
    new ResizeObserver(measureNavigation).observe(navigation);

    window.addEventListener("scroll", () => {
        const currentScroll = Math.max(0, window.scrollY);
        navigation.classList.toggle("is-hidden",
            !narrowScreen.matches &&
            currentScroll > previousScroll &&
            currentScroll > navigation.offsetHeight &&
            !navigation.matches(":focus-within")
        );
        previousScroll = currentScroll;
    }, { passive: true });

    navigation.addEventListener("focusin", () => {
        navigation.classList.remove("is-hidden");
    });
}
