import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Injector-specific quotes for content placement
const INJECTOR_QUOTES = [
  "Perhaps your monsters need more... character?",
  "I sense your campaign could use darker elements.",
  "These encounters feel rather... tame.",
  "Let me share secrets of true horror.",
  "Your players haven't seen real fear yet.",
  "Subscribe for access to forbidden tactics.",
  "Ready to craft truly memorable nightmares?"
];

interface InjectionPoint {
  element: Element;
  position: 'before' | 'after';
  priority: number;
}

@customElement('skull-upsell-injector')
export class SkullUpsellInjector extends LitElement {
  @property({ type: Boolean })
  enabled: boolean = true;

  @property({ type: Number })
  minSkulls: number = 2;

  @property({ type: Number })
  maxSkulls: number = 3;

  @property({ type: Number })
  activationDelay: number = 5000; // 5 seconds for faster activation

  @property({ type: String })
  injectedClass: string = 'centered';

  private _modal?: HTMLElement;
  private _injectedSkulls: HTMLElement[] = [];
  private _activationTimer?: number;

  static styles = css`
    :host {
      display: none;
    }

    .injected-skull {
      margin: 2rem auto;
      text-align: center;
      display: block;
    }

    .injected-skull.end-placement {
      margin-top: 3rem;
      margin-bottom: 1rem;
    }

    .injected-skull.middle-placement {
      margin: 2rem auto;
      padding: 1rem 0;
      border-top: 1px solid rgba(139, 69, 19, 0.2);
      border-bottom: 1px solid rgba(139, 69, 19, 0.2);
    }

    .skull-wrapper {
      background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 40"><path d="M0,20 Q100,0 200,20 Q100,40 0,20" fill="%23d4af37" opacity="0.1"/></svg>') center/contain no-repeat;
      padding: 20px;
      display: inline-block;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    
    if (this.enabled) {
      // Delay injection to allow page content to fully render
      setTimeout(() => {
        this._injectSkulls();
        this._setupModal();
        this._startActivationTimer();
      }, 1000);
    }
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._cleanup();
  }

  private _injectSkulls(): void {
    const contentElement = this._findContentContainer();
    if (!contentElement) {
      console.warn('SkullUpsellInjector: Could not find content container');
      return;
    }

    const injectionPoints = this._findInjectionPoints(contentElement);
    const selectedPoints = this._selectInjectionPoints(injectionPoints);

    selectedPoints.forEach((point, index) => {
      this._injectSkullAtPoint(point, index);
    });

    trackEvent('skull_injector_initialized', {
      skulls_injected: selectedPoints.length,
      injection_points_found: injectionPoints.length,
      content_length: contentElement.textContent?.length || 0
    });
  }

  private _findContentContainer(): Element | null {
    // Try to find the main content container
    const selectors = [
      'main',
      '.content',
      '#content',
      'article',
      '.md-content__inner',
      '.page-content'
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) return element;
    }

    // Fallback to body if no specific content container found
    return document.body;
  }

  private _findInjectionPoints(container: Element): InjectionPoint[] {
    const points: InjectionPoint[] = [];

    // High priority: page breaks and horizontal rules
    container.querySelectorAll('div[page-break], hr').forEach(element => {
      points.push({
        element,
        position: 'after',
        priority: 10
      });
    });

    // Medium priority: H2 headers
    container.querySelectorAll('h2').forEach(element => {
      points.push({
        element,
        position: 'after',
        priority: 7
      });
    });

    // Lower priority: H3 headers
    container.querySelectorAll('h3').forEach(element => {
      points.push({
        element,
        position: 'after',
        priority: 5
      });
    });

    // Always add end placement
    const lastChild = container.lastElementChild;
    if (lastChild) {
      points.push({
        element: lastChild,
        position: 'after',
        priority: 8
      });
    }

    return points.sort((a, b) => b.priority - a.priority);
  }

  private _selectInjectionPoints(points: InjectionPoint[]): InjectionPoint[] {
    const selected: InjectionPoint[] = [];

    // Always include the end placement (highest priority after page breaks)
    const endPoint = points.find(p => p.priority === 8);
    if (endPoint) {
      selected.push(endPoint);
    }

    // Select middle placements
    const middlePoints = points.filter(p => p.priority !== 8);
    
    if (middlePoints.length > 0) {
      // Try to place one in the middle third of content
      const middleIndex = Math.floor(middlePoints.length / 2);
      const targetIndex = Math.max(0, Math.min(middleIndex, middlePoints.length - 1));
      
      if (middlePoints[targetIndex]) {
        selected.push(middlePoints[targetIndex]);
      }

      // Add additional skulls if we have good injection points and haven't reached max
      if (selected.length < this.maxSkulls && middlePoints.length > 2) {
        const additionalIndex = Math.floor(middlePoints.length * 0.25);
        if (additionalIndex !== targetIndex && middlePoints[additionalIndex]) {
          selected.push(middlePoints[additionalIndex]);
        }
      }
    }

    // Ensure we have at least minSkulls
    while (selected.length < this.minSkulls && middlePoints.length > selected.length - 1) {
      const remaining = middlePoints.filter(p => !selected.includes(p));
      if (remaining.length > 0) {
        selected.push(remaining[0]);
      } else {
        break;
      }
    }

    return selected.slice(0, this.maxSkulls);
  }

  private _injectSkullAtPoint(point: InjectionPoint, index: number): void {
    const skullElement = document.createElement('div');
    skullElement.className = `injected-skull ${point.priority === 8 ? 'end-placement' : 'middle-placement'}`;
    
    const wrapper = document.createElement('div');
    wrapper.className = 'skull-wrapper';
    
    const skull = document.createElement('animated-skull') as any;
    skull.display = 'visible'; // Start visible and enabled
    skull.quotes = INJECTOR_QUOTES.join(';');
    skull.quoteIndex = index % INJECTOR_QUOTES.length;
    skull.injectedClass = this.injectedClass; // Apply injected class for styling
    skull.onClick = () => this._handleSkullClick(index);

    wrapper.appendChild(skull);
    skullElement.appendChild(wrapper);

    if (point.position === 'after') {
      point.element.insertAdjacentElement('afterend', skullElement);
    } else {
      point.element.insertAdjacentElement('beforebegin', skullElement);
    }

    this._injectedSkulls.push(skullElement);
  }

  private _setupModal(): void {
    this._modal = document.createElement('upsell-modal') as any;
    (this._modal as any).source = 'skull_injector';
    document.body.appendChild(this._modal);

    this._modal.addEventListener('modal-closed', () => {
      // Modal was closed, maybe delay before showing skulls again
    });
  }

  private _startActivationTimer(): void {
    // Skulls are now enabled immediately, but we can still delay quote showing
    this._activationTimer = window.setTimeout(() => {
      this._activateQuotes();
    }, this.activationDelay);
  }

  private _activateQuotes(): void {
    // Activate quotes on skulls with a staggered delay
    this._injectedSkulls.forEach((skullElement, index) => {
      const skull = skullElement.querySelector('animated-skull') as any;
      if (skull) {
        // Stagger the quote activation slightly
        setTimeout(() => {
          // Show a quote briefly to indicate interactivity
          skull.showQuote = true;
          setTimeout(() => {
            skull.showQuote = false;
          }, 3000); // Show for 3 seconds
        }, index * 1000); // 1 second between each skull
      }
    });

    trackEvent('skull_injector_quotes_activated', {
      skulls_activated: this._injectedSkulls.length,
      delay_ms: this.activationDelay
    });
  }

  private _handleSkullClick(skullIndex: number): void {
    trackEvent('injected_skull_clicked', {
      skull_index: skullIndex,
      placement: skullIndex === this._injectedSkulls.length - 1 ? 'end' : 'middle'
    });

    if (this._modal) {
      (this._modal as any).open = true;
    }

    // Show quote on clicked skull
    const clickedSkull = this._injectedSkulls[skullIndex]?.querySelector('animated-skull') as any;
    if (clickedSkull) {
      clickedSkull.showQuote = true;
      
      // Hide quote after a few seconds
      setTimeout(() => {
        if (clickedSkull) {
          clickedSkull.showQuote = false;
        }
      }, 5000);
    }
  }

  private _cleanup(): void {
    if (this._activationTimer) {
      clearTimeout(this._activationTimer);
    }

    // Remove injected skulls
    this._injectedSkulls.forEach(skull => {
      skull.remove();
    });
    this._injectedSkulls = [];

    // Remove modal
    if (this._modal) {
      this._modal.remove();
      this._modal = undefined;
    }
  }

  render() {
    // This component doesn't render anything in its own shadow DOM
    // All injection happens in the main document
    return html``;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'skull-upsell-injector': SkullUpsellInjector;
  }
}