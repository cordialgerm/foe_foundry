import { PowerLoadout, Power } from './powers';


export interface Monster {
    key: string;
    name: string;
    image: string;
    backgroundImage: string;
    creature_type: string;
    monster_template: string;
    monster_families: string[];
    size: string;
    cr: string;
    tag_line: string;
    loadouts: PowerLoadout[];
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
}

export interface StatblockChange {
    type: StatblockChangeType;
    changedPower: Power | null;
}

export interface MonsterStore {

    getMonster(key: string): Promise<Monster | null>;

    getStatblock(request: StatblockRequest, change: StatblockChange | null): Promise<HTMLElement>;
}