import { MonsterSearchRequest, MonsterSearchResult, SearchFacets, IMonsterSearchApi, MonsterInfo } from './search.js';

export class MonsterSearchApi implements IMonsterSearchApi {
    private baseUrl: string;

    constructor(baseUrl: string = '/api') {
        this.baseUrl = baseUrl;
    }

    async searchMonsters(request: MonsterSearchRequest): Promise<MonsterSearchResult> {
        const body = {
            query: request.query || '',
            limit: request.limit || 50,
            target_cr: undefined as number | undefined,
            creature_types: request.creatureTypes || undefined
        };

        // Handle CR range - backend expects single target_cr, so we'll use the midpoint
        if (request.minCr !== undefined && request.maxCr !== undefined) {
            body.target_cr = (request.minCr + request.maxCr) / 2.0;
        } else if (request.minCr !== undefined) {
            body.target_cr = request.minCr;
        } else if (request.maxCr !== undefined) {
            body.target_cr = request.maxCr;
        }

        const url = `${this.baseUrl}/v1/search/monsters`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error(`Search API request failed: ${response.status} ${response.statusText}`);
            }

            const monsters: MonsterInfo[] = await response.json();

            // TODO: Backend doesn't return facets yet, so we'll mock them for now
            const facets: SearchFacets = {
                creatureTypes: [
                    { value: 'Giant', count: 0 },
                    { value: 'Dragon', count: 0 },
                    { value: 'Undead', count: 0 },
                    { value: 'Beast', count: 0 },
                    { value: 'Humanoid', count: 0 },
                    { value: 'Monstrosity', count: 0 },
                    { value: 'Elemental', count: 0 },
                    { value: 'Fey', count: 0 },
                    { value: 'Fiend', count: 0 },
                    { value: 'Celestial', count: 0 },
                    { value: 'Aberration', count: 0 },
                    { value: 'Construct', count: 0 },
                    { value: 'Ooze', count: 0 },
                    { value: 'Plant', count: 0 }
                ],
                crRange: { min: 0, max: 30 }
            };

            return {
                monsters: monsters,
                facets: facets
            };
        } catch (error) {
            console.error('Monster search API error:', error);
            throw error;
        }
    }

    async getFacets(): Promise<SearchFacets> {
        try {
            // TODO: Backend doesn't have a facets endpoint yet, so we'll return static facets
            // When backend is ready, use: const response = await fetch(`${this.baseUrl}/v1/search/facets`);

            await new Promise(resolve => setTimeout(resolve, 100)); // Simulate API delay

            const facets: SearchFacets = {
                creatureTypes: [
                    { value: 'Giant', count: 45 },
                    { value: 'Dragon', count: 32 },
                    { value: 'Undead', count: 78 },
                    { value: 'Beast', count: 156 },
                    { value: 'Humanoid', count: 234 },
                    { value: 'Monstrosity', count: 89 },
                    { value: 'Elemental', count: 28 },
                    { value: 'Fey', count: 41 },
                    { value: 'Fiend', count: 67 },
                    { value: 'Celestial', count: 19 },
                    { value: 'Aberration', count: 34 },
                    { value: 'Construct', count: 22 },
                    { value: 'Ooze', count: 12 },
                    { value: 'Plant', count: 18 }
                ],
                crRange: { min: 0, max: 30 }
            };

            return facets;
        } catch (error) {
            console.error('Monster facets API error:', error);
            throw error;
        }
    }
}
