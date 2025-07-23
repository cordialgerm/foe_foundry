import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { MockMonsterStore } from '../data/mock';
import { Power } from '../data/powers';
import './MonsterArt';
import './MonsterInfo';
import './PowerLoadout';
import './SvgIcon';

@customElement('monster-card')
export class MonsterCard extends LitElement {
  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  static styles = css`
    :host {
      display: block;
      margin: 1rem;
      padding: 1rem;
      border: 1px solid var(--bs-secondary);
      border-radius: 0.375rem;
      background-color: var(--bs-dark);
      position: relative;
    }

    .monster-card {
      position: relative;
    }

    .randomize-button {
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: transparent;
      border: 1px solid var(--bs-light);
      color: var(--bs-light);
      border-radius: 0.375rem;
      padding: 0.5rem;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
      z-index: 10;
    }

    .randomize-button:hover {
      background-color: var(--bs-light);
      color: var(--bs-dark);
    }

    .randomize-icon {
      width: 1.5rem;
      height: 1.5rem;
    }
  `;

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

  private handleHpChanged = (event: Event) => {
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'hp-changed',
        monsterCard: this
      },
      bubbles: true,
      composed: true
    }));
  };

  private handleDamageChanged = (event: Event) => {
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'damage-changed',
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

  private handleRandomizeAll = () => {
    // Find all power-loadout elements and call randomize on each
    const powerLoadouts = this.shadowRoot?.querySelectorAll('power-loadout');
    powerLoadouts?.forEach((loadout: any) => {
      if (typeof loadout.randomize === 'function') {
        loadout.randomize();
      }
    });
  };

  public getSelectedPowers(): Array<Power> {
    const powerLoadouts = this.shadowRoot?.querySelectorAll('power-loadout');
    if (!powerLoadouts) return [];
    return Array.from(powerLoadouts)
      .map((loadout: any) => (typeof loadout.getSelectedPower === 'function' ? loadout.getSelectedPower() : undefined))
      .filter(power => power !== undefined);
  }

  render() {
    const monsterStore = new MockMonsterStore();
    const monster = monsterStore.getMonster(this.monsterKey);

    if (!monster) {
      return html`<p>Monster not found for key "${this.monsterKey}"</p>`;
    }

    return html`
    <div class="monster-card">
        <button
          class="randomize-button"
          @click=${this.handleRandomizeAll}
          title="Randomize all powers"
        >
          <svg-icon
            class="randomize-icon"
            src="dice-twenty-faces-twenty"
          ></svg-icon>
        </button>

        <monster-info
          name="${monster.name}"
          type="${monster.creature_type}"
          tag="${monster.tag_line}"
          cr="${monster.cr}"
          hp-rating="3"
          damage-rating="3"
        ></monster-info>


        <monster-art
          monster-image="${monster.image}"
        background-image="${monster.backgroundImage}"
          background-color="rgba(255, 255, 255, 0.55)"
        ></monster-art>

        ${monster.loadouts.map(
      loadout => html`
            <power-loadout
              monster-key="${monster.key}"
              loadout-key="${loadout.key}"
            ></power-loadout>
          `
    )}
      </div>
    `;
  }
}
