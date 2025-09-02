// MonsterInfo type matching backend MonsterInfoModel
export interface MonsterInfo {
    key: string;
    name: string;
    cr: number;
    template: string;
    monsterFamilies?: string[];
    background_image?: string;
}

// Enhanced search request interface
export interface MonsterSearchRequest {
    query?: string;
    limit?: number;
    creatureTypes?: string[];
    minCr?: number;
    maxCr?: number;
}

// Facet data for filters
export interface SearchFacet {
    value: string;
    count: number;
}

export interface SearchFacets {
    creatureTypes: SearchFacet[];
    crRange: {
        min: number;
        max: number;
    };
}

// Enhanced search response with facets
export interface MonsterSearchResult {
    monsters: MonsterInfo[];
    facets: SearchFacets;
    total?: number;
}

// Search API interface
export interface IMonsterSearchApi {
    /**
     * Search for monsters with optional filters
     * @param request Search parameters and filters
     * @returns Promise resolving to search results with facets for current query
     */
    searchMonsters(request: MonsterSearchRequest): Promise<MonsterSearchResult>;

    /**
     * Get all available facets with counts across the entire monster database
     * Used for initial page load to populate filter options
     * @returns Promise resolving to facets with total counts
     */
    getFacets(): Promise<SearchFacets>;
}
