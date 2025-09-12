import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { Task } from '@lit/task';
import Swiper from 'swiper';
import { Autoplay, Navigation, Keyboard, Parallax } from 'swiper/modules';
import { apiMonsterStore, MonsterTemplate } from '../data/api';
import { trackMonsterClick } from '../utils/analytics.js';
import './swiper.css';

interface CardData {
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
      min-height: 300px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-sizing: border-box;
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
      position: relative !important;
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
  max-width: 225px;
  height: 300px;
  min-height: 300px;
  max-height: 300px;
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
  max-width: 225px;
  min-height: 300px;
  max-height: 300px;
    }

    /* Fallback layout card sizing */
    .carousel-fallback .swiper-slide {
  flex: 0 0 auto;
  width: 225px;
  min-width: 225px;
  max-width: 225px;
  height: 300px;
  min-height: 300px;
  max-height: 300px;
    }

    @media (max-width: 576px) {
      .carousel-fallback .swiper-slide {
        width: 200px;
        min-width: 200px;
        max-width: 200px;
        height: 260px;
        min-height: 260px;
        max-height: 260px;
      }

      .swiper-slide.card,
      .swiper-slide.card.tall {
        width: 200px;
        min-width: 200px;
        max-width: 200px;
        height: 260px;
        min-height: 260px;
        max-height: 260px;
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
      background: linear-gradient(135deg, rgba(40,40,40,0.60) 60%, rgba(80,80,80,0.40) 100%);
      box-shadow: 0 2px 12px 2px rgba(0,0,0,0.18);
      border-radius: 0.75em;
      display: inline-block;
      padding: 0.5rem 0.85rem;
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

    /* Swiper navigation buttons matching homepage */
    .swiper-button-next,
    .swiper-button-prev {
      position: absolute !important;
      top: 50% !important;
      width: 60px !important;
      height: 60px !important;
      margin-top: -30px !important;
      z-index: 10 !important;
      cursor: pointer !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      color: var(--primary-color) !important;
      background: rgba(0, 0, 0, 0.3) !important;
      border: 2px solid var(--primary-color) !important;
      border-radius: 50% !important;
      transform: translateY(-50%) !important;
      transition: all 0.3s ease !important;
    }

    .swiper-button-prev {
      left: 10px !important;
      right: auto !important;
    }

    .swiper-button-next {
      right: 10px !important;
      left: auto !important;
    }

    .swiper-button-next:after {
      content: '>' !important;
      font-size: 28px !important;
      font-weight: bold !important;
      font-family: inherit !important;
    }

    .swiper-button-prev:after {
      content: '<' !important;
      font-size: 28px !important;
      font-weight: bold !important;
      font-family: inherit !important;
    }

    .swiper-button-next:hover,
    .swiper-button-prev:hover {
      color: rgba(255, 255, 255, 1) !important;
      background: rgba(255, 107, 53, 0.8) !important;
      border-color: rgba(255, 107, 53, 1) !important;
      transform: translateY(-50%) scale(1.1) !important;
    }

    .swiper-button-disabled {
      opacity: 0.3 !important;
    }

    /* Additional template styling properties */
    .card.grayscale {
      filter: grayscale(100%);
    }

    .card.transparent-edges img {
      padding: 0;
    }
  `;

  private async fetchMonsterTemplates(filter: string): Promise<CardData[]> {
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

      // Convert MonsterTemplate to MonsterData format for rendering
      const result = templates.map(template => this.convertTemplateToMonsterData(template));
      return result;
    } catch (error) {
      console.error('Error in fetchMonsterTemplates:', error);
      throw error;
    }
  }

  private convertTemplateToMonsterData(template: MonsterTemplate): CardData {
    // Use the rich styling information provided by the template API
    let customStyle = '';

    if (template.background_color) {
      customStyle = `background-color: ${template.background_color};`;
    } else {
      // Choose gradients based on whether the template is grayscale
      let gradients: string[];

      if (template.grayscale) {
        // Very pale, subtle gradients for grayscale templates - won't interfere with black and white images
        gradients = [
          'background: linear-gradient(135deg, #fdfefe 0%, #f8f9fa 100%);', // Almost white to very light gray
          'background: linear-gradient(135deg, #f8fcff 0%, #f0f7ff 100%);', // Pale blue tint to slightly deeper pale blue
          'background: linear-gradient(135deg, #fefaff 0%, #f5f0ff 100%);', // Pale lavender tint to light lavender
          'background: linear-gradient(135deg, #f8fff8 0%, #f0f8f0 100%);', // Pale mint tint to light mint
          'background: linear-gradient(135deg, #fffcf8 0%, #fcf5e8 100%);', // Pale cream to light cream
          'background: linear-gradient(135deg, #fffef8 0%, #faf8f0 100%);', // Pale warm white to light warm
          'background: linear-gradient(135deg, #f8f8ff 0%, #f0f0f8 100%);', // Pale cool white to light cool
          'background: linear-gradient(135deg, #fff8fa 0%, #f8f0f3 100%);', // Pale rose tint to light rose
          'background: linear-gradient(135deg, #f8fff8 0%, #f0f8f8 100%);', // Pale seafoam to light seafoam
          // Radial gradients for soft, organic feel
          'background: radial-gradient(ellipse at center, #fdfefe 0%, #f5f7f8 70%);',
          'background: radial-gradient(circle at top left, #fff8fa 0%, #f3f0f2 60%);',
          'background: radial-gradient(ellipse at bottom right, #f8fcff 0%, #f0f6fa 80%);',
          // Conic gradients for subtle texture
          'background: conic-gradient(from 45deg at 50% 50%, #fdfefe 0deg, #f8f9fa 90deg, #f5f7f8 180deg, #f2f4f5 270deg, #fdfefe 360deg);',
          'background: conic-gradient(from 0deg at 30% 70%, #fff8fa 0deg, #f8f0f3 120deg, #f5f0f2 240deg, #fff8fa 360deg);',
        ];
      } else {
        // Moderate, subtle gradients for non-grayscale templates - still muted to not overpower the monster
        gradients = [
          'background: linear-gradient(135deg, #e8f0fe 0%, #e3e8f5 100%);', // Soft blue to muted purple
          'background: linear-gradient(135deg, #fef0f3 0%, #f8e8ec 100%);', // Soft pink to muted rose
          'background: linear-gradient(135deg, #e8f7fe 0%, #e0f4f8 100%);', // Soft blue to muted cyan
          'background: linear-gradient(135deg, #f0fef3 0%, #e8f8ec 100%);', // Soft green to muted mint
          'background: linear-gradient(135deg, #fef5e8 0%, #f8f0e0 100%);', // Soft yellow to muted cream
          'background: linear-gradient(135deg, #f0fffe 0%, #e8f5f3 100%);', // Soft cyan to muted seafoam
          'background: linear-gradient(135deg, #f5f0fe 0%, #f0e8f8 100%);', // Soft lavender to muted purple
          'background: linear-gradient(135deg, #ffe8f0 0%, #f8e0e8 100%);', // Soft coral to muted peach
          'background: linear-gradient(135deg, #f0ffe8 0%, #e8f8e0 100%);', // Soft lime to muted green
          'background: linear-gradient(135deg, #fff0e8 0%, #f8e8e0 100%);', // Soft peach to muted apricot
          // Radial gradients for depth and focus
          'background: radial-gradient(ellipse at center, #e8f0fe 0%, #e3e8f5 70%);',
          'background: radial-gradient(circle at top right, #fef0f3 0%, #f5e5ea 65%);',
          'background: radial-gradient(ellipse at bottom left, #f0fef3 0%, #e5f5ea 75%);',
          'background: radial-gradient(circle at center, #fef5e8 20%, #f5f0e0 80%);',
          // Conic gradients for magical/mystical feel
          'background: conic-gradient(from 60deg at 50% 50%, #e8f0fe 0deg, #fef0f3 90deg, #f0fef3 180deg, #fef5e8 270deg, #e8f0fe 360deg);',
          'background: conic-gradient(from 0deg at 40% 60%, #f5f0fe 0deg, #ffe8f0 120deg, #f0ffe8 240deg, #f5f0fe 360deg);',
          // Multi-stop linear gradients for richer transitions
          'background: linear-gradient(135deg, #e8f0fe 0%, #f0fffe 33%, #fef0f3 66%, #f0e8f8 100%);',
          'background: linear-gradient(45deg, #f0fef3 0%, #e8f7fe 25%, #fef0f3 75%, #fef5e8 100%);',
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

  private handleCardClick(url: string, card: CardData) {
    if (url) {
      const templateKey = card.key;

      // Track analytics - this is a template click since carousel shows templates
      trackMonsterClick(
        templateKey,
        'template',
        'carousel',
      );

      // Navigate to the monster page
      window.location.href = url;
    }
  }

  private handleImageError(event: Event, monster: CardData) {
    const img = event.target as HTMLImageElement;
    console.warn(`Failed to load image for ${monster.name}: ${img.src}`);
    // Set fallback image or hide the image element
    img.style.display = 'none';
  }

  private initializeSwiper() {

    if (this.swiperInstance) {
      //swiper already initialized
      return;
    }

    const swiperContainer = this.shadowRoot!.querySelector('.swiper-container')!;

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

      // Force wrapper to be horizontal before initializing Swiper
      const wrapper = swiperContainer.querySelector('.swiper-wrapper') as HTMLElement;
      if (wrapper) {
        wrapper.style.display = 'flex';
        wrapper.style.flexDirection = 'row';
        wrapper.style.alignItems = 'flex-start';
      }

      // Calculate how many slides are visible based on current viewport
      const calculateSlidesPerView = () => {
        const width = window.innerWidth;
        if (width >= 1400) return 3;
        if (width >= 1200) return 3;
        if (width >= 768) return 3;
        if (width >= 576) return 2;
        return 1;
      };

      // Get total number of slides
      const totalSlides = wrapper?.children.length || 0;
      const slidesPerView = calculateSlidesPerView();

      // Only enable autoplay if there are more slides than fit in the viewport
      const shouldAutoplay = totalSlides > slidesPerView;
      const delay = 5000 + Math.random() * 3000;

      // Get navigation elements from shadow root
      const nextEl = this.shadowRoot!.querySelector('.swiper-button-next') as HTMLElement;
      const prevEl = this.shadowRoot!.querySelector('.swiper-button-prev') as HTMLElement;

      // Use configuration that matches homepage for consistent navigation
      this.swiperInstance = new Swiper(swiperContainer as HTMLElement, {
        modules: [Autoplay, Navigation, Keyboard, Parallax],
        slidesPerView: 3,
        spaceBetween: 16,
        initialSlide: 0, // Start at first slide
        centeredSlides: false, // Left-align slides
        grabCursor: true,
        direction: 'horizontal', // Explicitly set horizontal direction
        loop: false, // Disable infinite loop
        keyboard: {
          enabled: true,
        },
        navigation: {
          nextEl: nextEl,
          prevEl: prevEl,
        },
        parallax: true,
        simulateTouch: true,
        autoplay: shouldAutoplay ? {
          delay: delay,
          disableOnInteraction: true,
          pauseOnMouseEnter: true, // Pause autoplay when user hovers for better UX
          stopOnLastSlide: true
        } : false,
        breakpoints: breakpoints,
        on: {
          init: function (this: any) {
            this.el.classList.remove('preload');
          },
          slideChange: function (this: any) {
            // Stop autoplay if we've reached the Nth to last slide
            // where N is the number of slides visible in the current viewport
            if (this.autoplay && this.autoplay.running) {
              const currentSlide = this.activeIndex;
              const totalSlides = this.slides.length;

              // Calculate current slides per view based on viewport (same logic as initialization)
              const getCurrentSlidesPerView = () => {
                const width = window.innerWidth;
                if (width >= 1400) return 3;
                if (width >= 1200) return 3;
                if (width >= 768) return 3;
                if (width >= 576) return 2;
                return 1;
              };

              const currentSlidesPerView = getCurrentSlidesPerView();

              // Calculate the last slide index where we still have a full view
              // If we have 5 slides total and 3 fit in view, we stop after slide 2 (0-indexed)
              // because moving to slide 3 would only show slides 3,4 (only 2 slides instead of 3)
              const lastFullViewSlide = totalSlides - currentSlidesPerView;

              if (currentSlide >= lastFullViewSlide) {
                this.autoplay.stop();
              }
            }
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
    } catch (error) {
      console.warn('Failed to initialize Swiper:', error);
    }
  }

  updated(changedProperties: any) {
    super.updated(changedProperties);

    // Clean up Swiper when filter changes
    if (changedProperties.has('filter') && this.swiperInstance) {
      this.swiperInstance.destroy(true, true);
      this.swiperInstance = null;
    }

    // Only reinitialize Swiper when templates data is loaded and rendered
    // TaskStatus.COMPLETE = 2 in @lit/task
    if (this.templatesTask.status === 2 && !this.swiperInstance) {
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
    return this.templatesTask.render({
      pending: () => {
        return html`<div class="loading">Loading monster templates...</div>`;
      },
      complete: (templates) => {
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
            <!-- Navigation buttons explicitly rendered in template -->
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

  private renderMonsterCard(template: CardData) {
    const cardClasses = [
      'swiper-slide',
      'card',
      'tall',
      template.mask_css,
      template.is_new ? 'new' : '',
      template.grayscale ? 'grayscale' : '',
      template.transparent_edges ? 'transparent-edges' : ''
    ].filter(Boolean).join(' ');

    // Only prepend baseUrl if the template.url is a relative path
    const url = template.url.startsWith('http://') || template.url.startsWith('https://') || template.url.startsWith('/')
      ? template.url
      : window.baseUrl ? `${window.baseUrl}/${template.url}` : template.url;

    return html`
      <div
        class="${cardClasses}"
        data-url="${url}"
        style="${template.custom_style}"
        @click="${() => this.handleCardClick(url, template)}"
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