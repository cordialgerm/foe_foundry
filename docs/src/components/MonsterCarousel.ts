import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Task } from '@lit/task';
import Swiper from 'swiper';
import { Autoplay, Navigation, Keyboard, Parallax } from 'swiper/modules';
import './swiper.css';

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
      color: var(--bs-light);
    }

    .error {
      text-align: center;
      padding: 2rem;
      color: var(--danger-color);
      background-color: rgba(220, 53, 69, 0.1);
      border: 1px solid rgba(220, 53, 69, 0.2);
      border-radius: 4px;
    }

    .no-monsters {
      text-align: center;
      padding: 2rem;
      color: var(--tertiary-color);
    }

    /* Swiper container styles similar to homepage */
    .swiper-container {
      position: relative;
      max-width: 100%;
      overflow: hidden;
      min-height: 300px;
    }

    .swiper-wrapper {
      display: flex;
      flex-direction: row;
      align-items: flex-start;
    }

    .swiper-container.preload .swiper-wrapper {
      display: flex;
      flex-direction: row;
      flex-wrap: nowrap;
      overflow-x: auto;
      gap: 1rem;
    }

    /* Fallback styles when Swiper is not available */
    .carousel-fallback {
      position: relative;
      max-width: 100%;
      overflow: hidden;
      min-height: 300px;
      display: flex;
      flex-direction: row;
      flex-wrap: nowrap;
      overflow-x: auto;
      gap: 1rem;
      padding: 1rem 0;
      scroll-behavior: smooth;
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

    /* Card styles matching homepage */
    .swiper-slide {
      position: relative;
      cursor: pointer;
      transition: transform 0.3s ease;
      border-radius: var(--medium-margin);
      overflow: hidden;
    }

    .swiper-slide:hover {
      transform: scale(1.02);
    }

    .swiper-slide[data-url] {
      cursor: pointer;
    }

    .swiper-slide.card {
      padding: 1.25em;
      aspect-ratio: 4/3;
      width: 225px;
      min-width: 225px;
      flex-shrink: 0;
      overflow: hidden;
      font-size: var(--primary-font-size);
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      justify-content: center;
      background: var(--card-bg-color);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      border-radius: var(--medium-margin);
    }

    .swiper-slide.card.tall {
      height: 300px;
      width: 225px;
      min-width: 225px;
      min-height: 300px;
    }

    /* Fallback layout card sizing */
    .carousel-fallback .swiper-slide {
      flex: 0 0 auto;
      width: 225px;
    }

    @media (max-width: 576px) {
      .carousel-fallback .swiper-slide {
        width: 200px;
      }

      .swiper-slide.card.tall {
        width: 200px;
      }
    }

    /* NEW badge matching homepage */
    .swiper-slide.card.new::before {
      content: '';
      position: absolute;
      top: 0.5rem;
      left: 0.5rem;
      width: 80px;
      height: 80px;
      background: url('/img/misc/new-stamp.png') no-repeat center/contain;
      transform: rotate(-15deg);
      z-index: 2;
      pointer-events: none;
    }

    /* Card image styles matching homepage */
    .card-image {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 0;
      object-fit: contain;
      object-position: center;
      padding: 20px;
    }

    .card-image.contain {
      object-fit: contain;
      object-position: center;
      padding: 20px;
    }

    .card-image.blend {
      mix-blend-mode: multiply;
    }

    /* Card content styles matching homepage */
    .card-content {
      position: relative;
      z-index: 1;
      text-align: center;
      padding: 1rem;
      height: 100%;
      display: flex;
      flex-direction: column;
      justify-content: center;
      pointer-events: none;
      isolation: isolate;
      text-align: center;
    }

    /* Masked label matching homepage */
    .masked-label {
      background-color: rgba(80, 80, 80, 0.60);
      display: inline-block;
      padding: 0.5rem;
      mask-image: url('/img/backgrounds/watercolor-mask2.webp');
      -webkit-mask-image: url('/img/backgrounds/watercolor-mask2.webp');
      mask-size: 100% 100%;
      -webkit-mask-size: 100% 100%;
      mask-repeat: no-repeat;
      -webkit-mask-repeat: no-repeat;
      mask-position: center;
      -webkit-mask-position: center;
    }

    /* Card title styles matching homepage */
    .card-title,
    .card-title a {
      font-size: 1.2rem;
      color: var(--card-title-color);
      margin: 0 0 0.5rem 0;
    }

    .masked-label .card-title,
    .card-title.highlight,
    .card-title.highlight a {
      font-size: 1.3rem;
      font-weight: bold;
      color: var(--card-title-highlight-color);
      text-shadow: 0 3px 4px rgba(0, 0, 0, 1);
    }

    @media (max-width: 900px) {
      .card-title {
        font-size: 1.0rem;
      }
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
      color: var(--card-title-highlight-color);
      margin-top: 0.25rem;
    }

    .masked-label .card-tagline {
      color: var(--card-title-highlight-color);
    }

    /* Mask classes from homepage CSS */
    .mask-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .mask-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .mask-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .mask-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .mask-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

    /* Swiper navigation buttons */
    .swiper-button-next,
    .swiper-button-prev {
      color: var(--primary-color);
    }
  `;

  private async fetchMonsters(filter: string): Promise<MonsterData[]> {
    console.log('fetchMonsters called with filter:', filter);
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

    console.log('Fetching from URL:', apiUrl);

    try {
      const response = await fetch(apiUrl);
      console.log('Response status:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`Failed to fetch monsters: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

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

      console.log('Converted monsters:', monsters);

      // Convert MonsterInfo to MonsterData format for rendering
      const result = monsters.map(monster => this.convertToMonsterData(monster));
      console.log('Final result:', result);
      return result;
    } catch (error) {
      console.error('Error in fetchMonsters:', error);
      throw error;
    }
  }

  private formatMonsterName(key: string): string {
    // Convert monster key to a readable name (e.g., "dire-wolf" -> "Dire Wolf")
    return key.split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  private convertToMonsterData(monster: MonsterInfo): MonsterData {
    // Generate mask and styling similar to homepage
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
      is_new: false // TODO: Could be enhanced to check actual creation dates
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
    console.log('initializeSwiper called');
    if (this.swiperInstance) {
      console.log('Swiper already exists, returning');
      return;
    }

    const swiperContainer = this.shadowRoot?.querySelector('.swiper-container');
    console.log('Swiper container found:', !!swiperContainer);
    if (!swiperContainer) {
      console.warn('No swiper container found in shadow root');
      return;
    }

    // Check if Swiper is available
    if (typeof Swiper === 'undefined') {
      console.error('Swiper is not available. Make sure it is imported correctly.');
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

    try {
      console.log('Creating Swiper instance...');
      console.log('Available Swiper modules:', { Autoplay, Navigation, Keyboard, Parallax });

      // Force wrapper to be horizontal before initializing Swiper
      const wrapper = swiperContainer.querySelector('.swiper-wrapper') as HTMLElement;
      if (wrapper) {
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'row';
        wrapper.style.alignItems = 'flex-start';
      }

      // Use the simplest possible Swiper configuration that should work
      this.swiperInstance = new Swiper(swiperContainer as HTMLElement, {
        modules: [Autoplay, Navigation, Keyboard, Parallax],
        slidesPerView: 3,
        spaceBetween: 16,
        centeredSlides: false,
        grabCursor: true,
        direction: 'horizontal', // Explicitly set horizontal direction
        keyboard: {
          enabled: true,
        },
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev',
        },
        autoplay: {
          delay: 6000,
          disableOnInteraction: true,
        },
        breakpoints: breakpoints,
        on: {
          init: function (this: any) {
            console.log('Swiper init callback called');
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

      console.log('Swiper initialized successfully');
    } catch (error) {
      console.warn('Failed to initialize Swiper:', error);
    }
  }

  updated(changedProperties: any) {
    super.updated(changedProperties);

    // Debug logging
    console.log('MonsterCarousel updated:', {
      filter: this.filter,
      taskStatus: this.monstersTask.status,
      hasSwiper: !!this.swiperInstance,
      swiperAvailable: typeof Swiper !== 'undefined'
    });

    // Clean up Swiper when filter changes
    if (changedProperties.has('filter') && this.swiperInstance) {
      this.swiperInstance.destroy(true, true);
      this.swiperInstance = null;
    }

    // Only reinitialize Swiper when monsters data is loaded and rendered
    // TaskStatus.COMPLETE = 2 in @lit/task
    if (this.monstersTask.status === 2 && !this.swiperInstance) {
      console.log('Attempting to initialize Swiper...');
      // Wait for the next frame to ensure DOM is fully rendered
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          // Double RAF to ensure DOM is ready
          this.initializeSwiper();
        });
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
    console.log('MonsterCarousel render() called, filter:', this.filter);
    return this.monstersTask.render({
      pending: () => {
        console.log('Task pending state');
        return html`<div class="loading">Loading monsters...</div>`;
      },
      complete: (monsters) => {
        console.log('Task complete state, monsters:', monsters);
        if (monsters.length === 0) {
          return html`<div class="no-monsters">No monsters found for this filter.</div>`;
        }

        // Always render swiper container structure, then initialize Swiper on it
        const containerClass = 'swiper-container';

        return html`
          <div class="${containerClass} preload">
            <div class="swiper-wrapper">
              ${monsters.map(monster => this.renderMonsterCard(monster))}
            </div>
            <div class="swiper-button-next"></div>
            <div class="swiper-button-prev"></div>
          </div>
          <style>
            /* Inline styles to ensure horizontal layout */
            .swiper-wrapper {
              display: flex !important;
              flex-direction: row !important;
              align-items: flex-start !important;
            }
            .swiper-slide {
              flex-shrink: 0 !important;
              width: 225px !important;
              min-width: 225px !important;
            }
          </style>
        `;
      },
      error: (error) => {
        console.error('Task error state:', error);
        return html`<div class="error">Error loading monsters: ${error instanceof Error ? error.message : 'Unknown error'}</div>`;
      }
    });
  }

  private renderMonsterCard(monster: MonsterData) {
    return html`
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
      </div>
    `;
  }

}

declare global {
  interface HTMLElementTagNameMap {
    'monster-carousel': MonsterCarousel;
  }
}