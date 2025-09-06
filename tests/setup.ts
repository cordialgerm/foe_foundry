import { vi } from 'vitest';
import { expect as chaiExpect } from '@open-wc/testing';

// Set up Chai with DOM testing capabilities for global access
(global as any).chaiExpect = chaiExpect;

// Mock the CSS adoption utility to avoid errors in tests
vi.mock('../docs/src/utils/css-adoption.js', () => ({
  SiteCssMixin: (base: any) => base,
  adoptExternalCss: vi.fn()
}));

// Mock analytics
vi.mock('../docs/src/utils/analytics.js', () => ({
  trackStatblockEdit: vi.fn(),
  trackSearch: vi.fn(),
  trackMonsterClick: vi.fn(),
  trackForgeClick: vi.fn(),
  trackFilterUsage: vi.fn(),
  trackStatblockClick: vi.fn(),
  trackDownloadClick: vi.fn(),
  trackEmailSubscribeClick: vi.fn(),
  trackRerollClick: vi.fn(),
  trackEvent: vi.fn(),
  getCurrentPageType: vi.fn().mockReturnValue('other')
}));

// Mock GrowthBook utilities
vi.mock('../docs/src/utils/growthbook.js', () => ({
  getFeatureFlags: vi.fn().mockResolvedValue({
    showTutorial: false,
    showStatblockDownloadOptions: false
  }),
  initGrowthBook: vi.fn().mockResolvedValue({
    isOn: vi.fn().mockReturnValue(false)
  })
}));

// Set up global test environment
(global as any).HTMLElement = global.HTMLElement || class { };
(global as any).customElements = global.customElements || {
  define: vi.fn(),
  get: vi.fn()
};

// Mock IntersectionObserver
(global as any).IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
  takeRecords: vi.fn().mockReturnValue([])
}));

// Mock ResizeObserver
(global as any).ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  disconnect: vi.fn(),
  unobserve: vi.fn()
}));

// Mock fetch to prevent network calls from SVG icon loading and API calls
(global as any).fetch = vi.fn().mockImplementation((url: string) => {
  // Mock SVG icon loading
  if (typeof url === 'string' && url.includes('/img/icons/')) {
    return Promise.resolve({
      ok: true,
      text: () => Promise.resolve('<svg><path d="M0,0 L10,10"></path></svg>')
    });
  }

  // Mock API calls to foefoundry.com to prevent real network calls
  if (typeof url === 'string' && url.includes('foefoundry.com')) {
    console.warn(`Mocking API call to: ${url}`);

    // Return mock API responses based on the endpoint
    if (url.includes('/loadouts')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      });
    }

    if (url.includes('/monsters/')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          key: 'test-monster',
          name: 'Test Monster',
          loadouts: []
        })
      });
    }

    if (url.includes('/statblocks/')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          statblock_html: '<div class="stat-block">Mock Statblock</div>'
        })
      });
    }

    // Default mock response for any other foefoundry.com API calls
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({})
    });
  }

  // Mock any other network calls to prevent real API calls
  console.warn(`Unmocked fetch call to: ${url}`);
  return Promise.reject(new Error(`Network call blocked in tests: ${url}`));
});