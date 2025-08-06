import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { initializeMonsterStore } from '../data/api';
import { Monster } from '../data/monster';
import { Power } from '../data/powers';
import { Task } from '@lit/task';
import './MonsterArt';
import './MonsterInfo';
import './PowerLoadout';
import type { PowerLoadout } from './PowerLoadout';
import './SvgIcon';

@customElement('monster-card')
export class MonsterCard extends LitElement {

  // Use Lit Task for async monster loading
  private _monsterTask = new Task(this, {
    task: async ([monsterKey], { signal }) => {
      const store = initializeMonsterStore();
      const monster = await store.getMonster(monsterKey);
      return monster;
    },
    args: () => [this.monsterKey]
  });

  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  @property({ type: String }) contentTab: 'powers' | 'lore' | 'encounters' = 'powers';

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
      border-bottom: 2px solid var(--bs-border-color);
      margin-bottom: 1rem;
      margin-top: 1rem;
    }

    .content-tab {
      flex: 1;
      padding: 0.75rem 1rem;
      border: none;
      border-bottom: 3px solid transparent;
      background: transparent;
      color: var(--bs-secondary);
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .content-tab:hover {
      background: var(--bs-light);
      color: var(--bs-primary);
    }

    .content-tab.active {
      color: var(--bs-primary);
      border-bottom-color: var(--bs-primary);
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
        font-size: 0.8rem;
        padding: 0.6rem 0.5rem;
      }
    }
  `;

  private hpRating: number = 3;
  private damageRating: number = 3;

  connectedCallback() {
    super.connectedCallback();
    this.addEventListener('hp-changed', this.handleHpChanged);
    this.addEventListener('damage-changed', this.handleDamageChanged);
    this.addEventListener('power-selected', this.handlePowerSelected);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener('hp-changed', this.handleHpChanged);
    this.removeEventListener('damage-changed', this.handleDamageChanged);
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

  setContentTab(tab: 'powers' | 'lore' | 'encounters'): void {
    this.contentTab = tab;
    this.requestUpdate();
  }

  private handleHpChanged = (event: Event) => {
    const customEvent = event as CustomEvent;
    const newRating = customEvent.detail?.score ?? 3;
    this.hpRating = newRating;
    const hp_multiplier = this.ratingToMultiplier(newRating);
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'hp-changed',
        hp_multiplier,
        monsterCard: this
      },
      bubbles: true,
      composed: true
    }));
  };

  private handleDamageChanged = (event: Event) => {
    const customEvent = event as CustomEvent;
    const newRating = customEvent.detail?.score ?? 3;
    this.damageRating = newRating;
    const damage_multiplier = this.ratingToMultiplier(newRating);
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'damage-changed',
        damage_multiplier,
        monsterCard: this
      },
      bubbles: true,
      composed: true
    }));
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
      complete: (monster: Monster | null) => {
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
                jiggle="true"
                src="dice-twenty-faces-twenty"
              ></svg-icon>
            </button>
            <monster-info
              name="${monster.name}"
              type="${monster.creatureType}"
              tag="${monster.tagLine}"
              cr="${monster.cr}"
              hp-rating="3"
              damage-rating="3"
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
                ${monster.loadouts.map(
          loadout => html`
                    <power-loadout
                      monster-key="${monster.key}"
                      loadout-key="${loadout.key}"
                    ></power-loadout>
                  `
        )}
              </div>

              <div class="tab-content ${this.contentTab === 'lore' ? 'active' : ''}" data-content="lore">
                ${monster.overviewElement
            ? unsafeHTML(monster.overviewElement.outerHTML)
            : html`<p>No lore available for this monster.</p>`
          }
              </div>

              <div class="tab-content ${this.contentTab === 'encounters' ? 'active' : ''}" data-content="encounters">
                ${monster.encounterElement
            ? unsafeHTML(monster.encounterElement.outerHTML)
            : html`<p>No encounter information available for this monster.</p>`
          }
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
