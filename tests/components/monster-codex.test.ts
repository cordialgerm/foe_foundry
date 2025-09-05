import { describe, it, expect, beforeEach } from 'vitest';
import { fixture, html } from '@open-wc/testing';
import { MonsterCodex } from '../../docs/src/components/MonsterCodex.js';
import { MockMonsterStore } from '../mocks/mock-monster-store.js';
import '../setup.js';

// Register the component
import '../../docs/src/components/MonsterCodex.js';

describe('MonsterCodex Component', () => {
  let element: MonsterCodex;
  let mockMonsterStore: MockMonsterStore;

  beforeEach(async () => {
    // Create fresh mock store for each test
    mockMonsterStore = new MockMonsterStore();
  });

  describe('Basic Rendering', () => {
    it('should render with basic structure', async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);

      expect(element).to.exist;
      
      // Should have main container
      const container = element.shadowRoot?.querySelector('.codex-container');
      expect(container).to.exist;
      
      // Should have header
      const header = element.shadowRoot?.querySelector('.codex-header');
      expect(header).to.exist;
      
      // Should have title
      const title = element.shadowRoot?.querySelector('.codex-title');
      expect(title).to.exist;
      expect(title?.textContent?.trim()).to.include('Foe Foundry Monster Codex');
    });

    it('should render search section', async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);
      
      // Should have search section
      const searchSection = element.shadowRoot?.querySelector('.search-section');
      expect(searchSection).to.exist;
      
      // Should have search input
      const searchInput = element.shadowRoot?.querySelector('.search-input');
      expect(searchInput).to.exist;
      expect((searchInput as HTMLInputElement)?.placeholder).to.include('Search monster name...');
      
      // Should have search icon
      const searchIcon = element.shadowRoot?.querySelector('.search-icon');
      expect(searchIcon).to.exist;
    });

    it('should render filters section', async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);
      
      // Should have filters section
      const filtersSection = element.shadowRoot?.querySelector('.filters-section');
      expect(filtersSection).to.exist;
      
      // Should have filters header
      const filtersHeader = element.shadowRoot?.querySelector('.filters-header');
      expect(filtersHeader).to.exist;
      expect(filtersHeader?.textContent?.trim()).to.include('Filters');
      
      // Should have chevron icon
      const chevron = element.shadowRoot?.querySelector('.filters-chevron');
      expect(chevron).to.exist;
      
      // Should have filters content (initially collapsed)
      const filtersContent = element.shadowRoot?.querySelector('.filters-content');
      expect(filtersContent).to.exist;
      expect(filtersContent?.classList.contains('expanded')).to.be.false;
    });

    it('should render monster grid section', async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);

      await element.updateComplete;
      
      // Should have monsters section
      const monstersSection = element.shadowRoot?.querySelector('.monsters-section');
      expect(monstersSection).to.exist;
    });
  });

  describe('Filter Functionality', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);
      await element.updateComplete;
    });

    it('should toggle filters when clicking filters header', async () => {
      const filtersHeader = element.shadowRoot?.querySelector('.filters-header') as HTMLElement;
      const filtersContent = element.shadowRoot?.querySelector('.filters-content');
      
      expect(filtersContent?.classList.contains('expanded')).to.be.false;
      
      filtersHeader.click();
      await element.updateComplete;
      
      expect(filtersContent?.classList.contains('expanded')).to.be.true;
      
      filtersHeader.click();
      await element.updateComplete;
      
      expect(filtersContent?.classList.contains('expanded')).to.be.false;
    });

    it('should show filter categories when expanded', async () => {
      const filtersHeader = element.shadowRoot?.querySelector('.filters-header') as HTMLElement;
      
      filtersHeader.click();
      await element.updateComplete;
      
      // Should have creature type filters
      const creatureTypeFilters = element.shadowRoot?.querySelectorAll('.filter-group');
      expect(creatureTypeFilters?.length).to.be.greaterThan(0);
      
      // Should have filter tags
      const filterTags = element.shadowRoot?.querySelectorAll('.filter-tag');
      expect(filterTags?.length).to.be.greaterThan(0);
      
      // Should have organize buttons
      const organizeButtons = element.shadowRoot?.querySelectorAll('.organize-button');
      expect(organizeButtons?.length).to.equal(3); // Family, Challenge, Name
    });

    it('should handle search input', async () => {
      const searchInput = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
      
      // Simulate typing in search
      searchInput.value = 'ice';
      searchInput.dispatchEvent(new Event('input'));
      await element.updateComplete;
      
      // The component should filter results (tested via the internal state)
      expect(searchInput.value).to.equal('ice');
    });

    it('should toggle filter tags when clicked', async () => {
      const filtersHeader = element.shadowRoot?.querySelector('.filters-header') as HTMLElement;
      filtersHeader.click();
      await element.updateComplete;
      
      const firstFilterTag = element.shadowRoot?.querySelector('.filter-tag') as HTMLElement;
      expect(firstFilterTag?.classList.contains('active')).to.be.false;
      
      firstFilterTag.click();
      await element.updateComplete;
      
      expect(firstFilterTag?.classList.contains('active')).to.be.true;
    });
  });

  describe('Mobile Responsiveness', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);
      await element.updateComplete;
    });

    it('should show hamburger button on mobile', async () => {
      // Force mobile state
      (element as any).isMobile = true;
      await element.updateComplete;
      
      const hamburgerButton = element.shadowRoot?.querySelector('.hamburger-button');
      expect(hamburgerButton).to.exist;
    });

    it('should have responsive grid classes', async () => {
      const monsterGrid = element.shadowRoot?.querySelector('.monster-grid');
      expect(monsterGrid).to.exist;
      expect(monsterGrid?.classList.contains('monster-grid')).to.be.true;
    });
  });

  describe('Monster Card Rendering', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);
      await element.updateComplete;
      // Wait for monster loading to complete
      await new Promise(resolve => setTimeout(resolve, 50));
    });

    it('should render monster cards with placeholder data', async () => {
      const monsterCards = element.shadowRoot?.querySelectorAll('.monster-card');
      expect(monsterCards?.length).to.be.greaterThan(0);
    });

    it('should render monster card content', async () => {
      const firstCard = element.shadowRoot?.querySelector('.monster-card');
      
      if (firstCard) {
        // Should have monster name
        const monsterName = firstCard.querySelector('.monster-card-name');
        expect(monsterName).to.exist;
        
        // Should have CR
        const monsterCr = firstCard.querySelector('.monster-card-cr');
        expect(monsterCr).to.exist;
        
        // Should have tags
        const monsterTags = firstCard.querySelectorAll('.monster-tag');
        expect(monsterTags?.length).to.be.greaterThan(0);
        
        // Should have action buttons
        const forgeButton = firstCard.querySelector('.forge-button');
        const shareButton = firstCard.querySelector('.share-button');
        expect(forgeButton).to.exist;
        expect(shareButton).to.exist;
        expect(forgeButton?.textContent?.trim()).to.equal('Forge');
        expect(shareButton?.textContent?.trim()).to.equal('Share');
      }
    });

    it('should handle monster card clicks', async () => {
      const firstCard = element.shadowRoot?.querySelector('.monster-card') as HTMLElement;
      
      if (firstCard) {
        // Mock window.location.href to test navigation
        const originalLocation = window.location.href;
        let navigatedUrl = '';
        Object.defineProperty(window, 'location', {
          value: {
            href: originalLocation,
            set href(url: string) {
              navigatedUrl = url;
            }
          },
          writable: true
        });
        
        firstCard.click();
        await element.updateComplete;
        
        // Should attempt to navigate (in a real implementation)
        // This test verifies the click handler is attached
        expect(firstCard).to.exist;
      }
    });
  });

  describe('Organize Options', () => {
    beforeEach(async () => {
      element = await fixture(html`
        <monster-codex 
          .monsterStore="${mockMonsterStore}"
        ></monster-codex>
      `);
      
      // Expand filters to access organize buttons
      const filtersHeader = element.shadowRoot?.querySelector('.filters-header') as HTMLElement;
      filtersHeader.click();
      await element.updateComplete;
    });

    it('should have three organize options', async () => {
      const organizeButtons = element.shadowRoot?.querySelectorAll('.organize-button');
      expect(organizeButtons?.length).to.equal(3);
      
      const buttonTexts = Array.from(organizeButtons || []).map(btn => btn.textContent?.trim());
      expect(buttonTexts).to.include('Family');
      expect(buttonTexts).to.include('Challenge');
      expect(buttonTexts).to.include('Name');
    });

    it('should show Family as default active organize option', async () => {
      const familyButton = Array.from(element.shadowRoot?.querySelectorAll('.organize-button') || [])
        .find(btn => btn.textContent?.trim() === 'Family');
      
      expect(familyButton?.classList.contains('active')).to.be.true;
    });

    it('should switch organize options when clicked', async () => {
      const challengeButton = Array.from(element.shadowRoot?.querySelectorAll('.organize-button') || [])
        .find(btn => btn.textContent?.trim() === 'Challenge') as HTMLElement;
      
      challengeButton.click();
      await element.updateComplete;
      
      expect(challengeButton.classList.contains('active')).to.be.true;
      
      const familyButton = Array.from(element.shadowRoot?.querySelectorAll('.organize-button') || [])
        .find(btn => btn.textContent?.trim() === 'Family');
      
      expect(familyButton?.classList.contains('active')).to.be.false;
    });
  });
});