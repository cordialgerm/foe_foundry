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

        // If no target is specified, check if inside shadow DOM and get the host MonsterStatblock
        if (!this.target) {
            const rootNode = this.getRootNode() as Document | ShadowRoot;
            if (rootNode && rootNode !== document && 'host' in rootNode) {
                // We're in a shadow DOM, check if the host is a MonsterStatblock
                const host = rootNode.host;
                if (host && host.tagName.toLowerCase() === 'monster-statblock') {
                    return host as MonsterStatblock;
                }
            }
            return null;
        }

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
