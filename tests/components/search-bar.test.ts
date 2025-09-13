import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fixture, html, expect as chaiExpect, oneEvent } from '@open-wc/testing';
import { SearchBar } from '../../docs/src/components/SearchBar.js';
import '../setup.js';

// Mock analytics
vi.mock('../../docs/src/utils/analytics.js', () => ({
    trackSearch: vi.fn()
}));

// Register the component
import '../../docs/src/components/SearchBar.js';

describe('SearchBar Component', () => {
    let element: SearchBar;

    beforeEach(async () => {
        element = await fixture(html`<search-bar></search-bar>`);
    });

    describe('Basic Rendering', () => {
        it('should render with default props', async () => {
            expect(element).to.exist;

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            const button = element.shadowRoot?.querySelector('.search-button');

            expect(input).to.exist;
            expect(button).to.exist;
            expect(input.placeholder).to.equal('Search for monsters...');
            expect(button?.textContent?.trim()).to.include('Search');
        });

        it('should render with custom placeholder', async () => {
            element = await fixture(html`<search-bar placeholder="Custom placeholder..."></search-bar>`);

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            expect(input.placeholder).to.equal('Custom placeholder...');
        });

        it('should render with custom button text', async () => {
            element = await fixture(html`<search-bar button-text="Find"></search-bar>`);

            const button = element.shadowRoot?.querySelector('.search-button');
            expect(button?.textContent?.trim()).to.include('Find');
        });

        it('should render with initial value', async () => {
            element = await fixture(html`<search-bar initial-value="test query"></search-bar>`);

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            expect(input.value).to.equal('test query');
        });
    });

    describe('User Interaction', () => {
        it('should update value when typing', async () => {
            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;

            input.value = 'dragon';
            input.dispatchEvent(new Event('input'));

            await element.updateComplete;

            expect(element.getSearchValue()).to.equal('dragon');
        });

        it('should dispatch search-query event on button click in event mode', async () => {
            element = await fixture(html`<search-bar mode="event"></search-bar>`);

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            const button = element.shadowRoot?.querySelector('.search-button') as HTMLButtonElement;

            input.value = 'test search';
            input.dispatchEvent(new Event('input'));

            const eventPromise = oneEvent(element, 'search-query');
            button.click();

            const event = await eventPromise;
            expect(event.detail.query).to.equal('test search');
        });

        it('should dispatch search-navigate event on button click in navigation mode', async () => {
            element = await fixture(html`<search-bar mode="navigation"></search-bar>`);

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            const button = element.shadowRoot?.querySelector('.search-button') as HTMLButtonElement;

            input.value = 'test navigation';
            input.dispatchEvent(new Event('input'));

            const eventPromise = oneEvent(element, 'search-navigate');
            button.click();

            const event = await eventPromise;
            expect(event.detail.query).to.equal('test navigation');
        });

        it('should dispatch search event on Enter key', async () => {
            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;

            input.value = 'enter search';
            input.dispatchEvent(new Event('input'));

            const eventPromise = oneEvent(element, 'search-query');

            const keydownEvent = new KeyboardEvent('keydown', { key: 'Enter' });
            input.dispatchEvent(keydownEvent);

            const event = await eventPromise;
            expect(event.detail.query).to.equal('enter search');
        });

        it('should not dispatch event for empty search', async () => {
            const button = element.shadowRoot?.querySelector('.search-button') as HTMLButtonElement;

            let eventFired = false;
            element.addEventListener('search-query', () => {
                eventFired = true;
            });

            button.click();

            // Wait a bit to ensure event doesn't fire
            await new Promise(resolve => setTimeout(resolve, 10));

            expect(eventFired).to.be.false;
        });
    });

    describe('Public Methods', () => {
        it('should set search value programmatically', async () => {
            element.setSearchValue('programmatic value');
            await element.updateComplete;

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            expect(input.value).to.equal('programmatic value');
            expect(element.getSearchValue()).to.equal('programmatic value');
        });

        it('should clear search value', async () => {
            element.setSearchValue('some value');
            await element.updateComplete;

            element.clearSearch();
            await element.updateComplete;

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            expect(input.value).to.equal('');
            expect(element.getSearchValue()).to.equal('');
        });

        it('should focus input when focusInput is called', async () => {
            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            const focusSpy = vi.spyOn(input, 'focus');

            element.focusInput();

            expect(focusSpy).toHaveBeenCalled();
        });
    });

    describe('Analytics', () => {
        it('should call trackSearch with correct parameters', async () => {
            const { trackSearch } = await import('../../docs/src/utils/analytics.js');

            element = await fixture(html`<search-bar analytics-surface="test-surface"></search-bar>`);

            const input = element.shadowRoot?.querySelector('.search-input') as HTMLInputElement;
            const button = element.shadowRoot?.querySelector('.search-button') as HTMLButtonElement;

            input.value = 'analytics test';
            input.dispatchEvent(new Event('input'));

            button.click();

            expect(trackSearch).toHaveBeenCalledWith('analytics test', 0, 'test-surface');
        });
    });
});
