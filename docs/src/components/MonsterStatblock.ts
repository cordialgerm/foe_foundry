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

    @property({ type: Object })
    monsterStore?: MonsterStore;
    private statblockRef: Ref<HTMLDivElement> = createRef();
    private _cachedStatblock: Element | null = null;
    private _changedPower: Power | null = null;

    connectedCallback() {
        super.connectedCallback();

        // If we have slotted content, cache it for potential future use
        if (this.useSlot) {
            const slottedStatblock = this.getSlottedContent();
            if (slottedStatblock) {
                this._cachedStatblock = slottedStatblock.cloneNode(true) as Element;
            }
        }
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
            return html`
                <div class="statblock-wrapper">
                    <div ${ref(this.statblockRef)} id="statblock-container">
                        <slot></slot>
                    </div>
                    ${!this.hideButtons ? this._renderButtonPanel() : ''}
                </div>
            `;
        }

        // Otherwise use the existing dynamic task-based rendering
        return html`
            <div class="statblock-wrapper">
                ${this._statblockTask.render({
            pending: () => {
                if (this._cachedStatblock) {
                    // Show cached statblock while loading new one
                    return html`
                                <div ${ref(this.statblockRef)} id="statblock-container" class="loading cached">
                                    ${this._cachedStatblock}
                                </div>
                            `;
                }
                return html`
                            <div class="loading empty">
                                Loading...
                            </div>
                        `;
            },
            error: (e) => html`
                        <div class="error">
                            Error: ${e instanceof Error ? e.message : String(e)}
                        </div>
                    `,
            complete: (statblockElement: Element) => {

                // Cache the new statblock
                this._cachedStatblock = statblockElement;
                return html`
                            <div ${ref(this.statblockRef)} id="statblock-container">
                                ${statblockElement}
                            </div>
                        `;
            }
        })}
                ${!this.hideButtons ? this._renderButtonPanel() : ''}
            </div>
        `;
    }

    private _renderButtonPanel() {
        return html`
            <div class="statblock-button-panel">
                <reroll-button></reroll-button>
                <forge-button></forge-button>
            </div>
        `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'monster-statblock': MonsterStatblock;
    }
}