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
    private showSearchInterface = false;

    private timerDuration = 0;
    private timerStartTime = 0;
    private timerAnimationId: number | null = null;
    private messageInterval: number | null = null;
    private intersectionObserver: IntersectionObserver | null = null;
    private timerHasCompletedOnce = false;

    private readonly messages = [
        "A worthy foe approaches...",
        "A deadly foe approaches...",
        "A formidable enemy emerges...",
        "Something sinister stirs...",
        "A dangerous creature awakens...",
        "Your nemesis draws near...",
        "Looking for something specific?",
        "Discover monsters by theme!",
        "Find the perfect foe!"
    ];

    private getMonsterKeyFromUrl(): string | null {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('monster-key') || urlParams.get('template');
    }

    static styles = css`
        :host {
            display: block;
            font-size: var(--header-font-size);
        }

        .showcase-container {
            padding: 4rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 2rem;
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
            margin-bottom: 1rem;
            text-align: center;
        }

        .instructions {
            color: var(--bg-color);
            margin-bottom: 1rem;
            text-align: center;
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
            max-width: 300px;
            text-align: center;
            cursor: pointer;
            padding-bottom: 20px;
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

        .search-interface {
            margin-top: 1rem;
            padding: 1.5rem;
            border: 2px solid var(--tertiary-color, #c29a5b);
            border-radius: 12px;
            background: rgba(26, 26, 26, 0.8);
            backdrop-filter: blur(4px);
            max-width: 500px;
            width: 100%;
            display: none;
            animation: slideIn 0.3s ease-out;
        }

        .search-interface.visible {
            display: block;
        }

        .search-interface-header {
            color: var(--bg-color);
            font-family: var(--header-font);
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .search-interface-description {
            color: var(--bg-color);
            font-size: 0.9rem;
            margin-bottom: 1rem;
            text-align: center;
            opacity: 0.8;
        }

        .search-interface search-bar {
            --fg-color: var(--bg-color);
            --muted-color: rgba(255, 255, 255, 0.1);
            --tertiary-color: var(--primary-color);
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

        // Add event listener for search events
        this.addEventListener('search-query', this._handleSearchQuery.bind(this));
        this.addEventListener('search-navigate', this._handleSearchNavigate.bind(this));

        // Set up intersection observer to detect when component comes into view
        this.setupIntersectionObserver();
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        this.cleanupTimer();
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
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

        // Decide whether to show search interface or normal timer
        // 30% chance to show search interface instead of normal timer
        const shouldShowSearchInterface = Math.random() < 0.3;
        
        if (shouldShowSearchInterface) {
            this._showSearchInterface();
            return;
        }

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

    private _showSearchInterface() {
        // Set a search-related message
        const searchMessages = this.messages.slice(-3); // Last 3 are search-related
        this.currentMessage = searchMessages[Math.floor(Math.random() * searchMessages.length)];
        
        this.showSearchInterface = true;
        this.timerActive = false;
        this.timerHasCompletedOnce = true; // Prevent timer from starting again
        
        // Hide search interface after 15 seconds
        setTimeout(() => {
            this.showSearchInterface = false;
        }, 15000);
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

    private _newsletterClick() {
        window.open('https://buttondown.com/cordialgerm', '_blank');
    }

    private _handleSearchQuery(event: CustomEvent) {
        // Handle search-query event from SearchBar
        const query = event.detail.query;
        if (query) {
            // Navigate to search page with the query
            window.location.href = `/powers/all/?q=${encodeURIComponent(query)}`;
        }
    }

    private _handleSearchNavigate(event: CustomEvent) {
        // Handle search-navigate event from SearchBar  
        const query = event.detail.query;
        if (query) {
            // Navigate to search page with the query
            window.location.href = `/powers/all/?q=${encodeURIComponent(query)}`;
        }
    }

    render() {
        const effectiveMonsterKey = this.monsterKey || this.getMonsterKeyFromUrl();
        const statblockClass = effectiveMonsterKey ? '' : 'hidden';
        const timerClass = this.timerActive ? '' : 'hidden';

        return html`
            <div class="showcase-container bg-object scroll">
                <span class="lead">Summon Your First Foe</span>
                <p class="instructions">Roll the <strong>Die</strong> below to summon a random monster, click the <strong>Anvil</strong> to forge it into the perfect foe, or read the <strong>Tome</strong> for DM tips and tricks.</p>
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
                        title="Subscribe to the Foe Foundry Newsletter"
                        src="death-note"
                        jiggle="jiggleUntilClick"
                        class="showcase-button newsletter"
                        @click="${this._newsletterClick}"
                    >
                    </svg-icon-button>
                </div>
                <div class="timer-container ${timerClass}" @click="${this._handleTimerClick}">
                    <div class="timer-message">${this.currentMessage}</div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${this.timerProgress}%"></div>
                    </div>
                </div>
                
                <div class="search-interface ${this.showSearchInterface ? 'visible' : ''}">
                    <div class="search-interface-header">Discover Monsters</div>
                    <div class="search-interface-description">${this.currentMessage}</div>
                    <search-bar 
                        placeholder="Search for undead, fiends, dragons..."
                        button-text="Search"
                        mode="event"
                        seeds="3"
                        analytics-surface="generator-showcase">
                    </search-bar>
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
