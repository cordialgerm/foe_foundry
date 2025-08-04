import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { createRef, ref, Ref } from 'lit/directives/ref.js';
import { Task } from '@lit/task';
import { initializeMonsterStore } from '../data/api';
import { StatblockRequest, StatblockChange, StatblockChangeType } from '../data/monster';
import { Power } from '../data/powers';
import { adoptExternalCss } from '../utils';

@customElement('monster-statblock')
export class MonsterStatblock extends LitElement {
    static styles = css`
        :host {
            display: block;
            width: 100%;
        }

        #statblock-container {
            width: 100%;
            min-height: 300px;
            transition: height 0.3s ease-in-out;
            overflow: hidden;
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
            background-color: rgba(255, 255, 255, 0.2);
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

    private monsters = initializeMonsterStore();
    private statblockRef: Ref<HTMLDivElement> = createRef();
    private _cachedStatblock: Element | null = null;

    // Use Lit Task for async statblock loading
    private _statblockTask = new Task(this, {
        task: async ([monsterKey, hpMultiplier, damageMultiplier, powers, changeType, random], { signal }) => {
            if (this.shadowRoot) {
                await adoptExternalCss(this.shadowRoot);
            }

            // If random flag is set, use the random statblock endpoint
            if (random) {
                const statblockElement = await this.monsters.getRandomStatblock();

                if (!statblockElement) {
                    throw new Error('Failed to generate random statblock');
                }

                return statblockElement;
            }

            // Use provided monster key or fall back to window.defaultMonsterKey
            const effectiveMonsterKey = monsterKey || (window as any).defaultMonsterKey;

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
                changedPower: null
            } : null;

            const statblockElement = await this.monsters.getStatblock(request, change);

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
        random?: boolean;
    }): Promise<void> {

        // Update properties
        if (updates.monsterKey !== undefined) this.monsterKey = updates.monsterKey;
        if (updates.hpMultiplier !== undefined) this.hpMultiplier = updates.hpMultiplier;
        if (updates.damageMultiplier !== undefined) this.damageMultiplier = updates.damageMultiplier;
        if (updates.powers !== undefined) this.powers = updates.powers;
        if (updates.changeType !== undefined) this.changeType = updates.changeType;
        if (updates.random !== undefined) this.random = updates.random;

        // Wait for task to complete and new statblock to render
        await this.updateComplete;
        await this._statblockTask.taskComplete;
    }

    render() {
        return this._statblockTask.render({
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
        });
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'monster-statblock': MonsterStatblock;
    }
}