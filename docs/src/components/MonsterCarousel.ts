import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Task } from '@lit/task';
import Swiper from 'swiper';
import { Autoplay, Navigation, Keyboard, Parallax } from 'swiper/modules';
import { apiMonsterStore, MonsterTemplate } from '../data/api';
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
  transparent_edges: boolean;
  grayscale: boolean;
}

@customElement('monster-carousel')
export class MonsterCarousel extends LitElement {
  @property({ type: String })
  filter = '';

  @state()
  private swiperInstance: any = null;

  private templatesTask = new Task(this, {
    task: async ([filter], { signal }) => {
      return this.fetchMonsterTemplates(filter);
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
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      border-radius: var(--medium-margin);
    }

    /* Apply card background only when no mask class is present */
    .swiper-slide.card:not(.masked) {
      background: var(--card-bg-color);
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
      /* Always apply blending for better integration with background gradients */
      mix-blend-mode: multiply;
      opacity: 0.85;
    }

    /* For transparent edges, don't apply blend mode - just display image normally */
    .transparent-edges .card-image {
      mix-blend-mode: normal;
      opacity: 1;
    }

    .card-image.contain {
      object-fit: contain;
      object-position: center;
      padding: 0px !important;
    }

    /* Alternative blend modes for different effects */
    .card-image.overlay {
      mix-blend-mode: overlay;
      opacity: 0.8;
    }

    .card-image.soft-light {
      mix-blend-mode: soft-light;
      opacity: 0.9;
    }

    .card-image.darken {
      mix-blend-mode: darken;
      opacity: 0.8;
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

    /* Mask Styles - replicated from site.css for shadow DOM */
    .masked {
      mask-size: 100% 100%;
      mask-repeat: no-repeat;
      mask-position: center;
      -webkit-mask-size: 100% 100%;
      -webkit-mask-repeat: no-repeat;
      -webkit-mask-position: center;
    }

    .masked:not(.v1):not(.v2):not(.v3):not(.v4):not(.v5):not(.v6) {
      mask-image: url('/img/backgrounds/watercolor-mask.webp');
      -webkit-mask-image: url('/img/backgrounds/watercolor-mask.webp');
    }

    .masked.v1 {
      mask-image: url('/img/backgrounds/masks/mask-watercolor.webp');
      -webkit-mask-image: url('/img/backgrounds/masks/mask-watercolor.webp');
    }

    .masked.v2 {
      mask-image: url('/img/backgrounds/masks/mask-watercolor2.webp');
      -webkit-mask-image: url('/img/backgrounds/masks/mask-watercolor2.webp');
      mask-mode: luminance;
      -webkit-mask-mode: luminance;
    }

    .masked.v3 {
      mask-image: url('/img/backgrounds/masks/mask-paper.webp');
      -webkit-mask-image: url('/img/backgrounds/masks/mask-paper.webp');
      mask-mode: luminance;
      -webkit-mask-mode: luminance;
    }

    .masked.v4 {
      mask-image: url('/img/backgrounds/masks/mask-charcoal.webp');
      -webkit-mask-image: url('/img/backgrounds/masks/mask-charcoal.webp');
      mask-mode: luminance;
      -webkit-mask-mode: luminance;
    }

    .masked.v5 {
      mask-image: url('/img/backgrounds/masks/mask-charcoal2.webp');
      -webkit-mask-image: url('/img/backgrounds/masks/mask-charcoal2.webp');
      mask-mode: luminance;
      -webkit-mask-mode: luminance;
    }

    .masked.v6 {
      mask-image: url('/img/backgrounds/masks/mask-paper2.webp');
      -webkit-mask-image: url('/img/backgrounds/masks/mask-paper2.webp');
      mask-mode: luminance;
      -webkit-mask-mode: luminance;
    }

    /* Swiper navigation buttons */
    .swiper-button-next,
    .swiper-button-prev {
      color: var(--primary-color);
    }

    /* Additional template styling properties */
    .card.grayscale {
      filter: grayscale(100%);
    }

    .card.transparent-edges img {
      padding: 0;
    }
  `;

  private async fetchMonsterTemplates(filter: string): Promise<MonsterData[]> {
    console.log('fetchMonsterTemplates called with filter:', filter);
    if (!filter) {
      return [];
    }

    try {
      let templates: MonsterTemplate[];
      const limit = 12;

      if (filter === 'new') {
        templates = await apiMonsterStore.getNewMonsterTemplates(limit);
      } else if (filter.startsWith('family:')) {
        const familyKey = filter.substring(7);
        templates = await apiMonsterStore.getMonsterTemplatesByFamily(familyKey);
      } else if (filter.startsWith('query:')) {
        const query = filter.substring(6);
        templates = await apiMonsterStore.searchMonsterTemplates(query, limit);
      } else {
        throw new Error(`Invalid filter: ${filter}`);
      }

      console.log('Fetched templates:', templates);

      // Convert MonsterTemplate to MonsterData format for rendering
      const result = templates.map(template => this.convertTemplateToMonsterData(template));
      console.log('Final result:', result);
      return result;
    } catch (error) {
      console.error('Error in fetchMonsterTemplates:', error);
      throw error;
    }
  }

  private convertTemplateToMonsterData(template: MonsterTemplate): MonsterData {
    // Use the rich styling information provided by the template API
    let customStyle = '';

    if (template.background_color) {
      customStyle = `background-color: ${template.background_color};`;
    } else {
      // Choose gradients based on whether the template is grayscale
      let gradients: string[];

      if (template.grayscale) {
        // Light, muted gradients for grayscale templates
        gradients = [
          'background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);', // Light gray to lighter gray
          'background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);', // Very light blue to pale blue
          'background: linear-gradient(135deg, #f8f0ff 0%, #e7d9ff 100%);', // Very light purple to pale lavender
          'background: linear-gradient(135deg, #f0f8f0 0%, #d4e6d4 100%);', // Very light green to pale mint
          'background: linear-gradient(135deg, #fff8f0 0%, #f5e6d3 100%);', // Cream to light beige
          'background: linear-gradient(135deg, #f8f8f8 0%, #ececec 100%);', // Light gray to medium gray
        ];
      } else {
        // Original vibrant gradients for non-grayscale templates
        gradients = [
          'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);', // Blue to purple
          'background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);', // Pink to red
          'background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);', // Blue to cyan
          'background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);', // Green to teal
          'background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);', // Pink to yellow
          'background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);', // Cyan to pink
        ];
      }

      const randomGradient = gradients[Math.floor(Math.random() * gradients.length)];
      customStyle = randomGradient;
    }

    return {
      key: template.key,
      name: template.name,
      tagline: template.tagline,
      image: template.image,
      url: template.url,
      mask_css: template.mask_css,
      custom_style: customStyle,
      is_new: template.is_new,
      transparent_edges: template.transparent_edges,
      grayscale: template.grayscale
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
      taskStatus: this.templatesTask.status,
      hasSwiper: !!this.swiperInstance,
      swiperAvailable: typeof Swiper !== 'undefined'
    });

    // Clean up Swiper when filter changes
    if (changedProperties.has('filter') && this.swiperInstance) {
      this.swiperInstance.destroy(true, true);
      this.swiperInstance = null;
    }

    // Only reinitialize Swiper when templates data is loaded and rendered
    // TaskStatus.COMPLETE = 2 in @lit/task
    if (this.templatesTask.status === 2 && !this.swiperInstance) {
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
    return this.templatesTask.render({
      pending: () => {
        console.log('Task pending state');
        return html`<div class="loading">Loading monster templates...</div>`;
      },
      complete: (templates) => {
        console.log('Task complete state, templates:', templates);
        if (templates.length === 0) {
          return html`<div class="no-monsters">No monster templates found for this filter.</div>`;
        }

        // Always render swiper container structure, then initialize Swiper on it
        const containerClass = 'swiper-container';

        return html`
          <div class="${containerClass} preload">
            <div class="swiper-wrapper">
              ${templates.map(template => this.renderMonsterCard(template))}
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
        return html`<div class="error">Error loading monster templates: ${error instanceof Error ? error.message : 'Unknown error'}</div>`;
      }
    });
  }

  private renderMonsterCard(template: MonsterData) {
    const cardClasses = [
      'swiper-slide',
      'card',
      'tall',
      template.mask_css,
      template.is_new ? 'new' : '',
      template.grayscale ? 'grayscale' : '',
      template.transparent_edges ? 'transparent-edges' : ''
    ].filter(Boolean).join(' ');

    return html`
      <div
        class="${cardClasses}"
        data-url="${template.url}"
        style="${template.custom_style}"
        @click="${() => this.handleCardClick(template.url)}"
      >
        <img
          class="card-image contain"
          src="${template.image}"
          alt="${template.name}"
          loading="lazy"
          @error="${(e: Event) => this.handleImageError(e, template)}"
        />
        <div class="card-content">
          <div class="masked-label">
            <h3 class="card-title">
              <a href="${template.url}">${template.name}</a>
            </h3>
            <p class="card-tagline">${template.tagline}</p>
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