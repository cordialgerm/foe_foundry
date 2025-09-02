import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { MockPowerStore, MockMonsterStore, mockPowers, mockPowerLoadouts, mockMonster } from '../mocks/index.js';
import { StatblockChangeType } from '../../docs/src/data/monster.js';

describe('Mock Data Stores', () => {
  describe('MockPowerStore', () => {
    let store: MockPowerStore;

    beforeEach(() => {
      store = new MockPowerStore();
    });

    it('should return power loadouts for valid monster key', async () => {
      const loadouts = await store.getPowerLoadouts('test-monster');
      
      expect(loadouts).not.toBeNull();
      expect(loadouts).toBeInstanceOf(Array);
      expect(loadouts!.length).toBeGreaterThan(0);
      expect(loadouts![0]).toHaveProperty('key');
      expect(loadouts![0]).toHaveProperty('name');
      expect(loadouts![0]).toHaveProperty('powers');
    });

    it('should return null for invalid monster key', async () => {
      const loadouts = await store.getPowerLoadouts('invalid-monster');
      expect(loadouts).toBeNull();
    });

    it('should allow setting custom mock data', async () => {
      const customLoadouts = [mockPowerLoadouts[0]];
      store.setMockData('custom-monster', customLoadouts);
      
      const result = await store.getPowerLoadouts('custom-monster');
      expect(result).toEqual(customLoadouts);
    });

    it('should clear mock data correctly', async () => {
      store.clearMockData();
      
      const result = await store.getPowerLoadouts('test-monster');
      expect(result).toBeNull();
    });
  });

  describe('MockMonsterStore', () => {
    let store: MockMonsterStore;

    beforeEach(() => {
      store = new MockMonsterStore();
    });

    it('should return monster for valid key', async () => {
      const monster = await store.getMonster('test-monster');
      
      expect(monster).not.toBeNull();
      expect(monster!.key).toBe('test-monster');
      expect(monster!.name).toBe('Test Monster');
      expect(monster!.loadouts).toBeInstanceOf(Array);
      expect(monster!.overviewElement).toBeTruthy();
      expect(monster!.encounterElement).toBeTruthy();
    });

    it('should return null for invalid monster key', async () => {
      const monster = await store.getMonster('invalid-monster');
      expect(monster).toBeNull();
    });

    it('should return similar monsters', async () => {
      const similarGroups = await store.getSimilarMonsters('test-monster');
      
      expect(similarGroups).toBeInstanceOf(Array);
      expect(similarGroups.length).toBeGreaterThan(0);
      expect(similarGroups[0]).toHaveProperty('name');
      expect(similarGroups[0]).toHaveProperty('monsters');
    });

    it('should return empty array for monsters with no similar groups', async () => {
      const similarGroups = await store.getSimilarMonsters('invalid-monster');
      expect(similarGroups).toBeInstanceOf(Array);
      expect(similarGroups.length).toBe(0);
    });

    it('should generate random statblock', async () => {
      const statblock = await store.getRandomStatblock();
      
      expect(statblock).toBeInstanceOf(HTMLElement);
      expect(statblock.className).toBe('monster-statblock');
      expect(statblock.innerHTML).toContain('Random Monster');
    });

    it('should generate statblock from request', async () => {
      const request = {
        monsterKey: 'test-monster',
        powers: [mockPowers[0]],
        hpMultiplier: 1.5,
        damageMultiplier: null
      };

      const statblock = await store.getStatblock(request, null);
      
      expect(statblock).toBeInstanceOf(HTMLElement);
      expect(statblock.innerHTML).toContain('test-monster');
      expect(statblock.innerHTML).toContain('Fire Breath');
      expect(statblock.innerHTML).toContain('45'); // 30 * 1.5
    });

    it('should include change information in statblock', async () => {
      const request = {
        monsterKey: 'test-monster',
        powers: [mockPowers[0]],
        hpMultiplier: null,
        damageMultiplier: null
      };

      const change = {
        type: StatblockChangeType.PowerChanged,
        changedPower: mockPowers[0]
      };

      const statblock = await store.getStatblock(request, change);
      
      expect(statblock.innerHTML).toContain('Changed: power-changed');
    });

    it('should allow setting custom mock monster', async () => {
      const customMonster = {
        ...mockMonster,
        key: 'custom-monster',
        name: 'Custom Monster'
      };

      store.setMockMonster('custom-monster', customMonster);
      
      const result = await store.getMonster('custom-monster');
      expect(result!.name).toBe('Custom Monster');
    });

    it('should clear mock data correctly', async () => {
      store.clearMockData();
      
      const monster = await store.getMonster('test-monster');
      expect(monster).toBeNull();
    });
  });
});