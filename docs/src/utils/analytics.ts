
/// <reference types="vite/client" />
/**
 * Analytics tracking utility for Foe Foundry
 * Provides a centralized wrapper around Google Analytics 4 (GA4) and GrowthBook
 */

import { StatblockChangeType } from '../data/monster.js';
import { trackGrowthBookEvent } from './growthbook.js';

// Global gtag type declaration
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}

export type PageType = 'homepage' | 'generator' | 'monster-page' | 'power' | 'blog-post' | 'codex' | 'other';

export interface AnalyticsParams {
  monster_key?: string;
  monster_change_type?: StatblockChangeType;
  power_key?: string;
  export_format?: string;
  search_query?: string;
  search_result_count?: number;
  monster_family?: string;
  tab?: string;
  filter_type?: string;
  filter_value?: string;
  click_context?: string;
}

/**
 * Track an analytics event
 */
export function trackEvent(name: string, params: AnalyticsParams = {}): void {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') return;

  const pageType = getCurrentPageType();
  const args = {
    page_type: pageType,
    ...params
  };

  // Track to Google Analytics if available and in production
  if (typeof window.gtag !== 'undefined' && import.meta.env.PROD) {
    window.gtag('event', name, args);
  }

  // Track to GrowthBook
  trackGrowthBookEvent(name, args);

  // Log in development for debugging
  if (!import.meta.env.PROD) {
    console.log('Analytics Event:', name, args);
  }
}

/**
 * Get the current page type based on the URL path
 */
export function getCurrentPageType(): PageType {
  if (typeof window === 'undefined') return 'other';

  const path = window.location.pathname;

  if (path === '/' || path === '/index.html') {
    return 'homepage';
  } else if (path.includes('/generate/')) {
    return 'generator';
  } else if (path.includes('/monsters/')) {
    return 'monster-page';
  } else if (path.includes('/powers/')) {
    return 'power';
  } else if (path.includes('/blog/')) {
    return 'blog-post';
  } else if (path === '/codex/' || path === '/codex') {
    return 'codex';
  } else {
    return 'other';
  }
}

/**
 * Track reroll button click
 */
export function trackRerollClick(monsterKey: string, tab?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
  };
  
  if (tab) {
    params.tab = tab;
  }
  
  trackEvent('reroll_button_click', params);
}

/**
 * Track forge button click
 */
export function trackForgeClick(monsterKey: string, tab?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
  };
  
  if (tab) {
    params.tab = tab;
  }
  
  trackEvent('forge_button_click', params);
}

/**
 * Track statblock view button click
 */
export function trackStatblockClick(monsterKey: string, tab?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
  };
  
  if (tab) {
    params.tab = tab;
  }
  
  trackEvent('statblock_button_click', params);
}

/**
 * Track statblock edit
 */
export function trackStatblockEdit(monsterKey: string, changeType: StatblockChangeType, powerKey?: string): void {
  trackEvent('statblock_edited', {
    monster_key: monsterKey,
    monster_change_type: changeType,
    power_key: powerKey,
  });
}

/**
 * Track download button click
 */
export function trackDownloadClick(monsterKey: string, format?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
  };
  
  // Add format type if provided
  if (format) {
    params.export_format = format;
  }
  
  trackEvent('download_button_click', params);
}

/**
 * Track email subscribe click
 */
export function trackEmailSubscribeClick(): void {
  trackEvent('email_subscribe_click');
}

/**
 * Track search performed
 */
export function trackSearch(query: string, resultCount?: number, tab?: string): void {
  const params: AnalyticsParams = {
    search_query: query,
  };
  
  if (resultCount !== undefined) {
    params.search_result_count = resultCount;
  }
  
  if (tab) {
    params.tab = tab;
  }
  
  trackEvent('search_performed', params);
}

/**
 * Track monster click (family, search result, etc.)
 */
export function trackMonsterClick(monsterKey: string, context: string, tab?: string, familyName?: string, query?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
    click_context: context,
  };
  
  if (tab) {
    params.tab = tab;
  }
  
  if (familyName) {
    params.monster_family = familyName;
  }
  
  if (query) {
    params.search_query = query;
  }
  
  trackEvent('monster_clicked', params);
}

/**
 * Track filter usage
 */
export function trackFilterUsage(filterType: string, filterValue: string, tab?: string): void {
  const params: AnalyticsParams = {
    filter_type: filterType,
    filter_value: filterValue,
  };
  
  if (tab) {
    params.tab = tab;
  }
  
  trackEvent('filter_used', params);
}

// Legacy functions for backward compatibility - these can be deprecated later
/**
 * @deprecated Use trackSearch() instead
 */
export function trackCodexSearch(query: string, resultCount: number): void {
  trackSearch(query, resultCount, 'search');
}

/**
 * @deprecated Use trackMonsterClick() instead
 */
export function trackCodexMonsterFamilyClick(monsterKey: string, familyName: string): void {
  trackMonsterClick(monsterKey, 'family', 'browse', familyName);
}

/**
 * @deprecated Use trackMonsterClick() instead
 */
export function trackCodexSearchResultClick(monsterKey: string, query?: string): void {
  trackMonsterClick(monsterKey, 'search_result', 'search', undefined, query);
}

/**
 * @deprecated Use trackForgeClick() instead
 */
export function trackCodexForgeClick(monsterKey: string, tab: 'browse' | 'search'): void {
  trackForgeClick(monsterKey, tab);
}

/**
 * @deprecated Use trackStatblockClick() instead
 */
export function trackCodexStatblockClick(monsterKey: string, tab: 'browse' | 'search'): void {
  trackStatblockClick(monsterKey, tab);
}

/**
 * @deprecated Use trackFilterUsage() instead
 */
export function trackCodexFilterUsage(filterType: string, filterValue: string): void {
  trackFilterUsage(filterType, filterValue, 'search');
}
