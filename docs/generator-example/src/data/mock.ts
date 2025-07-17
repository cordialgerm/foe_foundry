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
    backgroundImage: '../img/backgrounds/textures/undead.webp',
    creature_type: 'Undead',
    size: 'Medium',
    cr: 'CR 1/4',
    tag_line: 'A fearsome undead warrior',
    loadouts: mockLoadouts
};
const mockBasilisk: Monster = {
    key: 'basilisk',
    name: 'Basilisk',
    image: '../img/monsters/basilisk.webp',
    backgroundImage: '../img/backgrounds/textures/monstrosity.webp',
    creature_type: 'Monstrosity',
    size: 'Medium',
    cr: 'CR 4',
    tag_line: 'A fearsome monstrosity',
    loadouts: mockLoadouts
};
const mockGelatinousCube: Monster = {
    key: 'gelatinous-cube',
    name: 'Gelatinous Cube',
    image: '../img/monsters/gelatinous-cube.webp',
    backgroundImage: '../img/backgrounds/textures/ooze.webp',
    creature_type: 'Ooze',
    size: 'Large',
    cr: 'CR 2',
    tag_line: 'A mindless, gelatinous mass',
    loadouts: mockLoadouts
}
const mockKnight: Monster = {
    key: 'knight',
    name: 'Knight',
    image: '../img/monsters/knight.webp',
    backgroundImage: '../img/backgrounds/textures/humanoid.webp',
    creature_type: 'Humanoid',
    size: 'Medium',
    cr: 'CR 3',
    tag_line: 'A skilled warrior',
    loadouts: mockLoadouts
}

const monsters: Record<string, Monster> = {
    'skeleton': mockSkeleton,
    'basilisk': mockBasilisk,
    'gelatinous-cube': mockGelatinousCube,
    'knight': mockKnight
}

export class MockPowerStore implements PowerStore {

    getPowerLoadouts(monsterKey: string): PowerLoadout[] | null {

        const monsters = initializeMockMonsterStore();
        const monster = monsters.getMonster(monsterKey);
        if (!monster) {
            return null;
        }

        return mockLoadouts;
    }
}

export class MockMonsterStore implements MonsterStore {
    getMonster(key: string): Monster | null {
        return monsters[key] || null;
    }
}

// Function to initialize the mock power store
export function initializeMockPowerStore(): MockPowerStore {
    return new MockPowerStore();
}

export function initializeMockMonsterStore(): MockMonsterStore {
    return new MockMonsterStore();
}
