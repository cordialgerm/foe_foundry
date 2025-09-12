import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { Task } from '@lit/task';
import { apiMonsterStore, MonsterFamily } from '../data/api.js';
import './MonsterCarousel.js';
import './SvgIcon.js';

@customElement('monster-family-browse')
export class MonsterFamilyBrowse extends LitElement {
  @state() private shuffledFamilies: MonsterFamily[] = [];
  @state() private alphabeticalFamilies: MonsterFamily[] = [];

  private familiesTask = new Task(this, async () => {
    const families = await apiMonsterStore.getAllFamilies();

    // Create shuffled version for main content display
    this.shuffledFamilies = [...families].sort(() => 0.5 - Math.random());

    // Create alphabetical version for left navigation
    this.alphabeticalFamilies = [...families].sort((a, b) => a.name.localeCompare(b.name));

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
      height: 100%; /* Set full height for proper scrolling */
      min-height: 600px;
      align-items: flex-start; /* Top align both panels */
    }

    /* Table of Contents Panel */
    .toc-panel {
      width: 280px;
      background: var(--bg-color);
      border-right: 2px solid var(--border-color);
      overflow-y: auto;
      padding: 1rem; /* Reduced padding for better mobile experience */
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
      padding: 1rem; /* Reduced padding for better mobile experience */
      padding-top: 0rem;
      height: auto; /* Allow natural height for better scrolling */
      position: relative; /* For scroll indicator positioning */
    }

    /* Scroll indicator for mobile to show more content is available */
    .content-panel::after {
      content: "";
      position: sticky;
      bottom: 0;
      left: 0;
      right: 0;
      height: 20px;
      background: linear-gradient(transparent, rgba(255, 107, 53, 0.1));
      pointer-events: none;
      z-index: 2;
    }

    @media (max-width: 1040px) {
      .content-panel::after {
        height: 30px;
        background: linear-gradient(transparent, rgba(255, 107, 53, 0.2));
      }
    }

    .carousel-section {
      margin-bottom: 1.5rem;
      border-radius: 8px;
      background: var(--bg-color); /* Removed black background */
      padding: 1rem; /* Reduced padding for better mobile experience */
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
        height: 100vh; /* Set full viewport height for proper mobile scrolling */
        align-items: stretch; /* Stack layout for mobile */
      }

      .toc-panel {
        display: none; /* Hide the left navigation panel on mobile */
      }

      .content-panel {
        padding: 0.75rem; /* Further reduced padding for smaller screens */
        padding-top: 0rem;
        height: 100%; /* Take full available height */
        overflow-y: auto; /* Enable vertical scrolling to see all families */
      }

      .carousel-section {
        margin-bottom: 2rem;
        padding: 0.75rem; /* Reduced padding for smaller screens */
      }

      .carousel-title {
        font-size: 1.6rem; /* Smaller on mobile but still larger than before */
      }

      .carousel-icon {
        width: 24px;
        height: 24px;
      }
    }

    /* Additional mobile improvements for smaller screens */
    @media (max-width: 768px) {
      .toc-panel {
        display: none; /* Ensure toc-panel is hidden on smaller screens too */
      }

      .content-panel {
        padding: 0.625rem; /* Even less padding for smallest screens */
        padding-top: 0;
      }

      .carousel-section {
        padding: 0.625rem; /* Minimal padding for smallest screens */
        margin-bottom: 1.5rem;
      }

      .carousel-title {
        font-size: 1.5rem;
      }

      .carousel-tagline {
        font-size: 0.95rem;
      }
    }

    @media (max-width: 480px) {
      .toc-panel {
        display: none; /* Ensure toc-panel is hidden on smallest screens too */
      }

      .content-panel {
        padding: 0.5rem; /* Minimal padding for very small screens */
        padding-top: 0;
      }

      .carousel-section {
        padding: 0.5rem; /* Minimal padding for very small screens */
        margin-bottom: 1.5rem;
      }

      .carousel-title {
        font-size: 1.375rem;
      }

      .carousel-icon {
        width: 22px;
        height: 22px;
      }

      .carousel-tagline {
        font-size: 0.9rem;
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

    /* Mobile scrollbar enhancements for better visibility */
    @media (max-width: 1040px) {
      .content-panel::-webkit-scrollbar {
        width: 12px; /* Wider scrollbar on mobile for better visibility */
      }

      .content-panel::-webkit-scrollbar-track {
        background: rgba(255, 107, 53, 0.1); /* More visible track on mobile */
        border-radius: 6px;
      }

      .content-panel::-webkit-scrollbar-thumb {
        background: var(--tertiary-color); /* More prominent color */
        border-radius: 6px;
        border: 2px solid var(--bg-color);
        box-shadow: 0 0 0 1px rgba(255, 107, 53, 0.3); /* Add glow for visibility */
      }

      .content-panel::-webkit-scrollbar-thumb:active {
        background: var(--primary-color);
      }

      /* Enhanced Firefox scrollbar on mobile */
      .content-panel {
        scrollbar-width: auto; /* Use default width for better visibility */
        scrollbar-color: var(--tertiary-color) rgba(255, 107, 53, 0.1);
      }

      /* Force scrollbar to always be visible on mobile webkit browsers */
      .content-panel {
        overflow-y: scroll; /* Force scrollbar to be visible */
        -webkit-overflow-scrolling: touch; /* Smooth scrolling on iOS */
      }
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
            ${this.alphabeticalFamilies.map(family => this.renderFamilyLink(family))}
          </ul>
        </div>

        <!-- Main Content Panel -->
        <div class="content-panel">
          ${this.shuffledFamilies.map((family, index) => html`
            <section class="carousel-section" id="family-${family.key}">
              <div class="carousel-header">
                <svg-icon class="carousel-icon" src="${family.icon}"></svg-icon>
                <div class="carousel-title-section">
                  <h2 class="carousel-title">
                    <a href="${family.url}" title="View ${family.name} family page">
                      ${family.name}
                    </a>
                  </h2>
                  <p class="carousel-tagline">${family.tag_line}</p>
                </div>
              </div>
              <monster-carousel filter="family:${family.key}"></monster-carousel>
            </section>
          `)}
        </div>
      </div>
    `;
  }

  private renderFamilyLink(family: MonsterFamily) {
    return html`
      <li class="family-item">
        <a
          href="${family.url}"
          class="family-link"
          @click=${(e: Event) => this.handleFamilyClick(e, family)}
          title="View ${family.name} family page">
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
    // Prevent navigation for anchor click behavior
    e.preventDefault();

    // Scroll to the family section
    this.scrollToFamily(family.key);
  }

  private scrollToFamily(familyKey: string) {
    // Wait for the next frame to ensure the DOM is ready
    requestAnimationFrame(() => {
      const familySection = this.shadowRoot?.querySelector(`#family-${familyKey}`);
      if (familySection) {
        familySection.scrollIntoView({
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