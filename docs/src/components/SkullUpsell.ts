import { LitElement, html, css, PropertyValues } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Skull upsell copy library - promoting skull/undead content
const SKULL_UPSELL_COPY = [
  "💀 Discover eerie skull creatures to haunt your campaign!",
  "🔥 Add some bone-chilling undead to your monster collection!",
  "💀 Need more sinister creatures? Check out our skull monsters!",
  "⚰️ Unleash the power of undead with our skull collection!",
  "💀 Looking for spine-tingling encounters? Explore skull creatures!"
];

// Skull creature keywords that trigger the upsell
const SKULL_KEYWORDS = [
  'skull', 'bone', 'undead', 'skeleton', 'lich', 'zombie', 'ghost', 
  'wraith', 'specter', 'banshee', 'vampire', 'mummy', 'necromancer'
];

// Local storage key for tracking dismissal
const STORAGE_KEY = 'ff_skull_upsell';
const UPSELL_VERSION = 'v1_skull';

interface SkullUpsellState {
  isActive: boolean;
  currentStatblock: Element | null;
  currentMessage: string;
  showTime: number;
  upsellElement: HTMLElement | null;
}

@customElement('skull-upsell')
export class SkullUpsell extends LitElement {
  @property({ type: Boolean })
  enabled: boolean = false;

  private _upsellState: SkullUpsellState = {
    isActive: false,
    currentStatblock: null,
    currentMessage: '',
    showTime: 0,
    upsellElement: null
  };

  private _intersectionObserver?: IntersectionObserver;
  private _statblocks: Element[] = [];
  private _visibilityMap = new Map<Element, number>();
  private _initTimeout?: number;
  private _displayTimeout?: number;
  private _firedEvents = new Set<string>();

  static styles = css`
    :host {
      position: relative;
      z-index: 999;
      pointer-events: none;
    }

    /* Skull upsell floating banner animation */
    @keyframes skullFloat {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-5px) rotate(2deg); }
    }

    @keyframes fadeInUp {
      from { 
        opacity: 0; 
        transform: translateY(20px); 
      }
      to { 
        opacity: 1; 
        transform: translateY(0); 
      }
    }

    @keyframes pulseGlow {
      0%, 100% { box-shadow: 0 0 5px rgba(255, 69, 0, 0.3); }
      50% { box-shadow: 0 0 20px rgba(255, 69, 0, 0.6); }
    }
  `;

  connectedCallback() {
    super.connectedCallback();

    // Check if upsell is enabled
    if (!this.enabled) {
      return;
    }

    // Check if upsell was recently dismissed
    if (this._isDismissed()) {
      return;
    }

    // Wait 2 seconds after component loads before initializing
    this._initTimeout = window.setTimeout(() => {
      if (this.enabled && !this._isDismissed()) {
        this._initializeUpsell();
      }
    }, 2000);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._cleanup();
  }

  updated(changedProperties: PropertyValues) {
    super.updated(changedProperties);

    // Handle enabled property changes
    if (changedProperties.has('enabled')) {
      if (this.enabled) {
        // Upsell was just enabled - start it if not dismissed
        if (!this._isDismissed()) {
          this._initTimeout = window.setTimeout(() => {
            if (this.enabled && !this._isDismissed()) {
              this._initializeUpsell();
            }
          }, 1000);
        }
      } else {
        // Upsell was disabled - clean up
        this._cleanup();
      }
    }
  }

  private _isDismissed(): boolean {
    const dismissedAt = localStorage.getItem(STORAGE_KEY);
    if (!dismissedAt) return false;
    
    // Check if 24 hours have passed since dismissal
    const dismissTime = parseInt(dismissedAt);
    const now = Date.now();
    const dayInMs = 24 * 60 * 60 * 1000;
    
    return (now - dismissTime) < dayInMs;
  }

  private _markDismissed(): void {
    localStorage.setItem(STORAGE_KEY, Date.now().toString());
  }

  private _initializeUpsell(): void {
    // Check for required browser features
    if (!this._checkBrowserSupport()) {
      this._trackAnalytics('skull_upsell_skipped_unsupported', {
        missing: this._getMissingFeatures()
      }, true);
      return;
    }

    // Find all statblock components
    this._findStatblocks();

    if (this._statblocks.length === 0) {
      // Retry after a short delay in case components are still loading
      setTimeout(() => {
        this._findStatblocks();
        if (this._statblocks.length > 0) {
          this._setupIntersectionObserver();
          this._trackAnalytics('skull_upsell_impression', {
            upsell_version: UPSELL_VERSION,
            page: window.location.pathname,
            count_statblocks: this._statblocks.length
          }, true);
        }
      }, 1500);
      return;
    }

    // Set up intersection observer
    this._setupIntersectionObserver();

    // Track upsell impression
    this._trackAnalytics('skull_upsell_impression', {
      upsell_version: UPSELL_VERSION,
      page: window.location.pathname,
      count_statblocks: this._statblocks.length
    }, true);
  }

  private _checkBrowserSupport(): boolean {
    return !!(window.IntersectionObserver && window.localStorage && document.querySelector);
  }

  private _getMissingFeatures(): string[] {
    const missing: string[] = [];
    if (!window.IntersectionObserver) missing.push('IntersectionObserver');
    if (!window.localStorage) missing.push('localStorage');
    if (!document.querySelector) missing.push('selectors');
    return missing;
  }

  private _findStatblocks(): void {
    // Find all monster-statblock elements
    this._statblocks = Array.from(document.querySelectorAll('monster-statblock'));
  }

  private _setupIntersectionObserver(): void {
    this._intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          const visibilityRatio = entry.intersectionRatio;
          this._visibilityMap.set(entry.target, visibilityRatio);
        });

        this._updateMostVisibleStatblock();
      },
      { threshold: [0, 0.25, 0.5, 0.75, 1.0] }
    );

    this._statblocks.forEach(statblock => {
      this._intersectionObserver!.observe(statblock);
    });
  }

  private _updateMostVisibleStatblock(): void {
    let mostVisible: Element | null = null;
    let maxVisibility = 0;

    this._visibilityMap.forEach((visibility, statblock) => {
      if (visibility > maxVisibility) {
        maxVisibility = visibility;
        mostVisible = statblock;
      }
    });

    // Only show upsell if statblock is significantly visible and contains skull-related content
    if (mostVisible && maxVisibility > 0.4) {
      if (this._shouldShowUpsellForStatblock(mostVisible)) {
        if (mostVisible !== this._upsellState.currentStatblock || !this._upsellState.isActive) {
          this._showUpsellForStatblock(mostVisible);
        }
      }
    } else if (this._upsellState.isActive) {
      // No suitable statblock is visible, hide upsell
      this._removeUpsell();
      this._upsellState.isActive = false;
    }
  }

  private _shouldShowUpsellForStatblock(statblock: Element): boolean {
    // Get statblock text content to check for skull-related keywords
    const text = statblock.textContent?.toLowerCase() || '';
    
    // Check if any skull keywords are present
    return SKULL_KEYWORDS.some(keyword => text.includes(keyword));
  }

  private _showUpsellForStatblock(statblock: Element): void {
    // Don't show multiple upsells at once
    if (this._upsellState.isActive) {
      return;
    }

    // Wait a moment for the statblock to be fully rendered
    setTimeout(() => {
      const randomMessage = SKULL_UPSELL_COPY[Math.floor(Math.random() * SKULL_UPSELL_COPY.length)];

      this._upsellState = {
        isActive: true,
        currentStatblock: statblock,
        currentMessage: randomMessage,
        showTime: Date.now(),
        upsellElement: null
      };

      this._showUpsellBanner(randomMessage);
      
      // Auto-dismiss after 8 seconds
      this._displayTimeout = window.setTimeout(() => {
        this._removeUpsell();
      }, 8000);

    }, 500);
  }

  private _showUpsellBanner(message: string): void {
    // Remove any existing upsell
    this._removeUpsell();

    // Create upsell banner element
    const banner = document.createElement('div');
    banner.className = 'skull-upsell-banner';

    // Apply inline styles since the banner will be outside the shadow DOM
    this._applyBannerStyles(banner);

    // Create banner content
    banner.innerHTML = `
      <div class="skull-icon">💀</div>
      <div class="upsell-message">${message}</div>
      <button class="upsell-cta">Explore Skulls</button>
      <button class="upsell-dismiss">×</button>
    `;

    // Position banner at the bottom of the viewport
    this._positionBanner(banner);

    // Add click handlers
    const ctaButton = banner.querySelector('.upsell-cta') as HTMLElement;
    const dismissButton = banner.querySelector('.upsell-dismiss') as HTMLElement;
    
    ctaButton.addEventListener('click', () => this._handleCtaClick());
    dismissButton.addEventListener('click', () => this._handleDismissClick());

    // Add to body
    document.body.appendChild(banner);

    // Track analytics
    this._trackAnalytics('skull_upsell_shown', {
      message,
      visibility_ratio: this._visibilityMap.get(this._upsellState.currentStatblock!) || 0
    }, true);

    // Store reference
    this._upsellState.upsellElement = banner;
  }

  private _positionBanner(banner: HTMLElement): void {
    banner.style.position = 'fixed';
    banner.style.bottom = '20px';
    banner.style.left = '50%';
    banner.style.transform = 'translateX(-50%)';
    banner.style.zIndex = '1000';
  }

  private _applyBannerStyles(banner: HTMLElement): void {
    banner.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: linear-gradient(135deg, #2a0a0a, #1a1a1a);
      border: 2px solid #8b0000;
      border-radius: 12px;
      padding: 12px 20px;
      box-shadow: 0 4px 20px rgba(139, 0, 0, 0.4);
      font-family: var(--primary-font, system-ui);
      color: #f4f1e6;
      max-width: 400px;
      min-width: 300px;
      z-index: 1000;
      pointer-events: auto;
      animation: fadeInUp 0.5s ease-out, pulseGlow 3s infinite;
      display: flex;
      align-items: center;
      gap: 12px;
    `;

    // Add pseudo-element styles via a style element
    const style = document.createElement('style');
    style.textContent = `
      @keyframes fadeInUp {
        from { opacity: 0; transform: translateX(-50%) translateY(20px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
      }
      @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 4px 20px rgba(139, 0, 0, 0.4); }
        50% { box-shadow: 0 4px 30px rgba(139, 0, 0, 0.7); }
      }
      @keyframes skullFloat {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-3px) rotate(5deg); }
      }
      .skull-upsell-banner .skull-icon {
        font-size: 1.5rem;
        animation: skullFloat 2s infinite;
      }
      .skull-upsell-banner .upsell-message {
        flex: 1;
        font-size: 0.9rem;
        font-weight: 500;
      }
      .skull-upsell-banner .upsell-cta {
        background: #8b0000;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.8rem;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s ease;
      }
      .skull-upsell-banner .upsell-cta:hover {
        background: #a50000;
      }
      .skull-upsell-banner .upsell-dismiss {
        background: transparent;
        color: #999;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        padding: 0;
        width: 20px;
        height: 20px;
        transition: color 0.2s ease;
      }
      .skull-upsell-banner .upsell-dismiss:hover {
        color: #fff;
      }
    `;

    // Add the style to the document head if it doesn't exist
    if (!document.querySelector('#skull-upsell-styles')) {
      style.id = 'skull-upsell-styles';
      document.head.appendChild(style);
    }
  }

  private _removeUpsell(): void {
    const existingBanner = document.querySelector('.skull-upsell-banner');
    if (existingBanner) {
      existingBanner.remove();
    }

    if (this._upsellState.upsellElement) {
      this._upsellState.upsellElement.remove();
      this._upsellState.upsellElement = null;
    }

    // Clear display timeout
    if (this._displayTimeout) {
      clearTimeout(this._displayTimeout);
      this._displayTimeout = undefined;
    }

    this._upsellState.isActive = false;
  }

  private _handleCtaClick(): void {
    const timeElapsed = Date.now() - this._upsellState.showTime;

    this._trackAnalytics('skull_upsell_cta_click', {
      message: this._upsellState.currentMessage,
      ms_since_show: timeElapsed
    });

    // Navigate to skull creatures page (assuming this exists)
    window.location.href = '/monsters/?search=skull';

    this._markDismissed();
    this._removeUpsell();
  }

  private _handleDismissClick(): void {
    const timeElapsed = Date.now() - this._upsellState.showTime;

    this._trackAnalytics('skull_upsell_dismiss', {
      message: this._upsellState.currentMessage,
      ms_since_show: timeElapsed
    });

    this._markDismissed();
    this._removeUpsell();
  }

  private _cleanup(): void {
    if (this._initTimeout) {
      clearTimeout(this._initTimeout);
    }

    if (this._displayTimeout) {
      clearTimeout(this._displayTimeout);
    }

    if (this._intersectionObserver) {
      this._intersectionObserver.disconnect();
    }

    this._removeUpsell();

    // Remove injected styles
    const styleElement = document.querySelector('#skull-upsell-styles');
    if (styleElement) {
      styleElement.remove();
    }

    this._upsellState = {
      isActive: false,
      currentStatblock: null,
      currentMessage: '',
      showTime: 0,
      upsellElement: null
    };
  }

  private _trackAnalytics(eventName: string, params: any, firstTimeOnly: boolean = false): void {
    if (firstTimeOnly) {
      if (this._firedEvents.has(eventName)) {
        return; // Skip if already fired
      }
      this._firedEvents.add(eventName);
    }
    trackEvent(eventName, params);
  }

  render() {
    return html`<!-- SkullUpsell renders promotional banners via DOM manipulation -->`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'skull-upsell': SkullUpsell;
  }
}