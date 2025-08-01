
import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { MonsterCard } from '../components/MonsterCard';
import { initializeMonsterStore } from '../data/api';
import { Power } from '../data/powers';
import { StatblockChange, StatblockChangeType } from '../data/monster';
import { Task } from '@lit/task';
import { Monster, RelatedMonster } from '../data/monster';

@customElement('monster-builder')
export class MonsterBuilder extends LitElement {
    static styles = css`
    .monster-header {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }
    .monster-title {
      font-size: 2rem;
      font-weight: bold;
    }
    .nav-pills {
      display: flex;
      gap: 0.5rem;
    }
    .nav-pill {
      background: var(--bs-dark);
      color: var(--bs-light);
      border-radius: 999px;
      padding: 0.5rem;
      cursor: pointer;
      border: none;
      font-size: 1rem;
      transition: background 0.2s;
    }
    .nav-pill.active {
      background: var(--bs-light);
      color: var(--bs-dark);
      font-weight: bold;
    }
    .container {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      width: 100%;
    }
    .panels-row {
      display: flex;
      flex-direction: row;
      gap: 2rem;
      width: 100%;
    }
    .left-panel {
      flex: 0 0 400px;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .right-panel {
      flex: 1 1 auto;
      min-width: 0;
    }
    #statblock-holder {
      width: 100%;
      transition: height 0.3s cubic-bezier(0.4,0,0.2,1);
      overflow: hidden;
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
    .hp-changed,
    .damage-changed,
    .power-changed {
        color: rgb(255, 255, 122);
        animation: pop-in 0.8s ease;
        will-change: transform, opacity;
    }
  `;

    // Use Lit Task for async monster loading
    private _monsterTask = new Task(this, {
        task: async ([monsterKey], { signal }) => {

            await this.adoptSiteCss();

            const store = initializeMonsterStore();
            const monster = await store.getMonster(monsterKey);

            return monster;
        },
        args: () => [this.monsterKey]
    });

    @property({ type: String, attribute: 'monster-key' })
    monsterKey: string = '';

    private monsters = initializeMonsterStore();


    onRelatedMonsterChanged(key: string) {
        this.monsterKey = key;
    }

    async onMonsterChanged(monsterCard: MonsterCard, eventDetail?: any) {
        console.log('Monster changed:', monsterCard, eventDetail);
        if (!monsterCard) return;

        const statblockHolder = this.shadowRoot?.getElementById('statblock-holder');
        let prevHeight: string | null = null;
        if (statblockHolder) {
            // Store current height and set it as an explicit style to prevent flicker/animate
            prevHeight = `${statblockHolder.offsetHeight}px`;
            statblockHolder.style.height = prevHeight;
            statblockHolder.innerHTML = '';
        }

        // Get selected powers
        const selectedPowers = monsterCard.getSelectedPowers();

        // Highlight changed powers if present in event.detail.power
        let change: StatblockChange | null = null;
        if (eventDetail?.power && eventDetail.power.key) {
            change = {
                type: StatblockChangeType.PowerChanged,
                changedPower: eventDetail.power
            };
        }
        else if (eventDetail?.changeType === 'damage-changed') {
            change = {
                type: StatblockChangeType.DamageChanged,
                changedPower: null
            };
        }
        else if (eventDetail?.changeType === 'hp-changed') {
            change = {
                type: StatblockChangeType.HpChanged,
                changedPower: null
            };
        }

        await this.loadStatblock(monsterCard.monsterKey, selectedPowers, monsterCard.hpMultiplier, monsterCard.damageMultiplier, change);
    }

    async loadStatblock(monsterKey: string, powers: Power[], hpMultiplier: number = 1, damageMultiplier: number = 1, change: StatblockChange | null = null) {

        const request = {
            monsterKey: monsterKey,
            powers: powers,
            hpMultiplier: hpMultiplier,
            damageMultiplier: damageMultiplier,
        };

        const statblockElement = await this.monsters.getStatblock(request, change);

        const statblockHolder = this.shadowRoot?.getElementById('statblock-holder');
        if (statblockHolder && statblockElement) {
            statblockHolder.appendChild(statblockElement);

            // Animate to new height
            await new Promise(requestAnimationFrame); // Wait for DOM update

            // force the height to the current scrollHeight, triggering an animation
            const newHeight = `${statblockHolder.scrollHeight}px`;
            statblockHolder.style.height = newHeight;

            // Wait for the animation to complete and then remove the explicit height
            const onTransitionEnd = (e: TransitionEvent) => {
                if (e.propertyName === 'height') {
                    statblockHolder.style.height = '';
                    statblockHolder.removeEventListener('transitionend', onTransitionEnd);
                }
            };
            statblockHolder.addEventListener('transitionend', onTransitionEnd);
        }
    }

    async adoptSiteCss() {
        // Adopt site.css as a constructable stylesheet if supported
        const supportsAdopted = 'adoptedStyleSheets' in Document.prototype && 'replace' in CSSStyleSheet.prototype;
        if (supportsAdopted && this.shadowRoot) {
            try {
                const resp = await fetch('/css/site.css');
                const cssText = await resp.text();
                const sheet = new CSSStyleSheet();
                await sheet.replace(cssText);
                this.shadowRoot.adoptedStyleSheets = [sheet, ...this.shadowRoot.adoptedStyleSheets];
            } catch (e) {
                // fallback: do nothing, let Lit styles apply
            }
        } else if (this.shadowRoot) {
            // Fallback for browsers like Firefox: inject <style> tag
            fetch('/css/site.css').then(r => r.text()).then(cssText => {
                const style = document.createElement('style');
                style.textContent = cssText;
                this.shadowRoot?.prepend(style);
            });
        }
    }

    firstUpdated() {
        this.shadowRoot?.addEventListener('monster-changed', async (event: any) => {
            const monsterCard = event.detail.monsterCard;
            await this.onMonsterChanged(monsterCard, event.detail);
        });
    }


    render() {
        return this._monsterTask.render({
            pending: () => html`<p>Loading monster...</p>`,
            complete: (monster: Monster | null) => {
                if (!monster) {
                    return html`<p>Monster not found for key "${this.monsterKey}"</p>`;
                }

                this.updateComplete.then(() => {
                    const card = this.shadowRoot?.querySelector('monster-card') as MonsterCard | null;
                    if (!card) return;
                    this.onMonsterChanged(card, null);
                });

                return html`
                    <div class="container pamphlet-main">
                        <div class="monster-header">
                            <h2 class="monster-title">${monster?.name}</h2>
                            <div class="nav-pills">
                                ${monster.relatedMonsters.map((rel: RelatedMonster) => html`
                                    <button
                                    class="nav-pill ${rel.key === this.monsterKey ? 'active' : ''}"
                                    @click=${() => this.onRelatedMonsterChanged(rel.key)}
                                    >${rel.name || rel.key}</button>
                                `)}
                            </div>
                        </div>
                        <div class="panels-row">
                            <div class="left-panel">
                                <monster-card monster-key="${this.monsterKey}"></monster-card>
                            </div>
                            <div class="right-panel">
                                <div id="statblock-holder"></div>
                            </div>
                        </div>
                    </div>
                    `;
            },
            error: (e) => html`<p>Error loading monster: ${e}</p>`
        })
    }


}
