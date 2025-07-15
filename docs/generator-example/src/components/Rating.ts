import Raty from './raty.js';
import { LitElement, html, css } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

@customElement('rating')
export class Rating extends LitElement {

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

    @state()
    private currentLabel = 'Medium';

    private raty?: Raty;

    static styles = css`
        .rating-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .rating-label {
            font-weight: bold;
            min-width: 80px;
        }
    `;

    firstUpdated() {
        this.initializeRating();
    }

    private initializeRating() {
        const container = this.shadowRoot?.querySelector('.rating-container');
        if (!container) return;

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
                this.dispatchEvent(new CustomEvent('rating-change', {
                    detail: { score, label: this.currentLabel },
                    bubbles: true
                }));
            }
        });

        this.raty.init();
    }

    updated(changedProperties: Map<string | number | symbol, unknown>) {
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
            <div class="rating-wrapper">
                <div class="rating-container"></div>
                <span class="rating-label">${this.currentLabel}</span>
            </div>
        `;
    }
}