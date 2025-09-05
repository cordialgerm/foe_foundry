import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { createRef, ref, Ref } from 'lit/directives/ref.js';
import { Task } from '@lit/task';
import { initializeMonsterStore } from '../data/api';
import { StatblockRequest, StatblockChange, StatblockChangeType, MonsterStore } from '../data/monster';
import { Power } from '../data/powers';
import { adoptExternalCss } from '../utils';
import './ForgeButton.js';
import './RerollButton.js';
import './DownloadButton.js';
import { getFeatureFlags, FeatureFlags } from '../utils/growthbook';

@customElement('monster-statblock')
export class MonsterStatblock extends LitElement {
    static styles = css`
        :host {
            display: block;
            width: 100%;
        }

        .statblock-wrapper {
            display: flex;
            gap: 1rem;
            align-items: flex-start;
        }

        .statblock-button-panel {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            align-items: flex-start;
        }

            @media print {
                .statblock-button-panel {
                    display: none !important;
                }
            }

        #statblock-container {
            width: 100%;
            min-height: 300px;
            transition: height 0.3s ease-in-out;
            overflow: hidden;
            contain: layout style; /* Prevent layout shifts from statblock changes */
        }

        .loading.empty {
            text-align: center;
            padding: 2rem;
            color: var(--bs-muted, #6c757d);
        }

        .loading.cached {
            position: relative;
        }

        .loading.cached::after {
            content: "Loading...";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--tertiary-color, #0d6efd);
            z-index: 10;
            backdrop-filter: blur(1px);
        }

        .error {
            text-align: center;
            padding: 2rem;
            color: var(--bs-danger, #dc3545);
            background-color: var(--bs-danger-bg, #f8d7da);
            border: 1px solid var(--bs-danger-border, #f5c2c7);
            border-radius: 0.375rem;
        }

        .hp-changed,
        .damage-changed,
        .power-changed {
            color: var(--tertiary-color);
            animation: pop-in 0.8s ease;
            will-change: transform, opacity;
        }
        @keyframes pop-in {
        0% {
            transform: scale(1);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.2);
            opacity: 1;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }

        /* Responsive styles */
        @media (max-width: 600px) {
            .statblock-wrapper {
                flex-direction: column;
                align-items: center;
            }

            .statblock-button-panel {
                flex-direction: row;
                justify-content: center;
            }
        }
    `;

    @property({ attribute: 'monster-key' })
    monsterKey: string = '';

    @property({ type: Number, attribute: 'hp-multiplier' })
    hpMultiplier: number = 1;

    @property({ type: Number, attribute: 'damage-multiplier' })
    damageMultiplier: number = 1;

    @property({ attribute: 'powers' })
    powers: string = '';

    @property({ attribute: 'change-type' })
    changeType?: StatblockChangeType;

    @property({ type: Boolean })
    random: boolean = false;

    @property({ type: Boolean, attribute: 'use-slot' })
    useSlot: boolean = false;

    @property({ type: Boolean, attribute: 'hide-buttons' })
    hideButtons: boolean = false;

    @property({ type: Boolean, attribute: 'print-preview' })
    printPreview: boolean = false;

    @property({ type: Boolean, attribute: 'src-from-url' })
    srcFromUrl: boolean = false;

    @property({ attribute: 'link-header' })
    linkHeader: string = '';

    @property({ type: Object })
    monsterStore?: MonsterStore;
    private statblockRef: Ref<HTMLDivElement> = createRef();
    private _cachedStatblock: Element | null = null;
    private _changedPower: Power | null = null;
    private _cachedFlags: FeatureFlags | null = null;

    async connectedCallback() {
        super.connectedCallback();

        // Load feature flags early
        this._cachedFlags = await getFeatureFlags();

        // If src-from-url is set, load state from URL parameters
        if (this.srcFromUrl) {
            this.fromUrlParams();
        }

        // If we have slotted content, cache it for potential future use
        if (this.useSlot) {
            const slottedStatblock = this.getSlottedContent();
            if (slottedStatblock) {
                this._cachedStatblock = slottedStatblock.cloneNode(true) as Element;
            }
        }

        // Trigger re-render after flags are loaded
        this.requestUpdate();
    }

    updated(changedProperties: Map<string | number | symbol, unknown>) {
        super.updated(changedProperties);

        // If src-from-url property changed to true, load from URL
        if (changedProperties.has('srcFromUrl') && this.srcFromUrl) {
            this.fromUrlParams();
        }

        // Apply print-preview class after content updates
        this.applyPrintPreviewClass();
    }

    getSlottedContent(): Element | null {
        if (this.useSlot) {
            return this.querySelector('.stat-block') || this.querySelector('[slot]') || this.firstElementChild;
        }
        return null;
    }

    getSlottedMonsterKey(): string | null {
        const slottedContent = this.getSlottedContent();
        // get data-monster attribute
        return slottedContent ? slottedContent.getAttribute('data-monster') : null;
    }

    getEffectiveMonsterKey() {
        return this.monsterKey || this.getSlottedMonsterKey() || this.statblockRef.value?.querySelector('.stat-block')?.getAttribute('data-monster') || null;
    }

    /**
     * Convert current component state to URL parameters
     * @returns URLSearchParams object with current state
     */
    toUrlParams(): URLSearchParams {
        const params = new URLSearchParams();

        const effectiveMonsterKey = this.getEffectiveMonsterKey();
        if (effectiveMonsterKey) {
            params.set('monster-key', effectiveMonsterKey);
        }

        if (this.hpMultiplier !== 1) {
            params.set('hp-multiplier', this.hpMultiplier.toString());
        }

        if (this.damageMultiplier !== 1) {
            params.set('damage-multiplier', this.damageMultiplier.toString());
        }

        if (this.powers && this.powers.trim()) {
            params.set('powers', this.powers);
        }

        return params;
    }

    /**
     * Get the payload object for API statblock generation requests
     * @returns Object with current component state formatted for API
     */
    getStatblockPayload(): { monster_key: string; powers: string[]; hp_multiplier: number; damage_multiplier: number } {
        const effectiveMonsterKey = this.getEffectiveMonsterKey() || '';
        const powers = this.powers ? this.powers.split(',').map((p: string) => p.trim()).filter((p: string) => p) : [];

        return {
            monster_key: effectiveMonsterKey,
            powers: powers,
            hp_multiplier: this.hpMultiplier || 1,
            damage_multiplier: this.damageMultiplier || 1
        };
    }

    /**
     * Set component state from URL parameters
     * @param urlParams Optional URLSearchParams object. If not provided, uses current window location
     */
    fromUrlParams(urlParams?: URLSearchParams): void {
        const params = urlParams || new URLSearchParams(window.location.search);

        const monsterKey = params.get('monster-key');
        if (monsterKey) {
            this.monsterKey = monsterKey;
        }

        const hpMultiplier = params.get('hp-multiplier');
        if (hpMultiplier) {
            const parsed = parseFloat(hpMultiplier);
            if (!isNaN(parsed) && parsed > 0) {
                this.hpMultiplier = parsed;
            }
        }

        const damageMultiplier = params.get('damage-multiplier');
        if (damageMultiplier) {
            const parsed = parseFloat(damageMultiplier);
            if (!isNaN(parsed) && parsed > 0) {
                this.damageMultiplier = parsed;
            }
        }

        const powers = params.get('powers');
        if (powers) {
            this.powers = powers;
        }
    }

    /**
     * Apply print-preview class to stat-block elements if print-preview flag is set
     */
    private applyPrintPreviewClass() {
        if (this.printPreview) {
            // For slotted content, check the light DOM
            if (this.useSlot) {
                const statBlocks = this.querySelectorAll('.stat-block');
                statBlocks.forEach(block => {
                    block.classList.add('print-preview');
                });
            }
            // For dynamically loaded content, check the shadow DOM container
            else if (this.statblockRef.value) {
                const statBlocks = this.statblockRef.value.querySelectorAll('.stat-block');
                statBlocks.forEach(block => {
                    block.classList.add('print-preview');
                });
            }
        }
    }

    /**
     * Apply link-header functionality to make monster names clickable
     */
    private applyLinkHeader(statblockElement: Element) {
        if (!this.linkHeader) return;

        // Find the monster name header elements in the statblock
        const nameHeaders = statblockElement.querySelectorAll('.stat-block .creature-heading h1, .stat-block .creature-heading .creature-name, .stat-block h1');
        
        nameHeaders.forEach(header => {
            const monsterKey = this.getEffectiveMonsterKey();
            if (monsterKey && header.textContent) {
                // Create a link element
                const link = document.createElement('a');
                link.href = `/monsters/${this.linkHeader}/#${monsterKey}`;
                link.style.color = 'inherit';
                link.style.textDecoration = 'none';
                link.textContent = header.textContent;
                
                // Replace the header content with the link
                header.innerHTML = '';
                header.appendChild(link);
            }
        });
    }

    /**
     * Apply link-header functionality to slotted content
     */
    private applyLinkHeaderToSlottedContent() {
        if (!this.linkHeader) return;

        // Find the monster name header elements in slotted content
        const nameHeaders = this.querySelectorAll('.stat-block .creature-heading h1, .stat-block .creature-heading .creature-name, .stat-block h1');
        
        nameHeaders.forEach(header => {
            const monsterKey = this.getEffectiveMonsterKey();
            if (monsterKey && header.textContent && !header.querySelector('a')) {
                // Create a link element (only if not already linked)
                const link = document.createElement('a');
                link.href = `/monsters/${this.linkHeader}/#${monsterKey}`;
                link.style.color = 'inherit';
                link.style.textDecoration = 'none';
                link.textContent = header.textContent;
                
                // Replace the header content with the link
                header.innerHTML = '';
                header.appendChild(link);
            }
        });
    }

    // Use Lit Task for async statblock loading
    private _statblockTask = new Task(this, {
        task: async ([monsterKey, hpMultiplier, damageMultiplier, powers, changeType, random], { signal }) => {

            if (this.shadowRoot) {
                await adoptExternalCss(this.shadowRoot);
            }

            const store = this.monsterStore || initializeMonsterStore();

            // If random flag is set, use the random statblock endpoint
            if (random) {
                const statblockElement = await store.getRandomStatblock();

                if (!statblockElement) {
                    throw new Error('Failed to generate random statblock');
                }

                return statblockElement;
            }

            // Use provided monster key, slotted key, or fall back to window.defaultMonsterKey
            const effectiveMonsterKey = monsterKey || this.getSlottedMonsterKey() || (window as any).defaultMonsterKey;

            if (!effectiveMonsterKey) {
                throw new Error('No monster key provided and no default monster key available');
            }

            // Parse powers CSV string into Power array
            const powerArray: Power[] = [];
            if (powers && powers.trim()) {
                const powerKeys = powers.split(',').map(key => key.trim()).filter(key => key);
                // Note: For now we'll create basic Power objects with just the key
                // In a full implementation, we'd fetch full power data
                powerArray.push(...powerKeys.map(key => ({
                    key,
                    name: key,
                    powerCategory: '',
                    icon: ''
                })));
            }

            const request: StatblockRequest = {
                monsterKey: effectiveMonsterKey,
                powers: powerArray,
                hpMultiplier: hpMultiplier || 1,
                damageMultiplier: damageMultiplier || 1,
            };

            // Create StatblockChange object if changeType is provided
            const change: StatblockChange | null = changeType ? {
                type: changeType,
                changedPower: this._changedPower
            } : null;

            const statblockElement = await store.getStatblock(request, change);

            if (!statblockElement) {
                throw new Error('Failed to generate statblock');
            }

            return statblockElement;
        },
        args: () => [this.monsterKey, this.hpMultiplier, this.damageMultiplier, this.powers, this.changeType, this.random]
    });

    /**
     * Unified reroll method that handles bulk property updates, animations, and height preservation
     */
    async reroll(updates: {
        monsterKey?: string;
        hpMultiplier?: number;
        damageMultiplier?: number;
        powers?: string;
        changeType?: StatblockChangeType;
        changedPower?: Power;
        random?: boolean;
    }): Promise<void> {

        // if there are no updates, force task to re-run to regenerate statblock
        if (Object.keys(updates).length === 0) {
            // If using slot, transition to dynamic rendering to allow refresh
            if (this.useSlot) {
                const monsterKey = this.getSlottedMonsterKey();
                if (!monsterKey) {
                    throw new Error('No monster key provided and no slotted monster key available');
                }

                // Cache the current slotted content before transitioning to prevent stutter
                const currentSlottedContent = this.getSlottedContent();
                if (currentSlottedContent && !this._cachedStatblock) {
                    this._cachedStatblock = currentSlottedContent.cloneNode(true) as Element;
                }

                this.useSlot = false;  // replace any slotted content with dynamic rendering
                this.monsterKey = monsterKey;  // ensure we have a monster key going forward

                // Wait for the component to re-render with dynamic content
                await this.updateComplete;
            }

            // Force the task to re-run by updating the task args
            this._statblockTask.run();
            await this._statblockTask.taskComplete;
            return;
        }

        // Update properties
        if (updates.monsterKey !== undefined) this.monsterKey = updates.monsterKey;
        if (updates.hpMultiplier !== undefined) this.hpMultiplier = updates.hpMultiplier;
        if (updates.damageMultiplier !== undefined) this.damageMultiplier = updates.damageMultiplier;
        if (updates.powers !== undefined) this.powers = updates.powers;
        if (updates.changeType !== undefined) this.changeType = updates.changeType;
        if (updates.random !== undefined) this.random = updates.random;

        this._changedPower = updates.changedPower || null;

        if (this.useSlot) {
            const monsterKey = this.getSlottedMonsterKey();
            if (!monsterKey) {
                throw new Error('No monster key provided and no slotted monster key available');
            }

            // Cache the current slotted content before transitioning to prevent stutter
            const currentSlottedContent = this.getSlottedContent();
            if (currentSlottedContent && !this._cachedStatblock) {
                this._cachedStatblock = currentSlottedContent.cloneNode(true) as Element;
            }

            this.useSlot = false;  // replace any slotted content with dynamic rendering
            this.monsterKey = monsterKey;  // ensure we have a monster key going forward
        }

        // Wait for task to complete and new statblock to render
        await this.updateComplete;
        await this._statblockTask.taskComplete;
    }

    render() {

        // If using slot-based content, render the slotted content directly
        if (this.useSlot) {
            // Apply link-header functionality to existing slotted content
            if (this.linkHeader) {
                this.applyLinkHeaderToSlottedContent();
            }
            
            return html`
                <div class="statblock-wrapper">
                    <div ${ref(this.statblockRef)} id="statblock-container">
                        <slot></slot>
                    </div>
                    ${!this.hideButtons ? this._renderButtonPanel(this._cachedFlags?.showStatblockDownloadOptions) : ''}
                </div>
            `;
        }

        return this._statblockTask.render({
            pending: () => {
                if (this._cachedStatblock && this._cachedFlags) {
                    // Show cached statblock while loading new one
                    return this._renderStatblock(this._cachedStatblock, this._cachedFlags, "loading cached");
                }
                return html`
                            <div class="loading empty">
                                Loading...
                            </div>
                        `;
            },
            error: (e) => {
                console.error(e);
                return html`
                    <div class="error">
                        Error: ${e instanceof Error ? e.message : String(e)}
                    </div>
                `;
            },
            complete: (statblockElement) => {

                // Cache the new statblock
                this._cachedStatblock = statblockElement;

                // Apply print-preview class if needed
                if (this.printPreview) {
                    const statBlocks = statblockElement.querySelectorAll('.stat-block');
                    statBlocks.forEach(block => {
                        block.classList.add('print-preview');
                    });
                }

                // Apply link-header functionality if provided
                this.applyLinkHeader(statblockElement);

                return this._renderStatblock(statblockElement, this._cachedFlags || undefined);
            }
        })
    }

    private _renderStatblock(statblockElement: Element, flags?: FeatureFlags, classes?: string) {
        return html`
        <div class="statblock-wrapper">
            <div ${ref(this.statblockRef)} id="statblock-container" class="${classes}">
                ${statblockElement}
            </div>
            ${!this.hideButtons ? this._renderButtonPanel(flags?.showStatblockDownloadOptions) : ''}
        </div>
        `;
    }

    private _renderButtonPanel(showDownload?: boolean) {

        const items = [];
        items.push(html`<reroll-button></reroll-button>`);
        items.push(html`<forge-button></forge-button>`);

        if (showDownload) {
            items.push(html`<download-button></download-button>`);
        }

        return html`
            <div class="statblock-button-panel">
                ${items}
            </div>
        `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'monster-statblock': MonsterStatblock;
    }
}