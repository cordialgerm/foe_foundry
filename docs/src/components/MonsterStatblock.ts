import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { Task } from '@lit/task';
import { initializeMonsterStore } from '../data/api';
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
    `;

    @property({ attribute: 'monster-key' })
    monsterKey: string = '';

    private monsters = initializeMonsterStore();

    // Use Lit Task for async statblock loading
    private _statblockTask = new Task(this, {
        task: async ([monsterKey], { signal }) => {
            // Use provided monster key or fall back to window.defaultMonsterKey
            const effectiveMonsterKey = monsterKey || (window as any).defaultMonsterKey;

            if (!effectiveMonsterKey) {
                throw new Error('No monster key provided and no default monster key available');
            }

            if (this.shadowRoot) {
                await adoptExternalCss(this.shadowRoot);
            }

            const request = {
                monsterKey: effectiveMonsterKey,
                powers: [], // Default to no additional powers
                hpMultiplier: 1,
                damageMultiplier: 1,
            };

            const statblockElement = await this.monsters.getStatblock(request, null);

            if (!statblockElement) {
                throw new Error('Failed to generate statblock');
            }

            return statblockElement;
        },
        args: () => [this.monsterKey]
    });

    private renderStatblock(statblockElement: Element) {
        // Use updateComplete to ensure the DOM is ready before appending
        this.updateComplete.then(() => {
            const container = this.shadowRoot?.getElementById('statblock-container');
            if (container) {
                // Clear existing content
                container.innerHTML = '';
                // Append new statblock
                container.appendChild(statblockElement);
            }
        });

        return html`
            <div id="statblock-container"></div>
        `;
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
            complete: (statblockElement: Element) => this.renderStatblock(statblockElement)
        });
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'monster-statblock': MonsterStatblock;
    }
}