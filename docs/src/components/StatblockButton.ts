import { LitElement } from 'lit';
import { property } from 'lit/decorators.js';
import { MonsterStatblock } from './MonsterStatblock.js';

/**
 * Base class for buttons that operate on statblocks.
 */
export abstract class StatblockButton extends LitElement {
    @property({ type: String })
    target = '';

    @property({ type: Boolean, reflect: true })
    disabled = false;

    findTargetStatblock(): MonsterStatblock | null {
        if (!this.target) return null;

        // First try the main document
        let element = document.getElementById(this.target);

        // Button and target are siblings within the same shadow DOM
        if (!element) {
            const rootNode = this.getRootNode() as Document | ShadowRoot;
            if (rootNode && rootNode !== document) {
                element = rootNode.getElementById?.(this.target) || null;
            }
        }

        if (!element) return null;

        return element as MonsterStatblock;
    }

    get monsterKey(): string | null {
        const statblock = this.findTargetStatblock();
        const key = statblock?.getEffectiveMonsterKey() || null;
        return key;
    }
}
