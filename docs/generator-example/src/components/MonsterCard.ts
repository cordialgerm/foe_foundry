import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { MockMonsterStore } from '../data/mock';
import './MonsterArt';
import './MonsterInfo';
import './PowerLoadout';

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
        changeType: 'hp-changed'
      },
      bubbles: true,
      composed: true
    }));
  };

  private handleDamageChanged = (event: Event) => {
    this.dispatchEvent(new CustomEvent('monster-changed', {
      detail: {
        changeType: 'damage-changed',
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
        power
      },
      bubbles: true,
      composed: true
    }));
  };

  render() {
    const monsterStore = new MockMonsterStore();
    const monster = monsterStore.getMonster(this.monsterKey);

    if (!monster) {
      return html`<p>Monster not found for key "${this.monsterKey}"</p>`;
    }

    return html`
    <div class="monster-card">

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
