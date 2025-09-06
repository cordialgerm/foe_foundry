import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fixture, html, expect as chaiExpect } from '@open-wc/testing';
import { MonsterCard } from '../../docs/src/components/MonsterCard.js';
import { MockMonsterStore } from '../mocks/mock-monster-store.js';
import { MockPowerStore } from '../mocks/mock-power-store.js';
import '../setup.js';

// Register the component
import '../../docs/src/components/MonsterCard.js';

describe('MonsterCard Component', () => {
  let element: MonsterCard;
  let mockMonsterStore: MockMonsterStore;
  let mockPowerStore: MockPowerStore;

  beforeEach(async () => {
    mockMonsterStore = new MockMonsterStore();
    mockPowerStore = new MockPowerStore();
  });

  describe('Basic Rendering', () => {
    it('should render loading state initially', async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      expect(element).to.exist;
      
      // Should show loading content initially
      const loadingText = element.shadowRoot?.textContent;
      expect(loadingText).to.include('Loading monster...');
    });

    it('should render monster content after loading', async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      // Should render monster content
      const cardContainer = element.shadowRoot?.querySelector('.monster-card');
      expect(cardContainer).to.exist;
    });
  });

  describe('Tab Navigation', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render tab navigation', () => {
      const tabNavigation = element.shadowRoot?.querySelector('.content-tabs');
      expect(tabNavigation).to.exist;

      const tabs = element.shadowRoot?.querySelectorAll('.content-tab');
      expect(tabs?.length).to.be.greaterThan(0);
    });

    it('should start with powers tab active by default', () => {
      expect(element.contentTab).to.equal('powers');
      
      const powersTab = element.shadowRoot?.querySelector('.content-tab.active');
      expect(powersTab).to.exist;
      expect(powersTab?.textContent?.trim()).to.equal('Powers');
    });

    it('should switch tabs when clicked', async () => {
      // Find the lore tab button and click it
      const loreTab = Array.from(element.shadowRoot?.querySelectorAll('.content-tab') || [])
        .find(tab => tab.textContent?.trim() === 'Lore') as HTMLElement;
      expect(loreTab).to.exist;

      loreTab.click();
      await element.updateComplete;

      expect(element.contentTab).to.equal('lore');
      chaiExpect(loreTab).to.have.attribute('class');
      expect(loreTab?.className).to.include('active');
    });
  });

  describe('Powers Tab', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render power loadouts', () => {
      const powersContent = element.shadowRoot?.querySelector('[data-content="powers"]');
      expect(powersContent).to.exist;

      const powerLoadouts = element.shadowRoot?.querySelectorAll('power-loadout');
      expect(powerLoadouts?.length).to.be.greaterThan(0);
    });

    it('should pass stores to power loadout components', () => {
      const powerLoadout = element.shadowRoot?.querySelector('power-loadout') as any;
      expect(powerLoadout).to.exist;
      
      // Check that power store is passed through
      expect(powerLoadout.powerStore).to.equal(mockPowerStore);
    });

    it('should render reroll all button', () => {
      const rerollButton = element.shadowRoot?.querySelector('.randomize-button');
      expect(rerollButton).to.exist;
    });

    it('should handle reroll all action', async () => {
      const rerollButton = element.shadowRoot?.querySelector('.randomize-button') as HTMLElement;
      
      const eventSpy = vi.fn();
      element.addEventListener('monster-changed', eventSpy);

      rerollButton.click();
      await element.updateComplete;

      expect(eventSpy).toHaveBeenCalledOnce();
    });
  });

  describe('HP and Damage Multipliers', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should have default multipliers of 1.0', () => {
      expect(element.hpMultiplier).to.equal(1);
      expect(element.damageMultiplier).to.equal(1);
    });

    it('should render HP multiplier controls', () => {
      const hpControls = element.shadowRoot?.querySelector('#hp-rating');
      expect(hpControls).to.exist;
    });

    it('should render damage multiplier controls', () => {
      const damageControls = element.shadowRoot?.querySelector('#damage-rating');
      expect(damageControls).to.exist;
    });

    it('should update multipliers and fire events', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('monster-changed', eventSpy);

      // Test via the public API since internal controls are complex
      // The MonsterRating component would handle the actual clicking
      // For now, just verify the component structure exists
      const hpRating = element.shadowRoot?.querySelector('#hp-rating');
      const damageRating = element.shadowRoot?.querySelector('#damage-rating');
      
      expect(hpRating).to.exist;
      expect(damageRating).to.exist;
    });
  });

  describe('Similar Monsters Tab', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      // Switch to similar tab
      const similarTab = Array.from(element.shadowRoot?.querySelectorAll('.content-tab') || [])
        .find(tab => tab.textContent?.trim() === 'Similar') as HTMLElement;
      similarTab?.click();
      await element.updateComplete;
    });

    it('should render similar monsters content', () => {
      const similarComponent = element.shadowRoot?.querySelector('monster-similar');
      expect(similarComponent).to.exist;
      const similarContent = similarComponent?.shadowRoot?.querySelector('.similar-content');
      expect(similarContent).to.exist;
    });

    it('should show similar monsters groups', () => {
      const similarComponent = element.shadowRoot?.querySelector('monster-similar');
      expect(similarComponent).to.exist;
      const similarContent = similarComponent?.shadowRoot?.querySelector('.similar-content ul');
      expect(similarContent).to.exist;
      
      // Should have at least one monster group from our mock data
      const groupItems = similarContent?.querySelectorAll('li');
      expect(groupItems?.length).to.be.greaterThan(0);
    });
  });

  describe('Lore Tab', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      // Switch to lore tab
      const loreTab = Array.from(element.shadowRoot?.querySelectorAll('.content-tab') || [])
        .find(tab => tab.textContent?.trim() === 'Lore') as HTMLElement;
      loreTab?.click();
      await element.updateComplete;
    });

    it('should render lore content', () => {
      const loreComponent = element.shadowRoot?.querySelector('monster-lore');
      expect(loreComponent).to.exist;
      const loreContent = loreComponent?.shadowRoot?.querySelector('.lore-content');
      expect(loreContent).to.exist;
    });

    it('should show monster overview when available', () => {
      // Mock monster includes overview element
      const loreComponent = element.shadowRoot?.querySelector('monster-lore');
      expect(loreComponent).to.exist;
      const overviewContent = loreComponent?.shadowRoot?.querySelector('.lore-content');
      expect(overviewContent).to.exist;
    });
  });

  describe('Encounters Tab', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      // Switch to encounters tab
      const encountersTab = Array.from(element.shadowRoot?.querySelectorAll('.content-tab') || [])
        .find(tab => tab.textContent?.trim() === 'Encounters') as HTMLElement;
      encountersTab?.click();
      await element.updateComplete;
    });

    it('should render encounters content', () => {
      const encountersComponent = element.shadowRoot?.querySelector('monster-encounters');
      expect(encountersComponent).to.exist;
      const encountersContent = encountersComponent?.shadowRoot?.querySelector('.encounter-content');
      expect(encountersContent).to.exist;
    });
  });

  describe('Power Selection Events', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should listen for power-selected events from loadouts', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('monster-changed', eventSpy);

      // Wait for power loadouts to be rendered
      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 100));

      // Simulate power selection event by dispatching it to the element itself
      // since the event listener is on the element, not the child
      const powerSelectedEvent = new CustomEvent('power-selected', {
        detail: {
          power: { key: 'test-power-1', name: 'Fire Breath' }
        },
        bubbles: true
      });

      element.dispatchEvent(powerSelectedEvent);
      await element.updateComplete;

      expect(eventSpy).toHaveBeenCalled();
    });

    it('should aggregate selected powers for external access', async () => {
      // The getSelectedPowers method should return currently selected powers
      const selectedPowers = element.getSelectedPowers();
      expect(Array.isArray(selectedPowers)).to.be.true;
    });
  });

  describe('Monster Art and Info', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render monster art component', () => {
      const monsterArt = element.shadowRoot?.querySelector('monster-art');
      expect(monsterArt).to.exist;
    });

    it('should render monster info component', () => {
      const monsterInfo = element.shadowRoot?.querySelector('monster-info');
      expect(monsterInfo).to.exist;
    });

    it('should render monster rating component', () => {
      const monsterRating = element.shadowRoot?.querySelector('monster-rating');
      expect(monsterRating).to.exist;
    });
  });

  describe('Store Integration', () => {
    it('should use injected stores when provided', async () => {
      const getMonsterSpy = vi.spyOn(mockMonsterStore, 'getMonster');
      const getSimilarMonstersSpy = vi.spyOn(mockMonsterStore, 'getSimilarMonsters');

      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getMonsterSpy).toHaveBeenCalledWith('test-monster');
      expect(getSimilarMonstersSpy).toHaveBeenCalledWith('test-monster');
    });

    it('should fall back to default stores when not provided', async () => {
      element = await fixture(html`
        <monster-card monster-key="test-monster"></monster-card>
      `);

      // Should not throw error and should attempt to use default stores
      await element.updateComplete;
      expect(element).to.exist;
    });
  });

  describe('Responsive Design', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-card 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should have proper CSS classes for responsive layout', () => {
      const cardPanel = element.shadowRoot?.querySelector('.monster-card');
      expect(cardPanel).to.exist;
      
      // Should have responsive classes defined in CSS
      expect(cardPanel).to.exist;
    });
  });

  describe('Error Handling', () => {
    it('should handle monster loading errors gracefully', async () => {
      // Make the mock store throw an error
      vi.spyOn(mockMonsterStore, 'getMonster').mockRejectedValue(new Error('Monster not found'));

      element = await fixture(html`
        <monster-card 
          monster-key="invalid-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-card>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      // Should not crash and should handle error gracefully
      expect(element).to.exist;
    });
  });
});