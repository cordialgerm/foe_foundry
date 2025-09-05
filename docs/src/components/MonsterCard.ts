import { LitElement, html, css, PropertyValues } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { initializeMonsterStore } from '../data/api';
import { Power, PowerStore } from '../data/powers';
import { MonsterStore } from '../data/monster';
import { Task } from '@lit/task';
import './MonsterArt';
import './MonsterInfo';
import './MonsterRating';
import './PowerLoadout';
import './MonsterSimilar';
import './MonsterLore';
import './MonsterEncounters';
import type { PowerLoadout } from './PowerLoadout';
import './SvgIcon';

@customElement('monster-card')
export class MonsterCard extends LitElement {

  // Use Lit Task for async monster loading
  private _monsterTask = new Task(this, {
    task: async ([monsterKey], { signal }) => {
      const store = this.monsterStore || initializeMonsterStore();
      const monster = await store.getMonster(monsterKey);
      return { monster };
    },
    args: () => [this.monsterKey]
  });

  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  @property({ type: Object })
  monsterStore?: MonsterStore;

  @property({ type: Object })
  powerStore?: PowerStore;

  @property({ type: String }) contentTab: 'powers' | 'similar' | 'lore' | 'encounters' = 'powers';

  static styles = css`
    :host {
      display: block;
      padding: 2px;

      border: 1px solid var(--tertiary-color);
      border-radius: var(--medium-margin);
      outline: 1px solid var(--tertiary-color);
      outline-offset: -4px;

      background-color: var(--bs-dark);
      position: relative;
      contain: layout style; /* Isolate layout changes within monster card */

      --max-text-content-height: 700px; /* Default max height for content */
    }

    .monster-card {
      position: relative;
      margin: 2px;
    }

    .randomize-button {
      position: absolute;
      top: 5px;
      right: 5px;
      background: transparent;
      color: var(--bs-light);
      border: none;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
      z-index: 10;
    }

    .randomize-icon {
      width: 2rem;
      height: 2rem;
    }

    .randomize-button.rolling {
        animation: roll-dice 1.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes roll-dice {
        0% {
            transform: rotate(0deg) scale(1);
        }

        50% {
            transform: rotate(720deg) scale(1.2);
            /* 2 full spins */
        }

        70% {
            transform: rotate(720deg) scale(0.95);
            /* squish bounce */
        }

        85% {
            transform: rotate(720deg) scale(1.05) translateX(-2px);
        }

        95% {
            transform: rotate(720deg) scale(1.02) translateX(2px);
        }

        100% {
            transform: rotate(720deg) scale(1) translateX(0);
        }
    }

    /* Content tabs styling */
    .content-tabs {
      display: flex;
      border-bottom: 2px solid var(--tertiary-color);
      margin-bottom: 1rem;
      margin-top: 1rem;
    }

    .content-tab {
      flex: 1;
      padding: 0.75rem 1rem;
      border: none;
      border-bottom: 3px solid transparent;
      background: transparent;
      color: var(--primary-tertiary);
      cursor: pointer;
      font-size: 1.0rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .content-tab:hover {
      background: var(--fg-color);
      color: var(--bg-color);
    }

    .content-tab.active {
      color: var(--tertiary-color);
      border-bottom-color: var(--tertiary-color);
      font-weight: 600;
    }

    /* Tab content visibility control */
    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
    }

    /* Mobile responsiveness */
    @media (max-width: 480px) {
      .content-tab {
        padding: 0.6rem 0.5rem;
      }
    }

    .tab-content-container {
      min-height: 300px;
    }

    .powers-rating-container {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      margin-bottom: 1rem;
      padding: 0.5rem;
      border-radius: 0.25rem;
      gap: 0.5rem;
    }

    .rating-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .rating-row h4 {
      margin: 0;
      font-size: 1.1rem;
      color: var(--fg-color);
      font-weight: 600;
      min-width: 80px;
    }


  `;

  private hpRating: number = 3;
  private damageRating: number = 3;

  connectedCallback() {
    super.connectedCallback();
    this.addEventListener('rating-change', this.handleRatingChange);
    this.addEventListener('power-selected', this.handlePowerSelected);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener('rating-change', this.handleRatingChange);
    this.removeEventListener('power-selected', this.handlePowerSelected);
  }

  /**
   * Converts a rating value to a multiplier
   */
  private ratingToMultiplier(rating: number): number {
    switch (rating) {
      case 1: return 0.75;
      case 2: return 0.85;
      case 3: return 1.0;
      case 4: return 1.15;
      case 5: return 1.25;
      default: return 1.0;
    }
  }

  setContentTab(tab: 'powers' | 'lore' | 'encounters' | 'similar'): void {
    this.contentTab = tab;
    this.requestUpdate();
  }

  private handleRatingChange = (event: Event) => {
    const customEvent = event as CustomEvent;
    const { score, label } = customEvent.detail;

    // Get the original target using composedPath
    const composedPath = event.composedPath();
    const originalTarget = composedPath[0] as HTMLElement;

    if (originalTarget.id === 'hp-rating') {
      this.hpRating = score;
      const hp_multiplier = this.ratingToMultiplier(score);
      this.dispatchEvent(new CustomEvent('monster-changed', {
        detail: {
          changeType: 'hp-changed',
          hp_multiplier,
          monsterCard: this
        },
        bubbles: true,
        composed: true
      }));
    } else if (originalTarget.id === 'damage-rating') {
      this.damageRating = score;
      const damage_multiplier = this.ratingToMultiplier(score);
      this.dispatchEvent(new CustomEvent('monster-changed', {
        detail: {
          changeType: 'damage-changed',
          damage_multiplier,
          monsterCard: this
        },
        bubbles: true,
        composed: true
      }));
    }
  };

  private handlePowerSelected = (event: Event) => {
    const customEvent = event as CustomEvent;
    const { power } = customEvent.detail;
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'power-selected',
        power,
        monsterCard: this
      },
      bubbles: true,
      composed: true
    }));
  };

  private handleRandomizeAll = (event?: Event) => {
    // Animate the button
    let button: HTMLButtonElement | null = null;
    if (event && event.currentTarget instanceof HTMLButtonElement) {
      button = event.currentTarget;
    } else {
      // fallback: try to find the button in shadowRoot
      button = this.shadowRoot?.querySelector('.randomize-button') ?? null;
    }
    if (button) {
      button.classList.add('rolling');
      button.disabled = true;
      setTimeout(() => {
        button!.classList.remove('rolling');
        button!.disabled = false;
      }, 600);
    }

    // Find all power-loadout elements and call randomize on each, suppressing individual events
    const powerLoadouts = this.shadowRoot?.querySelectorAll<PowerLoadout>('power-loadout') ?? [];
    powerLoadouts.forEach(loadout => {
      loadout.suppressEvents(true);
      loadout.randomize();
      loadout.suppressEvents(false);
    });

    // Fire a single reroll event
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'reroll',
        monsterCard: this
      },
      bubbles: true,
      composed: true
    }));
  };

  public getSelectedPowers(): Array<Power> {
    const powerLoadouts = this.shadowRoot?.querySelectorAll<PowerLoadout>('power-loadout') ?? [];
    return Array.from(powerLoadouts)
      .map(loadout => loadout.getSelectedPower())
      .filter((power): power is Power => power !== undefined);
  }

  /**
   * Expose current multipliers for downstream consumers
   */
  public get hpMultiplier(): number {
    return this.ratingToMultiplier(this.hpRating);
  }

  public get damageMultiplier(): number {
    return this.ratingToMultiplier(this.damageRating);
  }

  render() {
    return this._monsterTask.render({
      pending: () => html`<p>Loading monster...</p>`,
      complete: (result) => {
        const { monster } = result;
        if (!monster) {
          return html`<p>Monster not found for key "${this.monsterKey}"</p>`;
        }
        return html`
          <div class="monster-card">
            <button
              class="randomize-button"
              @click=${(e: Event) => this.handleRandomizeAll(e)}
              title="Randomize all powers"
            >
              <svg-icon
                class="randomize-icon"
                jiggle="jiggleUntilClick"
                src="dice-twenty-faces-twenty"
              ></svg-icon>
            </button>
            <monster-info
              name="${monster.name}"
              type="${monster.creatureType}"
              tag="${monster.tagLine}"
              cr="${monster.cr}"
            ></monster-info>
            <monster-art
              monster-image="${monster.image}"
              background-image="${monster.backgroundImage}"
              background-color="rgba(255, 255, 255, 0.55)"
            ></monster-art>

            <div class="content-tabs">
              <button class="content-tab ${this.contentTab === 'powers' ? 'active' : ''}"
                      @click=${() => this.setContentTab('powers')}>
                Powers
              </button>
              <button class="content-tab ${this.contentTab === 'similar' ? 'active' : ''}"
                      @click=${() => this.setContentTab('similar')}>
                Similar
              </button>
              <button class="content-tab ${this.contentTab === 'lore' ? 'active' : ''}"
                      @click=${() => this.setContentTab('lore')}>
                Lore
              </button>
              <button class="content-tab ${this.contentTab === 'encounters' ? 'active' : ''}"
                      @click=${() => this.setContentTab('encounters')}>
                Encounters
              </button>
            </div>

            <div class="tab-content-container">
              <div class="tab-content ${this.contentTab === 'powers' ? 'active' : ''}" data-content="powers">
                <div class="powers-rating-container">
                  <div class="rating-row">
                    <h4>HP</h4>
                    <monster-rating id="hp-rating" emoji="❤️" score="3"></monster-rating>
                  </div>
                  <div class="rating-row">
                    <h4>Damage</h4>
                    <monster-rating id="damage-rating" emoji="💀" score="3"></monster-rating>
                  </div>
                </div>
                ${monster.loadouts.map(
          loadout => html`
                    <power-loadout
                      monster-key="${monster.key}"
                      loadout-key="${loadout.key}"
                      .powerStore="${this.powerStore}"
                    ></power-loadout>
                  `
        )}
              </div>

              <div class="tab-content ${this.contentTab === 'lore' ? 'active' : ''}" data-content="lore">
                <monster-lore
                  monster-key="${monster.key}"
                  font-size="0.82rem"
                  max-height="calc(80px + var(--max-text-content-height, 700px))"
                  .monsterStore="${this.monsterStore}"
                ></monster-lore>
              </div>

              <div class="tab-content ${this.contentTab === 'encounters' ? 'active' : ''}" data-content="encounters">
                <monster-encounters
                  monster-key="${monster.key}"
                  font-size="0.82rem"
                  max-height="calc(80px + var(--max-text-content-height, 700px))"
                  .monsterStore="${this.monsterStore}"
                ></monster-encounters>
              </div>

              <div class="tab-content ${this.contentTab === 'similar' ? 'active' : ''}" data-content="similar">
                <monster-similar
                  monster-key="${monster.key}"
                  font-size="0.82rem"
                  max-height="var(--max-text-content-height, 700px)"
                  .monsterStore="${this.monsterStore}"
                ></monster-similar>
              </div>
            </div>
          </div>
        `;
      },
      error: (e) => html`<p>Error loading monster: ${e}</p>`
    });
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-card': MonsterCard;
  }
}
