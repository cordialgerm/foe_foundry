if (window.location.pathname === '/generate/' || window.location.pathname === '/generate') {
    console.log('Loaded generator page');

    // Desktop browser check (screen width > 1000px)
    if (window.innerWidth > 1000) {
        setupBetaBanner();
    }
}

function setupBetaBanner() {
    const banner = document.getElementById('site-banner');
    if (banner) {
        const betaMsg = document.createElement('div');
        betaMsg.className = 'beta-banner my-2';

        const targetParams = new URLSearchParams({
            utm_source: 'generate_page',
            utm_medium: 'banner',
            utm_campaign: 'beta'
        });

        const existingParams = new URLSearchParams(window.location.search);
        const monsterKey = existingParams.get('monster-key');
        const template = existingParams.get('template');
        if (monsterKey) targetParams.set('monster-key', monsterKey);
        if (template) targetParams.set('template', template);

        const targetUrl = `/generate/v2/?${targetParams.toString()}`;
        betaMsg.innerHTML = `
                <span>Do you want to try the new <a href="${targetUrl}" class="monster-generator-link"><svg-icon src="anvil-impact" jiggle="jiggleUntilClick"></svg-icon>Interactive Monster Generator</a> (Beta)?</span>
            `;
        banner.appendChild(betaMsg);
    }
}
