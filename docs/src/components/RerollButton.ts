import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import './SvgIcon';

@customElement('reroll-button')
export class RerollButton extends LitElement {

    @property({ type: String })
    target = '';

    @property({ type: Boolean, reflect: true })
    disabled = false;

    @property({ type: Boolean, reflect: true })
    rolling = false;

    private static stylesInjected = false;

    static styles = css`
    :host {
      display: inline-block;
      position: absolute;
      top: -0.5rem;
      right: -4rem;
    }

    button {
      font-size: 3rem;
      background: none;
      border: none;
      cursor: pointer;
      padding: 8px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
      color: var(--fg-color);
    }

    button:hover:not(:disabled) {
      background-color: rgba(255, 255, 255, 0.1);
      transform: scale(1.05);
    }

    button:active:not(:disabled) {
      transform: scale(0.95);
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      color: inherit;
    }

    .d20-icon {
      width: 3rem;
      height: 3rem;
      color: var(--primary-color, #007bff);
      fill: var(--fg-color);
    }

    /* Rolling animation for the button */
    :host([rolling]) button {
      animation: roll-dice 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Rolling animation for the d20 icon */
    :host([rolling]) .d20-icon {
      animation: roll 0.6s cubic-bezier(0.4, 0, 0.2, 1) 1;
    }

    @keyframes roll {
      0% {
        transform: rotate(0deg);
      }
      25% {
        transform: rotate(90deg) scale(1.1);
      }
      50% {
        transform: rotate(180deg) scale(1.2);
      }
      75% {
        transform: rotate(270deg) scale(1.1);
      }
      100% {
        transform: rotate(360deg);
      }
    }

    @keyframes roll-dice {
      0% {
        transform: rotate(0deg) scale(1);
      }
      50% {
        transform: rotate(720deg) scale(1.2);
      }
      70% {
        transform: rotate(720deg) scale(0.95);
      }
      85% {
        transform: rotate(720deg) scale(1.05) translateX(-2px);
      }
      95% {
        transform: rotate(720deg) scale(1.02) translateX(2px);
      }
      100% {
        transform: rotate(720deg) scale(1) translateX(0);
      }
    }

    /* Hover effect: glow + gentle jiggle */
    button:hover:not(:disabled) .d20-icon {
      filter: drop-shadow(0 0 5px var(--box-shadow-color));
      animation: jiggle 0.6s cubic-bezier(0.4, 0, 0.2, 1) 1;
    }

    @keyframes jiggle {
      0% {
        transform: rotate(0deg) translateX(0);
      }
      25% {
        transform: rotate(1.5deg) translateX(1px);
      }
      50% {
        transform: rotate(0deg) translateX(0);
      }
      75% {
        transform: rotate(-1.5deg) translateX(-1px);
      }
      100% {
        transform: rotate(0deg) translateX(0);
      }
    }

    /* On small screens: stack below */
    @media (max-width: 600px) {
      :host {
        position: static;
        display: block;
        margin: 1rem auto 0 auto;
      }
    }
  `;

    connectedCallback() {
        super.connectedCallback();
        this._injectGlobalStyles();
        this._setupStatblock();
    }

    private _injectGlobalStyles() {
        // Only inject once, even if multiple RerollButton instances exist
        if (RerollButton.stylesInjected) return;

        const styleSheet = document.createElement('style');
        styleSheet.id = 'reroll-button-global-styles';
        styleSheet.textContent = `
            /* Styles for Pop Out / In when rerolling */
            @keyframes pop-out {
                from {
                    transform: scale(1);
                    opacity: 1;
                }
                to {
                    transform: scale(0.95);
                    opacity: 0;
                }
            }

            @keyframes pop-in {
                from {
                    transform: scale(1.05);
                    opacity: 0;
                }
                to {
                    transform: scale(1);
                    opacity: 1;
                }
            }

            .stat-block.pop-out {
                animation: pop-out 0.2s forwards;
            }

            .stat-block.pop-in {
                animation: pop-in 0.2s forwards;
            }

            @keyframes summon-flash {
                0% {
                    box-shadow: 0 0 0 0 var(--primary-color);
                }
                10% {
                    box-shadow: 0 0 4px 1px var(--primary-color);
                }
                30% {
                    box-shadow: 0 0 8px 3px var(--primary-color);
                }
                50% {
                    box-shadow: 0 0 12px 6px var(--primary-color);
                }
                70% {
                    box-shadow: 0 0 8px 3px var(--primary-color);
                }
                90% {
                    box-shadow: 0 0 4px 1px var(--primary-color);
                }
                100% {
                    box-shadow: 0 0 0 0 var(--primary-color);
                }
            }

            @keyframes scale-throb {
                0% {
                    transform: scale(1);
                }
                40% {
                    transform: scale(1.025);
                }
                60% {
                    transform: scale(1.015);
                }
                100% {
                    transform: scale(1);
                }
            }

            @keyframes summon-fade {
                0%, 100% {
                    opacity: 1;
                    filter: brightness(1);
                }
                50% {
                    opacity: 0.8;
                    filter: brightness(1.3);
                }
            }

            .stat-block.summon-effect {
                animation:
                    summon-flash 0.4s ease,
                    scale-throb 0.4s ease,
                    summon-fade 0.4s ease;
            }
        `;

        document.head.appendChild(styleSheet);
        RerollButton.stylesInjected = true;
    }

    get monsterKey() {
        const statblock = this.findTargetStatblock();
        return statblock?.dataset.monster || '';
    }

    findTargetStatblock() {
        return this.target ? document.getElementById(this.target) : null;
    }

    private _setupStatblock() {
        const statblock = this.findTargetStatblock();
        if (statblock && !statblock.closest('.statblock-wrapper')) {
            this._wrapStatblock(statblock);
        }
    }

    private _wrapStatblock(statblock: Element) {
        // Wrap statblock in a container to position the button relative to it
        const wrapper = document.createElement('div');
        wrapper.className = 'statblock-wrapper';
        wrapper.setAttribute('data-monster', statblock.getAttribute('data-monster') || '');

        // Apply wrapper styles directly since it's not in shadow DOM
        Object.assign(wrapper.style, {
            position: 'relative'
        });

        // Apply responsive styles for small screens
        const mediaQuery = window.matchMedia('(max-width: 600px)');
        const updateWrapperStyles = (e: MediaQueryListEvent | MediaQueryList) => {
            if (e.matches) {
                // Small screen styles
                Object.assign(wrapper.style, {
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center'
                });
            } else {
                // Large screen styles
                Object.assign(wrapper.style, {
                    display: '',
                    flexDirection: '',
                    alignItems: ''
                });
            }
        };

        updateWrapperStyles(mediaQuery);
        mediaQuery.addEventListener('change', updateWrapperStyles);

        statblock.parentNode?.insertBefore(wrapper, statblock);
        wrapper.appendChild(statblock);
        wrapper.appendChild(this);
    }

    private async _rerollStatblock() {
        const statblock = this.findTargetStatblock();
        if (!statblock) return;

        const monsterKey = statblock.getAttribute('data-monster');
        if (!monsterKey) return;

        const url = `/api/v1/statblocks/${monsterKey}?output=monster_only`;

        statblock.classList.add("pop-out");

        try {
            const res = await fetch(url);
            const html = await res.text();

            // Parse the new statblock HTML into a DOM element
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newStatblock = doc.querySelector('.stat-block');

            if (newStatblock) {
                // Preserve the same HTML ID
                newStatblock.id = statblock.id;

                // Replace old with new
                statblock.replaceWith(newStatblock);
                newStatblock.classList.add("pop-in");

                // Wait for pop-in animation, then trigger summon effect
                await this._sleep(200);
                newStatblock.classList.remove("pop-in");

                // wait a little bit before starting summon effect
                await this._sleep(200);
                newStatblock.classList.add("summon-effect");

                // Remove summon-effect after it's done
                await this._sleep(400);
                newStatblock.classList.remove("summon-effect");
            }
        } catch (err) {
            console.error("Failed to reroll monster:", err);
        }
    }

    private _sleep(ms: number) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    private _handleClick() {
        if (this.disabled || this.rolling || !this.monsterKey) return;

        // Trigger the rolling animation
        this.rolling = true;
        this.disabled = true;

        // Remove rolling state after animation completes
        setTimeout(() => {
            this.rolling = false;
            this.disabled = false;
        }, 600); // Match the animation duration

        // Perform the reroll
        this._rerollStatblock();
    }

    render() {
        return html`
      <button
        @click=${this._handleClick}
        ?disabled=${this.disabled}
        aria-label="Reroll this monster"
        title="Reroll this monster"
      >
        <svg-icon
          src="d20"
          class="d20-icon"
          jiggle="true"
        ></svg-icon>
      </button>
    `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'reroll-button': RerollButton;
    }
}