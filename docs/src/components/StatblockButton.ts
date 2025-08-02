import { LitElement } from 'lit';
import { property } from 'lit/decorators.js';

/**
 * Base class for buttons that operate on statblocks.
 * Handles auto-registration with the StatblockController.
 */
export abstract class StatblockButton extends LitElement {
    @property({ type: String })
    target = '';

    @property({ type: Boolean, reflect: true })
    disabled = false;

    @property({ type: Boolean })
    detached = false;

    private _isRegistered = false;
    private _isBeingMoved = false;

    connectedCallback() {
        super.connectedCallback();
        if (this.target && !this._isRegistered && !this._isBeingMoved && !this.detached) {
            this._isRegistered = true;
            StatblockController.getInstance().registerButton(this.target, this);
        }
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        // Only unregister if we're not being moved to a new location and we were actually registered
        if (this.target && this._isRegistered && !this._isBeingMoved && !this.detached) {
            this._isRegistered = false;
            StatblockController.getInstance().unregisterButton(this.target, this);
        }
    }

    findTargetStatblock(): Element | null {
        if (!this.target) return null;

        const element = document.getElementById(this.target);
        if (!element) return null;

        // Case 1: Direct stat-block div with data-monster attribute
        if (element.classList.contains('stat-block') && element.hasAttribute('data-monster')) {
            return element;
        }

        // Case 2: Custom <monster-statblock> element - look in shadow DOM
        if (element.tagName.toLowerCase() === 'monster-statblock') {
            const shadowRoot = element.shadowRoot;
            if (shadowRoot) {
                const statBlock = shadowRoot.querySelector('.stat-block[data-monster]');
                if (statBlock) {
                    return statBlock;
                }
            }
        }

        return null;
    }

    get monsterKey(): string {
        const statblock = this.findTargetStatblock();
        return statblock?.getAttribute('data-monster') || '';
    }
}

/**
 * Manages statblock wrappers and button panels.
 * Automatically creates wrappers when the first button is registered.
 */
class StatblockController {
    private static instance: StatblockController;
    private wrappers = new Map<string, StatblockWrapper>();

    static getInstance(): StatblockController {
        if (!StatblockController.instance) {
            StatblockController.instance = new StatblockController();
        }
        return StatblockController.instance;
    }

    registerButton(statblockId: string, button: StatblockButton): void {
        let wrapper = this.wrappers.get(statblockId);

        if (!wrapper) {
            // First button for this statblock - create wrapper and panel
            const newWrapper = this.createWrapper(statblockId);
            if (newWrapper) {
                wrapper = newWrapper;
                this.wrappers.set(statblockId, wrapper);
            } else {
                return; // Could not create wrapper
            }
        }

        wrapper.addButton(button);
    }

    unregisterButton(statblockId: string, button: StatblockButton): void {
        const wrapper = this.wrappers.get(statblockId);
        if (wrapper) {
            wrapper.removeButton(button);

            // If no buttons left, clean up the wrapper
            if (wrapper.isEmpty()) {
                wrapper.destroy();
                this.wrappers.delete(statblockId);
            }
        }
    }

    private createWrapper(statblockId: string): StatblockWrapper | null {
        const statblock = document.getElementById(statblockId);
        if (!statblock || statblock.closest('.statblock-wrapper')) {
            return null; // Already wrapped or doesn't exist
        }

        // Create wrapper div
        const wrapperEl = document.createElement('div');
        wrapperEl.className = 'statblock-wrapper';
        wrapperEl.setAttribute('data-monster', statblock.getAttribute('data-monster') || '');

        // Create button panel
        const buttonPanel = document.createElement('div');
        buttonPanel.className = 'statblock-button-panel';

        // Insert wrapper into DOM
        statblock.parentNode?.insertBefore(wrapperEl, statblock);
        wrapperEl.appendChild(statblock);
        wrapperEl.appendChild(buttonPanel);

        return new StatblockWrapper(wrapperEl, buttonPanel);
    }
}

/**
 * Manages a single statblock wrapper and its button panel.
 */
class StatblockWrapper {
    private buttons: StatblockButton[] = [];
    private mediaQuery!: MediaQueryList;

    constructor(
        private wrapperElement: HTMLDivElement,
        private buttonPanel: HTMLDivElement
    ) {
        this.setupStyles();
        this.setupResponsiveStyles();
    }

    addButton(button: StatblockButton): void {
        if (!this.buttons.includes(button)) {
            this.buttons.push(button);
            // Only move the button if it's not already in the panel and it's not detached
            if (button.parentNode !== this.buttonPanel && !button.detached) {
                // Set flag to prevent re-registration during DOM move
                (button as any)._isBeingMoved = true;
                this.buttonPanel.appendChild(button);
                (button as any)._isBeingMoved = false;
            }
        }
    }

    removeButton(button: StatblockButton): void {
        const index = this.buttons.indexOf(button);
        if (index > -1) {
            this.buttons.splice(index, 1);
            // Only remove from DOM if it's actually in the panel
            if (button.parentNode === this.buttonPanel) {
                this.buttonPanel.removeChild(button);
            }
        }
    }

    isEmpty(): boolean {
        return this.buttons.length === 0;
    }

    destroy(): void {
        // Move statblock back to original position
        const statblock = this.wrapperElement.querySelector('.stat-block');
        if (statblock && this.wrapperElement.parentNode) {
            this.wrapperElement.parentNode.insertBefore(statblock, this.wrapperElement);
        }

        // Remove wrapper from DOM
        this.wrapperElement.remove();

        // Clean up media query listener
        this.mediaQuery?.removeEventListener('change', this.updateResponsiveStyles);
    }

    private setupStyles(): void {
        // Apply base wrapper styles
        Object.assign(this.wrapperElement.style, {
            display: 'flex',
            gap: '1rem',
            alignItems: 'flex-start'
        });

        // Apply button panel styles
        Object.assign(this.buttonPanel.style, {
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem',
            alignItems: 'flex-start'
        });
    }

    private setupResponsiveStyles(): void {
        this.mediaQuery = window.matchMedia('(max-width: 600px)');
        this.updateResponsiveStyles = this.updateResponsiveStyles.bind(this);
        this.updateResponsiveStyles(this.mediaQuery);
        this.mediaQuery.addEventListener('change', this.updateResponsiveStyles);
    }

    private updateResponsiveStyles(e: MediaQueryListEvent | MediaQueryList): void {
        if (e.matches) {
            // Small screen: stack vertically, center buttons
            Object.assign(this.wrapperElement.style, {
                flexDirection: 'column',
                alignItems: 'center'
            });
            Object.assign(this.buttonPanel.style, {
                flexDirection: 'row',
                justifyContent: 'center'
            });
        } else {
            // Large screen: side by side
            Object.assign(this.wrapperElement.style, {
                flexDirection: 'row',
                alignItems: 'flex-start'
            });
            Object.assign(this.buttonPanel.style, {
                flexDirection: 'column',
                justifyContent: 'flex-start'
            });
        }
    }
}
