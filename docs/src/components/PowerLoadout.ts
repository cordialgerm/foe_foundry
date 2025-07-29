import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { initializePowerStore } from '../data/api';
import { PowerLoadout as PowerLoadoutData, Power } from '../data/powers';
import { Task } from '@lit/task';
import './SvgIcon';

@customElement('power-loadout')
export class PowerLoadout extends LitElement {

  // Use Lit Task for async loadout fetching
  private _loadoutsTask = new Task(this, {
    task: async ([monsterKey], { signal }) => {
      // Simulate async fetch from store
      const store = initializePowerStore();
      const loadouts = await store.getPowerLoadouts(monsterKey);
      return loadouts || [];
    },
    args: () => [this.monsterKey]
  });

  static styles = css`
    :host {
      display: block;
    }

    .power-slot-block {
      margin-bottom: 0rem;
      padding: 0.25rem;
      background-color: var(--bs-dark);
      position: relative;
    }

    .power-slot-header {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      margin-bottom: 0.25rem;
      flex-wrap: wrap;
    }

    .power-slot-title {
      margin-bottom: 0;
      margin-top: 0;
      margin-right: 0;
      font-size: 1.1rem;
      font-weight: 500;
    }

    .power-slot-flavor {
      font-style: italic;
      font-size: 0.8rem;
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

    .power-button:hover, .dropdown-item:hover {
      background-color: var(--bs-light);
      color: var(--bs-dark);
    }

    .power-icon {
      width: 1.5rem;
      height: 1.5rem;
      flex-shrink: 0;
      fill: currentColor;
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

    .dropdown-separator {
      border-top: 1px solid var(--bs-secondary);
      margin: 0.25rem 0;
    }
  `;

  @property({ type: String, attribute: 'monster-key' })
  monsterKey = '';

  @property({ type: String, attribute: 'loadout-key' })
  loadoutKey = '';

  @state()
  private selectedPower?: Power;
  /**
   * Suppress firing events (used for reroll-all)
   */
  private _suppressEvents = false;

  public suppressEvents(s: boolean) {
    this._suppressEvents = s;
  }

  /**
   * Public getter to expose the currently selected power
   */
  public getSelectedPower(): Power | undefined {
    return this.selectedPower;
  }

  @state()
  private dropdownOpen = false;

  @state()
  private powers: Power[] = [];

  private toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  private selectPower(power: Power) {
    this.selectedPower = power;
    this.dropdownOpen = false;

    // Dispatch a custom event to notify the parent about the selected power
    // Only dispatch if not suppressed
    if (!this._suppressEvents) {
      this.dispatchEvent(new CustomEvent('power-selected', {
        detail: { power },
        bubbles: true,
        composed: true
      }));
    }
  }

  public randomize() {
    if (this.powers.length === 0) return;

    const randomIndex = Math.floor(Math.random() * this.powers.length);
    const randomPower = this.powers[randomIndex];
    // Only dispatch if not suppressed
    if (this._suppressEvents) {
      // Temporarily select without firing event
      const prev = this._suppressEvents;
      this._suppressEvents = true;
      this.selectPower(randomPower);
      this._suppressEvents = prev;
    } else {
      this.selectPower(randomPower);
    }
  }

  private handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      this.dropdownOpen = false;
    }
  }

  private renderLoadoutContent(loadout: PowerLoadoutData) {
    // Update powers state if loadout has changed
    if (loadout?.powers && this.powers !== loadout.powers) {
      this.powers = loadout.powers;
    }

    // Set initial selected power if available and none is selected
    if (this.powers?.length && !this.selectedPower) {
      this.selectedPower = this.powers[0];
    }

    const currentPower = this.selectedPower || this.powers?.[0];

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
              <svg-icon
                class="power-icon"
                src="${currentPower.icon}"
              ></svg-icon>
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
            ${this.powers?.map((power: Power) => html`
              <button
                class="dropdown-item"
                @click=${() => this.selectPower(power)}
              >
                <svg-icon
                  class="power-icon"
                  src="${power.icon}"
                ></svg-icon>
                <span>${power.name}</span>
              </button>
            `)}
            ${this.powers?.length ? html`
              <div class="dropdown-separator"></div>
              <button
                class="dropdown-item"
                @click=${() => this.randomize()}
              >
                <svg-icon
                  class="power-icon"
                  src="dice-twenty-faces-twenty"
                ></svg-icon>
                <span>Randomize</span>
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  }

  render() {
    return this._loadoutsTask.render({
      pending: () => html`<p>Loading loadouts...</p>`,
      complete: (loadouts) => {
        // Convert to mutable array for .find
        const arr = Array.isArray(loadouts) ? [...loadouts] : [];
        const loadout = arr.find(l => l.key === this.loadoutKey);
        if (!loadout) {
          return html`<p>No loadout found for key "${this.loadoutKey}"</p>`;
        }
        return this.renderLoadoutContent(loadout);
      },
      error: (e) => html`<p>Error loading loadouts: ${e}</p>`
    });
  }
}