
import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import { MonsterCard } from '../components/MonsterCard';
import { initializeMonsterStore } from '../data/api';
import { Power } from '../data/powers';
import { StatblockChange, StatblockChangeType } from '../data/monster';
import { Task } from '@lit/task';
import { Monster, RelatedMonster } from '../data/monster';

@customElement('monster-builder')
export class MonsterBuilder extends LitElement {
    static styles = css`
    :host {
      display: block;
    }
    .monster-header {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }
    .monster-title {
      font-size: 2.5rem !important;
      font-weight: bold;
      margin-top: 3px;
      margin-bottom: 3px;
    }
    .nav-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .nav-pill {
      background: var(--bs-dark);
      color: var(--bs-light);
      border-radius: 999px;
      padding: 0.5rem;
      cursor: pointer;
      border: none;
      font-size: 1rem;
      transition: background 0.2s;
      min-width: 100px;
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      text-decoration: none;
      display: inline-block;
      text-align: center;
    }
    .nav-pill.active {
      background: var(--bs-light);
      color: var(--bs-dark);
      font-weight: bold;
    }
    .container {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      width: 100%;
    }
    .panels-row {
      display: flex;
      flex-direction: row;
      gap: 2rem;
      width: 100%;
    }
    .left-panel {
      flex: 0 0 400px;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .right-panel {
      flex: 1 1 auto;
      min-width: 0;
    }
    #statblock-holder {
      width: 100%;
      transition: height 0.3s cubic-bezier(0.4,0,0.2,1);
      overflow: hidden;
    }
    @keyframes pop-in {
        0% {
            transform: scale(1);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.2);
            opacity: 1;
        }
        100% {
            transform: scale(1);
            opacity: 1;
        }
    }
    .hp-changed,
    .damage-changed,
    .power-changed {
        color: rgb(255, 255, 122);
        animation: pop-in 0.8s ease;
        will-change: transform, opacity;
    }
    .loading,
    .error-message {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .loading p,
    .error-message p {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--bs-secondary, #6c757d);
        margin: 0;
        text-align: center;
    }
    .error-message p {
        color: var(--bs-danger, #dc3545);
    }
  `;

    // Use Lit Task for async monster loading
    private _monsterTask = new Task(this, {
        task: async ([monsterKey], { signal }) => {

            await this.adoptSiteCss();

            const store = initializeMonsterStore();
            const monster = await store.getMonster(monsterKey);

            if (monster === null) {
                throw new Error(`Monster not found for key "${monsterKey}"`);
            }

            return monster;
        },
        args: () => [this.monsterKey]
    });

    @property({ type: String, attribute: 'monster-key' })
    monsterKey: string = '';

    private monsters = initializeMonsterStore();

    private lastKnownHeight: number = 600;
    private heightTransitionCleanup: (() => void) | null = null;

    private captureCurrentHeight(): void {
        const container = this.shadowRoot?.querySelector('.container') as HTMLElement | null;
        if (container) {
            const currentHeight = container.offsetHeight;
            this.lastKnownHeight = Math.max(currentHeight, this.lastKnownHeight);
            console.log('Captured current height:', this.lastKnownHeight);
        }
    }

    // Unified height preservation for both monster and statblock changes
    private preserveHeightDuringTransition(): () => void {
        // Clean up any existing transition
        if (this.heightTransitionCleanup) {
            this.heightTransitionCleanup();
        }

        const container = this.shadowRoot?.querySelector('.container') as HTMLElement | null;
        if (!container) return () => { };

        // Capture current height and set it explicitly
        this.captureCurrentHeight();

        container.style.height = `${this.lastKnownHeight}px`;
        container.style.transition = 'height 0.3s cubic-bezier(0.4,0,0.2,1)';

        const cleanup = () => {
            if (container) {
                requestAnimationFrame(() => {
                    // Animate to natural height
                    const naturalHeight = `${container.scrollHeight}px`;
                    container.style.height = naturalHeight;

                    // Clean up after animation
                    const onTransitionEnd = (e: TransitionEvent) => {
                        if (e.target === container && e.propertyName === 'height') {
                            container.style.height = '';
                            container.style.transition = '';
                            container.removeEventListener('transitionend', onTransitionEnd);
                        }
                    };
                    container.addEventListener('transitionend', onTransitionEnd);
                });
            }
        };

        this.heightTransitionCleanup = cleanup;
        return cleanup;
    }

    private async waitForPowerLoadouts(monsterCard: MonsterCard): Promise<void> {
        // Wait for the monster card's power loadouts to be ready
        const maxAttempts = 20; // Maximum 2 seconds (20 * 100ms)
        let attempts = 0;

        while (attempts < maxAttempts) {
            const powerLoadouts = monsterCard.shadowRoot?.querySelectorAll('power-loadout') ?? [];

            if (powerLoadouts.length === 0) {
                // Power loadouts haven't rendered yet, wait and try again
                await new Promise(resolve => setTimeout(resolve, 100));
                attempts++;
                continue;
            }

            // Check if all power loadouts have loaded their powers and selected an initial power
            let allReady = true;
            for (let i = 0; i < powerLoadouts.length; i++) {
                const loadout = powerLoadouts[i] as any;
                const selectedPower = loadout.getSelectedPower?.();
                if (!selectedPower) {
                    allReady = false;
                    break;
                }
            }

            if (allReady) {
                return; // All power loadouts are ready
            }

            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }

        // If we get here, we've waited too long. Log a warning but continue.
        console.warn('Power loadouts did not fully load within timeout, proceeding anyway');
    }

    onMonsterKeyChanged(key: string) {
        // Preserve height during monster change
        this.preserveHeightDuringTransition();

        this.monsterKey = key;
        this.dispatchEvent(new CustomEvent('monster-key-changed', {
            detail: { monsterKey: key },
            bubbles: true,
            composed: true
        }));
    }

    // Handle statblock changes (same monster, different powers/multipliers)
    async onStatblockChanged(monsterCard: MonsterCard, eventDetail?: any) {
        if (!monsterCard) return;

        // Preserve height during statblock change
        const finishTransition = this.preserveHeightDuringTransition();

        const statblockHolder = this.shadowRoot?.getElementById('statblock-holder');
        if (statblockHolder) {
            statblockHolder.innerHTML = '';
        }

        // Get selected powers
        const selectedPowers = monsterCard.getSelectedPowers();

        // Highlight changed powers if present in event.detail.power
        let change: StatblockChange | null = null;
        if (eventDetail?.power && eventDetail.power.key) {
            change = {
                type: StatblockChangeType.PowerChanged,
                changedPower: eventDetail.power
            };
        }
        else if (eventDetail?.changeType === 'damage-changed') {
            change = {
                type: StatblockChangeType.DamageChanged,
                changedPower: null
            };
        }
        else if (eventDetail?.changeType === 'hp-changed') {
            change = {
                type: StatblockChangeType.HpChanged,
                changedPower: null
            };
        }

        await this.loadStatblock(monsterCard.monsterKey, selectedPowers, monsterCard.hpMultiplier, monsterCard.damageMultiplier, change);

        // Complete the height transition
        finishTransition();
    }

    // Handle initial monster load (after Task completes)
    private async onMonsterLoaded(monsterCard: MonsterCard) {
        // Wait for power loadouts to finish loading their powers
        await this.waitForPowerLoadouts(monsterCard);

        // For initial loads, just load the statblock without animation
        this.loadStatblock(monsterCard.monsterKey, monsterCard.getSelectedPowers(), monsterCard.hpMultiplier, monsterCard.damageMultiplier, null);

        // Complete any ongoing height transition and capture new height
        if (this.heightTransitionCleanup) {
            this.heightTransitionCleanup();
        }

        setTimeout(() => this.captureCurrentHeight(), 150);
    }

    async loadStatblock(monsterKey: string, powers: Power[], hpMultiplier: number = 1, damageMultiplier: number = 1, change: StatblockChange | null = null) {

        const request = {
            monsterKey: monsterKey,
            powers: powers,
            hpMultiplier: hpMultiplier,
            damageMultiplier: damageMultiplier,
        };

        const statblockElement = await this.monsters.getStatblock(request, change);

        const statblockHolder = this.shadowRoot?.getElementById('statblock-holder');
        if (statblockHolder && statblockElement) {
            statblockHolder.appendChild(statblockElement);
        }
    }

    async adoptSiteCss() {
        // Adopt site.css as a constructable stylesheet if supported
        const supportsAdopted = 'adoptedStyleSheets' in Document.prototype && 'replace' in CSSStyleSheet.prototype;
        if (supportsAdopted && this.shadowRoot) {
            try {
                const resp = await fetch('/css/site.css');
                const cssText = await resp.text();
                const sheet = new CSSStyleSheet();
                await sheet.replace(cssText);
                this.shadowRoot.adoptedStyleSheets = [sheet, ...this.shadowRoot.adoptedStyleSheets];
            } catch (e) {
                // fallback: do nothing, let Lit styles apply
            }
        } else if (this.shadowRoot) {
            // Fallback for browsers like Firefox: inject <style> tag
            fetch('/css/site.css').then(r => r.text()).then(cssText => {
                const style = document.createElement('style');
                style.textContent = cssText;
                this.shadowRoot?.prepend(style);
            });
        }
    }

    firstUpdated() {
        this.shadowRoot?.addEventListener('monster-changed', async (event: any) => {
            const monsterCard = event.detail.monsterCard;
            await this.onStatblockChanged(monsterCard, event.detail);
        });
    }

    renderMessage(message: string, messageClass: string = '') {
        console.log('Rendering message with height ', this.lastKnownHeight);
        return html`
            <div class="container pamphlet-main ${messageClass}" style="height: ${this.lastKnownHeight + 'px'}; overflow: hidden;">
                <p>${message}</p>
            </div>
        `;
    }

    renderContent(monster: Monster) {
        this.updateComplete.then(() => {
            const card = this.shadowRoot?.querySelector('monster-card') as MonsterCard | null;
            if (!card) return;
            this.onMonsterLoaded(card);
        });

        const previousTemplate = html`
        <a href="/generate?monster-key=${monster.previousTemplate.monsterKey}"
            @click=${(e: MouseEvent) => {
                e.preventDefault();
                this.onMonsterKeyChanged(monster.previousTemplate.monsterKey);
            }}
            style="font-size: 2rem; text-decoration: none; cursor: pointer; padding-right: 1rem; color: var(--primary-color)">
            &lt;
        </a>`;

        const nextTemplate = html`
        <a href="/generate?monster-key=${monster.nextTemplate.monsterKey}"
            @click=${(e: MouseEvent) => {
                e.preventDefault();
                this.onMonsterKeyChanged(monster.nextTemplate.monsterKey);
            }}
            style="font-size: 2rem; text-decoration: none; cursor: pointer; padding-left: 1rem; color: var(--primary-color)">
            &gt;
        </a>`;

        return html`
            <div class="container pamphlet-main">
                <div class="monster-header">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <h1 class="monster-title">
                            ${previousTemplate}
                            <span>${monster.monsterTemplateName}</span>
                            ${nextTemplate}
                        </h1>
                    </div>
                    <div class="nav-pills">
                        ${monster.relatedMonsters.map((rel: RelatedMonster) => html`
                            <a
                            href="/monsters/${rel.template}#${rel.key}"
                            class="nav-pill ${rel.key === this.monsterKey ? 'active' : ''}"
                            @click=${(e: MouseEvent) => {
                e.preventDefault();
                this.onMonsterKeyChanged(rel.key);
            }}
                            >${rel.name}</a>
                        `)}
                    </div>
                </div>
                <div class="panels-row">
                    <div class="left-panel">
                        <monster-card monster-key="${this.monsterKey}"></monster-card>
                    </div>
                    <div class="right-panel">
                        <div id="statblock-holder"></div>
                    </div>
                </div>
            </div>
            `;
    }

    render() {
        return this._monsterTask.render({
            pending: () => this.renderMessage('Loading...', 'loading'),
            error: (e) => this.renderMessage(`Error loading monster: ${e}`, 'error-message'),
            complete: (monster: Monster) => this.renderContent(monster)
        })
    }


}
