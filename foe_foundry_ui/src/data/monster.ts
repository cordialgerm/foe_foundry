import { PowerLoadout, Power } from './powers';


export interface RelatedMonster {
    key: string;
    name: string;
    cr: string;
    template: string;
    sameTemplate: boolean;
    family: string | null
}

export interface RelatedMonsterTemplate {
    monsterKey: string;
    templateKey: string;
}

export interface SimilarMonsterGroup {
    name: string;
    url: string;
    monsters: RelatedMonster[];  // Note: keeping the typo to match API response
}

export interface Monster {
    key: string;
    name: string;
    image: string;
    backgroundImage: string;
    creatureType: string;
    monsterTemplateName: string;
    monsterTemplate: string;
    monsterFamilies: string[];
    size: string;
    cr: string;
    tagLine: string;
    loadouts: PowerLoadout[];
    relatedMonsters: RelatedMonster[];
    nextTemplate: RelatedMonsterTemplate;
    previousTemplate: RelatedMonsterTemplate;

    overviewElement: HTMLElement | null;
    encounterElement: HTMLElement | null;
}

export interface StatblockRequest {
    monsterKey: string;
    powers: Power[];
    hpMultiplier: number | null;
    damageMultiplier: number | null;
}

export enum StatblockChangeType {
    Rerolled = 'rerolled',
    PowerChanged = 'power-changed',
    DamageChanged = 'damage-changed',
    HpChanged = 'hp-changed',
    MonsterChanged = 'monster-changed'
}

export interface StatblockChange {
    type: StatblockChangeType;
    changedPower: Power | null;
}

export interface MonsterStore {

    getMonster(key: string): Promise<Monster | null>;

    getSimilarMonsters(key: string): Promise<SimilarMonsterGroup[]>;

    getStatblock(request: StatblockRequest, change: StatblockChange | null): Promise<HTMLElement>;

    getRandomStatblock(): Promise<HTMLElement>;
}