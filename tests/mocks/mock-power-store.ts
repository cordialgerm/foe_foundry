import { PowerStore, PowerLoadout, Power } from '../../docs/src/data/powers.js';

// Test data fixtures
export const mockPowers: Power[] = [
  {
    key: 'test-power-1',
    name: 'Fire Breath',
    powerCategory: 'offense',
    icon: 'fire'
  },
  {
    key: 'test-power-2', 
    name: 'Ice Shield',
    powerCategory: 'defense',
    icon: 'ice'
  },
  {
    key: 'test-power-3',
    name: 'Lightning Bolt',
    powerCategory: 'offense', 
    icon: 'lightning'
  }
];

export const mockPowerLoadouts: PowerLoadout[] = [
  {
    key: 'loadout-1',
    name: 'Elemental Warrior',
    flavorText: 'Masters of fire and ice.',
    powers: [mockPowers[0], mockPowers[1]],
    selectionCount: 1,
    locked: false,
    replaceWithSpeciesPowers: false
  },
  {
    key: 'loadout-2',
    name: 'Storm Caller',
    flavorText: 'Wielders of lightning and thunder.',
    powers: [mockPowers[2]],
    selectionCount: 1,
    locked: true,
    replaceWithSpeciesPowers: false
  }
];

export class MockPowerStore implements PowerStore {
  private mockData: Map<string, PowerLoadout[]> = new Map();

  constructor() {
    // Set up test data
    this.mockData.set('test-monster', mockPowerLoadouts);
    this.mockData.set('ogre', [mockPowerLoadouts[0]]);
    this.mockData.set('knight', mockPowerLoadouts);
  }

  async getPowerLoadouts(monsterKey: string): Promise<PowerLoadout[] | null> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 10));
    
    return this.mockData.get(monsterKey) || null;
  }

  // Test helper methods
  setMockData(monsterKey: string, loadouts: PowerLoadout[]): void {
    this.mockData.set(monsterKey, loadouts);
  }

  clearMockData(): void {
    this.mockData.clear();
  }
}