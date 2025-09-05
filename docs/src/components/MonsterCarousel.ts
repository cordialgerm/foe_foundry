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

    .swiper-container {
      width: 100%;
      height: 400px;
      overflow: hidden;
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

    const monsters: MonsterInfo[] = await response.json();
    
    // Convert MonsterInfo to MonsterData format for rendering
    return monsters.map(monster => this.convertToMonsterData(monster));
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
    if (changedProperties.has('filter') && this.swiperInstance) {
      // Reinitialize swiper when filter changes
      this.swiperInstance.destroy(true, true);
      this.swiperInstance = null;
      this.requestUpdate();
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    if (this.swiperInstance) {
      this.swiperInstance.destroy(true, true);
    }
  }

  render() {
    return this.monstersTask.render({
      pending: () => html`<div class="loading">Loading monsters...</div>`,
      complete: (monsters) => html`
        <div class="swiper-container preload">
          <div class="swiper-wrapper">
            ${monsters.map(monster => html`
              <div 
                class="swiper-slide card tall ${monster.mask_css} ${monster.is_new ? 'new' : ''}"
                data-url="${monster.url}"
                style="${monster.custom_style}"
              >
                <img 
                  class="card-image contain ${monster.custom_style ? '' : 'blend'}"
                  src="${monster.image}"
                  alt="${monster.name}"
                  loading="lazy"
                  @error="${() => this.handleImageError(monster)}"
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
        </div>
      `,
      error: (error) => html`<div class="error">Error loading monsters: ${error instanceof Error ? error.message : 'Unknown error'}</div>`
    });
  }

  private handleImageError(monster: MonsterData) {
    // Fallback to a default image if the monster image fails to load
    const imgElement = this.shadowRoot?.querySelector(`img[alt="${monster.name}"]`) as HTMLImageElement;
    if (imgElement) {
      imgElement.src = '/img/monsters/default.webp';
    }
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