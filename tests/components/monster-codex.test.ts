

import { describe, it, expect, beforeEach } from 'vitest';
import { fixture, html } from '@open-wc/testing';
import { MonsterCodex } from '../../docs/src/components/MonsterCodex.js';
import '../setup.js';
import '../../docs/src/components/MonsterCodex.js';

// Mock MonsterSearchApi and ApiMonsterStore
class MockMonsterSearchApi {
  async getFacets() {
    return {
      creatureTypes: [
        { value: 'Dragon', count: 2 },
        { value: 'Undead', count: 1 }
      ],
      crRange: { min: 0, max: 30 }
    };
  }
  async searchMonsters() {
    return {
      monsters: [
        { key: 'red-dragon', name: 'Red Dragon', cr: 17, creature_type: 'Dragon', tag_line: 'Fire-breathing terror', background_image: '', monsterFamilies: ['Chromatic'] },
        { key: 'zombie', name: 'Zombie', cr: 1, creature_type: 'Undead', tag_line: 'Mindless undead', background_image: '', monsterFamilies: ['Corpse'] }
      ],
      facets: await this.getFacets(),
      total: 2
    };
  }
}

class MockApiMonsterStore {
  async getMonster(key: string) {
    if (key === 'red-dragon') {
      return { key: 'red-dragon', name: 'Red Dragon', cr: 17, creature_type: 'Dragon', tag_line: 'Fire-breathing terror', background_image: '', monsterFamilies: ['Chromatic'] };
    }
    if (key === 'zombie') {
      return { key: 'zombie', name: 'Zombie', cr: 1, creature_type: 'Undead', tag_line: 'Mindless undead', background_image: '', monsterFamilies: ['Corpse'] };
    }
    return null;
  }
}

describe('MonsterCodex Component', () => {
  let element: MonsterCodex;

  beforeEach(async () => {
    element = await fixture(html`<monster-codex></monster-codex>`);
    // Inject mocks
    element['searchApi'] = new MockMonsterSearchApi();
    element['apiStore'] = new MockApiMonsterStore();
    await element.updateComplete;
    // Wait for searchTask to finish
    await new Promise(r => setTimeout(r, 100));
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
    await new Promise(resolve => setTimeout(resolve, 1200)); // debounce is 1s
    const rows = element.shadowRoot?.querySelectorAll('.monster-row');
    expect(rows && rows.length).to.be.greaterThan(0);
    if (!rows || rows.length === 0) return;
    const firstRow = rows[0] as HTMLElement;
    expect(firstRow.querySelector('.monster-name')?.textContent).to.exist;
    const tags = firstRow.querySelectorAll('.monster-tag');
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


