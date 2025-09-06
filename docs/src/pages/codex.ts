// Codex page interactivity - tab navigation and URL handling

// Export to make this file a module
export {};

// Initialize codex functionality when on the codex page
if (window.location.pathname === '/codex' || window.location.pathname === '/codex/') {
    console.log('Loaded codex page');
    initializeCodex();
}

function initializeCodex() {
    // Handle tab navigation
    setupTabNavigation();

    // Handle URL hash and query parameters
    handleInitialUrlState();

    // Setup search functionality
    setupSearchNavigation();

    // Setup monster search event listener for URL updates
    setupMonsterSearchListener();

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange);
}

function setupTabNavigation() {
    const tabs = document.querySelectorAll('.codex-tab');
    const contents = document.querySelectorAll('.codex-tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');

            if (targetTab) {
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update active content
                contents.forEach(c => c.classList.remove('active'));
                const targetContent = document.querySelector(`.codex-tab-content[data-content="${targetTab}"]`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }

                // Update URL hash
                updateUrlForTab(targetTab);
            }
        });
    });
}

function setupSearchNavigation() {
    const searchInput = document.getElementById('codex-search-input') as HTMLInputElement;
    const searchButton = document.getElementById('codex-search-button');

    function performSearch() {
        const query = searchInput?.value?.trim();
        if (query) {
            // Switch to search tab and set query
            switchToSearchTab(query);
        }
    }

    // Handle search button click
    searchButton?.addEventListener('click', performSearch);

    // Handle enter key in search input
    searchInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
}

function switchToSearchTab(query?: string) {
    // Activate search tab
    const searchTab = document.querySelector('.codex-tab[data-tab="search"]') as HTMLElement;
    const searchContent = document.querySelector('.codex-tab-content[data-content="search"]') as HTMLElement;

    if (searchTab && searchContent) {
        // Update tab states
        document.querySelectorAll('.codex-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.codex-tab-content').forEach(c => c.classList.remove('active'));

        searchTab.classList.add('active');
        searchContent.classList.add('active');

        // Update URL
        const url = new URL(window.location.href);
        url.hash = 'search';
        if (query) {
            url.searchParams.set('query', query);
        }
        window.history.pushState({}, '', url.toString());

        // Update monster-codex component with search query
        const monsterCodex = document.querySelector('monster-codex') as any;
        if (monsterCodex && query) {
            // Use the new public method to set search query
            if (typeof monsterCodex.setSearchQuery === 'function') {
                monsterCodex.setSearchQuery(query);
            } else {
                // Fallback to attribute setting
                monsterCodex.setAttribute('initial-query', query);

                // Dispatch custom event
                monsterCodex.dispatchEvent(new CustomEvent('search-query-changed', {
                    detail: { query }
                }));
            }
        }
    }
}

function switchToBrowseTab() {
    const browseTab = document.querySelector('.codex-tab[data-tab="browse"]') as HTMLElement;
    const browseContent = document.querySelector('.codex-tab-content[data-content="browse"]') as HTMLElement;

    if (browseTab && browseContent) {
        // Update tab states
        document.querySelectorAll('.codex-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.codex-tab-content').forEach(c => c.classList.remove('active'));

        browseTab.classList.add('active');
        browseContent.classList.add('active');

        // Update URL
        const url = new URL(window.location.href);
        url.hash = 'browse';
        url.searchParams.delete('query'); // Remove query when switching to browse
        window.history.pushState({}, '', url.toString());
    }
}

function handleInitialUrlState() {
    const url = new URL(window.location.href);
    const hash = url.hash.substring(1); // Remove #
    const query = url.searchParams.get('query');
    let focused = false;
    if (hash === 'search' || query) {
        // Switch to search tab
        switchToSearchTab(query || undefined);
        // Focus search input if present and hash is search
        if (hash === 'search') {
            setTimeout(() => {
                const searchInput = document.getElementById('codex-search-input') as HTMLInputElement;
                if (searchInput) searchInput.focus();
            }, 0);
            focused = true;
        }
    } else if (hash === 'browse') {
        // Switch to browse tab (already default, but ensure state is correct)
        switchToBrowseTab();
    } else {
        // Default to browse tab
        switchToBrowseTab();
    }
}

function handleHashChange() {
    handleInitialUrlState();
}

function setupMonsterSearchListener() {
    // Listen for monster search events to update URL parameters
    document.addEventListener('monster-search-changed', (e: any) => {
        const { query, creatureTypes, minCr, maxCr } = e.detail;
        const url = new URL(window.location.href);

        // Only update URL if we're on the search tab
        if (url.hash === '#search') {
            // Update query parameter
            if (query) {
                url.searchParams.set('query', query);
            } else {
                url.searchParams.delete('query');
            }

            // Update other search parameters if needed in the future
            // (for now just focusing on query as requested)

            // Update URL without triggering navigation
            window.history.replaceState({}, '', url.toString());
        }
    });
}

function updateUrlForTab(tabName: string) {
    const url = new URL(window.location.href);
    url.hash = tabName;

    // Clear query param when switching to browse tab
    if (tabName === 'browse') {
        url.searchParams.delete('query');
    }

    window.history.replaceState({}, '', url.toString());
}

// Export functions for potential external use
declare global {
    interface Window {
        codexPageFunctions?: {
            switchToSearchTab: (query?: string) => void;
            switchToBrowseTab: () => void;
        };
    }
}

window.codexPageFunctions = {
    switchToSearchTab,
    switchToBrowseTab
};