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
