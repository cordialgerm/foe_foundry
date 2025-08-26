import { LitElement, html, css } from 'lit';
import { customElement } from 'lit/decorators.js';
import { trackEvent } from '../utils/analytics.js';

// Tutorial copy library
const TUTORIAL_COPY = {
  dice: [
    "Not tough enough for your party? Roll again.",
    "Your PCs need a real challenge. Click me to re-roll.",
    "Not what you're looking for? Roll for a fresh take."
  ],
  anvil: [
    "Think you can forge a nastier foe? Try it out!",
    "Forge the perfect foe with a couple clicks.",
    "Tired of boring statblocks? Forge an unforgettable foe."
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
  private _scrollCheckInterval?: number;
  private _currentButton?: Element;
  private _lastBubblePosition = { top: 0, left: 0 };

  static styles = css`
    :host {
      position: relative;
      z-index: 1000;
      pointer-events: none;
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

    // Random duration between 7-9 seconds (8 +/- 1)
    const randomDelay = 7000 + (Math.random() * 2000);

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

      // Restart the timer to keep it running continuously
      this._startCycleTimer();
    }, randomDelay);
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

    // Store current button reference
    this._currentButton = button;

    // Create bubble element
    const bubble = document.createElement('div');
    bubble.className = 'tutorial-bubble';

    // Add inline styles since the bubble will be outside the shadow DOM
    this._applyBubbleStyles(bubble);

    // Create the text element without animation initially
    bubble.innerHTML = `<p class="tutorial-text" style="margin: 0; white-space: normal; line-height: 1.4; border-right: 2px solid var(--tertiary-color, #c29a5b); animation: blink 1s step-end infinite;"></p>`;

    // Start the typewriter effect
    this._startTypewriterEffect(bubble.querySelector('.tutorial-text') as HTMLElement, text);

    // Position bubble relative to button
    this._positionBubble(bubble, button);

    // Add click handlers
    bubble.addEventListener('click', () => this._handleBubbleClick(target));
    button.addEventListener('click', () => this._handleIconClick(target));

    // Find the statblock container and append bubble there
    let container: Element | null = button.closest('monster-statblock');
    if (!container) {
      container = document.body;
    }
    container.appendChild(bubble);

    // Add highlighting class to host
    this.classList.add(`highlighting-${target}`);

    // Start scroll monitoring
    this._startScrollMonitoring();

    // Track analytics
    this._trackAnalytics('tutorial_bubble_shown', {
      line: text,
      target,
      visibility_ratio: this._visibilityMap.get(this._tutorialState.currentStatblock!) || 0
    });
  }

  private _startTypewriterEffect(textElement: HTMLElement, fullText: string): void {
    let currentIndex = 0;
    const baseTypingSpeed = 50; // base milliseconds per character

    const typeNextCharacter = () => {
      if (currentIndex < fullText.length) {
        textElement.textContent = fullText.substring(0, currentIndex + 1);
        currentIndex++;

        // Add random delay of +/- 5ms for more natural typing
        const randomDelay = baseTypingSpeed + (Math.random() * 10 - 5);
        setTimeout(typeNextCharacter, randomDelay);
      } else {
        // Typing complete, stop cursor blinking
        textElement.style.borderRight = '2px solid transparent';
        textElement.style.animation = 'none';
      }
    };

    typeNextCharacter();
  }

  private _positionBubble(bubble: Element, button: Element): void {
    const buttonRect = button.getBoundingClientRect();
    const bubbleElement = bubble as HTMLElement;

    // Find the monster-statblock container for proper positioning
    let statblockContainer: Element | null = button.closest('monster-statblock');

    let newTop: number;
    let newLeft: number;
    let transform: string;

    if (statblockContainer) {
      // Position relative to the statblock container
      const containerRect = statblockContainer.getBoundingClientRect();

      // Check available space and choose positioning
      const viewportWidth = window.innerWidth;
      const bubbleWidth = 220; // Fixed width from CSS
      const spaceOnRight = viewportWidth - containerRect.right;
      const spaceOnLeft = containerRect.left;

      let positionedOnRight = true;

      if (spaceOnRight >= bubbleWidth + 32) {
        // Position to the right of the statblock
        newLeft = containerRect.right + 16;
        newTop = buttonRect.top + (buttonRect.height / 2);
        transform = 'translateY(-50%)';
        positionedOnRight = true;
      } else if (spaceOnLeft >= bubbleWidth + 32) {
        // Position to the left of the statblock
        newLeft = containerRect.left - bubbleWidth - 16;
        newTop = buttonRect.top + (buttonRect.height / 2);
        transform = 'translateY(-50%)';
        positionedOnRight = false;
      } else {
        // Fallback to above the button if no side space
        newLeft = buttonRect.left + (buttonRect.width / 2);
        newTop = buttonRect.top - 70;
        transform = 'translateX(-50%)';
        positionedOnRight = true; // Use default arrow
      }

      // Add class to indicate arrow direction
      if (positionedOnRight) {
        bubbleElement.classList.add('arrow-left');
        bubbleElement.classList.remove('arrow-right');
      } else {
        bubbleElement.classList.add('arrow-right');
        bubbleElement.classList.remove('arrow-left');
      }

      // Ensure it doesn't go above or below viewport
      const bubbleTop = buttonRect.top + (buttonRect.height / 2);
      if (bubbleTop < 80) {
        newTop = 80;
        transform = positionedOnRight ? 'translateY(0)' : 'translateY(0)';
      } else if (bubbleTop > window.innerHeight - 80) {
        newTop = window.innerHeight - 80;
        transform = positionedOnRight ? 'translateY(-100%)' : 'translateY(-100%)';
      }
    } else {
      // Fallback to original positioning if no statblock container found
      newLeft = buttonRect.left + (buttonRect.width / 2);
      newTop = buttonRect.top - 70;
      transform = 'translateX(-50%)';
      bubbleElement.classList.add('arrow-top');
    }

    // Only update position if there's a meaningful change (reduce jitter)
    const positionThreshold = 3; // pixels
    const topDiff = Math.abs(newTop - this._lastBubblePosition.top);
    const leftDiff = Math.abs(newLeft - this._lastBubblePosition.left);

    if (topDiff > positionThreshold || leftDiff > positionThreshold) {
      bubbleElement.style.position = 'fixed';
      bubbleElement.style.left = `${newLeft}px`;
      bubbleElement.style.top = `${newTop}px`;
      bubbleElement.style.transform = transform;

      // Update tracked position
      this._lastBubblePosition = { top: newTop, left: newLeft };
    }

    // Store reference to bubble element
    this._tutorialState.bubbleElement = bubbleElement;
  }

  private _startScrollMonitoring(): void {
    // Clear any existing scroll monitoring
    this._stopScrollMonitoring();

    // Check scroll position every 150ms for smoother animation (reduced frequency)
    this._scrollCheckInterval = window.setInterval(() => {
      this._checkBubbleVisibility();
    }, 150);
  }

  private _stopScrollMonitoring(): void {
    if (this._scrollCheckInterval) {
      clearInterval(this._scrollCheckInterval);
      this._scrollCheckInterval = undefined;
    }
  }

  private _checkBubbleVisibility(): void {
    if (!this._tutorialState.isActive || !this._tutorialState.bubbleElement || !this._currentButton) {
      return;
    }

    // Check if current button is still visible and reasonably positioned
    const buttonRect = this._currentButton.getBoundingClientRect();
    const isButtonVisible = buttonRect.top >= 0 &&
      buttonRect.bottom <= window.innerHeight &&
      buttonRect.left >= 0 &&
      buttonRect.right <= window.innerWidth;

    if (!isButtonVisible) {
      // Current button is not visible, find the closest visible button
      const closestVisibleButton = this._findClosestVisibleButton();
      if (closestVisibleButton) {
        // Move bubble to the closest visible button
        this._repositionBubbleToButton(closestVisibleButton);
      } else {
        // No visible buttons, hide bubble temporarily but keep timer running
        this._temporarilyHideBubble();
      }
    } else {
      // Button is visible, ensure bubble is properly positioned
      this._ensureBubblePosition();
    }
  }

  private _findClosestVisibleButton(): Element | null {
    let closestButton: Element | null = null;
    let closestDistance = Infinity;

    // Check all statblocks for visible buttons
    for (const statblock of this._statblocks) {
      const visibility = this._visibilityMap.get(statblock) || 0;
      if (visibility < 0.1) continue; // Skip barely visible statblocks

      const buttons = this._findButtonsInStatblock(statblock);
      for (const button of buttons) {
        const buttonRect = button.getBoundingClientRect();
        const isVisible = buttonRect.top >= 0 &&
          buttonRect.bottom <= window.innerHeight &&
          buttonRect.left >= 0 &&
          buttonRect.right <= window.innerWidth;

        if (isVisible) {
          // Calculate distance from center of viewport
          const viewportCenterY = window.innerHeight / 2;
          const buttonCenterY = buttonRect.top + buttonRect.height / 2;
          const distance = Math.abs(viewportCenterY - buttonCenterY);

          if (distance < closestDistance) {
            closestDistance = distance;
            closestButton = button;
          }
        }
      }
    }

    return closestButton;
  }

  private _repositionBubbleToButton(newButton: Element): void {
    if (!this._tutorialState.bubbleElement) return;

    // Update current button reference
    this._currentButton = newButton;

    // Update tutorial state to match new button
    const newTarget = newButton.tagName.toLowerCase() === 'reroll-button' ? 'dice' : 'anvil' as TutorialTarget;
    this._tutorialState.currentTarget = newTarget;

    // Update statblock reference
    const newStatblock = newButton.closest('monster-statblock');
    if (newStatblock) {
      this._tutorialState.currentStatblock = newStatblock;
    }

    // Use requestAnimationFrame for smoother position updates
    requestAnimationFrame(() => {
      // Reposition the bubble
      this._positionBubble(this._tutorialState.bubbleElement!, newButton);

      // Update highlighting
      this.classList.remove('highlighting-dice', 'highlighting-anvil');
      this.classList.add(`highlighting-${newTarget}`);

      // Show bubble if it was hidden
      if (this._tutorialState.bubbleElement!.style.display === 'none') {
        this._tutorialState.bubbleElement!.style.display = 'block';
      }
    });
  }

  private _temporarilyHideBubble(): void {
    if (this._tutorialState.bubbleElement) {
      this._tutorialState.bubbleElement.style.display = 'none';
    }
    // Remove highlighting while hidden
    this.classList.remove('highlighting-dice', 'highlighting-anvil');
  }

  private _ensureBubblePosition(): void {
    if (!this._tutorialState.bubbleElement || !this._currentButton) return;

    // Use requestAnimationFrame for smoother updates
    requestAnimationFrame(() => {
      // Reposition bubble to ensure it stays next to the button
      this._positionBubble(this._tutorialState.bubbleElement!, this._currentButton!);

      // Ensure bubble is visible
      if (this._tutorialState.bubbleElement!.style.display === 'none') {
        this._tutorialState.bubbleElement!.style.display = 'block';

        // Restore highlighting
        if (this._tutorialState.currentTarget) {
          this.classList.add(`highlighting-${this._tutorialState.currentTarget}`);
        }
      }
    });
  }

  private _applyBubbleStyles(bubble: HTMLElement): void {
    // Apply all the CSS styles inline since the bubble is outside the shadow DOM
    bubble.style.cssText = `
      position: fixed;
      background: var(--bg-color, #1a1a1a);
      border: 2px solid var(--tertiary-color, #c29a5b);
      border-radius: 12px;
      padding: 8px 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-family: var(--primary-font, system-ui);
      font-size: 0.9rem;
      color: var(--fg-color, #f4f1e6);
      min-width: 220px;
      max-width: 250px;
      min-height: 50px;
      max-height: 80px;
      z-index: 1001;
      pointer-events: auto;
      cursor: pointer;
      animation: popIn 0.25s ease-out;
      white-space: normal;
      line-height: 1.4;
      transition: top 0.2s ease-out, left 0.2s ease-out, transform 0.2s ease-out;
    `;

    // Add pseudo-element styles via a style element for the arrow
    const style = document.createElement('style');
    style.textContent = `
      @keyframes popIn {
        from { transform: scale(0.8); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
      @keyframes blink {
        from, to { border-color: transparent }
        50% { border-color: var(--tertiary-color, #c29a5b) }
      }
      .tutorial-bubble.arrow-left::after {
        content: '';
        position: absolute;
        border: 8px solid transparent;
        border-left-color: var(--bg-color, #1a1a1a);
        top: 50%;
        left: -8px;
        transform: translateY(-50%);
      }
      .tutorial-bubble.arrow-left::before {
        content: '';
        position: absolute;
        border: 9px solid transparent;
        border-left-color: var(--tertiary-color, #c29a5b);
        top: 50%;
        left: -9px;
        transform: translateY(-50%);
        z-index: -1;
      }
      .tutorial-bubble.arrow-right::after {
        content: '';
        position: absolute;
        border: 8px solid transparent;
        border-right-color: var(--bg-color, #1a1a1a);
        top: 50%;
        right: -8px;
        transform: translateY(-50%);
      }
      .tutorial-bubble.arrow-right::before {
        content: '';
        position: absolute;
        border: 9px solid transparent;
        border-right-color: var(--tertiary-color, #c29a5b);
        top: 50%;
        right: -9px;
        transform: translateY(-50%);
        z-index: -1;
      }
      .tutorial-bubble.arrow-top::after {
        content: '';
        position: absolute;
        border: 8px solid transparent;
        border-top-color: var(--bg-color, #1a1a1a);
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
      }
      .tutorial-bubble.arrow-top::before {
        content: '';
        position: absolute;
        border: 9px solid transparent;
        border-top-color: var(--tertiary-color, #c29a5b);
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        z-index: -1;
      }
    `;

    // Add the style to the document head if it doesn't exist
    if (!document.querySelector('#tutorial-bubble-styles')) {
      style.id = 'tutorial-bubble-styles';
      document.head.appendChild(style);
    }
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

    // Stop scroll monitoring
    this._stopScrollMonitoring();

    // Clear current button reference
    this._currentButton = undefined;

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
    this._stopScrollMonitoring();

    if (this._intersectionObserver) {
      this._intersectionObserver.disconnect();
    }

    this._removeTutorialBubble();

    // Remove injected styles
    const styleElement = document.querySelector('#tutorial-bubble-styles');
    if (styleElement) {
      styleElement.remove();
    }

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