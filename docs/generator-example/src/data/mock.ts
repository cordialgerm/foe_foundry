import { PowerStore, PowerLoadout, Power } from './powers';
import { Monster, MonsterStore } from './monster';

// Mock data based on generator_old.html
const mockPowers: Record<string, Power[]> = {
    'skeletal-boon': [
        {
            key: 'skeletal-reconstruction',
            name: 'Skeletal Reconstruction',
            power_category: 'healing',
            icon: 'raise-skeleton'
        },
        {
            key: 'bone-spear',
            name: 'Bone Spear',
            power_category: 'attack',
            icon: 'spine-arrow'
        },
        {
            key: 'undead-resilience',
            name: 'Undead Resilience',
            power_category: 'defense',
            icon: 'raise-zombie'
        }
    ],
    'martial-memories': [
        {
            key: 'coordinated-strike',
            name: 'Coordinated Strike',
            power_category: 'attack',
            icon: 'switch-weapons'
        },
        {
            key: 'battle-fury',
            name: 'Battle Fury',
            power_category: 'buff',
            icon: 'wind-hole'
        }
    ]
};

const mockLoadouts: PowerLoadout[] = [
    {
        key: 'skeletal-boon',
        name: 'Skeletal Boon',
        flavorText: 'Rattling bones and grinning skulls',
        powers: mockPowers['skeletal-boon'],
        selectionCount: 1,
        locked: false,
        replaceWithSpeciesPowers: false
    },
    {
        key: 'martial-memories',
        name: 'Martial Memories',
        flavorText: 'Half-remember martial prowess',
        powers: mockPowers['martial-memories'],
        selectionCount: 1,
        locked: false,
        replaceWithSpeciesPowers: false
    }
];

const mockSkeleton: Monster = {
    key: 'skeleton',
    name: 'Skeleton',
    image: '../img/monsters/skeleton.webp',
    backgroundImage: '../img/backgrounds/textures/undead-painting.webp',
    creature_type: 'Undead',
    size: 'Medium',
    cr: 'CR 1/4',
    tag_line: 'A fearsome undead warrior',
    loadouts: mockLoadouts
};

export class MockPowerStore implements PowerStore {

    getPowerLoadouts(monsterKey: string): PowerLoadout[] {
        // // Simulate async behavior
        // await new Promise(resolve => setTimeout(resolve, 100));

        // For this mock, return the same loadouts for any monster
        return mockLoadouts;
    }
}

export class MockMonsterStore implements MonsterStore {
    getMonster(key: string): Monster {
        // Simulate async behavior
        // await new Promise(resolve => setTimeout(resolve, 100));

        // For this mock, return the skeleton monster for any key
        return mockSkeleton;
    }
}

// Function to initialize the mock power store
export function initializeMockPowerStore(): MockPowerStore {
    return new MockPowerStore();
}

export function initializeMockMonsterStore(): MockMonsterStore {
    return new MockMonsterStore();
}
