/**
 * Utility for adopting external CSS files into Shadow DOM components
 */

/**
 * Adopts an external CSS file into a Shadow DOM component
 * @param shadowRoot The shadow root to adopt the CSS into
 * @param cssPath The path to the CSS file to adopt (default: '/css/site.css')
 * @returns Promise that resolves when CSS is adopted or falls back
 */
export async function adoptExternalCss(shadowRoot: ShadowRoot, cssPath: string = '/css/site.css'): Promise<void> {
    // Check if the browser supports constructable stylesheets
    const supportsAdopted = 'adoptedStyleSheets' in Document.prototype && 'replace' in CSSStyleSheet.prototype;

    if (supportsAdopted) {
        try {
            const resp = await fetch(cssPath);
            const cssText = await resp.text();
            const sheet = new CSSStyleSheet();
            await sheet.replace(cssText);
            shadowRoot.adoptedStyleSheets = [sheet, ...shadowRoot.adoptedStyleSheets];
        } catch (e) {
            // fallback: do nothing, let component styles apply
            console.warn(`Failed to adopt CSS from ${cssPath}:`, e);
        }
    } else {
        // Fallback for browsers like Firefox: inject <style> tag
        try {
            const resp = await fetch(cssPath);
            const cssText = await resp.text();
            const style = document.createElement('style');
            style.textContent = cssText;
            shadowRoot.prepend(style);
        } catch (e) {
            console.warn(`Failed to inject CSS from ${cssPath}:`, e);
        }
    }
}

/**
 * Mixin for Lit components to easily adopt site CSS
 * Usage: Apply this mixin to your Lit component class
 */
export function SiteCssMixin<T extends new (...args: any[]) => any>(Base: T) {
    return class extends Base {
        /**
         * Adopt the site CSS into this component's shadow root
         * Call this in firstUpdated() or connectedCallback()
         */
        async adoptSiteCss(cssPath: string = '/css/site.css'): Promise<void> {
            if (this.shadowRoot) {
                await adoptExternalCss(this.shadowRoot, cssPath);
            }
        }
    };
}
