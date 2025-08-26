import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Tutorial copy library
const TUTORIAL_COPY = {
  dice: [
    "Not tough enough for your party? Roll again",
    "Your PCs need a real challenge. Click me to re-roll",
    "Not what you're looking for? Roll for a fresh take"
  ],
  anvil: [
    "Think you can forge a nastier foe?",
    "Forge the perfect foe with a couple clicks", 
    "Tired of boring statblocks? Forge an unforgettable foe"
  ]
};

// Local storage key for tracking completion
const STORAGE_KEY = 'ff_statblock_tutorial';
const TUTORIAL_VERSION = 'v1_done';

type TutorialTarget = 'dice' | 'anvil';

interface TutorialState {
  isActive: boolean;
  currentStatblock: Element | null;
  currentTarget: TutorialTarget | null;
  currentLine: string;
  showTime: number;
  bubbleElement: HTMLElement | null;
}

@customElement('statblock-tutorial')
export class StatblockTutorial extends LitElement {
  private _tutorialState: TutorialState = {
    isActive: false,
    currentStatblock: null,
    currentTarget: null,
    currentLine: '',
    showTime: 0,
    bubbleElement: null
  };

  private _intersectionObserver?: IntersectionObserver;
  private _statblocks: Element[] = [];
  private _visibilityMap = new Map<Element, number>();
  private _initTimeout?: number;
  private _cycleTimeout?: number;
  private _currentTargetIndex = 0;

  static styles = css`
    :host {
      position: relative;
      z-index: 1000;
      pointer-events: none;
    }

    .tutorial-bubble {
      position: absolute;
      background: var(--bg-color, #1a1a1a);
      border: 2px solid var(--tertiary-color, #c29a5b);
      border-radius: 12px;
      padding: 8px 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-family: var(--primary-font, system-ui);
      font-size: 0.9rem;
      color: var(--fg-color, #f4f1e6);
      max-width: 250px;
      z-index: 1001;
      pointer-events: auto;
      cursor: pointer;
      animation: popIn 0.25s ease-out;
      white-space: nowrap;
    }

    .tutorial-bubble::after {
      content: '';
      position: absolute;
      border: 8px solid transparent;
      border-top-color: var(--bg-color, #1a1a1a);
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
    }

    .tutorial-bubble::before {
      content: '';
      position: absolute;
      border: 9px solid transparent;
      border-top-color: var(--tertiary-color, #c29a5b);
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      z-index: -1;
    }

    .tutorial-text {
      margin: 0;
      overflow: hidden;
      white-space: nowrap;
      border-right: 2px solid var(--tertiary-color, #c29a5b);
      animation: typing 2s steps(40, end), blink 1s step-end infinite;
    }

    @keyframes popIn {
      from { 
        transform: scale(0.8); 
        opacity: 0; 
      }
      to { 
        transform: scale(1); 
        opacity: 1; 
      }
    }

    @keyframes typing {
      from { width: 0 }
      to { width: 100% }
    }

    @keyframes blink {
      from, to { border-color: transparent }
      50% { border-color: var(--tertiary-color, #c29a5b) }
    }

    /* Icon highlighting animations */
    :host(.highlighting-dice) ::slotted(reroll-button),
    :host(.highlighting-dice) reroll-button {
      animation: wiggle 0.6s infinite;
    }

    :host(.highlighting-anvil) ::slotted(forge-button),
    :host(.highlighting-anvil) forge-button {
      animation: pulseGlow 1.2s infinite;
    }

    @keyframes wiggle {
      0% { transform: rotate(0deg); }
      25% { transform: rotate(5deg); }
      75% { transform: rotate(-5deg); }
      100% { transform: rotate(0deg); }
    }

    @keyframes pulseGlow {
      0%, 100% { filter: drop-shadow(0 0 0px #ffcc66); }
      50% { filter: drop-shadow(0 0 6px #ffcc66); }
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    
    // Check if tutorial is already completed
    if (this._isCompleted()) {
      return;
    }

    // Wait 300ms after FCP before initializing
    this._initTimeout = window.setTimeout(() => {
      this._initializeTutorial();
    }, 300);
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this._cleanup();
  }

  private _isCompleted(): boolean {
    return localStorage.getItem(STORAGE_KEY) === TUTORIAL_VERSION;
  }

  private _markCompleted(): void {
    localStorage.setItem(STORAGE_KEY, TUTORIAL_VERSION);
  }

  private _initializeTutorial(): void {
    // Check for required browser features
    if (!this._checkBrowserSupport()) {
      this._trackAnalytics('tutorial_skipped_unsupported', {
        missing: this._getMissingFeatures()
      });
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
          this._trackAnalytics('tutorial_impression', {
            tutorial_version: TUTORIAL_VERSION,
            page: window.location.pathname,
            count_statblocks: this._statblocks.length
          });
        }
      }, 1000);
      return;
    }

    // Set up intersection observer
    this._setupIntersectionObserver();
    
    // Track tutorial impression
    this._trackAnalytics('tutorial_impression', {
      tutorial_version: TUTORIAL_VERSION,
      page: window.location.pathname,
      count_statblocks: this._statblocks.length
    });
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
      { threshold: [0, 0.1, 0.25, 0.5, 0.75, 1.0] }
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

    if (mostVisible && maxVisibility > 0.1) {
      if (mostVisible !== this._tutorialState.currentStatblock || !this._tutorialState.isActive) {
        this._attachTutorialToStatblock(mostVisible);
      }
    } else if (this._tutorialState.isActive) {
      // No statblock is visible, hide tutorial
      this._removeTutorialBubble();
      this._tutorialState.isActive = false;
    }
  }

  private _attachTutorialToStatblock(statblock: Element): void {
    // Wait for the statblock to be fully rendered
    setTimeout(() => {
      // Find available buttons in the statblock
      const buttons = this._findButtonsInStatblock(statblock);
      
      if (buttons.length === 0) {
        // Try again after another short delay
        setTimeout(() => {
          const buttonsRetry = this._findButtonsInStatblock(statblock);
          if (buttonsRetry.length > 0) {
            this._showTutorialForButtons(statblock, buttonsRetry);
          }
        }, 500);
        return;
      }

      this._showTutorialForButtons(statblock, buttons);
      this._startCycleTimer();
    }, 100);
  }

  private _showTutorialForButtons(statblock: Element, buttons: Element[]): void {
    // Cycle through available buttons
    const targetButton = buttons[this._currentTargetIndex % buttons.length];
    const target = targetButton.tagName.toLowerCase() === 'reroll-button' ? 'dice' : 'anvil';
    
    // Get random copy for this target
    const copyArray = TUTORIAL_COPY[target];
    const randomLine = copyArray[Math.floor(Math.random() * copyArray.length)];

    this._tutorialState = {
      isActive: true,
      currentStatblock: statblock,
      currentTarget: target,
      currentLine: randomLine,
      showTime: Date.now(),
      bubbleElement: null
    };

    this._showTutorialBubble(targetButton, target, randomLine);
    this.requestUpdate();
  }

  private _findButtonsInStatblock(statblock: Element): Element[] {
    const buttons: Element[] = [];
    
    // Look for buttons in the shadow DOM
    const shadowRoot = (statblock as any).shadowRoot;
    if (shadowRoot) {
      // Look for buttons in the statblock-button-panel
      const buttonPanel = shadowRoot.querySelector('.statblock-button-panel');
      if (buttonPanel) {
        const rerollButton = buttonPanel.querySelector('reroll-button');
        const forgeButton = buttonPanel.querySelector('forge-button');
        
        if (rerollButton) buttons.push(rerollButton);
        if (forgeButton) buttons.push(forgeButton);
      }
    }
    
    return buttons;
  }

  private _startCycleTimer(): void {
    this._clearCycleTimer();
    
    this._cycleTimeout = window.setTimeout(() => {
      if (this._tutorialState.isActive && this._tutorialState.currentStatblock) {
        // Move to next target
        this._currentTargetIndex++;
        
        // Find buttons in current statblock
        const buttons = this._findButtonsInStatblock(this._tutorialState.currentStatblock);
        if (buttons.length > 0) {
          this._showTutorialForButtons(this._tutorialState.currentStatblock, buttons);
        }
      }
    }, 4000); // Cycle every 4 seconds
  }

  private _clearCycleTimer(): void {
    if (this._cycleTimeout) {
      clearTimeout(this._cycleTimeout);
      this._cycleTimeout = undefined;
    }
  }

  private _showTutorialBubble(button: Element, target: TutorialTarget, text: string): void {
    // Remove any existing bubble
    this._removeTutorialBubble();

    // Create bubble element
    const bubble = document.createElement('div');
    bubble.className = 'tutorial-bubble';
    bubble.innerHTML = `<p class="tutorial-text">${text}</p>`;
    
    // Position bubble relative to button
    this._positionBubble(bubble, button);
    
    // Add click handlers
    bubble.addEventListener('click', () => this._handleBubbleClick(target));
    button.addEventListener('click', () => this._handleIconClick(target));
    
    // Find the statblock container and append bubble there
    let container = button.closest('monster-statblock');
    if (!container) {
      container = document.body;
    }
    container.appendChild(bubble);
    
    // Add highlighting class to host
    this.classList.add(`highlighting-${target}`);
    
    // Track analytics
    this._trackAnalytics('tutorial_bubble_shown', {
      line: text,
      target,
      visibility_ratio: this._visibilityMap.get(this._tutorialState.currentStatblock!) || 0
    });
  }

  private _positionBubble(bubble: Element, button: Element): void {
    const buttonRect = button.getBoundingClientRect();
    const bubbleElement = bubble as HTMLElement;
    
    // Find the statblock container for positioning context
    let positioningParent = button.closest('monster-statblock');
    if (!positioningParent) {
      positioningParent = document.body;
    }
    
    // Position relative to the positioning parent
    bubbleElement.style.position = 'absolute';
    
    // Calculate position relative to the button
    const parentRect = positioningParent.getBoundingClientRect();
    const left = buttonRect.left - parentRect.left + (buttonRect.width / 2);
    const top = buttonRect.top - parentRect.top - 70;
    
    bubbleElement.style.left = `${left}px`;
    bubbleElement.style.top = `${top}px`;
    bubbleElement.style.transform = 'translateX(-50%)';
    
    // Store reference to bubble element
    this._tutorialState.bubbleElement = bubbleElement;
  }

  private _removeTutorialBubble(): void {
    const existingBubble = document.querySelector('.tutorial-bubble');
    if (existingBubble) {
      existingBubble.remove();
    }
    
    if (this._tutorialState.bubbleElement) {
      this._tutorialState.bubbleElement.remove();
      this._tutorialState.bubbleElement = null;
    }
    
    // Remove highlighting classes
    this.classList.remove('highlighting-dice', 'highlighting-anvil');
    
    // Clear cycle timer
    this._clearCycleTimer();
  }

  private _handleBubbleClick(target: TutorialTarget): void {
    const timeElapsed = Date.now() - this._tutorialState.showTime;
    
    this._trackAnalytics('tutorial_click_bubble', {
      line: this._tutorialState.currentLine,
      target,
      ms_since_show: timeElapsed
    });
    
    this._completeTutorial(target);
  }

  private _handleIconClick(target: TutorialTarget): void {
    const timeElapsed = Date.now() - this._tutorialState.showTime;
    
    this._trackAnalytics('tutorial_click_icon', {
      line: this._tutorialState.currentLine,
      target,
      ms_since_show: timeElapsed
    });
    
    this._completeTutorial(target);
  }

  private _completeTutorial(completionMethod: TutorialTarget): void {
    const totalTime = Date.now() - this._tutorialState.showTime;
    
    this._trackAnalytics('tutorial_complete', {
      completion: completionMethod,
      line: this._tutorialState.currentLine,
      ms_total: totalTime,
      tutorial_version: TUTORIAL_VERSION
    });
    
    this._markCompleted();
    this._removeTutorialBubble();
    this._cleanup();
  }

  private _cleanup(): void {
    if (this._initTimeout) {
      clearTimeout(this._initTimeout);
    }
    
    this._clearCycleTimer();
    
    if (this._intersectionObserver) {
      this._intersectionObserver.disconnect();
    }
    
    this._removeTutorialBubble();
    
    this._tutorialState = {
      isActive: false,
      currentStatblock: null,
      currentTarget: null,
      currentLine: '',
      showTime: 0,
      bubbleElement: null
    };
  }

  private _trackAnalytics(eventName: string, params: any): void {
    trackEvent(eventName, params);
  }

  render() {
    return html`<!-- StatblockTutorial renders tutorial bubbles via DOM manipulation -->`;
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'statblock-tutorial': StatblockTutorial;
  }
}