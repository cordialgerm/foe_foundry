var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';
let PowerIcon = class PowerIcon extends LitElement {
    constructor() {
        super(...arguments);
        this.src = '';
        this.svgContent = '';
    }
    async connectedCallback() {
        super.connectedCallback();
        if (this.src) {
            try {
                const response = await fetch(this.src);
                if (response.ok) {
                    this.svgContent = await response.text();
                    this.requestUpdate();
                }
                else {
                    console.error(`Failed to load SVG: ${response.statusText}`);
                }
            }
            catch (error) {
                console.error(`Error fetching SVG: ${error}`);
            }
        }
    }
    render() {
        return html `<div .innerHTML=${this.svgContent}></div>`;
    }
};
PowerIcon.styles = css `
    :host {
      display: inline-block;
      width: 24px;
      height: 24px;
    }
    svg {
      width: 100%;
      height: 100%;
    }
  `;
__decorate([
    property()
], PowerIcon.prototype, "src", void 0);
PowerIcon = __decorate([
    customElement('power-icon')
], PowerIcon);
export { PowerIcon };
