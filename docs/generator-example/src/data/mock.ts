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
        flavorText: 'Half-remembered martial prowess',
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
    monster_template: 'Skeleton',
    monster_families: ['Lesser Undead'],
    size: 'Medium',
    cr: 'CR 1/4',
    tag_line: 'Fleshless Servants to Greater Undead',
    loadouts: mockLoadouts
};
const mockBasilisk: Monster = {
    key: 'basilisk',
    name: 'Basilisk',
    image: '../img/monsters/basilisk.webp',
    backgroundImage: '../img/backgrounds/textures/monstrosity.webp',
    creature_type: 'Monstrosity',
    monster_template: 'Basilisk',
    monster_families: ['Petrifying Monstrosities'],
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
    monster_template: 'Gelatinous Cube',
    monster_families: [],
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
    monster_template: 'Knight',
    monster_families: ['Fanatics & Faithful', 'Martial NPCs'],
    size: 'Medium',
    cr: 'CR 3',
    tag_line: 'A skilled warrior',
    loadouts: mockLoadouts
}
const mockFrostGiant: Monster = {
    key: 'frost-giant',
    name: 'Frost Giant',
    image: '../img/monsters/frost-giant.webp',
    backgroundImage: '../img/backgrounds/textures/giant.webp',
    creature_type: 'Giant',
    monster_template: 'Frost Giant',
    monster_families: ['True Giants'],
    size: 'Medium',
    cr: 'CR 8',
    tag_line: 'Frozen Reavers of Blood and Battle',
    loadouts: mockLoadouts
}

const monsters: Record<string, Monster> = {
    'skeleton': mockSkeleton,
    'basilisk': mockBasilisk,
    'gelatinous-cube': mockGelatinousCube,
    'knight': mockKnight,
    'frost-giant': mockFrostGiant
}

export class MockPowerStore implements PowerStore {

    async getPowerLoadouts(monsterKey: string): Promise<PowerLoadout[] | null> {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 200));
        const monsters = initializeMockMonsterStore();
        const monster = await monsters.getMonster(monsterKey);
        if (!monster) {
            return null;
        }
        return mockLoadouts;
    }
}

export class MockMonsterStore implements MonsterStore {
    async getMonster(key: string): Promise<Monster | null> {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 200));
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
