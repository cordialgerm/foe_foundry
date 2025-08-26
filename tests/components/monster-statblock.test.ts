import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fixture, html } from '@open-wc/testing';
import { MonsterStatblock } from '../../docs/src/components/MonsterStatblock.js';
import { MockMonsterStore } from '../mocks/mock-monster-store.js';
import { StatblockChangeType } from '../../docs/src/data/monster.js';
import '../setup.js';

// Register the component
import '../../docs/src/components/MonsterStatblock.js';

describe('MonsterStatblock Component', () => {
  let element: MonsterStatblock;
  let mockMonsterStore: MockMonsterStore;

  beforeEach(async () => {
    mockMonsterStore = new MockMonsterStore();
  });

  describe('Basic Rendering', () => {
    it('should render loading state initially', async () => {
      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      expect(element).to.exist;
      
      // Should show loading state initially
      const loadingElement = element.shadowRoot?.querySelector('.loading');
      expect(loadingElement).to.exist;
    });

    it('should render statblock content after loading', async () => {
      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const statblockContainer = element.shadowRoot?.querySelector('#statblock-container');
      expect(statblockContainer).to.exist;
      
      // Should contain the mock statblock content
      const statblock = statblockContainer?.querySelector('.monster-statblock');
      expect(statblock).to.exist;
    });

    it('should render button panel by default', async () => {
      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const buttonPanel = element.shadowRoot?.querySelector('.statblock-button-panel');
      expect(buttonPanel).to.exist;
      
      const rerollButton = buttonPanel?.querySelector('reroll-button');
      const forgeButton = buttonPanel?.querySelector('forge-button');
      expect(rerollButton).to.exist;
      expect(forgeButton).to.exist;
    });

    it('should hide buttons when hide-buttons is set', async () => {
      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          hide-buttons
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const buttonPanel = element.shadowRoot?.querySelector('.statblock-button-panel');
      expect(buttonPanel).to.not.exist;
    });
  });

  describe('Power Integration', () => {
    it('should handle power parameters', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');

      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          powers="test-power-1,test-power-2"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getStatblockSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          monsterKey: 'test-monster',
          powers: expect.arrayContaining([
            expect.objectContaining({ key: 'test-power-1' }),
            expect.objectContaining({ key: 'test-power-2' })
          ])
        }),
        null
      );
    });

    it('should handle multiplier parameters', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');

      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          hp-multiplier="1.5"
          damage-multiplier="0.8"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getStatblockSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          monsterKey: 'test-monster',
          hpMultiplier: 1.5,
          damageMultiplier: 0.8
        }),
        null
      );
    });
  });

  describe('Random Statblock', () => {
    it('should generate random statblock when random flag is set', async () => {
      const getRandomStatblockSpy = vi.spyOn(mockMonsterStore, 'getRandomStatblock');

      element = await fixture(html`
        <monster-statblock 
          random
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getRandomStatblockSpy).toHaveBeenCalledOnce();
    });
  });

  describe('Slot Mode', () => {
    it('should render slotted content when use-slot is true', async () => {
      const slottedContent = document.createElement('div');
      slottedContent.className = 'stat-block';
      slottedContent.setAttribute('data-monster', 'slot-monster');
      slottedContent.innerHTML = '<h1>Slotted Statblock</h1>';

      element = await fixture(html`
        <monster-statblock 
          use-slot
          .monsterStore="${mockMonsterStore}"
        >${slottedContent}</monster-statblock>
      `);

      await element.updateComplete;

      const statblockContainer = element.shadowRoot?.querySelector('#statblock-container');
      expect(statblockContainer).to.exist;
      
      // Should contain slotted content
      const slot = statblockContainer?.querySelector('slot');
      expect(slot).to.exist;
    });

    it('should extract monster key from slotted content', async () => {
      const slottedContent = document.createElement('div');
      slottedContent.className = 'stat-block';
      slottedContent.setAttribute('data-monster', 'slot-monster');

      element = await fixture(html`
        <monster-statblock 
          use-slot
          .monsterStore="${mockMonsterStore}"
        >${slottedContent}</monster-statblock>
      `);

      const extractedKey = element.getSlottedMonsterKey();
      expect(extractedKey).to.equal('slot-monster');
    });
  });

  describe('Reroll Functionality', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should handle basic reroll without parameters', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');
      getStatblockSpy.mockClear(); // Clear initial call

      await element.reroll({});

      expect(getStatblockSpy).toHaveBeenCalledOnce();
    });

    it('should handle reroll with updated parameters', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');
      getStatblockSpy.mockClear();

      await element.reroll({
        monsterKey: 'new-monster',
        powers: 'new-power-1,new-power-2',
        hpMultiplier: 2.0,
        damageMultiplier: 1.5,
        changeType: StatblockChangeType.PowerChanged
      });

      expect(element.monsterKey).to.equal('new-monster');
      expect(element.powers).to.equal('new-power-1,new-power-2');
      expect(element.hpMultiplier).to.equal(2.0);
      expect(element.damageMultiplier).to.equal(1.5);
      expect(getStatblockSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          monsterKey: 'new-monster',
          hpMultiplier: 2.0,
          damageMultiplier: 1.5
        }),
        expect.objectContaining({
          type: StatblockChangeType.PowerChanged
        })
      );
    });

    it('should handle reroll with changed power tracking', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');
      getStatblockSpy.mockClear();

      const changedPower = {
        key: 'test-power-1',
        name: 'Fire Breath',
        powerCategory: 'offense',
        icon: 'fire'
      };

      await element.reroll({
        changeType: StatblockChangeType.PowerChanged,
        changedPower: changedPower
      });

      expect(getStatblockSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          type: StatblockChangeType.PowerChanged,
          changedPower: changedPower
        })
      );
    });

    it('should transition from slot mode to dynamic mode on reroll', async () => {
      const slottedContent = document.createElement('div');
      slottedContent.className = 'stat-block';
      slottedContent.setAttribute('data-monster', 'slot-monster');

      element = await fixture(html`
        <monster-statblock 
          use-slot
          .monsterStore="${mockMonsterStore}"
        >${slottedContent}</monster-statblock>
      `);

      expect(element.useSlot).to.be.true;

      await element.reroll({
        powers: 'new-power'
      });

      expect(element.useSlot).to.be.false;
      expect(element.monsterKey).to.equal('slot-monster');
    });
  });

  describe('Change Highlighting', () => {
    it('should pass change information to store for highlighting', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');

      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          change-type="hp-changed"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getStatblockSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          type: 'hp-changed'
        })
      );
    });
  });

  describe('Error Handling', () => {
    it('should show error message when statblock generation fails', async () => {
      // Make the mock store throw an error
      vi.spyOn(mockMonsterStore, 'getStatblock').mockRejectedValue(new Error('Statblock generation failed'));

      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const errorElement = element.shadowRoot?.querySelector('.error');
      expect(errorElement).to.exist;
      expect(errorElement?.textContent).to.include('Statblock generation failed');
    });

    it('should handle missing monster key gracefully', async () => {
      element = await fixture(html`
        <monster-statblock .monsterStore="${mockMonsterStore}"></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      const errorElement = element.shadowRoot?.querySelector('.error');
      expect(errorElement).to.exist;
      expect(errorElement?.textContent).to.include('No monster key provided');
    });
  });

  describe('Store Integration', () => {
    it('should use injected monster store when provided', async () => {
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');

      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(getStatblockSpy).toHaveBeenCalledOnce();
    });

    it('should fall back to default store when not provided', async () => {
      element = await fixture(html`
        <monster-statblock monster-key="test-monster"></monster-statblock>
      `);

      // Should not throw error and should attempt to use default store
      await element.updateComplete;
      expect(element).to.exist;
    });
  });

  describe('Caching', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-statblock 
          monster-key="test-monster"
          .monsterStore="${mockMonsterStore}"
        ></monster-statblock>
      `);

      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should cache statblock content after first load', async () => {
      // The first load should have cached the statblock
      expect(element['_cachedStatblock']).to.exist;
    });

    it('should show cached content while loading new statblock', async () => {
      // Ensure we have cached content first
      await element.updateComplete;
      await new Promise(resolve => setTimeout(resolve, 50));
      
      const getStatblockSpy = vi.spyOn(mockMonsterStore, 'getStatblock');
      
      // Add a delay to the mock to simulate loading
      getStatblockSpy.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve(document.createElement('div')), 100)
        )
      );

      // Start the reroll but don't await it yet
      const rerollPromise = element.reroll({ powers: 'new-power' });
      
      // Check immediately after starting the reroll for loading state
      await element.updateComplete;
      
      // Should show cached content with loading overlay
      const cachedElement = element.shadowRoot?.querySelector('.loading.cached');
      expect(cachedElement).to.exist;
      
      // Now await completion
      await rerollPromise;
    });
  });
});