import { LitElement, html, css } from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';
import { SiteCssMixin } from '../utils/css-adoption.js';
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
        "Your nemesis draws near..."
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
    `;

    firstUpdated() {
        // Adopt site CSS for access to CSS variables and other site styles
        this.adoptSiteCss();

        // Add event listeners for button interactions
        this.addEventListener('reroll-click', this._handleButtonClick.bind(this));
        this.addEventListener('forge-click', this._handleButtonClick.bind(this));

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

    private _newsletterClick() {
        window.open('https://buttondown.com/cordialgerm', '_blank');
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
            </div>
            <monster-statblock
                class="${statblockClass}"
                id="showcase-statblock"
                monster-key="${effectiveMonsterKey || ''}"
                ?random="${!effectiveMonsterKey}"
            ></monster-statblock>
        `;
    }
}
