import { LitElement, html, css } from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';
import { SiteCssMixin } from '../utils/css-adoption.js';
import './RerollButton.js';
import './ForgeButton.js';
import './MonsterStatblock.js';
import './SearchBar.js';

@customElement('generator-showcase')
export class GeneratorShowcase extends SiteCssMixin(LitElement) {
    @property({ type: String, attribute: 'monster-key' })
    monsterKey: string | null = null;

    @query('#showcase-statblock')
    private statblock!: HTMLElement;

    @state()
    private timerActive = false;

    @state()
    private timerProgress = 0;

    @state()
    private currentMessage = '';

    @state()
    private seedCount = this.getResponsiveSeedCount();

    private timerDuration = 0;
    private timerStartTime = 0;
    private timerAnimationId: number | null = null;
    private messageInterval: number | null = null;
    private intersectionObserver: IntersectionObserver | null = null;
    private timerHasCompletedOnce = false;
    private resizeObserver: ResizeObserver | null = null;

    private readonly messages = [
        "A worthy foe approaches...",
        "A deadly foe approaches...",
        "A formidable enemy emerges...",
        "Something sinister stirs...",
        "A dangerous creature awakens...",
        "Your nemesis draws near..."
    ];

    private getMonsterKeyFromUrl(): string | null {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('monster-key') || urlParams.get('template');
    }

    private getResponsiveSeedCount(): number {
        // Return 2 if mobile (768px or less), 3 otherwise
        return window.innerWidth <= 768 ? 2 : 3;
    }

    private handleResize() {
        const newSeedCount = this.getResponsiveSeedCount();
        if (newSeedCount !== this.seedCount) {
            this.seedCount = newSeedCount;
        }
    }

    static styles = css`
        :host {
            display: block;
            font-size: var(--header-font-size);
        }

        .showcase-container {
            padding-top: 5rem;
            padding-bottom: 5rem;
            padding-left: 1rem;
            padding-right: 1rem;
            position: relative;
            margin-bottom: 2rem;
        }

        .inner-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 1rem;
            margin-bottom: 1rem;
            margin-left: auto;
            margin-right: auto;
            padding: 1rem;
        }

        .showcase-controls {
            display: flex;
            gap: 0.5rem;
            padding: 0.5rem;
        }

        .lead {
            color: var(--bg-color);
            font-family: var(--header-font);
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            text-align: center;
            line-height: 1.2;
        }

        .instructions {
            color: var(--bg-color);
            margin-bottom: 1.5rem;
            text-align: center;
            font-size: 0.95rem;
            line-height: 1.4;
            padding: 0 0.5rem;
        }

        #showcase-statblock.hidden {
            display: none;
            margin-bottom: 2rem;
        }

        .showcase-button {
            --fg-color: var(--bg-color);
        }

        .timer-container {
            margin-top: 1rem;
            width: 100%;
            max-width: 280px;
            text-align: center;
            cursor: pointer;
            padding-bottom: 10px; /* Reduced bottom padding */
        }

        .timer-message {
            color: var(--bg-color);
            font-style: italic;
            margin-bottom: 0.5rem;
            min-height: 1.2em;
        }

        .progress-bar-container {
            width: 100%;
            height: 8px;
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background: var(--primary-color);
            border-radius: 4px;
            transition: width 0.1s ease;
        }

        .timer-container.hidden {
            display: none;
        }

        .search-interface-description {
            color: var(--bg-color);
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
            text-align: center;
            opacity: 0.8;
            padding: 0 0.5rem;
        }

        .search-interface {
            width: 100%;
            max-width: 100%;
            margin-bottom: 1rem;
        }

        .search-interface search-bar {
            --fg-color: var(--bg-color);
            --muted-color: rgba(255, 255, 255, 0.1);
            --tertiary-color: var(--primary-color);
        }

        /* Mobile responsiveness improvements */
        @media (max-width: 768px) {

            .instructions {
                font-size: 0.9rem; /* Smaller instructions text */
                margin-bottom: 1.25rem;
                padding: 0 0.25rem;
            }

            .search-interface {
                width: 100%;
                max-width: none; /* Remove max-width constraints on mobile */
            }

            .search-interface-description {
                font-size: 0.85rem;
                margin-bottom: 0.5rem;
                padding: 0 0.25rem;
            }

            .showcase-controls {
                gap: 0.375rem; /* Reduced gap between buttons */
                padding: 0.375rem;
                flex-wrap: wrap; /* Allow wrapping on very small screens */
            }

            .timer-container {
                max-width: 260px; /* Smaller timer on mobile */
                padding-bottom: 5px;
            }
        }

        @media (max-width: 480px) {

            .instructions {
                font-size: 0.8rem;
            }

            .timer-container {
                max-width: 240px;
            }
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;

    firstUpdated() {
        // Adopt site CSS for access to CSS variables and other site styles
        this.adoptSiteCss();

        // Add event listeners for button interactions
        this.addEventListener('reroll-click', this._handleButtonClick.bind(this));
        this.addEventListener('forge-click', this._handleButtonClick.bind(this));

        // Add event listener for search events (cast to EventListener to fix TypeScript)
        this.addEventListener('search-query', this._handleSearchQuery.bind(this) as EventListener);
        this.addEventListener('search-navigate', this._handleSearchNavigate.bind(this) as EventListener);

        // Set up intersection observer to detect when component comes into view
        this.setupIntersectionObserver();

        // Set up resize observer for responsive seed count
        this.setupResizeObserver();
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        this.cleanupTimer();
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
    }

    private setupResizeObserver() {
        this.resizeObserver = new ResizeObserver(() => {
            this.handleResize();
        });
        this.resizeObserver.observe(document.body);
    }

    private setupIntersectionObserver() {
        this.intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting && this.shouldStartTimer()) {
                        this.startTimer();
                    }
                });
            },
            { threshold: 0.5 }
        );
        this.intersectionObserver.observe(this);
    }

    private shouldStartTimer(): boolean {
        const effectiveMonsterKey = this.monsterKey || this.getMonsterKeyFromUrl();
        return !effectiveMonsterKey && !this.timerActive && !this.timerHasCompletedOnce;
    }

    private startTimer() {
        if (this.timerActive) return;

        // Random timer duration between 7-9 seconds
        this.timerDuration = (Math.random() * 2 + 7) * 1000;
        this.timerStartTime = Date.now();
        this.timerActive = true;
        this.timerProgress = 0;

        // Start message cycling
        this.startMessageCycling();

        // Start progress animation
        this.animateProgress();
    }



    private startMessageCycling() {
        // Set initial message
        this.currentMessage = this.getRandomMessage();

        this.messageInterval = window.setInterval(() => {
            this.currentMessage = this.getRandomMessage();
        }, 1800);
    }

    private getRandomMessage(): string {
        return this.messages[Math.floor(Math.random() * this.messages.length)];
    }

    private animateProgress() {
        const updateProgress = () => {
            if (!this.timerActive) return;

            const elapsed = Date.now() - this.timerStartTime;
            const progress = Math.min(elapsed / this.timerDuration, 1);
            this.timerProgress = progress * 100;

            if (progress >= 1) {
                this.completeTimer();
            } else {
                this.timerAnimationId = requestAnimationFrame(updateProgress);
            }
        };

        this.timerAnimationId = requestAnimationFrame(updateProgress);
    }

    private completeTimer() {
        this.cleanupTimer();
        this.timerHasCompletedOnce = true;
        this.showStatblock();
    }

    private cleanupTimer() {
        this.timerActive = false;

        if (this.timerAnimationId) {
            cancelAnimationFrame(this.timerAnimationId);
            this.timerAnimationId = null;
        }

        if (this.messageInterval) {
            clearInterval(this.messageInterval);
            this.messageInterval = null;
        }
    }

    private showStatblock() {
        if (this.statblock && this.statblock.classList.contains('hidden')) {
            this.statblock.classList.remove('hidden');
        }
    }

    private _handleTimerClick() {
        if (this.timerActive) {
            this.completeTimer();
        }
    }

    private _handleButtonClick() {
        // Cancel timer if active
        if (this.timerActive) {
            this.cleanupTimer();
        }

        // Remove the hidden class from the statblock to show it
        this.showStatblock();
    }

    private _handleCodexClick() {
        window.location.href = '/codex/#browse';
    }

    private _handleSearchQuery(event: CustomEvent) {
        // Handle search-query event from SearchBar
        const query = event.detail.query;
        if (query) {
            // Navigate to codex search page with the query (query params must come before hash)
            window.location.href = `/codex/?query=${encodeURIComponent(query)}#search`;
        }
    }

    private _handleSearchNavigate(event: CustomEvent) {
        // Handle search-navigate event from SearchBar
        const query = event.detail.query;
        if (query) {
            // Navigate to codex search page with the query (query params must come before hash)
            window.location.href = `/codex/?query=${encodeURIComponent(query)}#search`;
        }
    }

    render() {
        const effectiveMonsterKey = this.monsterKey || this.getMonsterKeyFromUrl();
        const statblockClass = effectiveMonsterKey ? '' : 'hidden';
        const timerClass = this.timerActive ? '' : 'hidden';

        return html`
            <div class="showcase-container bg-object scroll">
                <div class="inner-container">
                    <span class="lead">Summon Your First Foe</span>
                    <div class="search-interface">
                        <div class="search-interface-description">Find the perfect foe for your campaign:</div>
                        <search-bar
                            placeholder="Search for undead, fiends, dragons..."
                            button-text="Search"
                            mode="event"
                            seeds="${this.seedCount}"
                            analytics-surface="generator-showcase">
                        </search-bar>
                    </div>

                    <p class="instructions">Roll the <strong>Die</strong> below to summon a random monster, click the <strong>Anvil</strong> to forge it into the perfect foe, or read the <strong>Codex</strong> to discover unique foes.</p>
                    <div class="showcase-controls">
                        <reroll-button
                            jiggle="jiggleUntilClick"
                            class="showcase-button"
                            target="showcase-statblock"
                            ?random="${!effectiveMonsterKey}">
                        </reroll-button>
                        <forge-button
                            jiggle="jiggleUntilClick"
                            class="showcase-button"
                            target="showcase-statblock">
                        </forge-button>
                        <svg-icon-button
                            title="Read the Foe Foundry Codex"
                            src="death-note"
                            jiggle="jiggleUntilClick"
                            class="showcase-button codex"
                            @click="${this._handleCodexClick}"
                        >
                        </svg-icon-button>
                    </div>
                    <div class="timer-container ${timerClass}" @click="${this._handleTimerClick}">
                        <div class="timer-message">${this.currentMessage}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar" style="width: ${this.timerProgress}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            <monster-statblock
                class="${statblockClass}"
                id="showcase-statblock"
                monster-key="${effectiveMonsterKey || ''}"
                hide-buttons
                ?random="${!effectiveMonsterKey}"
            ></monster-statblock>
        `;
    }
}
