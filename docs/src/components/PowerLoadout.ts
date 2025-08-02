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

    .power-button.single-power {
      cursor: default;
      border-color: var(--bs-secondary);
      color: var(--bs-secondary);
    }

    .power-button:hover, .dropdown-item:hover {
      background-color: var(--bs-light);
      color: var(--bs-dark);
    }

    .power-button.single-power:hover {
      background-color: transparent;
      color: var(--bs-secondary);
    }

    .power-icon {
      width: 1.5rem;
      height: 1.5rem;
      flex-shrink: 0;
      fill: currentColor;
    }

    .edit-icon {
      margin: 5px;
      width: 0.9rem;
      height: 0.9rem;
      cursor: pointer;
    }

    .dropdown-container {
      position: relative;
    }

    .dropdown-menu {
      position: absolute;
      top: 100%;
      left: 0;
      z-index: 1000;
      background-color: var(--bs-dark);
      border: 1px solid var(--bs-secondary);
      border-radius: 0.375rem;
      padding: 0.25rem 0;
      margin-top: 0.25rem;
      width: 100%;
      max-height: 300px;
      overflow-y: auto;
      box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
      display: none;
      opacity: 0;
      transform: translateY(-10px);
      transition: opacity 0.15s ease-in-out, transform 0.15s ease-in-out;
    }

    .dropdown-menu.position-up {
      top: auto;
      bottom: 100%;
      margin-top: 0;
      margin-bottom: 0.25rem;
      transform: translateY(10px);
    }

    .dropdown-menu.show {
      display: block;
      opacity: 1;
      transform: translateY(0);
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

    .dropdown-item.focused {
      background-color: var(--bs-secondary);
      color: var(--bs-light);
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

  @state()
  private focusedIndex = -1;

  @state()
  private dropdownPosition: 'down' | 'up' = 'down';

  connectedCallback() {
    super.connectedCallback();
    // Add click-outside detection for dropdown
    document.addEventListener('click', this.handleDocumentClick);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    document.removeEventListener('click', this.handleDocumentClick);
  }

  private handleDocumentClick = (event: Event) => {
    // Close dropdown if clicking outside the component
    if (!this.contains(event.target as Node)) {
      this.closeDropdown();
    }
  };

  private toggleDropdown() {
    // Don't toggle if there's only one power
    if (this.powers.length <= 1) return;

    console.log('Toggle dropdown called, current state:', this.dropdownOpen, 'powers:', this.powers.length);

    this.dropdownOpen = !this.dropdownOpen;

    console.log('New dropdown state:', this.dropdownOpen);

    if (this.dropdownOpen) {
      // Reset focus index when opening
      this.focusedIndex = -1;

      // Calculate smart positioning
      this.updatePosition();

      // Focus the dropdown container after a brief delay to allow rendering
      setTimeout(() => {
        const dropdown = this.shadowRoot?.querySelector('.dropdown-menu');
        if (dropdown) {
          (dropdown as HTMLElement).focus();
        }
      }, 50);
    }
  }

  private handleButtonClick = (event: Event) => {
    // Stop the event from bubbling up to document
    event.stopPropagation();
    this.toggleDropdown();
  };

  private updatePosition() {
    // Wait for next frame to ensure dropdown is rendered
    requestAnimationFrame(() => {
      const button = this.shadowRoot?.querySelector('.power-button') as HTMLElement;
      const dropdown = this.shadowRoot?.querySelector('.dropdown-menu') as HTMLElement;

      if (!button || !dropdown) return;

      const buttonRect = button.getBoundingClientRect();
      const dropdownHeight = dropdown.offsetHeight || 300; // Use max-height as fallback
      const viewportHeight = window.innerHeight;
      const spaceBelow = viewportHeight - buttonRect.bottom;
      const spaceAbove = buttonRect.top;

      // If there's not enough space below and more space above, position up
      if (spaceBelow < dropdownHeight && spaceAbove > dropdownHeight) {
        this.dropdownPosition = 'up';
      } else {
        this.dropdownPosition = 'down';
      }
    });
  }

  private selectPower(power: Power) {
    this.selectedPower = power;
    this.closeDropdown();

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

  private handleDropdownClick(event: Event) {
    // Prevent clicks inside dropdown from closing it
    event.stopPropagation();
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
    if (!this.dropdownOpen) {
      // If dropdown is closed, open it with Enter or Space
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        this.toggleDropdown();
      }
      return;
    }

    // Handle keyboard navigation when dropdown is open
    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        this.closeDropdown();
        break;

      case 'ArrowDown':
        event.preventDefault();
        this.navigateDown();
        break;

      case 'ArrowUp':
        event.preventDefault();
        this.navigateUp();
        break;

      case 'Enter':
      case ' ':
        event.preventDefault();
        this.selectFocusedItem();
        break;

      case 'Home':
        event.preventDefault();
        this.focusedIndex = 0;
        break;

      case 'End':
        event.preventDefault();
        this.focusedIndex = this.getTotalItems() - 1;
        break;
    }
  }

  private navigateDown() {
    const totalItems = this.getTotalItems();
    if (totalItems === 0) return;

    this.focusedIndex = this.focusedIndex < totalItems - 1 ? this.focusedIndex + 1 : 0;
  }

  private navigateUp() {
    const totalItems = this.getTotalItems();
    if (totalItems === 0) return;

    this.focusedIndex = this.focusedIndex > 0 ? this.focusedIndex - 1 : totalItems - 1;
  }

  private getTotalItems(): number {
    // Powers + randomize button (if powers exist)
    return this.powers.length + (this.powers.length > 0 ? 1 : 0);
  }

  private selectFocusedItem() {
    if (this.focusedIndex < 0) return;

    if (this.focusedIndex < this.powers.length) {
      // Select a power
      this.selectPower(this.powers[this.focusedIndex]);
    } else {
      // Select randomize (last item)
      this.randomize();
    }
  }

  private closeDropdown() {
    this.dropdownOpen = false;
    this.focusedIndex = -1;

    // Return focus to the trigger button
    setTimeout(() => {
      const button = this.shadowRoot?.querySelector('.power-button') as HTMLElement;
      button?.focus();
    }, 50);
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
    const hasSinglePower = this.powers?.length === 1;

    return html`
      <div class="power-slot-block" @keydown=${this.handleKeydown}>
        <div class="power-slot-header">
          <h4 class="power-slot-title">
            ${loadout.name}
            ${!hasSinglePower ? html`
              <svg-icon
                class="edit-icon"
                jiggle="true"
                src="pencil"
                title="Customize by choosing a power from the list below"
                aria-label="Customize by choosing a power from the list below"
                tabindex="0"
                @click=${this.handleButtonClick}
              ></svg-icon>
            ` : ''}
          </h4>
          <span class="power-slot-flavor">${loadout.flavorText}</span>
        </div>

        <div class="dropdown-container">
          <button
            class="power-button ${hasSinglePower ? 'single-power' : ''}"
            @click=${this.handleButtonClick}
            aria-expanded=${this.dropdownOpen}
            aria-haspopup="true"
          >
            ${currentPower ? html`
              <svg-icon
                class="power-icon"
                jiggle="true"
                src="${currentPower.icon}"
              ></svg-icon>
              <span>${currentPower.name}</span>
            ` : html`
              <span>No powers available</span>
            `}
            ${!hasSinglePower ? html`
              <svg class="dropdown-chevron ${this.dropdownOpen ? 'open' : ''}"
                   width="24" height="24" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 10.5L3.5 6h9L8 10.5z"/>
              </svg>
            ` : ''}
          </button>

          <div class="dropdown-menu ${this.dropdownOpen ? 'show' : ''} ${this.dropdownPosition === 'up' ? 'position-up' : ''}"
               @click=${this.handleDropdownClick}
               tabindex="-1">
            ${!hasSinglePower ? html`
              ${this.powers?.map((power: Power, index: number) => html`
                <button
                  class="dropdown-item ${this.focusedIndex === index ? 'focused' : ''}"
                  @click=${() => this.selectPower(power)}
                  @mouseenter=${() => this.focusedIndex = index}
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
                  class="dropdown-item ${this.focusedIndex === this.powers.length ? 'focused' : ''}"
                  @click=${() => this.randomize()}
                  @mouseenter=${() => this.focusedIndex = this.powers.length}
                >
                  <svg-icon
                    class="power-icon"
                    src="dice-twenty-faces-twenty"
                  ></svg-icon>
                  <span>Randomize</span>
                </button>
              ` : ''}
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

declare global {
  interface HTMLElementTagNameMap {
    'power-loadout': PowerLoadout;
  }
}