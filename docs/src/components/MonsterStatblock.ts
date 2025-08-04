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
     */
    private captureCurrentHeight(): void {
        if (this.statblockRef.value) {
            const currentHeight = this.statblockRef.value.offsetHeight;
            this.lastKnownHeight = Math.max(currentHeight, this.lastKnownHeight);
        }
    }

    /**
     * Preserve height during transition to prevent flickering
     * Returns a cleanup function to restore natural height
     */
    private preserveHeightDuringTransition(): () => void {
        this.captureCurrentHeight();

        if (this.statblockRef.value && this.lastKnownHeight > 0) {
            this.statblockRef.value.style.height = `${this.lastKnownHeight}px`;
            this.statblockRef.value.style.transition = 'height 0.3s cubic-bezier(0.4,0,0.2,1)';
        }

        // Return cleanup function
        return () => {
            if (this.statblockRef.value) {
                requestAnimationFrame(() => {
                    if (this.statblockRef.value) {
                        const naturalHeight = this.statblockRef.value.scrollHeight;
                        this.statblockRef.value.style.height = `${naturalHeight}px`;

                        // After transition, remove explicit height
                        setTimeout(() => {
                            if (this.statblockRef.value) {
                                this.statblockRef.value.style.height = '';
                                this.statblockRef.value.style.transition = '';
                            }
                        }, 300);
                    }
                });
            }
        };
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
        finishTransition();
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
                // Use updateComplete to ensure the DOM is ready before appending
                this.updateComplete.then(() => {
                    if (this.statblockRef.value) {
                        // Clear existing content
                        this.statblockRef.value.innerHTML = '';
                        // Append new statblock
                        this.statblockRef.value.appendChild(statblockElement);
                    }
                });

                return html`
                    <div ${ref(this.statblockRef)} id="statblock-container"></div>
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