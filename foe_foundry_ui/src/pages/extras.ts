// General page functionality for Foe Foundry
// Includes beta banner, statblock wrapping, mask randomization, anchors, and MkDocs fixes

// Export to make this file a module
export { };

// Declare global types
declare global {
    interface Window {
        AnchorJS: any;
    }
}

let statblockId = 0;

// Initialize general functionality - can be called from any page
export function initializeGeneralFunctionality() {
    console.log('Initializing general Foe Foundry functionality...');
    initBetaBanner();
    wrapStatblocks();
    randomizeMasks();
    initAnchors();
    fixMkDocsLayout();
}

// Auto-initialize if this module is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeGeneralFunctionality);
} else {
    // DOM is already loaded
    initializeGeneralFunctionality();
}

function initBetaBanner() {
    const banner = document.getElementById("beta-banner") as HTMLElement;
    const dismissBtn = document.getElementById("dismiss-banner") as HTMLButtonElement;
    const params = new URLSearchParams(window.location.search);

    if (!banner || !dismissBtn) return;

    // Hide if user already dismissed it or in print mode
    if (localStorage.getItem("hideBetaBanner") === "true" || params.get('render') === 'print') {
        console.log("Beta banner previously dismissed by user.");
        banner.style.display = "none !important";
    } else {
        console.log("Displaying Beta banner.");
        banner.style.display = ""; // remove the previous style that was hiding the banner
    }

    dismissBtn.addEventListener("click", () => {
        console.log("Beta banner dismissed by user.");
        banner.style.display = "none !important";
        localStorage.setItem("hideBetaBanner", "true");
    });
}

function wrapStatblocks() {
    const statblocks = document.querySelectorAll('.stat-block');

    statblocks.forEach(statblock => {
        const statblockElement = statblock as HTMLElement;

        // Give the statblock a unique HTML ID if it doesn't have one
        if (!statblockElement.id) {
            statblockElement.id = `statblock-${++statblockId}`;
        }

        // Create the monster-statblock wrapper
        const wrapper = document.createElement('monster-statblock');
        wrapper.setAttribute('use-slot', '');

        // Insert the wrapper before the statblock
        if (statblockElement.parentNode) {
            statblockElement.parentNode.insertBefore(wrapper, statblockElement);

            // Move the statblock inside the wrapper as a slot
            wrapper.appendChild(statblockElement);
        }
    });
}

export function randomizeMasks() {
    const variants = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6'];

    document.querySelectorAll('.masked').forEach(el => {
        const element = el as HTMLElement;
        const hasVariant = variants.some(variant => element.classList.contains(variant));

        if (!hasVariant) {
            const random = variants[Math.floor(Math.random() * variants.length)];
            element.classList.add(random);
        }
    });
}

function initAnchors() {
    // Initialize anchor.js for linking to headings
    if (typeof window.AnchorJS !== 'undefined') {
        const anchors = new window.AnchorJS();
        anchors.options = {
            placement: 'right',
            class: 'anchor-link',
        };
        anchors.add('h1, h2, h3');
    }
}

function fixMkDocsLayout() {
    // Fix for MkDocs base.js applyTopPadding function
    // This overrides the problematic function to work with container-md
    function applyTopPadding() {
        // Update various absolute positions to match where the main container
        // starts. This is necessary for handling multi-line nav headers, since
        // that pushes the main container down.
        const container = document.querySelector('body > [class*="container"]') as HTMLElement;
        if (!container) return; // Exit early if no container found
        const offset = container.offsetTop;

        document.documentElement.style.scrollPaddingTop = offset + 'px';
        document.querySelectorAll('.bs-sidebar.affix').forEach(function (sidebar) {
            const sidebarElement = sidebar as HTMLElement;
            sidebarElement.style.top = offset + 'px';
        });
    }

    // Re-register the fixed function for resize events
    window.removeEventListener('resize', applyTopPadding);
    window.addEventListener('resize', applyTopPadding);

    // Apply immediately
    applyTopPadding();
}