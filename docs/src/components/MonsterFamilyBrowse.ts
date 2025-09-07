import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { Task } from '@lit/task';
import { apiMonsterStore, MonsterFamily } from '../data/api.js';
import './MonsterCarousel.js';
import './SvgIcon.js';

interface ActiveCarousel {
  familyKey: string;
  familyName: string;
  familyUrl: string;
  familyTagLine: string;
  familyIcon: string;
}

@customElement('monster-family-browse')
export class MonsterFamilyBrowse extends LitElement {
  @state() private activeCarousels: ActiveCarousel[] = [];
  @state() private selectedFamilyIndex: number = 0; // Which carousel slot to replace next

  private familiesTask = new Task(this, async () => {
    const families = await apiMonsterStore.getAllFamilies();

    // Randomly select 3 families for initial display
    const shuffled = [...families].sort(() => 0.5 - Math.random());
    this.activeCarousels = shuffled.slice(0, 3).map(family => ({
      familyKey: family.key,
      familyName: family.name,
      familyUrl: family.url,
      familyTagLine: family.tag_line,
      familyIcon: family.icon
    }));

    return families;
  }, () => []);

  static styles = css`
    :host {
      display: block;
      height: 100%;
      overflow: hidden;
    }

    .browse-container {
      display: flex;
      height: 100%; /* Fill the tab content area */
      min-height: 600px;
      align-items: flex-start; /* Top align both panels */
    }

    /* Table of Contents Panel */
    .toc-panel {
      width: 280px;
      background: var(--bg-color);
      border-right: 2px solid var(--border-color);
      overflow-y: auto;
      padding: 1.5rem;
      position: relative;
      flex-shrink: 0; /* Prevent panel from shrinking */
      height: 100%; /* Full height to match content panel */
    }

    .toc-title {
      font-family: var(--header-font);
      font-size: 1.4rem;
      color: var(--primary-color);
      margin-bottom: 1rem;
      border-bottom: 2px solid var(--border-color);
      padding-bottom: 0.5rem;
    }

    .family-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .family-item {
      margin-bottom: 0.5rem;
    }

    .family-link {
      display: flex;
      align-items: center;
      padding: 0.75rem 1rem;
      color: var(--fg-color);
      text-decoration: none;
      border-radius: 4px;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      font-family: var(--primary-font);
      line-height: 1.4;
    }

    .family-icon {
      width: 20px;
      height: 20px;
      margin-right: 0.75rem;
      flex-shrink: 0;
      color: currentColor;
    }

    .family-info {
      flex: 1;
    }

    .family-link:hover {
      background: var(--primary-color);
      color: var(--fg-color);
      border-color: var(--primary-color);
      transform: translateX(4px);
    }

    .family-link.active {
      background: var(--tertiary-color);
      color: var(--fg-color);
      border-color: var(--tertiary-color);
      font-weight: bold;
    }

    .family-monster-count {
      font-size: 0.85rem;
      opacity: 0.7;
      margin-top: 0.25rem;
    }

    /* Scroll indicator */
    .toc-panel::after {
      content: "";
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 20px;
      background: linear-gradient(transparent, var(--bg-color));
      pointer-events: none;
    }

    /* Main Content Panel */
    .content-panel {
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem;
      padding-top: 0rem;
      height: 100%; /* Full height to match toc panel */
    }

    .carousel-section {
      margin-bottom: 1.5rem;
      border-radius: 8px;
      background: var(--bg-color); /* Removed black background */
      padding: 1.5rem;
      border: 1px solid var(--border-color);
    }

    .carousel-header {
      display: flex;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 2px solid var(--border-color);
    }

    .carousel-icon {
      width: 32px;
      height: 32px;
      margin-right: 1rem;
      flex-shrink: 0;
      color: var(--primary-color);
    }

    .carousel-title-section {
      flex: 1;
    }

    .carousel-title {
      font-family: var(--header-font);
      font-size: 2rem; /* Made headers larger */
      margin: 0;
      color: var(--primary-color);
      line-height: 1.2;
    }

    .carousel-tagline {
      font-size: 1rem;
      color: var(--fg-color);
      opacity: 0.8;
      margin: 0.25rem 0 0 0;
      font-style: italic;
    }

    .carousel-title a {
      color: inherit;
      text-decoration: none;
      transition: color 0.2s ease;
    }

    .carousel-title a:hover {
      color: var(--tertiary-color);
    }

    /* Mobile responsiveness */
    @media (max-width: 1040px) {
      .browse-container {
        flex-direction: column;
        height: auto;
        align-items: stretch; /* Stack layout for mobile */
      }

      .toc-panel {
        width: 100%;
        max-height: 300px;
        border-right: none;
        border-bottom: 2px solid var(--border-color);
        height: auto;
        overflow-y: auto; /* Ensure scrolling works on mobile */
      }

      .content-panel {
        padding: 1rem;
        padding-top: 0rem;
        height: auto;
        overflow-y: visible; /* Remove scroll on mobile since container is auto height */
      }

      .carousel-section {
        margin-bottom: 2rem;
        padding: 1rem;
      }

      .carousel-title {
        font-size: 1.6rem; /* Smaller on mobile but still larger than before */
      }

      .carousel-icon {
        width: 24px;
        height: 24px;
      }
    }

    /* Custom scrollbar styling */
    .toc-panel::-webkit-scrollbar,
    .content-panel::-webkit-scrollbar {
      width: 8px;
    }

    .toc-panel::-webkit-scrollbar-track,
    .content-panel::-webkit-scrollbar-track {
      background: var(--muted-color);
      border-radius: 4px;
    }

    .toc-panel::-webkit-scrollbar-thumb,
    .content-panel::-webkit-scrollbar-thumb {
      background: var(--primary-color);
      border-radius: 4px;
      border: 1px solid var(--bg-color);
    }

    .toc-panel::-webkit-scrollbar-thumb:hover,
    .content-panel::-webkit-scrollbar-thumb:hover {
      background: var(--tertiary-color);
    }

    /* Firefox scrollbar styling */
    .toc-panel,
    .content-panel {
      scrollbar-width: thin;
      scrollbar-color: var(--primary-color) var(--muted-color);
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--fg-color);
      font-family: var(--primary-font);
    }

    .error {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--fg-color);
      text-align: center;
      font-family: var(--primary-font);
    }
  `;

  render() {
    return this.familiesTask.render({
      pending: () => this.renderPending(),
      complete: (families) => this.renderComplete(families),
      error: (e) => this.renderError(e)
    });
  }

  private renderPending() {
    return html`<div class="loading">Loading monster families...</div>`;
  }

  private renderError(error: unknown) {
    return html`<div class="error">Error loading families: ${error instanceof Error ? error.message : String(error)}</div>`;
  }

  private renderComplete(families: MonsterFamily[]) {
    return html`
      <div class="browse-container">
        <!-- Table of Contents Panel -->
        <div class="toc-panel">
          <h2 class="toc-title">Monster Families</h2>
          <ul class="family-list">
            ${families.map(family => this.renderFamilyLink(family))}
          </ul>
        </div>

        <!-- Main Content Panel -->
        <div class="content-panel">
          ${this.activeCarousels.map((carousel, index) => html`
            <section class="carousel-section">
              <div class="carousel-header">
                <svg-icon class="carousel-icon" src="${carousel.familyIcon}"></svg-icon>
                <div class="carousel-title-section">
                  <h2 class="carousel-title">
                    <a href="${carousel.familyUrl}" title="View ${carousel.familyName} family page">
                      ${carousel.familyName}
                    </a>
                  </h2>
                  <p class="carousel-tagline">${carousel.familyTagLine}</p>
                </div>
              </div>
              <monster-carousel filter="family:${carousel.familyKey}"></monster-carousel>
            </section>
          `)}
        </div>
      </div>
    `;
  }

  private renderFamilyLink(family: MonsterFamily) {
    const isActive = this.activeCarousels.some(carousel => carousel.familyKey === family.key);

    return html`
      <li class="family-item">
        <a
          href="${family.url}"
          class="family-link ${isActive ? 'active' : ''}"
          @click=${(e: Event) => this.handleFamilyClick(e, family)}
          title="Show ${family.name} monsters">
          <svg-icon class="family-icon" src="${family.icon}"></svg-icon>
          <div class="family-info">
            <div class="family-name">${family.name}</div>
            <div class="family-monster-count">${family.monster_count} monsters</div>
          </div>
        </a>
      </li>
    `;
  }

  private handleFamilyClick(e: Event, family: MonsterFamily) {
    // Prevent navigation for intercept behavior
    e.preventDefault();

    // Replace the current selected carousel with this family
    const newCarousel: ActiveCarousel = {
      familyKey: family.key,
      familyName: family.name,
      familyUrl: family.url,
      familyTagLine: family.tag_line,
      familyIcon: family.icon
    };

    // Create new array with the replacement
    const newCarousels = [...this.activeCarousels];
    newCarousels[this.selectedFamilyIndex] = newCarousel;
    this.activeCarousels = newCarousels;

    // Move to the next carousel slot for the next click
    this.selectedFamilyIndex = (this.selectedFamilyIndex + 1) % this.activeCarousels.length;

    // Scroll to the replaced carousel
    this.scrollToCarousel(this.selectedFamilyIndex === 0 ? this.activeCarousels.length - 1 : this.selectedFamilyIndex - 1);
  }

  private scrollToCarousel(index: number) {
    // Wait for the next frame to ensure the DOM has updated
    requestAnimationFrame(() => {
      const carouselSections = this.shadowRoot?.querySelectorAll('.carousel-section');
      if (carouselSections && carouselSections[index]) {
        carouselSections[index].scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'monster-family-browse': MonsterFamilyBrowse;
  }
}