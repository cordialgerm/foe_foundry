import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fixture, html } from '@open-wc/testing';
import { MonsterBuilder } from '../../docs/src/components/MonsterBuilder.js';
import { MockMonsterStore } from '../mocks/mock-monster-store.js';
import { MockPowerStore } from '../mocks/mock-power-store.js';
import '../setup.js';

// Register the component
import '../../docs/src/components/MonsterBuilder.js';

describe('MonsterBuilder Component', () => {
  let element: MonsterBuilder;
  let mockMonsterStore: MockMonsterStore;
  let mockPowerStore: MockPowerStore;

  beforeEach(async () => {
    // Create fresh mock stores for each test
    mockMonsterStore = new MockMonsterStore();
    mockPowerStore = new MockPowerStore();
  });

  describe('Basic Rendering', () => {
    it('should render loading state initially', async () => {
      element = await fixture(html`
        <monster-builder 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      expect(element).to.exist;
      
      // Should show loading state initially
      const loadingElement = element.shadowRoot?.querySelector('.loading');
      expect(loadingElement).to.exist;
    });

    it('should render monster content after loading', async () => {
      element = await fixture(html`
        <monster-builder 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      // Wait for the task to complete
      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50)); // Allow for async operations

      // Should show monster content
      const titleElement = element.shadowRoot?.querySelector('.monster-title');
      expect(titleElement).to.exist;
      expect(titleElement?.textContent?.trim()).to.include('Test Template');
    });

    it('should show error state for invalid monster key', async () => {
      element = await fixture(html`
        <monster-builder 
          monster-key="invalid-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      // Wait for the task to complete
      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      // Should show error message
      const errorElement = element.shadowRoot?.querySelector('.error-message');
      expect(errorElement).to.exist;
      expect(errorElement?.textContent).to.include('Monster not found');
    });
  });

  describe('Navigation', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-builder 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render navigation arrows', () => {
      const navArrows = element.shadowRoot?.querySelectorAll('.nav-arrow');
      expect(navArrows).to.have.length(2); // Previous and next

      const prevArrow = element.shadowRoot?.querySelector('.nav-arrow.prev');
      const nextArrow = element.shadowRoot?.querySelector('.nav-arrow.next');
      expect(prevArrow).to.exist;
      expect(nextArrow).to.exist;
    });

    it('should render navigation pills for related monsters', () => {
      const navPills = element.shadowRoot?.querySelectorAll('.nav-pill');
      expect(navPills?.length).to.be.greaterThan(0);
    });

    it('should handle monster key changes', async () => {
      const eventSpy = vi.fn();
      element.addEventListener('monster-key-changed', eventSpy);

      element.onMonsterKeyChanged('new-monster-key');

      expect(eventSpy).toHaveBeenCalledOnce();
      expect(eventSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: { monsterKey: 'new-monster-key' }
        })
      );
    });
  });

  describe('Mobile Interface', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-builder 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      // Simulate mobile viewport
      element.isMobile = true;
      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render mobile tabs when in mobile mode', () => {
      const mobileTabs = element.shadowRoot?.querySelector('.mobile-tabs');
      expect(mobileTabs).to.exist;

      const tabs = element.shadowRoot?.querySelectorAll('.mobile-tab');
      expect(tabs).to.have.length(2); // Edit and Statblock tabs
    });

    it('should switch between mobile tabs', async () => {
      const statblockTab = element.shadowRoot?.querySelector('.mobile-tab:nth-child(2)') as HTMLElement;
      expect(statblockTab).to.exist;

      statblockTab.click();
      await element.updateComplete;

      expect(element.mobileTab).to.equal('statblock');
    });

    it('should handle statblock updates in mobile mode', async () => {
      // Set mobile mode and tab
      element.isMobile = true;
      element.mobileTab = 'edit';
      await element.updateComplete;
      
      const mockMonsterCard = {
        monsterKey: 'test-monster',
        getSelectedPowers: () => [{ key: 'test-power-1', name: 'Fire Breath' }],
        hpMultiplier: 1,
        damageMultiplier: 1
      };

      // Dispatch the monster-changed event that triggers the statblockUpdated flag
      const monsterChangedEvent = new CustomEvent('monster-changed', {
        detail: {
          monsterCard: mockMonsterCard,
          changeType: 'power-selected',
          power: { key: 'test-power-1' }
        },
        bubbles: true
      });
      
      // Dispatch from a child element to simulate the real scenario
      const monsterCard = element.shadowRoot?.querySelector('monster-card');
      if (monsterCard) {
        monsterCard.dispatchEvent(monsterChangedEvent);
      } else {
        // Fallback: dispatch directly on shadowRoot
        element.shadowRoot?.dispatchEvent(monsterChangedEvent);
      }
      
      await element.updateComplete;

      // The statblockUpdated flag should be set when in mobile mode and not viewing statblock
      expect(element.statblockUpdated).to.be.true;
    });
  });

  describe('Panels Layout', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-builder 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render both card and statblock panels', () => {
      const cardPanel = element.shadowRoot?.querySelector('.card-panel');
      const statblockPanel = element.shadowRoot?.querySelector('.statblock-panel');

      expect(cardPanel).to.exist;
      expect(statblockPanel).to.exist;
    });

    it('should contain monster-card and monster-statblock components', () => {
      const monsterCard = element.shadowRoot?.querySelector('monster-card');
      const monsterStatblock = element.shadowRoot?.querySelector('monster-statblock');

      expect(monsterCard).to.exist;
      expect(monsterStatblock).to.exist;
    });

    it('should pass stores to child components', () => {
      const monsterCard = element.shadowRoot?.querySelector('monster-card') as any;
      const monsterStatblock = element.shadowRoot?.querySelector('monster-statblock') as any;

      // Check that stores are passed through
      expect(monsterCard.monsterStore).to.equal(mockMonsterStore);
      expect(monsterCard.powerStore).to.equal(mockPowerStore);
      expect(monsterStatblock.monsterStore).to.equal(mockMonsterStore);
    });
  });

  describe('Store Integration', () => {
    it('should use injected stores when provided', async () => {
      const getMonsterSpy = vi.spyOn(mockMonsterStore, 'getMonster');

      element = await fixture(html`
        <monster-builder 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
          .powerStore="${mockPowerStore}"
        ></monster-builder>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getMonsterSpy).toHaveBeenCalledWith('test-monster');
    });

    it('should fall back to default stores when not provided', async () => {
      element = await fixture(html`
        <monster-builder monster-key="test-monster"></monster-builder>
      `);

      // Should not throw error and should attempt to use default stores
      await element.updateComplete;
      expect(element).to.exist;
    });
  });
});