import Raty from '../raty/raty.js';
import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

@customElement('monster-rating')
export class MonsterRating extends LitElement {

    @property()
    onClass = 'rating-on';

    @property()
    offClass = 'rating-off';

    @property({ type: Array })
    hints = ['Very Low', 'Low', 'Medium', 'High', 'Very High'];

    @property({ type: Number })
    score = 3;

    @property({ type: Number })
    number = 5;

    @property()
    starType = 'i';

    @property()
    emoji = '❤️'; // Default emoji is a heart

    @state()
    private currentLabel = 'Medium';

    @state()
    private isInitialized = false;

    @state()
    private previousScore: number | null = null;

    private raty?: Raty;

    static styles = css`
        .rating-container i {
            font-style: normal;
            /* Prevent italic */
            font-size: 1.2rem;
            margin: 0 2px;
            cursor: pointer;
            user-select: none;
            transition: transform 0.15s ease;
        }

        .rating-container i:hover {
            transform: scale(1.2);
        }

        .rating-label {
            font-weight: bold;
            min-width: 80px;
        }
    `;

    private updateEmojiStyles() {
        // Remove any existing dynamic style
        const existingStyle = this.shadowRoot?.querySelector('#emoji-style');
        if (existingStyle) {
            existingStyle.remove();
        }

        // Create new style element with current emoji
        const style = document.createElement('style');
        style.id = 'emoji-style';
        style.textContent = `
            .rating-container i.rating-on::before {
                content: '${this.emoji}';
            }
            .rating-container i.rating-off::before {
                content: '${this.emoji}';
                opacity: 0.3;
            }
        `;
        this.shadowRoot?.appendChild(style);
    }

    firstUpdated() {
        this.updateEmojiStyles();
        this.initializeRating();
    }

    private initializeRating() {
        const container = this.shadowRoot?.querySelector('.rating-container');
        if (!container) return;

        // Reset initialization state
        this.isInitialized = false;
        this.previousScore = null;

        if (this.raty) {
            this.raty.cancel(true); // Clean up previous instance
            container.innerHTML = ''; // Ensure previous elements are removed
        }

        // Set initial label
        this.currentLabel = this.hints[this.score - 1] || '';

        this.raty = new Raty(container as HTMLElement, {
            number: this.number,
            starType: this.starType,
            score: this.score,
            starOn: this.onClass,
            starOff: this.offClass,
            hints: [...this.hints],
            click: (score: number) => {
                this.currentLabel = this.hints[score - 1] || '';

                // Only fire event if the score actually changed and previousScore is set
                if (this.isInitialized && this.previousScore !== null && score !== this.previousScore) {
                    this.previousScore = score;
                    let event = new CustomEvent('rating-change', {
                        detail: { score, label: this.currentLabel },
                        bubbles: true,
                        composed: true
                    });
                    this.dispatchEvent(event);
                } else if (this.isInitialized) {
                    // Update previousScore even if we don't fire an event
                    this.previousScore = score;
                }
            }
        });
        this.raty.init();
        this.previousScore = this.score; // Set initial previous score
        this.isInitialized = true;
    }

    updated(changedProperties: Map<string | number | symbol, unknown>) {
        // Update emoji styles if emoji changed
        if (changedProperties.has('emoji')) {
            this.updateEmojiStyles();
        }

        // Re-initialize if key properties change
        if (changedProperties.has('hints') ||
            changedProperties.has('score') ||
            changedProperties.has('number')) {
            this.initializeRating();
        }
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        // Clean up if needed
        this.raty = undefined;
    }

    getScore(): number | null {
        return this.raty?.getScore() ?? null;
    }

    setScore(score: number): void {
        this.raty?.setScore(score);
        this.currentLabel = this.hints[score - 1] || '';
    }

    render() {
        return html`
            <span class="rating-wrapper">
                <span class="rating-container"></span>
                <span class="rating-label">${this.currentLabel}</span>
            </span>
        `;
    }
}