// Codex page functionality
if (window.location.pathname === '/codex' || window.location.pathname === '/codex/') {
    console.log('Loaded codex page');
    
    // Initialize page on load
    document.addEventListener('DOMContentLoaded', initializeCodexPage);
    
    // Handle URL changes (back/forward)
    window.addEventListener('popstate', handlePopState);
}

interface CodexState {
    tab: 'browse' | 'search';
    query?: string;
}

function initializeCodexPage() {
    const currentState = parseUrlState();
    setActiveTab(currentState.tab);
    
    if (currentState.tab === 'search' && currentState.query) {
        setSearchQuery(currentState.query);
        performSearch(currentState.query);
    }
    
    setupEventListeners();
}

function setupEventListeners() {
    // Tab switching
    const browseTab = document.getElementById('browse-tab');
    const searchTab = document.getElementById('search-tab');
    
    browseTab?.addEventListener('click', () => switchToTab('browse'));
    searchTab?.addEventListener('click', () => switchToTab('search'));
    
    // Search functionality
    const searchInput = document.getElementById('codex-search-input') as HTMLInputElement;
    const clearSearchBtn = document.getElementById('clear-search');
    
    if (searchInput) {
        // Handle Enter key
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = searchInput.value.trim();
                if (query) {
                    switchToSearchWithQuery(query);
                }
            }
        });
        
        // Handle input changes for clear button visibility
        searchInput.addEventListener('input', () => {
            const hasValue = searchInput.value.length > 0;
            if (clearSearchBtn) {
                clearSearchBtn.style.display = hasValue ? 'flex' : 'none';
            }
        });
        
        // Focus search input when switching to search tab
        searchInput.addEventListener('focus', () => {
            if (getCurrentTab() === 'browse') {
                switchToTab('search');
            }
        });
    }
    
    // Clear search button
    clearSearchBtn?.addEventListener('click', () => {
        clearSearch();
    });
}

function parseUrlState(): CodexState {
    const hash = window.location.hash;
    const urlParams = new URLSearchParams(window.location.search);
    
    // Default to browse tab
    let tab: 'browse' | 'search' = 'browse';
    let query: string | undefined;
    
    if (hash === '#search') {
        tab = 'search';
        query = urlParams.get('query') || undefined;
    } else if (hash === '#browse') {
        tab = 'browse';
    }
    
    return { tab, query };
}

function getCurrentTab(): 'browse' | 'search' {
    const browseTab = document.getElementById('browse-tab');
    return browseTab?.classList.contains('active') ? 'browse' : 'search';
}

function setActiveTab(tab: 'browse' | 'search') {
    const browseTab = document.getElementById('browse-tab');
    const searchTab = document.getElementById('search-tab');
    const browseContent = document.getElementById('browse-content');
    const searchContent = document.getElementById('search-content');
    
    // Update tab buttons
    browseTab?.classList.toggle('active', tab === 'browse');
    searchTab?.classList.toggle('active', tab === 'search');
    
    // Update content visibility
    if (browseContent && searchContent) {
        browseContent.style.display = tab === 'browse' ? 'block' : 'none';
        searchContent.style.display = tab === 'search' ? 'block' : 'none';
    }
}

function switchToTab(tab: 'browse' | 'search') {
    setActiveTab(tab);
    updateUrl({ tab });
    
    // Clear search when switching to browse
    if (tab === 'browse') {
        clearSearchInput();
    }
}

function switchToSearchWithQuery(query: string) {
    setActiveTab('search');
    setSearchQuery(query);
    updateUrl({ tab: 'search', query });
    performSearch(query);
}

function setSearchQuery(query: string) {
    const searchInput = document.getElementById('codex-search-input') as HTMLInputElement;
    if (searchInput) {
        searchInput.value = query;
        
        // Update clear button visibility
        const clearSearchBtn = document.getElementById('clear-search');
        if (clearSearchBtn) {
            clearSearchBtn.style.display = query.length > 0 ? 'flex' : 'none';
        }
    }
}

function clearSearch() {
    clearSearchInput();
    const monsterCodex = document.getElementById('monster-codex') as any;
    if (monsterCodex) {
        monsterCodex.query = '';
    }
    // Switch to browse tab when clearing search
    switchToTab('browse');
}

function clearSearchInput() {
    const searchInput = document.getElementById('codex-search-input') as HTMLInputElement;
    if (searchInput) {
        searchInput.value = '';
        
        // Hide clear button
        const clearSearchBtn = document.getElementById('clear-search');
        if (clearSearchBtn) {
            clearSearchBtn.style.display = 'none';
        }
    }
}

function performSearch(query: string) {
    const monsterCodex = document.getElementById('monster-codex') as any;
    if (monsterCodex) {
        monsterCodex.query = query;
    }
}

function updateUrl(state: CodexState) {
    let url = '/codex/';
    
    if (state.tab === 'search') {
        url += '#search';
        if (state.query) {
            url += `?query=${encodeURIComponent(state.query)}`;
        }
    } else if (state.tab === 'browse') {
        url += '#browse';
    }
    
    // Only update if URL actually changed
    if (window.location.href !== window.location.origin + url) {
        window.history.pushState(state, '', url);
    }
}

function handlePopState(event: PopStateEvent) {
    const state = event.state as CodexState | null;
    
    if (state) {
        setActiveTab(state.tab);
        if (state.tab === 'search' && state.query) {
            setSearchQuery(state.query);
            performSearch(state.query);
        } else {
            clearSearchInput();
        }
    } else {
        // Fallback: parse URL state
        const currentState = parseUrlState();
        setActiveTab(currentState.tab);
        if (currentState.tab === 'search' && currentState.query) {
            setSearchQuery(currentState.query);
            performSearch(currentState.query);
        }
    }
}