

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { fixture, html } from '@open-wc/testing';
import { MonsterCodex } from '../../docs/src/components/MonsterCodex.js';
import '../setup.js';
import '../../docs/src/components/MonsterCodex.js';

// Mock MonsterSearchApi and ApiMonsterStore
class MockMonsterSearchApi {
  private baseUrl = 'https://test.foefoundry.com';

  async getFacets() {
    return {
      creatureTypes: [
        { value: 'Dragon', count: 2 },
        { value: 'Undead', count: 1 }
      ],
      crRange: { min: 0, max: 30 }
    };
  }
  async searchMonsters(request?: any) {
    return {
      monsters: [
        { 
          key: 'red-dragon', 
          name: 'Red Dragon', 
          cr: 17, 
          creature_type: 'Dragon', 
          tag_line: 'Fire-breathing terror', 
          background_image: '', 
          monsterFamilies: ['Chromatic'],
          tags: [
            { key: 'dragon', tag: 'Dragon', name: 'Dragon', description: 'Ancient magical creature', icon: 'dragon.svg', color: '#ff3737', category: 'creature_type', example_monsters: [] },
            { key: 'artillery', tag: 'Artillery', name: 'Artillery', description: 'Long-range attacker', icon: 'target.svg', color: '#28a745', category: 'monster_role', example_monsters: [] }
          ]
        },
        { 
          key: 'zombie', 
          name: 'Zombie', 
          cr: 1, 
          creature_type: 'Undead', 
          tag_line: 'Mindless undead', 
          background_image: '', 
          monsterFamilies: ['Corpse'],
          tags: [
            { key: 'undead', tag: 'Undead', name: 'Undead', description: 'Formerly living creature', icon: 'skull.svg', color: '#6c757d', category: 'creature_type', example_monsters: [] },
            { key: 'soldier', tag: 'Soldier', name: 'Soldier', description: 'Basic combatant', icon: 'sword.svg', color: '#17a2b8', category: 'monster_role', example_monsters: [] }
          ]
        }
      ],
      facets: await this.getFacets(),
      total: 2
    };
  }
}

class MockApiMonsterStore {
  async getNewMonsterTemplates(limit: number = 12) {
    return [];
  }

  async getMonsterTemplatesByFamily(familyKey: string) {
    return [];
  }

  async searchMonsterTemplates(query: string, limit: number = 12) {
    return [];
  }

  async getSimilarMonsters(key: string) {
    return [];
  }

  async getRandomStatblock() {
    const element = document.createElement('div');
    element.innerHTML = '<div class="stat-block">Mock Statblock</div>';
    return element.firstElementChild as HTMLElement;
  }

  async getStatblock(request: any, change: any) {
    const element = document.createElement('div');
    element.innerHTML = '<div class="stat-block">Mock Statblock</div>';
    return element.firstElementChild as HTMLElement;
  }

  async getMonster(key: string) {
    const mockData = {
      key,
      name: key === 'red-dragon' ? 'Red Dragon' : 'Zombie',
      image: '',
      backgroundImage: '',
      creatureType: key === 'red-dragon' ? 'Dragon' : 'Undead',
      monsterTemplateName: key === 'red-dragon' ? 'Dragon Template' : 'Undead Template',
      monsterTemplate: key === 'red-dragon' ? 'dragon' : 'undead',
      monsterFamilies: key === 'red-dragon' ? ['Chromatic'] : ['Corpse'],
      size: 'Large',
      cr: key === 'red-dragon' ? '17' : '1',
      tagLine: key === 'red-dragon' ? 'Fire-breathing terror' : 'Mindless undead',
      loadouts: [],
      relatedMonsters: [],
      nextTemplate: { monsterKey: '', templateKey: '' },
      previousTemplate: { monsterKey: '', templateKey: '' },
      overviewElement: null,
      encounterElement: null
    };

    if (key === 'red-dragon' || key === 'zombie') {
      return mockData;
    }
    return null;
  }
}

describe('MonsterCodex Component', () => {
  let element: MonsterCodex;

  beforeEach(async () => {
    // Create element but don't connect to DOM yet
    element = document.createElement('monster-codex') as MonsterCodex;

    // Inject mocks BEFORE connecting to DOM and triggering the task
    element['searchApi'] = new MockMonsterSearchApi() as any;
    element['apiStore'] = new MockApiMonsterStore() as any;

    // Now connect to DOM which will trigger the task with mocked APIs
    document.body.appendChild(element);
    await element.updateComplete;

    // Wait for searchTask to finish
    await new Promise(r => setTimeout(r, 500));
    await element.updateComplete;
  });

  afterEach(() => {
    // Clean up
    element.remove();
  });
  it('renders the main codex container', () => {
    const container = element.shadowRoot?.querySelector('.codex-container');
    expect(container).to.exist;
  });

  it('renders both mobile and desktop search bars', () => {
    const mobileBar = element.shadowRoot?.querySelector('.search-bar.mobile');
    const desktopBar = element.shadowRoot?.querySelector('.search-bar.desktop');
    expect(mobileBar).to.exist;
    expect(desktopBar).to.exist;
  });

  it('renders the filters panel and filter pills', () => {
    const filtersPanel = element.shadowRoot?.querySelector('.filters-panel');
    expect(filtersPanel).to.exist;
    const filtersHeader = element.shadowRoot?.querySelector('.filters-container h2');
    expect(filtersHeader?.textContent).to.include('Filters');
    const pills = element.shadowRoot?.querySelectorAll('.filter-pill');
    expect(pills && pills.length).to.be.greaterThan(0);
  });

  it('renders group-by buttons', () => {
    const groupBtns = element.shadowRoot?.querySelectorAll('.group-buttons .group-btn');
    expect(groupBtns && groupBtns.length).to.equal(4);
  });


  it('toggles a filter pill when clicked', async () => {
    // Set a query to trigger search and render pills as interactive
    // Use the search input to trigger search and render pills as interactive
    const searchInput = element.shadowRoot?.querySelector('.search-bar.desktop .search-input') as HTMLInputElement;
    searchInput.value = 'dragon';
    searchInput.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 1200)); // debounce is 1s
    let pill = element.shadowRoot?.querySelector('.filter-pill') as HTMLElement;
    if (!pill) return;
    const wasActive = pill.classList.contains('active');
    pill.click();
    await element.updateComplete;
    await new Promise(r => setTimeout(r, 50));
    // Re-query the pill after update (Lit may re-render the node)
    pill = element.shadowRoot?.querySelector('.filter-pill') as HTMLElement;
    expect(pill.classList.contains('active')).to.not.equal(wasActive);
  });

  it('updates search query on input', async () => {
    const searchInput = element.shadowRoot?.querySelector('.search-bar.desktop .search-input') as HTMLInputElement;
    searchInput.value = 'dragon';
    searchInput.dispatchEvent(new Event('input'));
    await new Promise(r => setTimeout(r, 1100)); // debounce is 1s
    expect(searchInput.value).to.equal('dragon');
  });


  it('renders monster rows with correct content', async () => {
    // Set a query to trigger search and monster rendering
    // Use the search input to trigger search and monster rendering
    const searchInput = element.shadowRoot?.querySelector('.search-bar.desktop .search-input') as HTMLInputElement;
    searchInput.value = 'dragon';
    searchInput.dispatchEvent(new Event('input'));

    // Also directly set the query to ensure the task runs
    element['query'] = 'dragon';
    element.requestUpdate();

    await new Promise(resolve => setTimeout(resolve, 1200)); // debounce is 1s
    await element.updateComplete;

    const rows = element.shadowRoot?.querySelectorAll('.monster-row');
    expect(rows && rows.length).to.be.greaterThan(0);
    if (!rows || rows.length === 0) return;
    const firstRow = rows[0] as HTMLElement;
    expect(firstRow.querySelector('.monster-name')?.textContent).to.exist;
    const tags = firstRow.querySelectorAll('.monster-tag-icon');
    expect(tags.length).to.be.greaterThan(0);
    const actions = firstRow.querySelectorAll('.monster-action-btn');
    expect(actions.length).to.be.greaterThan(0);
  });

  it('expands and collapses monster drawer on row click', async () => {
    await new Promise(resolve => setTimeout(resolve, 100));
    const row = element.shadowRoot?.querySelector('.monster-row') as HTMLElement;
    if (!row) return;
    row.click();
    await element.updateComplete;
    const drawer = row.parentElement?.querySelector('.monster-drawer');
    expect(drawer).to.exist;
    // Collapse
    row.click();
    await element.updateComplete;
    const drawerAfter = row.parentElement?.querySelector('.monster-drawer');
    expect(drawerAfter).to.not.exist;
  });
});


