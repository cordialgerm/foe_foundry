import { MonsterSearchRequest, MonsterSearchResult, SearchFacets, IMonsterSearchApi, MonsterInfo, SearchSeed } from './search.js';

export class MonsterSearchApi implements IMonsterSearchApi {
    private baseUrl: string;

    constructor(baseUrl: string = '/api') {
        this.baseUrl = baseUrl;
    }

    async searchMonsters(request: MonsterSearchRequest): Promise<MonsterSearchResult> {
        const body = {
            query: request.query || '',
            limit: request.limit || 50,
            min_cr: request.minCr,
            max_cr: request.maxCr,
            creature_types: request.creatureTypes || undefined
        };

        const url = `${this.baseUrl}/v1/search/monsters/enhanced`;

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

            const result: any = await response.json();
            
            // Transform backend family_names to frontend monsterFamilies
            const transformedResult: MonsterSearchResult = {
                ...result,
                monsters: result.monsters.map((monster: any) => ({
                    ...monster,
                    monsterFamilies: monster.family_names || []
                }))
            };
            
            return transformedResult;
        } catch (error) {
            console.error('Monster search API error:', error);
            throw error;
        }
    }

    async getFacets(): Promise<SearchFacets> {
        try {
            const response = await fetch(`${this.baseUrl}/v1/search/facets`);

            if (!response.ok) {
                throw new Error(`Facets API request failed: ${response.status} ${response.statusText}`);
            }

            const facets: SearchFacets = await response.json();
            return facets;
        } catch (error) {
            console.error('Monster facets API error:', error);
            throw error;
        }
    }

    async getSearchSeeds(): Promise<SearchSeed[]> {
        try {
            const response = await fetch(`${this.baseUrl}/v1/search/seeds`);

            if (!response.ok) {
                throw new Error(`Search seeds API request failed: ${response.status} ${response.statusText}`);
            }

            const seeds: SearchSeed[] = await response.json();
            return seeds;
        } catch (error) {
            console.error('Search seeds API error:', error);
            throw error;
        }
    }
}
