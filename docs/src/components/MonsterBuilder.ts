
import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import '../components/MonsterCard';
import { initializeMonsterStore } from '../data/api';
import { StatblockChange, StatblockChangeType } from '../data/monster';

@customElement('monster-builder')
export class MonsterBuilder extends LitElement {
    static styles = css`
    .container {
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


    @property({ type: String, attribute: 'monster-key' })
    monsterKey: string = '';

    private monsters = initializeMonsterStore();

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


    private async handleMonsterChanged(monsterCard: any, eventDetail?: any) {
        if (!monsterCard) return;

        const statblockHolder = this.shadowRoot?.getElementById('statblock-holder');
        if (statblockHolder) statblockHolder.innerHTML = '';

        // Get selected powers
        const selectedPowers = monsterCard.getSelectedPowers();

        const request = {
            monsterKey: monsterCard.monsterKey,
            powers: selectedPowers,
            hpMultiplier: monsterCard.hpMultiplier,
            damageMultiplier: monsterCard.damageMultiplier,
        };

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

        const statblockElement = await this.monsters.getStatblock(request, change);
        if (statblockHolder && statblockElement) {
            statblockHolder.appendChild(statblockElement);
        }
    }

    setupMonsterChanged() {
        const card = this.shadowRoot?.querySelector('monster-card');
        if (card) {
            card.addEventListener('monster-changed', async (event: any) => {
                const monsterCard = event.detail.monsterCard;
                await this.handleMonsterChanged(monsterCard, event.detail);
            });
        }
    }

    async firstUpdated() {
        this.setupMonsterChanged();
        await this.adoptSiteCss();
        // Show statblock on initial setup
        const card = this.shadowRoot?.querySelector('monster-card');
        if (card) {
            await this.handleMonsterChanged(card);
        }
    }

    render() {
        return html`
      <div class="container pamphlet-main">
        <div class="left-panel">
          <monster-card .monsterKey=${this.monsterKey}></monster-card>
        </div>
        <div class="right-panel">
          <div id="statblock-holder"></div>
        </div>
      </div>
    `;
    }
}
