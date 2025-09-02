import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MockPowerStore, MockMonsterStore } from '../mocks/index.js';

describe('Data Store Integration', () => {
  describe('Power Store Integration', () => {
    let mockStore: MockPowerStore;

    beforeEach(() => {
      mockStore = new MockPowerStore();
    });

    it('should provide consistent interface as real PowerStore', async () => {
      // Test the interface matches what components expect
      const loadouts = await mockStore.getPowerLoadouts('test-monster');
      
      expect(loadouts).not.toBeNull();
      expect(Array.isArray(loadouts)).toBe(true);
      
      const loadout = loadouts![0];
      expect(loadout).toHaveProperty('key');
      expect(loadout).toHaveProperty('name');
      expect(loadout).toHaveProperty('flavorText');
      expect(loadout).toHaveProperty('powers');
      expect(loadout).toHaveProperty('selectionCount');
      expect(loadout).toHaveProperty('locked');
      expect(loadout).toHaveProperty('replaceWithSpeciesPowers');

      expect(Array.isArray(loadout.powers)).toBe(true);
      if (loadout.powers.length > 0) {
        const power = loadout.powers[0];
        expect(power).toHaveProperty('key');
        expect(power).toHaveProperty('name');
        expect(power).toHaveProperty('powerCategory');
        expect(power).toHaveProperty('icon');
      }
    });
  });

  describe('Monster Store Integration', () => {
    let mockStore: MockMonsterStore;

    beforeEach(() => {
      mockStore = new MockMonsterStore();
    });

    it('should provide consistent interface as real MonsterStore', async () => {
      // Test the interface matches what components expect
      const monster = await mockStore.getMonster('test-monster');
      
      expect(monster).not.toBeNull();
      
      // Check all required properties exist
      const requiredProps = [
        'key', 'name', 'image', 'backgroundImage', 'creatureType',
        'monsterTemplateName', 'monsterTemplate', 'monsterFamilies',
        'size', 'cr', 'tagLine', 'loadouts', 'relatedMonsters',
        'nextTemplate', 'previousTemplate', 'overviewElement', 'encounterElement'
      ];

      requiredProps.forEach(prop => {
        expect(monster).toHaveProperty(prop);
      });

      // Test array properties
      expect(Array.isArray(monster!.monsterFamilies)).toBe(true);
      expect(Array.isArray(monster!.loadouts)).toBe(true);
      expect(Array.isArray(monster!.relatedMonsters)).toBe(true);

      // Test nested object properties
      expect(monster!.nextTemplate).toHaveProperty('monsterKey');
      expect(monster!.nextTemplate).toHaveProperty('templateKey');
      expect(monster!.previousTemplate).toHaveProperty('monsterKey');
      expect(monster!.previousTemplate).toHaveProperty('templateKey');
    });

    it('should handle statblock generation consistently', async () => {
      const request = {
        monsterKey: 'test-monster',
        powers: [],
        hpMultiplier: null,
        damageMultiplier: null
      };

      const statblock = await mockStore.getStatblock(request, null);
      
      expect(statblock).toBeInstanceOf(HTMLElement);
      expect(statblock.className).toBe('monster-statblock');
      expect(statblock.innerHTML.length).toBeGreaterThan(0);
    });

    it('should handle similar monsters consistently', async () => {
      const similarGroups = await mockStore.getSimilarMonsters('test-monster');
      
      expect(Array.isArray(similarGroups)).toBe(true);
      
      if (similarGroups.length > 0) {
        const group = similarGroups[0];
        expect(group).toHaveProperty('name');
        expect(group).toHaveProperty('url');
        expect(group).toHaveProperty('monsters');
        expect(Array.isArray(group.monsters)).toBe(true);
        
        if (group.monsters.length > 0) {
          const monster = group.monsters[0];
          expect(monster).toHaveProperty('key');
          expect(monster).toHaveProperty('name');
          expect(monster).toHaveProperty('cr');
          expect(monster).toHaveProperty('template');
          expect(monster).toHaveProperty('sameTemplate');
        }
      }
    });
  });

  describe('Mock Store Usage Patterns', () => {
    it('should allow test setup and teardown', async () => {
      const mockPowerStore = new MockPowerStore();
      const mockMonsterStore = new MockMonsterStore();

      // Setup test data
      mockPowerStore.setMockData('custom-test', []);
      mockMonsterStore.setMockMonster('custom-test', {
        key: 'custom-test',
        name: 'Custom Test Monster',
        image: '/test.webp',
        backgroundImage: '/test-bg.webp',
        creatureType: 'test',
        monsterTemplateName: 'Test',
        monsterTemplate: 'test',
        monsterFamilies: ['test'],
        size: 'Medium',
        cr: 'CR 1',
        tagLine: 'Test monster',
        loadouts: [],
        relatedMonsters: [],
        nextTemplate: { monsterKey: 'next', templateKey: 'next' },
        previousTemplate: { monsterKey: 'prev', templateKey: 'prev' },
        overviewElement: null,
        encounterElement: null
      });

      // Verify setup
      expect(await mockPowerStore.getPowerLoadouts('custom-test')).toEqual([]);
      expect((await mockMonsterStore.getMonster('custom-test'))?.name).toBe('Custom Test Monster');

      // Teardown
      mockPowerStore.clearMockData();
      mockMonsterStore.clearMockData();

      // Verify teardown
      expect(await mockPowerStore.getPowerLoadouts('custom-test')).toBeNull();
      expect(await mockMonsterStore.getMonster('custom-test')).toBeNull();
    });
  });
});