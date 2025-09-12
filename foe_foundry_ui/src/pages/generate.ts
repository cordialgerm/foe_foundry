if (window.location.pathname === '/generate' || window.location.pathname === '/generate/') {
    console.log('Loaded generator page');
    window.addEventListener('monster-key-changed', updateUrlOnMonsterKeyChange);

    // Handle URL parameters on page load
    initializeMonsterBuilderFromUrlParams();
}

function updateUrlOnMonsterKeyChange(event: Event) {
    const customEvent = event as CustomEvent;
    const newKey = customEvent.detail?.monsterKey;
    if (typeof newKey === 'string') {
        const url = new URL(window.location.href);
        url.searchParams.set('monster-key', newKey);
        window.history.replaceState({}, '', url.toString());
    }
}

function initializeMonsterBuilderFromUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);

    // Check for monster-key parameter first
    let monsterKey = urlParams.get('monster-key');

    // If no monster-key, check for template parameter
    if (!monsterKey) {
        const template = urlParams.get('template');
        if (template) {
            monsterKey = template;
        }
    }

    // If we have a monster key from URL params, update the monster-builder element
    if (monsterKey) {
        const monsterBuilder = document.querySelector('monster-builder');
        if (monsterBuilder) {
            monsterBuilder.setAttribute('monster-key', monsterKey);
        }
    }
}