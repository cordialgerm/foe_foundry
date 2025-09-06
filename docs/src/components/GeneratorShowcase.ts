import { LitElement, html, css } from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';
import { SiteCssMixin } from '../utils/css-adoption.js';
import { MonsterSearchApi } from '../data/searchApi.js';
import { SearchSeed } from '../data/search.js';
import './RerollButton.js';
import './ForgeButton.js';
import './MonsterStatblock.js';

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
    private searchSeeds: SearchSeed[] = [];

    @state()
    private selectedSeeds: SearchSeed[] = [];

    @state()
    private showSearchSeeds = false;

    private searchApi = new MonsterSearchApi();
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
        "Looking for something specific? Try searching!",
        "Discover monsters by theme or environment!",
        "Find the perfect foe for your adventure!"
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

        .search-seeds-section {
            margin-top: 1rem;
            padding: 1rem;
            border: 2px solid var(--tertiary-color, #c29a5b);
            border-radius: 12px;
            background: rgba(26, 26, 26, 0.8);
            backdrop-filter: blur(4px);
            max-width: 500px;
            width: 100%;
            display: none;
            animation: slideIn 0.3s ease-out;
        }

        .search-seeds-section.visible {
            display: block;
        }

        .search-seeds-header {
            color: var(--bg-color);
            font-family: var(--header-font);
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            text-align: center;
        }

        .search-seeds-description {
            color: var(--bg-color);
            font-size: 0.9rem;
            margin-bottom: 1rem;
            text-align: center;
            opacity: 0.8;
        }

        .search-seeds-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            justify-content: center;
        }

        .search-seed-button {
            background: var(--color-surface-variant, #f5f5f5);
            border: 1px solid var(--tertiary-color, #c29a5b);
            border-radius: 20px;
            padding: 0.75rem 1.25rem;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            color: var(--fg-color, #f4f1e6);
            font-family: var(--primary-font, system-ui);
            font-weight: 500;
            min-width: 120px;
            text-align: center;
        }

        .search-seed-button:hover {
            background: var(--tertiary-color, #c29a5b);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .search-seed-button:active {
            transform: translateY(0);
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

        // Load search seeds
        this._loadSearchSeeds();

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

    private async _loadSearchSeeds(): Promise<void> {
        try {
            const seeds = await this.searchApi.getSearchSeeds();
            this.searchSeeds = seeds;
            // Select 3 random seeds for display
            this._selectRandomSeeds();
        } catch (error) {
            console.error('Failed to load search seeds:', error);
            this.searchSeeds = [];
        }
    }

    private _selectRandomSeeds(): void {
        if (this.searchSeeds.length === 0) return;
        
        // Shuffle and take first 3
        const shuffled = [...this.searchSeeds].sort(() => Math.random() - 0.5);
        this.selectedSeeds = shuffled.slice(0, 3);
    }

    private startTimer() {
        if (this.timerActive) return;

        // Decide whether to show search seeds or normal timer
        // 30% chance to show search seeds instead of normal timer
        const shouldShowSearchSeeds = Math.random() < 0.3 && this.selectedSeeds.length > 0;
        
        if (shouldShowSearchSeeds) {
            this._showSearchSeeds();
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

    private _showSearchSeeds() {
        // Set a search-related message
        const searchMessages = this.messages.slice(-3); // Last 3 are search-related
        this.currentMessage = searchMessages[Math.floor(Math.random() * searchMessages.length)];
        
        this.showSearchSeeds = true;
        this.timerActive = false;
        this.timerHasCompletedOnce = true; // Prevent timer from starting again
        
        // Hide search seeds after 10 seconds
        setTimeout(() => {
            this.showSearchSeeds = false;
        }, 10000);
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

    private _handleSearchSeedClick(seedTerm: string) {
        // Navigate to search page with the selected seed term
        window.location.href = `/powers/all/?q=${encodeURIComponent(seedTerm)}`;
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
                
                <div class="search-seeds-section ${this.showSearchSeeds ? 'visible' : ''}">
                    <div class="search-seeds-header">Discover Monsters</div>
                    <div class="search-seeds-description">${this.currentMessage}</div>
                    <div class="search-seeds-container">
                        ${this.selectedSeeds.map(seed => html`
                            <button 
                                class="search-seed-button"
                                @click=${() => this._handleSearchSeedClick(seed.term)}
                                title="${seed.description}"
                            >
                                ${seed.term}
                            </button>
                        `)}
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
