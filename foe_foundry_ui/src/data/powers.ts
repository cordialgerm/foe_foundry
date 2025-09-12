export interface Power {
    key: string;
    name: string;
    powerCategory: string;
    icon: string;
}

export interface PowerLoadout {
    key: string;
    name: string;
    flavorText: string;
    powers: Power[];
    selectionCount: number;
    locked: boolean;
    replaceWithSpeciesPowers: boolean;
}

export interface PowerStore {

    getPowerLoadouts(monsterKey: string): Promise<PowerLoadout[] | null>;
}
