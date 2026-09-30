(() => {
    const root = document.documentElement;
    const system = window.matchMedia('(prefers-color-scheme: dark)');
    // Carry the preference in page URLs, without cookies or browser storage.
    const requested = new URL(window.location.href).searchParams.get('theme');
    let preference = ['light', 'dark'].includes(requested) ? requested : 'system';
    const apply = () => {
        root.dataset.theme = preference === 'system'
            ? (system.matches ? 'dark' : 'light') : preference;
    };
    apply();
    system.addEventListener('change', apply);

    document.addEventListener('DOMContentLoaded', () => {
        const switcher = document.getElementById('theme-switcher');
        const button = document.getElementById('theme-toggle');
        const panel = document.getElementById('theme-options');
        const choices = panel.querySelectorAll('button');
        switcher.hidden = false;
        const setPreference = url => {
            if (preference === 'system') url.searchParams.delete('theme');
            else url.searchParams.set('theme', preference);
            return url;
        };
        const updateLinks = () => {
            document.querySelectorAll('a[href]').forEach(link => {
                const href = link.getAttribute('href');
                // Fragment links already retain the current page's query string.
                if (href.startsWith('#') || link.hasAttribute('download')) return;
                const url = new URL(href, document.baseURI);
                if (url.origin !== window.location.origin) return;
                // Leave locally hosted PDFs, images and other files untouched.
                const filename = url.pathname.split('/').pop();
                if (filename.includes('.') && !/\.html?$/.test(filename)) return;
                link.href = setPreference(url).href;
            });
        };
        const updateChoices = () => {
            choices.forEach(option => {
                option.setAttribute('aria-pressed', String(option.dataset.themeChoice === preference));
            });
        };
        updateChoices();
        updateLinks();
        const close = () => {
            panel.hidden = true;
            button.setAttribute('aria-expanded', 'false');
        };
        choices.forEach(choice => {
            choice.addEventListener('click', () => {
                preference = choice.dataset.themeChoice;
                apply();
                window.history.replaceState(window.history.state, '', setPreference(new URL(window.location.href)));
                updateChoices();
                updateLinks();
                close();
                button.focus();
            });
        });
        button.addEventListener('click', () => {
            const opening = panel.hidden;
            panel.hidden = !opening;
            button.setAttribute('aria-expanded', String(opening));
            if (opening) panel.querySelector('[aria-pressed="true"]').focus();
        });
        const dismiss = event => {
            if (event.key === 'Escape' && !panel.hidden) {
                event.stopPropagation();
                close();
                button.focus();
            }
        };
        button.addEventListener('keydown', dismiss);
        panel.addEventListener('keydown', dismiss);
        const contains = target => switcher.contains(target) || panel.contains(target);
        document.addEventListener('click', event => {
            if (!contains(event.target)) close();
        });
        [switcher, panel].forEach(element => {
            element.addEventListener('focusout', event => {
                if (!contains(event.relatedTarget)) close();
            });
        });
    });
})();
