import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fixture, html, expect as chaiExpect } from '@open-wc/testing';
import { PowerLoadout } from '../../foe_foundry_ui/src/components/PowerLoadout.js';
import { MockPowerStore, mockPowerLoadouts } from '../mocks/mock-power-store.js';
import '../setup.js';

// Register the component
import '../../foe_foundry_ui/src/components/PowerLoadout.js';

describe('PowerLoadout Component', () => {
  let element: PowerLoadout;
  let mockPowerStore: MockPowerStore;

  beforeEach(async () => {
    mockPowerStore = new MockPowerStore();
  });

  describe('Basic Rendering', () => {
    it('should render loading state initially', async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      expect(element).to.exist;
      
      // Should show loading state initially
      const loadingText = element.shadowRoot?.textContent;
      expect(loadingText).to.include('Loading loadouts...');
    });

    it('should render loadout content after loading', async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const titleElement = element.shadowRoot?.querySelector('.power-slot-title');
      expect(titleElement).to.exist;
      expect(titleElement?.textContent?.trim()).to.include('Elemental Warrior');

      const flavorElement = element.shadowRoot?.querySelector('.power-slot-flavor');
      expect(flavorElement).to.exist;
      expect(flavorElement?.textContent?.trim()).to.include('Masters of fire and ice');
    });

    it('should show error for invalid loadout key', async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="invalid-loadout"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const errorText = element.shadowRoot?.textContent;
      expect(errorText).to.include('No loadout found for key "invalid-loadout"');
    });
  });

  describe('Power Selection', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render power button with initial power', () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button');
      expect(powerButton).to.exist;
      
      const powerName = powerButton?.textContent?.trim();
      expect(powerName).to.include('Fire Breath'); // First power in loadout-1
    });

    it('should show dropdown chevron for multi-power loadouts', () => {
      const chevron = element.shadowRoot?.querySelector('.dropdown-chevron');
      expect(chevron).to.exist;
    });

    it('should open dropdown when button is clicked', async () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      expect(powerButton).to.exist;

      powerButton.click();
      await element.updateComplete;

      const dropdown = element.shadowRoot?.querySelector('.dropdown-menu.show');
      expect(dropdown).to.exist;
    });

    it('should display all available powers in dropdown', async () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const dropdownItems = element.shadowRoot?.querySelectorAll('.dropdown-item');
      // Should have 2 powers + 1 randomize option = 3 items
      expect(dropdownItems).to.have.length(3);
    });

    it('should fire power-selected event when power is chosen', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('power-selected', eventSpy);

      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const secondPowerItem = element.shadowRoot?.querySelectorAll('.dropdown-item')[1] as HTMLElement;
      secondPowerItem.click();
      await element.updateComplete;

      expect(eventSpy).toHaveBeenCalledOnce();
      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: { 
            power: expect.objectContaining({
              key: 'test-power-2',
              name: 'Ice Shield'
            })
          }
        })
      );
    });

    it('should update selected power when new power is chosen', async () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const secondPowerItem = element.shadowRoot?.querySelectorAll('.dropdown-item')[1] as HTMLElement;
      secondPowerItem.click();
      await element.updateComplete;

      const updatedButton = element.shadowRoot?.querySelector('.power-button');
      expect(updatedButton?.textContent?.trim()).to.include('Ice Shield');
    });
  });

  describe('Locked Powers', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-2"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render single power without dropdown for locked loadouts', () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button');
      chaiExpect(powerButton).to.have.attribute('class');
      expect(powerButton?.className).to.include('single-power');

      const chevron = element.shadowRoot?.querySelector('.dropdown-chevron');
      expect(chevron).to.not.exist;
    });

    it('should not show edit icon for single power loadouts', () => {
      const editIcon = element.shadowRoot?.querySelector('.edit-icon');
      expect(editIcon).to.not.exist;
    });

    it('should not open dropdown when single power button is clicked', async () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const dropdown = element.shadowRoot?.querySelector('.dropdown-menu.show');
      expect(dropdown).to.not.exist;
    });
  });

  describe('Randomization', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should have randomize option in dropdown', async () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const randomizeItem = element.shadowRoot?.querySelector('[data-randomize="true"]');
      expect(randomizeItem).to.exist;
      expect(randomizeItem?.textContent?.trim()).to.include('Randomize');
    });

    it('should select random power when randomize is clicked', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('power-selected', eventSpy);

      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const randomizeItem = element.shadowRoot?.querySelector('[data-randomize="true"]') as HTMLElement;
      randomizeItem.click();
      await element.updateComplete;

      expect(eventSpy).toHaveBeenCalledOnce();
      const selectedPower = eventSpy.mock.calls[0][0].detail.power;
      expect(['test-power-1', 'test-power-2']).to.include(selectedPower.key);
    });

    it('should support programmatic randomization', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('power-selected', eventSpy);

      element.randomize();
      await element.updateComplete;

      expect(eventSpy).toHaveBeenCalledOnce();
    });
  });

  describe('Event Suppression', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should suppress events when configured', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('power-selected', eventSpy);

      element.suppressEvents(true);
      element.randomize();
      await element.updateComplete;

      expect(eventSpy).not.toHaveBeenCalled();
    });

    it('should resume events when suppression is disabled', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('power-selected', eventSpy);

      element.suppressEvents(true);
      element.suppressEvents(false);
      element.randomize();
      await element.updateComplete;

      expect(eventSpy).toHaveBeenCalledOnce();
    });
  });

  describe('Keyboard Navigation', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should open dropdown with Enter key', async () => {
      const powerSlotBlock = element.shadowRoot?.querySelector('.power-slot-block') as HTMLElement;
      
      const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
      powerSlotBlock.dispatchEvent(enterEvent);
      await element.updateComplete;

      const dropdown = element.shadowRoot?.querySelector('.dropdown-menu.show');
      expect(dropdown).to.exist;
    });

    it('should close dropdown with Escape key', async () => {
      // First open dropdown
      const powerSlotBlock = element.shadowRoot?.querySelector('.power-slot-block') as HTMLElement;
      const enterEvent = new KeyboardEvent('keydown', { key: 'Enter' });
      powerSlotBlock.dispatchEvent(enterEvent);
      await element.updateComplete;

      // Then close with Escape
      const escapeEvent = new KeyboardEvent('keydown', { key: 'Escape' });
      powerSlotBlock.dispatchEvent(escapeEvent);
      await element.updateComplete;

      const dropdown = element.shadowRoot?.querySelector('.dropdown-menu.show');
      expect(dropdown).to.not.exist;
    });
  });

  describe('Store Integration', () => {
    it('should use injected power store when provided', async () => {
      const getPowerLoadoutsSpy = vi.spyOn(mockPowerStore, 'getPowerLoadouts');

      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getPowerLoadoutsSpy).toHaveBeenCalledWith('test-monster');
    });

    it('should fall back to default store when not provided', async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
        ></power-loadout>
      `);

      // Should not throw error and should attempt to use default store
      await element.updateComplete;
      expect(element).to.exist;
    });
  });

  describe('Public API', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <power-loadout 
          monster-key="test-monster"
          loadout-key="loadout-1"
          .powerStore="${mockPowerStore}"
        ></power-loadout>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should expose selected power through getter', () => {
      const selectedPower = element.getSelectedPower();
      expect(selectedPower).to.exist;
      expect(selectedPower?.key).to.equal('test-power-1'); // First power is auto-selected
    });

    it('should update exposed power when selection changes', async () => {
      const powerButton = element.shadowRoot?.querySelector('.power-button') as HTMLElement;
      powerButton.click();
      await element.updateComplete;

      const secondPowerItem = element.shadowRoot?.querySelectorAll('.dropdown-item')[1] as HTMLElement;
      secondPowerItem.click();
      await element.updateComplete;

      const selectedPower = element.getSelectedPower();
      expect(selectedPower?.key).to.equal('test-power-2');
    });
  });
});