import { PowerLoadout } from './powers';


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

export interface MonsterStore {
    getMonster(key: string): Monster | null;
}