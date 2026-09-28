const navigation = document.getElementById("site-navigation");

if (navigation) {
    let previousScroll = Math.max(0, window.scrollY);

    const measureNavigation = () => {
        document.documentElement.style.setProperty(
            "--navigation-height", `${navigation.offsetHeight}px`
        );
    };

    measureNavigation();
    new ResizeObserver(measureNavigation).observe(navigation);

    window.addEventListener("scroll", () => {
        const currentScroll = Math.max(0, window.scrollY);
        navigation.classList.toggle("is-hidden",
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
