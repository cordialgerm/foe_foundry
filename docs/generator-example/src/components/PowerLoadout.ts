import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { consume } from '@lit/context';
import { Task } from '@lit/task';
import { initializeMockPowerStore } from './mock';
import { PowerStore, PowerLoadout as PowerLoadoutData, Power } from './powers';
import './SvgIcon';

@customElement('power-loadout')
export class PowerLoadout extends LitElement {
  static styles = css`
    :host {
      display: block;
    }

    .power-slot-block {
      margin-bottom: 1rem;
      padding: 1rem;
      border: 1px solid var(--bs-secondary);
      border-radius: 0.375rem;
      background-color: var(--bs-dark);
      position: relative;
    }

    .power-slot-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 0.5rem;
      flex-wrap: wrap;
    }

    .power-slot-title {
      margin-bottom: 0;
      margin-right: 0.5rem;
      font-size: 1.25rem;
      font-weight: 500;
    }

    .power-slot-flavor {
      font-style: italic;
      font-size: 0.875rem;
    }

    .power-button {
      border: 1px solid var(--bs-light);
      background: transparent;
      color: var(--bs-light);
      width: 100%;
      text-align: start;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
    }

    .power-button:hover {
      background-color: var(--bs-light);
      color: var(--bs-dark);
    }

    .power-icon {
      width: 1.25rem;
      height: 1.25rem;
      flex-shrink: 0;
    }

    .dropdown-menu {
      background-color: var(--bs-dark);
      border: 1px solid var(--bs-secondary);
      border-radius: 0.375rem;
      padding: 0.25rem 0;
      margin-top: 0.25rem;
      width: 100%;
      max-height: 300px;
      overflow-y: auto;
    }

    .dropdown-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 1rem;
      color: var(--bs-light);
      text-decoration: none;
      cursor: pointer;
      border: none;
      background: none;
      width: 100%;
      text-align: start;
      transition: background-color 0.15s ease-in-out;
    }

    .dropdown-item:hover {
      background-color: var(--bs-secondary);
      color: var(--bs-light);
    }

    .dropdown-item:focus {
      background-color: var(--bs-secondary);
      color: var(--bs-light);
      outline: none;
    }

    .dropdown-chevron {
      margin-left: auto;
      transition: transform 0.15s ease-in-out;
    }

    .dropdown-chevron.open {
      transform: rotate(180deg);
    }

    .show {
      display: block !important;
    }

    .d-none {
      display: none !important;
    }
  `;

  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  @property({ type: String, attribute: 'loadout-key' })
  loadoutKey = '';

  @state()
  private selectedPower?: Power;

  @state()
  private dropdownOpen = false;

  private toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  private selectPower(power: Power) {
    this.selectedPower = power;
    this.dropdownOpen = false;

    // Dispatch a custom event to notify the parent about the selected power
    this.dispatchEvent(new CustomEvent('power-selected', {
      detail: { power },
      bubbles: true,
      composed: true
    }));
  }

  private handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      this.dropdownOpen = false;
    }
  }

  private renderLoadoutContent(loadout: PowerLoadoutData) {
    // Set initial selected power if available and none is selected
    if (loadout?.powers?.length && !this.selectedPower) {
      this.selectedPower = loadout.powers[0];
    }

    const currentPower = this.selectedPower || loadout.powers?.[0];

    return html`
      <div class="power-slot-block" @keydown=${this.handleKeydown}>
        <div class="power-slot-header">
          <h4 class="power-slot-title">${loadout.name}</h4>
          <span class="power-slot-flavor">${loadout.flavorText}</span>
        </div>

        <div class="position-relative">
          <button
            class="power-button"
            @click=${this.toggleDropdown}
            aria-expanded=${this.dropdownOpen}
            aria-haspopup="true"
          >
            ${currentPower ? html`
              <power-icon
                class="power-icon"
                src="${currentPower.icon}"
              ></power-icon>
              <span>${currentPower.name}</span>
            ` : html`
              <span>No powers available</span>
            `}
            <svg class="dropdown-chevron ${this.dropdownOpen ? 'open' : ''}"
                 width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 10.5L3.5 6h9L8 10.5z"/>
            </svg>
          </button>

          <div class="dropdown-menu ${this.dropdownOpen ? 'show' : 'd-none'}">
            ${loadout.powers?.map((power: Power) => html`
              <button
                class="dropdown-item"
                @click=${() => this.selectPower(power)}
              >
                <power-icon
                  class="power-icon"
                  src="${power.icon}"
                ></power-icon>
                <span>${power.name}</span>
              </button>
            `)}
          </div>
        </div>
      </div>
    `;
  }

  render() {
    const powerStore = initializeMockPowerStore();
    const loadouts = powerStore.getPowerLoadouts(this.monsterKey) || [];
    const loadout = loadouts.find(l => l.key === this.loadoutKey);
    if (!loadout) {
      return html`<p>No loadout found for key "${this.loadoutKey}"</p>`;
    }
    return this.renderLoadoutContent(loadout);
  }
}