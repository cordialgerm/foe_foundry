import { html, css, LitElement } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { StatblockButton } from './StatblockButton.js';
import { trackDownloadClick } from '../utils/analytics.js';
import './SvgIcon.js';
import './ExportDialog.js';

@customElement('download-button')
export class DownloadButton extends StatblockButton {

    @state()
    dialogOpen = false;

    /**
     * Jiggle behavior for the icon. Can be:
     * - 'jiggleOnHover' (or true/"true" for backwards compatibility)
     * - 'jiggleUntilClick'
     */
    @property()
    jiggle: 'jiggleOnHover' | 'jiggleUntilClick' | boolean | 'true' = 'true';

    static styles = css`
        :host {
            display: inline-block;
            position: relative;
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
            transform: scale(1.05);
        }

        button:active:not(:disabled) {
            transform: scale(0.95);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        svg-icon {
            width: 3rem;
            height: 3rem;
            color: var(--fg-color);
        }
    `;

    private _handleClick(): void {
        if (this.disabled || !this.monsterKey) return;

        // Track analytics event
        trackDownloadClick(this.monsterKey);

        // Dispatch custom event to notify parent components
        this.dispatchEvent(new CustomEvent('download-click', {
            detail: {
                target: this.target,
                monsterKey: this.monsterKey
            },
            bubbles: true,
            composed: true
        }));

        // Open the export dialog
        this.dialogOpen = true;
    }

    private _handleDialogClose(): void {
        this.dialogOpen = false;
    }

    private _handleExport(event: CustomEvent): void {
        const { exportType, format } = event.detail;
        const statblock = this.findTargetStatblock();
        
        if (!statblock) {
            console.error('No target statblock found for export');
            return;
        }

        if (exportType === 'print-preview') {
            this._openPrintPreview(statblock);
        } else if (exportType === 'markdown') {
            this._downloadMarkdown(statblock, format);
        }

        // Close dialog after export
        this.dialogOpen = false;
    }

    private _openPrintPreview(statblock: any): void {
        // Create a new window with the statblock in print-preview mode
        const baseUrl = (window as any).baseUrl || '';
        
        // Build URL with current state parameters
        const params = new URLSearchParams();
        params.set('monster-key', statblock.monsterKey || '');
        if (statblock.hpMultiplier && statblock.hpMultiplier !== 1) {
            params.set('hp-multiplier', statblock.hpMultiplier.toString());
        }
        if (statblock.damageMultiplier && statblock.damageMultiplier !== 1) {
            params.set('damage-multiplier', statblock.damageMultiplier.toString());
        }
        if (statblock.powers) {
            params.set('powers', statblock.powers);
        }

        const printUrl = `${baseUrl}/print-preview/?${params.toString()}`;
        window.open(printUrl, '_blank', 'width=800,height=1000,scrollbars=yes,resizable=yes');
    }

    private async _downloadMarkdown(statblock: any, format: string): Promise<void> {
        try {
            const baseUrl = (window as any).baseUrl || '';
            
            // Prepare the POST payload with current statblock state
            const payload = {
                monster_key: statblock.monsterKey || statblock.getEffectiveMonsterKey(),
                powers: statblock.powers ? statblock.powers.split(',').map((p: string) => p.trim()).filter((p: string) => p) : [],
                hp_multiplier: statblock.hpMultiplier || 1,
                damage_multiplier: statblock.damageMultiplier || 1
            };

            const response = await fetch(`${baseUrl}/api/v1/statblocks/generate?output=${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Failed to generate markdown: ${response.statusText}`);
            }

            const markdown = await response.text();
            
            // Create and trigger download
            const blob = new Blob([markdown], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            
            const formatNames: Record<string, string> = {
                'md_5esrd': 'Simple-Markdown',
                'md_gmbinder': 'GMBinder',
                'md_homebrewery': 'Homebrewery',
                'md_blackflag': 'Black-Flag'
            };
            
            const monsterName = payload.monster_key.replace(/[^a-zA-Z0-9-_]/g, '-');
            const formatName = formatNames[format] || format;
            const filename = `${monsterName}-${formatName}.md`;
            
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error downloading markdown:', error);
            // Could dispatch an error event here for user feedback
        }
    }

    render() {
        return html`
            <button
                @click=${this._handleClick}
                ?disabled=${this.disabled}
                aria-label="Export this monster"
                title="Export this monster"
            >
                <svg-icon src="cloud-download" .jiggle=${this.jiggle}></svg-icon>
            </button>
            
            ${this.dialogOpen ? html`
                <export-dialog
                    @close=${this._handleDialogClose}
                    @export=${this._handleExport}
                ></export-dialog>
            ` : ''}
        `;
    }
}

declare global {
    interface HTMLElementTagNameMap {
        'download-button': DownloadButton;
    }
}