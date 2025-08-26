import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MockPowerStore, MockMonsterStore } from '../mocks/index.js';
import { StatblockChangeType } from '../../docs/src/data/monster.js';

// Example of how to test component interactions with data stores
describe('Component Data Integration Examples', () => {
  let mockPowerStore: MockPowerStore;
  let mockMonsterStore: MockMonsterStore;

  beforeEach(() => {
    mockPowerStore = new MockPowerStore();
    mockMonsterStore = new MockMonsterStore();
  });

  describe('PowerLoadout Component Integration', () => {
    it('should load and display power loadouts', async () => {
      // Simulate what the PowerLoadout component does
      const monsterKey = 'test-monster';
      
      // This is what the component's Lit Task would do
      const loadouts = await mockPowerStore.getPowerLoadouts(monsterKey);
      
      expect(loadouts).not.toBeNull();
      expect(loadouts!.length).toBeGreaterThan(0);
      
      // Verify the structure matches what the component expects
      const loadout = loadouts![0];
      expect(loadout.key).toBeDefined();
      expect(loadout.name).toBeDefined();
      expect(loadout.powers).toBeInstanceOf(Array);
      
      // Test power selection (what happens when user clicks a power)
      if (loadout.powers.length > 0) {
        const selectedPower = loadout.powers[0];
        expect(selectedPower.key).toBeDefined();
        expect(selectedPower.name).toBeDefined();
        expect(selectedPower.powerCategory).toBeDefined();
      }
    });

    it('should handle empty loadouts gracefully', async () => {
      // Test error case
      const loadouts = await mockPowerStore.getPowerLoadouts('nonexistent-monster');
      expect(loadouts).toBeNull();
      
      // Component should handle this case without crashing
      const displayLoadouts = loadouts || [];
      expect(displayLoadouts).toEqual([]);
    });
  });

  describe('MonsterBuilder Component Integration', () => {
    it('should load monster data and display correctly', async () => {
      // Simulate what the MonsterBuilder component does
      const monsterKey = 'test-monster';
      
      // This is what the component's Lit Task would do
      const monster = await mockMonsterStore.getMonster(monsterKey);
      
      expect(monster).not.toBeNull();
      expect(monster!.key).toBe(monsterKey);
      expect(monster!.name).toBeDefined();
      expect(monster!.loadouts).toBeInstanceOf(Array);
      
      // Test that overview and encounter elements are provided
      expect(monster!.overviewElement).toBeInstanceOf(HTMLElement);
      expect(monster!.encounterElement).toBeInstanceOf(HTMLElement);
    });

    it('should handle statblock generation for different configurations', async () => {
      // Simulate creating a statblock with different power configurations
      const monster = await mockMonsterStore.getMonster('test-monster');
      expect(monster).not.toBeNull();
      
      const loadouts = await mockPowerStore.getPowerLoadouts('test-monster');
      expect(loadouts).not.toBeNull();
      
      if (loadouts!.length > 0 && loadouts![0].powers.length > 0) {
        const selectedPowers = [loadouts![0].powers[0]];
        
        const statblockRequest = {
          monsterKey: 'test-monster',
          powers: selectedPowers,
          hpMultiplier: 1.2,
          damageMultiplier: null
        };
        
        const statblock = await mockMonsterStore.getStatblock(statblockRequest, null);
        
        expect(statblock).toBeInstanceOf(HTMLElement);
        expect(statblock.innerHTML).toContain('test-monster');
        expect(statblock.innerHTML).toContain(selectedPowers[0].name);
        expect(statblock.innerHTML).toContain('36'); // 30 * 1.2
      }
    });
  });

  describe('Full Workflow Integration', () => {
    it('should simulate complete user workflow', async () => {
      // 1. User navigates to monster page
      const monsterKey = 'test-monster';
      
      // 2. Component loads monster data
      const monster = await mockMonsterStore.getMonster(monsterKey);
      expect(monster).not.toBeNull();
      
      // 3. Component loads power loadouts
      const loadouts = await mockPowerStore.getPowerLoadouts(monsterKey);
      expect(loadouts).not.toBeNull();
      
      // 4. User selects powers from first loadout
      const selectedLoadout = loadouts![0];
      const selectedPowers = selectedLoadout.powers.slice(0, selectedLoadout.selectionCount);
      
      // 5. Component generates statblock
      const statblockRequest = {
        monsterKey,
        powers: selectedPowers,
        hpMultiplier: null,
        damageMultiplier: null
      };
      
      const statblock = await mockMonsterStore.getStatblock(statblockRequest, null);
      
      // 6. Verify final result
      expect(statblock).toBeInstanceOf(HTMLElement);
      expect(statblock.innerHTML).toContain(monster!.key);
      selectedPowers.forEach(power => {
        expect(statblock.innerHTML).toContain(power.name);
      });
    });

    it('should handle power changes and regeneration', async () => {
      // Initial setup
      const monsterKey = 'test-monster';
      const loadouts = await mockPowerStore.getPowerLoadouts(monsterKey);
      expect(loadouts).not.toBeNull();
      
      const initialPowers = loadouts![0].powers.slice(0, 1);
      
      // Generate initial statblock
      let statblockRequest = {
        monsterKey,
        powers: initialPowers,
        hpMultiplier: null,
        damageMultiplier: null
      };
      
      let statblock = await mockMonsterStore.getStatblock(statblockRequest, null);
      expect(statblock.innerHTML).toContain(initialPowers[0].name);
      
      // Change power selection
      const newPowers = loadouts![0].powers.slice(1, 2);
      if (newPowers.length > 0) {
        statblockRequest = {
          ...statblockRequest,
          powers: newPowers
        };
        
        const change = {
          type: StatblockChangeType.PowerChanged,
          changedPower: newPowers[0]
        };
        
        statblock = await mockMonsterStore.getStatblock(statblockRequest, change);
        
        // Verify the change was tracked
        expect(statblock.innerHTML).toContain('Changed: power-changed');
        expect(statblock.innerHTML).toContain(newPowers[0].name);
      }
    });
  });
});