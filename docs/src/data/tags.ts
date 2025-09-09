/**
 * Tag data interfaces for the API
 */

export interface TagInfo {
  key: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  category: string;
  example_monsters: MonsterInfo[];
}

export interface MonsterInfo {
  key: string;
  name: string;
  cr: number;
  template: string;
  background_image?: string;
  creature_type?: string;
  tag_line?: string;
  tags?: TagInfo[];
}
  color?: string;
}

export class TagApi {
  /**
   * Get detailed information about a specific tag
   */
  async getTag(tagKey: string): Promise<TagInfo> {
    const response = await fetch(`/api/v1/tags/tag/${encodeURIComponent(tagKey)}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch tag: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get all available tags, optionally filtered by category
   */
  async getAllTags(category?: string): Promise<TagInfo[]> {
    const url = category 
      ? `/api/v1/tags/all?category=${encodeURIComponent(category)}`
      : '/api/v1/tags/all';
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch tags: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get all available tag categories
   */
  async getCategories(): Promise<string[]> {
    const response = await fetch('/api/v1/tags/categories');
    if (!response.ok) {
      throw new Error(`Failed to fetch categories: ${response.statusText}`);
    }
    return response.json();
  }
}