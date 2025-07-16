import { LitElement, html } from 'lit';
import { customElement } from 'lit/decorators.js';
import { provide } from '@lit/context';
import { powerContext } from './context';
import { initializeMockPowerStore } from './mock';

@customElement('app-root')
export class AppRoot extends LitElement {

    @provide({ context: powerContext })
    powerStore = initializeMockPowerStore();

    render() {
        return html`<slot></slot>`;
    }
}