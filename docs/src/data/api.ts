import { PowerStore, PowerLoadout, Power } from './powers';
import { Monster, MonsterStore, StatblockChangeType, StatblockChange, StatblockRequest } from './monster';

function formatCr(cr: string | number): string {
    if (typeof cr === 'string') return cr;
    switch (cr) {
        case 0.125: return 'CR ⅛';
        case 0.25: return 'CR ¼';
        case 0.5: return 'CR ½';
        default: return `CR ${cr}`;
    }
}

export class ApiPowerStore implements PowerStore {

    async getPowerLoadouts(monsterKey: string): Promise<PowerLoadout[] | null> {
        const baseUrl: string = window.baseUrl ?? 'https://foefoundry.com';
        const response = await fetch(`${baseUrl}/api/v1/monsters/${monsterKey}/loadouts`);
        if (!response.ok) return null;

        const data = await response.json();

        // Map API PowerLoadoutModel to PowerLoadout
        return data.map((loadout: any) => ({
            key: loadout.key,
            name: loadout.name,
            flavorText: loadout.flavor_text,
            powers: loadout.powers.map((p: any) => ({
                key: p.key,
                name: p.name,
                powerCategory: p.power_category,
                icon: p.icon
            })),
            selectionCount: loadout.selection_count,
            locked: loadout.locked,
            replaceWithSpeciesPowers: loadout.replace_with_species_powers
        }));
    }
}

export class ApiMonsterStore implements MonsterStore {


    async getMonster(key: string): Promise<Monster | null> {
        const baseUrl: string = window.baseUrl ?? 'https://foefoundry.com';
        const response = await fetch(`${baseUrl}/api/v1/monsters/${key}`);
        if (!response.ok) return null;

        const data = await response.json();

        // Map MonsterModel to Monster
        return {
            key: data.key ?? key,
            name: data.name,
            tagLine: data.tag_line ?? '',
            image: (data.primary_image || (data.images && data.images[0])) ?? '',
            backgroundImage: data.background_image,
            creatureType: data.creature_type,
            monsterTemplate: data.template_key,
            monsterFamilies: [], // Not present in API, set empty or infer if possible
            size: data.size,
            cr: formatCr(data.cr),
            loadouts: (data.loadouts || []).map((loadout: any) => ({
                key: loadout.key,
                name: loadout.name,
                flavorText: loadout.flavor_text,
                powers: loadout.powers.map((p: any) => ({
                    key: p.key,
                    name: p.name,
                    powerCategory: p.power_category,
                    icon: p.icon
                })),
                selectionCount: loadout.selection_count,
                locked: loadout.locked,
                replaceWithSpeciesPowers: loadout.replace_with_species_powers
            })),
            relatedMonsters: (data.related_monsters || []).map((related: any) => ({
                key: related.key,
                name: related.name,
                cr: formatCr(related.cr),
                template: related.template,
                sameTemplate: related.same_template
            }))
        };
    }

    async getStatblock(request: StatblockRequest, change: StatblockChange | null): Promise<HTMLElement> {
        const payload = {
            monster_key: request.monsterKey,
            powers: request.powers?.map(p => p.key),
            hp_multiplier: request.hpMultiplier,
            damage_multiplier: request.damageMultiplier
        };
        const baseUrl: string = (window as any).baseUrl ?? 'https://foefoundry.com';
        const response = await fetch(`${baseUrl}/api/v1/statblocks/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Failed to generate statblock: ${response.statusText}`);
        }

        const result = await response.json();
        const statblock_html = result["statblock_html"];
        const parser = new DOMParser();
        const statblockElement = parser.parseFromString(statblock_html, 'text/html').body.firstElementChild as HTMLElement;
        statblockElement.part = 'stat-block';

        // Highlight changes
        if (change?.changedPower) {
            const changedKey = change.changedPower.key;
            statblockElement.querySelectorAll(`[data-power-key="${changedKey}"]`).forEach(el => {
                el.classList.add('power-changed');
            });
        }
        if (change?.type === StatblockChangeType.HpChanged) {
            statblockElement.querySelectorAll(`[data-statblock-property="hp"]`).forEach(el => {
                el.classList.add('hp-changed');
            });
        }
        if (change?.type === StatblockChangeType.DamageChanged) {
            statblockElement.querySelectorAll(`[data-statblock-property="attack"]`).forEach(el => {
                el.classList.add('damage-changed');
            });
        }

        // Remove the highlight classes after 5 seconds
        setTimeout(() => {
            statblockElement.querySelectorAll('.damage-changed').forEach(el => el.classList.remove('damage-changed'));
            statblockElement.querySelectorAll('.hp-changed').forEach(el => el.classList.remove('hp-changed'));
            statblockElement.querySelectorAll('.power-changed').forEach(el => el.classList.remove('power-changed'));
        }, 5000);
        return statblockElement;
    }
}

// Function to initialize the mock power store
export function initializePowerStore(): PowerStore {
    return new ApiPowerStore();
}

export function initializeMonsterStore(): MonsterStore {
    return new ApiMonsterStore();
}
