import { 
  MonsterStore, 
  Monster, 
  SimilarMonsterGroup, 
  StatblockRequest, 
  StatblockChange, 
  RelatedMonster, 
  RelatedMonsterTemplate 
} from '../../foe_foundry_ui/src/data/monster.js';
import { mockPowerLoadouts } from './mock-power-store.js';

// Test data fixtures
export const mockRelatedMonsters: RelatedMonster[] = [
  {
    key: 'skeleton',
    name: 'Skeleton',
    cr: 'CR ¼',
    template: 'skeleton',
    sameTemplate: true,
    family: 'undead'
  },
  {
    key: 'zombie',
    name: 'Zombie', 
    cr: 'CR ½',
    template: 'zombie',
    sameTemplate: false,
    family: 'undead'
  }
];

export const mockMonster: Monster = {
  key: 'test-monster',
  name: 'Test Monster',
  image: '/images/test-monster.webp',
  backgroundImage: '/images/test-bg.webp',
  creatureType: 'humanoid',
  monsterTemplateName: 'Test Template',
  monsterTemplate: 'test-template',
  monsterFamilies: ['test-family'],
  size: 'Medium',
  cr: 'CR 1',
  tagLine: 'A creature made for testing',
  loadouts: mockPowerLoadouts,
  relatedMonsters: mockRelatedMonsters,
  nextTemplate: {
    monsterKey: 'next-monster',
    templateKey: 'next-template'
  },
  previousTemplate: {
    monsterKey: 'prev-monster', 
    templateKey: 'prev-template'
  },
  overviewElement: null,
  encounterElement: null
};

export const mockSimilarMonsterGroups: SimilarMonsterGroup[] = [
  {
    name: 'Undead',
    url: '/monsters/undead',
    monsters: mockRelatedMonsters
  }
];

export class MockMonsterStore implements MonsterStore {
  private monsters: Map<string, Monster> = new Map();
  private similarGroups: Map<string, SimilarMonsterGroup[]> = new Map();

  constructor() {
    // Set up test data
    this.monsters.set('test-monster', mockMonster);
    this.monsters.set('ogre', {
      ...mockMonster,
      key: 'ogre',
      name: 'Ogre',
      cr: 'CR 2'
    });
    
    this.similarGroups.set('test-monster', mockSimilarMonsterGroups);
  }

  async getMonster(key: string): Promise<Monster | null> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    const monster = this.monsters.get(key);
    if (!monster) {
      return null;
    }

    // Create mock HTML elements for overview and encounter
    const mockOverview = document.createElement('div');
    mockOverview.innerHTML = '<p>Test monster overview</p>';
    
    const mockEncounter = document.createElement('div');
    mockEncounter.innerHTML = '<p>Test encounter description</p>';

    return {
      ...monster,
      overviewElement: mockOverview,
      encounterElement: mockEncounter
    };
  }

  async getSimilarMonsters(key: string): Promise<SimilarMonsterGroup[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    return this.similarGroups.get(key) || [];
  }

  async getRandomStatblock(): Promise<HTMLElement> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    const element = document.createElement('div');
    element.className = 'monster-statblock';
    element.setAttribute('data-monster', 'random-monster');
    element.innerHTML = `
      <h3>Random Monster</h3>
      <p><strong>AC:</strong> 15</p>
      <p><strong>HP:</strong> 30</p>
      <p><strong>Speed:</strong> 30 ft.</p>
    `;
    return element;
  }

  async getStatblock(request: StatblockRequest, change: StatblockChange | null): Promise<HTMLElement> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    const element = document.createElement('div');
    element.className = 'monster-statblock';
    element.setAttribute('data-monster', request.monsterKey);
    
    const powersList = request.powers && request.powers.length > 0 
      ? request.powers.map(p => p.name || p.key).join(', ')
      : 'No powers';
    
    element.innerHTML = `
      <h3>${request.monsterKey}</h3>
      <p><strong>AC:</strong> 15</p>
      <p><strong>HP:</strong> ${request.hpMultiplier ? Math.round(30 * request.hpMultiplier) : 30}</p>
      <p><strong>Speed:</strong> 30 ft.</p>
      <p><strong>Powers:</strong> ${powersList}</p>
      ${change ? `<p><em>Changed: ${change.type}</em></p>` : ''}
    `;
    
    // Add change-specific CSS classes for testing
    if (change?.type === 'hp-changed') {
      element.querySelectorAll('p').forEach(p => {
        if (p.textContent?.includes('HP:')) {
          p.setAttribute('data-statblock-property', 'hp');
        }
      });
    }
    if (change?.type === 'damage-changed') {
      element.querySelectorAll('p').forEach(p => {
        if (p.textContent?.includes('Powers:')) {
          p.setAttribute('data-statblock-property', 'attack');
        }
      });
    }
    if (change?.changedPower) {
      element.querySelectorAll('p').forEach(p => {
        if (p.textContent?.includes('Powers:')) {
          p.setAttribute('data-power-key', change.changedPower!.key);
        }
      });
    }
    
    return element;
  }

  // Test helper methods
  setMockMonster(key: string, monster: Monster): void {
    this.monsters.set(key, monster);
  }

  clearMockData(): void {
    this.monsters.clear();
    this.similarGroups.clear();
  }
}