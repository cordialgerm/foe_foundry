if (window.location.pathname === '/generate' || window.location.pathname === '/generate/') {
    console.log('Loading generator page');
    window.addEventListener('monster-key-changed', (event: Event) => {
        const customEvent = event as CustomEvent;
        const newKey = customEvent.detail?.monsterKey;
        if (typeof newKey === 'string') {
            const url = new URL(window.location.href);
            url.searchParams.set('monster-key', newKey);
            window.history.replaceState({}, '', url.toString());
        }
    });
}