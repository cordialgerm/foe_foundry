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
            transition: height 0.3s ease-out;
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--bs-muted, #6c757d);
        }

        .error {
            text-align: center;
            padding: 2rem;
            color: var(--bs-danger, #dc3545);
            background-color: var(--bs-danger-bg, #f8d7da);
            border: 1px solid var(--bs-danger-border, #f5c2c7);
            border-radius: 0.375rem;
        }

        /* Animation styles consolidated from RerollButton */
        .stat-block.pop-out {
            animation: pop-out 0.2s forwards;
        }

        .stat-block.pop-in {
            animation: pop-in 0.2s forwards;
        }

        .stat-block.summon-effect {
            animation:
                summon-flash 0.4s ease,
                scale-throb 0.4s ease,
                summon-fade 0.4s ease;
        }

        @keyframes pop-out {
            from {
                transform: scale(1);
                opacity: 1;
            }
            to {
                transform: scale(0.95);
                opacity: 0;
            }
        }

        @keyframes pop-in {
            from {
                transform: scale(1.05);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }

        @keyframes summon-flash {
            0% {
                box-shadow: 0 0 0 0 var(--primary-color);
            }
            10% {
                box-shadow: 0 0 4px 1px var(--primary-color);
            }
            30% {
                box-shadow: 0 0 8px 3px var(--primary-color);
            }
            50% {
                box-shadow: 0 0 12px 6px var(--primary-color);
            }
            70% {
                box-shadow: 0 0 8px 3px var(--primary-color);
            }
            90% {
                box-shadow: 0 0 4px 1px var(--primary-color);
            }
            100% {
                box-shadow: 0 0 0 0 var(--primary-color);
            }
        }

        @keyframes scale-throb {
            0% {
                transform: scale(1);
            }
            40% {
                transform: scale(1.025);
            }
            60% {
                transform: scale(1.015);
            }
            100% {
                transform: scale(1);
            }
        }

        @keyframes summon-fade {
            0%, 100% {
                opacity: 1;
                filter: brightness(1);
            }
            50% {
                opacity: 0.8;
                filter: brightness(1.3);
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

    private monsters = initializeMonsterStore();
    private statblockRef: Ref<HTMLDivElement> = createRef();
    private lastKnownHeight: number = 0;

    // Use Lit Task for async statblock loading
    private _statblockTask = new Task(this, {
        task: async ([monsterKey, hpMultiplier, damageMultiplier, powers, changeType], { signal }) => {
            // Use provided monster key or fall back to window.defaultMonsterKey
            const effectiveMonsterKey = monsterKey || (window as any).defaultMonsterKey;

            if (!effectiveMonsterKey) {
                throw new Error('No monster key provided and no default monster key available');
            }

            if (this.shadowRoot) {
                await adoptExternalCss(this.shadowRoot);
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
        args: () => [this.monsterKey, this.hpMultiplier, this.damageMultiplier, this.powers, this.changeType]
    });

    /**
     * Capture the current height of the statblock container for smooth transitions
     * Only captures if there's actual statblock content (not loading/error states)
     */
    private captureCurrentHeight(): void {
        if (this.statblockRef.value) {
            const statblockContent = this.statblockRef.value.querySelector('.stat-block');
            if (statblockContent) {
                const currentHeight = this.statblockRef.value.offsetHeight;
                this.lastKnownHeight = Math.max(this.lastKnownHeight, currentHeight, 300);
            }
        }
    }

    /**
     * Preserve height during transition to prevent flickering
     * Returns a cleanup function to restore natural height
     */
    private preserveHeightDuringTransition(): () => Promise<void> {

        return async () => {
            await this._sleep(50);
        }

        // // Capture current height if we have actual statblock content
        // const hasStatblockContent = this.statblockRef.value?.querySelector('.stat-block');
        // if (hasStatblockContent) {
        //     this.captureCurrentHeight();
        // }

        // // Set explicit height to current height
        // if (this.statblockRef.value && this.lastKnownHeight > 0) {
        //     this.statblockRef.value.style.height = `${this.lastKnownHeight}px`;
        //     this.statblockRef.value.style.overflow = 'hidden';
        // }

        // // Return async cleanup function
        // return async () => {
        //     if (!this.statblockRef.value) return;

        //     // Wait for new content to render
        //     await this._sleep(50);

        //     if (!this.statblockRef.value) return;

        //     // Enable transition and remove explicit height to animate to natural size
        //     this.statblockRef.value.style.transition = 'height 0.3s ease-out';
        //     this.statblockRef.value.style.height = '';

        //     // Wait for transition to complete
        //     await this._sleep(300);

        //     if (!this.statblockRef.value) return;

        //     // Clean up transition styles
        //     this.statblockRef.value.style.transition = '';
        //     this.statblockRef.value.style.overflow = '';
        // };
    }

    /**
     * Sleep utility for animations
     */
    private _sleep(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Unified reroll method that handles bulk property updates, animations, and height preservation
     */
    async reroll(updates: {
        monsterKey?: string;
        hpMultiplier?: number;
        damageMultiplier?: number;
        powers?: string;
        changeType?: StatblockChangeType;
    }): Promise<void> {
        // Preserve height during transition
        const finishTransition = this.preserveHeightDuringTransition();

        // Find current statblock for animations
        const currentStatblock = this.statblockRef.value?.querySelector('.stat-block');

        // Trigger pop-out animation
        // if (currentStatblock) {
        //     currentStatblock.classList.add('pop-out');
        // }

        // Wait for pop-out animation
        // await this._sleep(200);

        // Update properties
        if (updates.monsterKey !== undefined) this.monsterKey = updates.monsterKey;
        if (updates.hpMultiplier !== undefined) this.hpMultiplier = updates.hpMultiplier;
        if (updates.damageMultiplier !== undefined) this.damageMultiplier = updates.damageMultiplier;
        if (updates.powers !== undefined) this.powers = updates.powers;
        if (updates.changeType !== undefined) this.changeType = updates.changeType;

        // Wait for task to complete and new statblock to render
        await this.updateComplete;
        await this._statblockTask.taskComplete;

        // Find new statblock and trigger pop-in animation
        // const newStatblock = this.statblockRef.value?.querySelector('.stat-block');
        // if (newStatblock) {
        //     newStatblock.classList.add('pop-in');

        //     // Wait for pop-in animation
        //     await this._sleep(200);
        //     newStatblock.classList.remove('pop-in');

        //     // Wait a bit before summon effect
        //     await this._sleep(200);
        //     newStatblock.classList.add('summon-effect');

        //     // Remove summon effect after animation
        //     await this._sleep(400);
        //     newStatblock.classList.remove('summon-effect');
        // }

        // Clean up height transition
        await finishTransition();
    }

    render() {
        return this._statblockTask.render({
            pending: () => html`
                <div class="loading">
                    Loading statblock...
                </div>
            `,
            error: (e) => html`
                <div class="error">
                    Error: ${e instanceof Error ? e.message : String(e)}
                </div>
            `,
            complete: (statblockElement: Element) => {
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