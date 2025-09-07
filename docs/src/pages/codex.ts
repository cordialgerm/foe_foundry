// Codex page interactivity - tab navigation and URL handling

// Import components
import '../components/SearchBar.js';

// Export to make this file a module
export { };

// Initialize codex functionality when on the codex page
if (window.location.pathname === '/codex' || window.location.pathname === '/codex/' || window.location.pathname.includes('/codex')) {
    console.log('Loaded codex page');
    // Use DOMContentLoaded to ensure the page is fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCodex);
    } else {
        // DOM is already loaded
        initializeCodex();
    }
}

function initializeCodex() {
    console.log('Initializing codex functionality...');

    // Handle tab navigation
    setupTabNavigation();

    // Setup search functionality
    setupSearchNavigation();

    // Setup monster search event listener for URL updates
    setupMonsterSearchListener();

    // Setup catalog search event listener
    setupCatalogSearchListener();

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange);

    // Handle URL hash and query parameters
    // Add a small delay to ensure all components are ready
    setTimeout(() => {
        console.log('Running initial URL state handling...');
        handleInitialUrlState();
    }, 100);
} function setupTabNavigation() {
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
    // Use event delegation on the document to catch the search-navigate event
    // This avoids timing issues with custom element initialization
    document.addEventListener('search-navigate', (e: Event) => {
        // Check if this is a CustomEvent and came from the codex search bar
        const customEvent = e as CustomEvent;
        const target = e.target as HTMLElement;
        if (target && target.id === 'codex-search-bar' && customEvent.detail) {
            const { query } = customEvent.detail;
            switchToSearchTab(query);
        }
    });
}

function switchToSearchTab(query?: string) {
    console.log('switchToSearchTab called with query:', query);

    // Activate search tab
    const searchTab = document.querySelector('.codex-tab[data-tab="search"]') as HTMLElement;
    const searchContent = document.querySelector('.codex-tab-content[data-content="search"]') as HTMLElement;

    if (searchTab && searchContent) {
        console.log('Found search tab elements, activating...');
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
        console.log('Updating URL to:', url.toString());
        window.history.pushState({}, '', url.toString());

        // Update monster-codex component with search query
        const monsterCodex = document.querySelector('monster-codex') as any;
        if (monsterCodex && query) {
            // Use the public method to set search query
            if (typeof monsterCodex.setSearchQuery === 'function') {
                monsterCodex.setSearchQuery(query);
            } else {
                // Fallback: set the query directly on the component's query property
                monsterCodex.query = query;
                // Also set the attribute for consistency
                monsterCodex.setAttribute('initial-query', query);
                // Trigger a re-render to ensure the search executes
                monsterCodex.requestUpdate();
            }
        } else if (query) {
            // If monster-codex component isn't ready yet, try again after a short delay
            setTimeout(() => {
                const delayedMonsterCodex = document.querySelector('monster-codex') as any;
                if (delayedMonsterCodex) {
                    if (typeof delayedMonsterCodex.setSearchQuery === 'function') {
                        delayedMonsterCodex.setSearchQuery(query);
                    } else {
                        delayedMonsterCodex.query = query;
                        delayedMonsterCodex.setAttribute('initial-query', query);
                        delayedMonsterCodex.requestUpdate();
                    }
                }
            }, 100);
        }
    }
}

function switchToBrowseTab() {
    console.log('switchToBrowseTab called');
    const browseTab = document.querySelector('.codex-tab[data-tab="browse"]') as HTMLElement;
    const browseContent = document.querySelector('.codex-tab-content[data-content="browse"]') as HTMLElement;

    if (browseTab && browseContent) {
        console.log('Found browse tab elements, activating...');
        // Update tab states
        document.querySelectorAll('.codex-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.codex-tab-content').forEach(c => c.classList.remove('active'));

        browseTab.classList.add('active');
        browseContent.classList.add('active');

        // Update URL
        const url = new URL(window.location.href);
        url.hash = 'browse';
        url.searchParams.delete('query'); // Remove query when switching to browse
        console.log('Updating URL to:', url.toString());
        window.history.pushState({}, '', url.toString());
    }
}

function switchToCatalogTab() {
    const catalogTab = document.querySelector('.codex-tab[data-tab="catalog"]') as HTMLElement;
    const catalogContent = document.querySelector('.codex-tab-content[data-content="catalog"]') as HTMLElement;

    if (catalogTab && catalogContent) {
        // Update tab states
        document.querySelectorAll('.codex-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.codex-tab-content').forEach(c => c.classList.remove('active'));

        catalogTab.classList.add('active');
        catalogContent.classList.add('active');

        // Update URL
        const url = new URL(window.location.href);
        url.hash = 'catalog';
        url.searchParams.delete('query'); // Remove query when switching to catalog
        window.history.pushState({}, '', url.toString());
    }
}

function handleInitialUrlState() {
    const url = new URL(window.location.href);
    const hash = url.hash.substring(1); // Remove #
    const query = url.searchParams.get('query');

    console.log('Handling initial URL state:', {
        fullUrl: url.toString(),
        hash,
        query,
        pathname: window.location.pathname
    });

    if (hash === 'search' || query) {
        console.log('Detected search intent, switching to search tab with query:', query);
        // Switch to search tab
        switchToSearchTab(query || undefined);
        // Focus search input if present and hash is search
        if (hash === 'search') {
            // Focus search input in search tab after a brief delay
            setTimeout(() => {
                const searchBar = document.getElementById('codex-search-bar') as any;
                if (searchBar && typeof searchBar.focusInput === 'function') {
                    searchBar.focusInput();
                }
            }, 100); // Increased delay to ensure components are ready
        }
    } else if (hash === 'catalog') {
        console.log('Switching to catalog tab');
        // Switch to catalog tab
        switchToCatalogTab();
    } else if (hash === 'browse' || hash === '') {
        console.log('Switching to browse tab (default or explicit)');
        // Switch to browse tab (already default, but ensure state is correct)
        switchToBrowseTab();
    } else {
        console.log('Unknown hash, defaulting to browse:', hash);
        // Default to browse tab only for truly unknown hashes
        switchToBrowseTab();
    }
} function handleHashChange() {
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

function setupCatalogSearchListener() {
    // Listen for catalog search events to switch to search tab
    document.addEventListener('catalog-search', (e: any) => {
        const { query } = e.detail;
        if (query) {
            switchToSearchTab(query);
        }
    });
}

function updateUrlForTab(tabName: string) {
    const url = new URL(window.location.href);
    url.hash = tabName;

    // Clear query param when switching to browse or catalog tab
    if (tabName === 'browse' || tabName === 'catalog') {
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
            switchToCatalogTab: () => void;
        };
    }
}

window.codexPageFunctions = {
    switchToSearchTab,
    switchToBrowseTab,
    switchToCatalogTab
};