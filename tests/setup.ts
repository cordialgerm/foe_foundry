import { vi } from 'vitest';

// Mock the CSS adoption utility to avoid errors in tests
vi.mock('../docs/src/utils/css-adoption.js', () => ({
  SiteCssMixin: (base: any) => base,
  adoptExternalCss: vi.fn()
}));

// Mock analytics
vi.mock('../docs/src/utils/analytics.js', () => ({
  trackStatblockEdit: vi.fn()
}));

// Set up global test environment
global.HTMLElement = global.HTMLElement || class {};
global.customElements = global.customElements || {
  define: vi.fn(),
  get: vi.fn()
};

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn()
}));

// Mock ResizeObserver
global.ResizeObserver = vi.fn(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn()
}));