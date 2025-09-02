import { html, css, LitElement } from 'lit';
import { customElement, property } from 'lit/decorators.js';
import './SvgIcon.js';

@customElement('export-dialog')
export class ExportDialog extends LitElement {

    static styles = css`
        :host {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .dialog {
            background: var(--bg-color);
            color: var(--fg-color);
            border-radius: 8px;
            padding: 2rem;
            min-width: 400px;
            max-width: 500px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
            border: 1px solid var(--tertiary-color);
        }

        .dialog-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid var(--tertiary-color);
            padding-bottom: 1rem;
        }

        .dialog-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .close-button {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.25rem;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--fg-color);
        }

        .export-options {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .export-option {
            background: var(--muted-color);
            border: 1px solid var(--tertiary-color);
            border-radius: 6px;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .export-option:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .export-option:active {
            transform: translateY(0);
        }

        .option-icon {
            font-size: 1.5rem;
            width: 1.5rem;
            height: 1.5rem;
            color: var(--fg-color);
        }

        .option-content {
            flex: 1;
        }

        .option-title {
            font-weight: 600;
            margin: 0 0 0.25rem 0;
        }

        .option-description {
            font-size: 0.875rem;
            margin: 0;
        }

        .dialog-footer {
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--tertiary-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            color: var(--fg-color);
        }

        .help-link {
            color: var(--primary-color);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }

        .help-link:hover {
            text-decoration: underline;
        }

        .help-icon {
            width: 1rem;
            height: 1rem;
        }
    `;

    private _handleBackdropClick(event: Event): void {
        if (event.target === this) {
            this._close();
        }
    }

    private _close(): void {
        this.dispatchEvent(new CustomEvent('close', {
            bubbles: true,
            composed: true
        }));
    }

    private _handleExport(exportType: string, format?: string): void {
        this.dispatchEvent(new CustomEvent('export', {
            detail: { exportType, format },
            bubbles: true,
            composed: true
        }));
    }

    private _handleKeyDown(event: KeyboardEvent): void {
        if (event.key === 'Escape') {
            this._close();
        }
    }

    connectedCallback(): void {
        super.connectedCallback();
        document.addEventListener('keydown', this._handleKeyDown.bind(this));
    }

    disconnectedCallback(): void {
        super.disconnectedCallback();
        document.removeEventListener('keydown', this._handleKeyDown.bind(this));
    }

    render() {
        return html`
            <div class="backdrop" @click=${this._handleBackdropClick}>
                <div class="dialog" @click=${(e: Event) => e.stopPropagation()}>
                    <div class="dialog-header">
                        <h3 class="dialog-title">
                            <svg-icon src="cloud-download"></svg-icon>
                            Export Monster
                        </h3>
                        <button class="close-button" @click=${this._close} aria-label="Close dialog">
                            <svg-icon src="x"></svg-icon>
                        </button>
                    </div>

                    <div class="export-options">
                        <div class="export-option" @click=${() => this._handleExport('print-preview')}>
                            <svg-icon class="option-icon" src="papers"></svg-icon>
                            <div class="option-content">
                                <div class="option-title">Print Preview</div>
                                <div class="option-description">Open in new window optimized for printing</div>
                            </div>
                        </div>

                        <div class="export-option" @click=${() => this._handleExport('markdown', 'md_5esrd')}>
                            <svg-icon class="option-icon" src="rule-book"></svg-icon>
                            <div class="option-content">
                                <div class="option-title">Export to Markdown (Simple)</div>
                                <div class="option-description">Standard markdown format for general use</div>
                            </div>
                        </div>

                        <div class="export-option" @click=${() => this._handleExport('markdown', 'md_homebrewery')}>
                            <svg-icon class="option-icon" src="stabbed-note"></svg-icon>
                            <div class="option-content">
                                <div class="option-title">Export to Markdown (Homebrewery)</div>
                                <div class="option-description">Format optimized for Homebrewery publishing</div>
                            </div>
                        </div>

                        <div class="export-option" @click=${() => this._handleExport('markdown', 'md_gmbinder')}>
                            <svg-icon class="option-icon" src="notebook"></svg-icon>
                            <div class="option-content">
                                <div class="option-title">Export to Markdown (GMBinder)</div>
                                <div class="option-description">Format optimized for GMBinder publishing</div>
                            </div>
                        </div>

                        <div class="export-option" @click=${() => this._handleExport('markdown', 'md_blackflag')}>
                            <svg-icon class="option-icon" src="evil-book"></svg-icon>
                            <div class="option-content">
                                <div class="option-title">Export to Markdown (Black Flag)</div>
                                <div class="option-description">Format optimized for Black Flag RPG</div>
                            </div>
                        </div>
                    </div>

                    <div class="dialog-footer">
                        <svg-icon class="help-icon" src="help-circle"></svg-icon>
                        <a href="/topics/exports/" class="help-link" target="_blank">
                            Learn more about export formats
                        </a>
                    </div>
                </div>
            </div>
        `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'export-dialog': ExportDialog;
    }
}