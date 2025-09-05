import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Task } from '@lit/task';

interface MonsterInfo {
  key: string;
  name: string;
  cr: number;
  template: string;
}

interface MonsterData {
  key: string;
  name: string;
  tagline: string;
  image: string;
  url: string;
  mask_css: string;
  custom_style: string;
  is_new: boolean;
}

@customElement('monster-carousel')
export class MonsterCarousel extends LitElement {
  @property({ type: String })
  filter = '';

  @state()
  private swiperInstance: any = null;

  private monstersTask = new Task(this, {
    task: async ([filter], { signal }) => {
      return this.fetchMonsters(filter);
    },
    args: () => [this.filter]
  });

  static styles = css`
    :host {
      display: block;
      width: 100%;
    }

    .loading {
      text-align: center;
      padding: 2rem;
      color: #666;
    }

    .error {
      text-align: center;
      padding: 2rem;
      color: #dc3545;
      background-color: rgba(220, 53, 69, 0.1);
      border: 1px solid rgba(220, 53, 69, 0.2);
      border-radius: 4px;
    }

    .swiper-container {
      width: 100%;
      height: 400px;
      overflow: hidden;
    }

    /* Fallback styles when Swiper is not available */
    .carousel-fallback {
      display: flex;
      gap: 1rem;
      overflow-x: auto;
      padding: 1rem 0;
      scroll-behavior: smooth;
      height: 400px;
    }

    .carousel-fallback::-webkit-scrollbar {
      height: 8px;
    }

    .carousel-fallback::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
    }

    .carousel-fallback::-webkit-scrollbar-thumb {
      background: rgba(255, 107, 53, 0.6);
      border-radius: 4px;
    }

    .carousel-fallback::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 107, 53, 0.8);
    }

    .carousel-fallback .swiper-slide {
      flex: 0 0 auto;
      width: 280px;
    }

    @media (max-width: 576px) {
      .carousel-fallback .swiper-slide {
        width: 240px;
      }
    }

    .no-swiper-message {
      text-align: center;
      padding: 0.5rem;
      background: rgba(255, 193, 7, 0.1);
      border: 1px solid rgba(255, 193, 7, 0.3);
      border-radius: 4px;
      margin-bottom: 1rem;
      color: #856404;
      font-size: 0.85rem;
    }

    .swiper-slide {
      position: relative;
      border-radius: var(--medium-margin);
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.3s ease;
    }

    .swiper-slide:hover {
      transform: scale(1.02);
    }

    .card {
      position: relative;
      height: 100%;
      border-radius: var(--medium-margin);
      overflow: hidden;
      background: var(--bs-dark);
      border: 1px solid var(--tertiary-color);
    }

    .card.tall {
      min-height: 300px;
    }

    .card-image {
      width: 100%;
      height: 60%;
      object-fit: cover;
      object-position: center;
    }

    .card-image.contain {
      object-fit: contain;
    }

    .card-image.blend {
      mix-blend-mode: multiply;
    }

    .card-content {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
      padding: 1rem;
    }

    .masked-label {
      color: white;
    }

    .card-title {
      font-size: 1.2rem;
      font-weight: bold;
      margin: 0 0 0.5rem 0;
    }

    .card-title a {
      color: inherit;
      text-decoration: none;
    }

    .card-title a:hover {
      color: var(--primary-color);
    }

    .card-tagline {
      font-size: 0.9rem;
      margin: 0;
      opacity: 0.9;
    }

    .new-badge {
      position: absolute;
      top: 8px;
      right: 8px;
      background: var(--accent-color);
      color: white;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 0.75rem;
      font-weight: bold;
    }

    .loading {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--bs-light);
    }

    .error {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 200px;
      color: var(--danger-color);
    }

    /* Swiper navigation buttons */
    :host(.swiper-button-next),
    :host(.swiper-button-prev) {
      color: var(--primary-color);
    }
  `;

  private async fetchMonsters(filter: string): Promise<MonsterData[]> {
    if (!filter) {
      return [];
    }

    let apiUrl = '';
    let limit = 12;

    if (filter === 'new') {
      apiUrl = `/api/v1/monsters/new?limit=${limit}`;
    } else if (filter.startsWith('family:')) {
      const familyKey = filter.substring(7);
      apiUrl = `/api/v1/monsters/family/${familyKey}`;
    } else if (filter.startsWith('query:')) {
      const query = filter.substring(6);
      apiUrl = `/api/v1/search/monsters?query=${encodeURIComponent(query)}&limit=${limit}`;
    } else {
      throw new Error(`Invalid filter: ${filter}`);
    }

    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch monsters: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Handle different response formats from different endpoints
    let monsters: MonsterInfo[];
    if (filter === 'new') {
      // The /new endpoint returns a different format: [{monster_key, template_key}]
      monsters = data.map((item: any) => ({
        key: item.monster_key,
        name: this.formatMonsterName(item.monster_key),
        cr: 1, // Default CR since not provided
        template: item.template_key
      }));
    } else {
      // Other endpoints return the expected format: [{key, name, cr, template}]
      monsters = data;
    }
    
    // Convert MonsterInfo to MonsterData format for rendering
    return monsters.map(monster => this.convertToMonsterData(monster));
  }

  private formatMonsterName(key: string): string {
    // Convert monster key to a readable name (e.g., "dire-wolf" -> "Dire Wolf")
    return key.split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  private convertToMonsterData(monster: MonsterInfo): MonsterData {
    // Generate placeholder data similar to homepage monsters
    const maskClasses = ['mask-1', 'mask-2', 'mask-3', 'mask-4', 'mask-5'];
    const randomMask = maskClasses[Math.floor(Math.random() * maskClasses.length)];
    
    return {
      key: monster.key,
      name: monster.name,
      tagline: `CR ${monster.cr} ${monster.template.replace(/-/g, ' ')}`,
      image: `/img/monsters/${monster.template}.webp`,
      url: `/monsters/${monster.template}/`,
      mask_css: randomMask,
      custom_style: '',
      is_new: false // We'll implement this logic later if needed
    };
  }

  private handleCardClick(url: string) {
    if (url) {
      window.location.href = url;
    }
  }

  private handleImageError(event: Event, monster: MonsterData) {
    const img = event.target as HTMLImageElement;
    console.warn(`Failed to load image for ${monster.name}: ${img.src}`);
    // Set fallback image or hide the image element
    img.style.display = 'none';
  }

  private initializeSwiper() {
    if (this.swiperInstance || !window.Swiper) {
      return;
    }

    const swiperContainer = this.shadowRoot?.querySelector('.swiper-container');
    if (!swiperContainer) {
      return;
    }

    // Breakpoints similar to homepage
    const breakpoints = {
      320: {
        slidesPerView: 1,
        spaceBetween: 16
      },
      576: {
        slidesPerView: 2,
        spaceBetween: 16
      },
      768: {
        slidesPerView: 3,
        spaceBetween: 16
      },
      1200: {
        slidesPerView: 3,
        spaceBetween: 32
      },
      1400: {
        slidesPerView: 3,
        spaceBetween: 48
      },
    };

    this.swiperInstance = new window.Swiper(swiperContainer, {
      autoplay: {
        delay: 6000,
        disableOnInteraction: true
      },
      breakpoints: breakpoints,
      initialSlide: 1,
      centeredSlides: true,
      createElements: true,
      grabCursor: true,
      keyboard: true,
      navigation: true,
      parallax: true,
      simulateTouch: true,
      on: {
        init: function (this: any) {
          this.el.classList.remove('preload');
        }
      }
    });

    // Handle clicks
    this.swiperInstance.on('click', (swiper: any, event: Event) => {
      const slideEl = (event.target as HTMLElement).closest('.swiper-slide');
      if (slideEl) {
        const url = slideEl.getAttribute('data-url');
        if (url) {
          window.location.href = url;
        }
      }
    });
  }

  firstUpdated() {
    // Wait for Swiper to be available, with timeout
    let attempts = 0;
    const maxAttempts = 50; // 5 seconds max
    const checkSwiper = () => {
      attempts++;
      if (window.Swiper) {
        this.initializeSwiper();
      } else if (attempts < maxAttempts) {
        setTimeout(checkSwiper, 100);
      } else {
        console.warn('Swiper.js not loaded after 5 seconds');
      }
    };
    checkSwiper();
  }

  updated(changedProperties: any) {
    super.updated(changedProperties);
    
    // Clean up Swiper when filter changes
    if (changedProperties.has('filter') && this.swiperInstance) {
      this.swiperInstance.destroy(true, true);
      this.swiperInstance = null;
    }
    
    // Only reinitialize Swiper when monsters data is loaded and rendered
    if (this.monstersTask.status === 2 && !this.swiperInstance) { // 2 = COMPLETE status
      // Wait for the next frame to ensure DOM is fully rendered
      requestAnimationFrame(() => {
        this.initializeSwiper();
      });
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.swiperInstance) {
      this.swiperInstance.destroy(true, true);
    }
  }

  render() {
    const hasSwiper = !!window.Swiper;
    
    return this.monstersTask.render({
      pending: () => html`<div class="loading">Loading monsters...</div>`,
      complete: (monsters) => {
        if (monsters.length === 0) {
          return html`<div class="no-monsters">No monsters found for this filter.</div>`;
        }

        return html`
          ${!hasSwiper ? html`
            <div class="no-swiper-message">
              ⚠️ Swiper library not available - showing scrollable fallback layout
            </div>
          ` : ''}
          <div class="${hasSwiper ? 'swiper-container preload' : 'carousel-fallback'}">
            ${monsters.map(monster => html`
              <div 
                class="swiper-slide card tall ${monster.mask_css} ${monster.is_new ? 'new' : ''}"
                data-url="${monster.url}"
                style="${monster.custom_style}"
                @click="${() => this.handleCardClick(monster.url)}"
              >
                <img 
                  class="card-image contain ${monster.custom_style ? '' : 'blend'}"
                  src="${monster.image}"
                  alt="${monster.name}"
                  loading="lazy"
                  @error="${(e: Event) => this.handleImageError(e, monster)}"
                />
                <div class="card-content">
                  <div class="masked-label">
                    <h3 class="card-title">
                      <a href="${monster.url}">${monster.name}</a>
                    </h3>
                    <p class="card-tagline">${monster.tagline}</p>
                  </div>
                </div>
                ${monster.is_new ? html`<div class="new-badge">NEW</div>` : ''}
              </div>
            `)}
          </div>
        `;
      },
      error: (error) => html`<div class="error">Error loading monsters: ${error instanceof Error ? error.message : 'Unknown error'}</div>`
    });
  }

}

declare global {
  interface Window {
    Swiper: any;
  }
  interface HTMLElementTagNameMap {
    'monster-carousel': MonsterCarousel;
  }
}