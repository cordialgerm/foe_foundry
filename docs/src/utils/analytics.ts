
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

export type MonsterKeyType = 'monster' | 'template' | 'family';

export type PageType = 'homepage' | 'generator' | 'monster-page' | 'power' | 'blog-post' | 'codex' | 'other';

export interface AnalyticsParams {
  monster_key?: string;
  monster_key_type?: MonsterKeyType;
  monster_family?: string;
  monster_change_type?: StatblockChangeType;

  power_key?: string;

  export_format?: string;

  search_query?: string;
  search_result_count?: number;
  filter_type?: string;
  filter_value?: string;

  surface?: string;
  page_type?: PageType
}

/**
 * Track an analytics event
 */
export function trackEvent(name: string, params: AnalyticsParams = {}): void {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') return;

  if (!params.page_type) {
    params.page_type = getCurrentPageType();
  }

  // Track to Google Analytics if available and in production
  if (typeof window.gtag !== 'undefined' && import.meta.env.PROD) {
    window.gtag('event', name, params);
  }

  // Track to GrowthBook
  trackGrowthBookEvent(name, params);

  // Log in development for debugging
  if (!import.meta.env.PROD) {
    console.log('Analytics Event:', name, params);
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
export function trackRerollClick(monsterKey: string, surface?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
    monster_key_type: 'monster',
    surface: surface
  };


  trackEvent('reroll_button_click', params);
}

/**
 * Track forge button click
 */
export function trackForgeClick(monsterKey: string, surface?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
    monster_key_type: 'monster',
    surface: surface
  };

  trackEvent('forge_button_click', params);
}

/**
 * Track statblock view button click
 */
export function trackStatblockClick(monsterKey: string, surface?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
    monster_key_type: 'monster',
    surface: surface
  };

  trackEvent('statblock_button_click', params);
}

/**
 * Track statblock edit
 */
export function trackStatblockEdit(monsterKey: string, changeType: StatblockChangeType, powerKey?: string): void {
  trackEvent('statblock_edited', {
    monster_key: monsterKey,
    monster_key_type: 'monster',
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
    monster_key_type: 'monster'
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
export function trackSearch(query: string, resultCount?: number, surface?: string): void {
  const params: AnalyticsParams = {
    search_query: query,
    surface: surface
  };

  if (resultCount !== undefined) {
    params.search_result_count = resultCount;
  }

  trackEvent('search_performed', params);
}


export function trackMonsterClick(monsterKey: string, monsterKeyType: MonsterKeyType, surface?: string, query?: string): void {
  const params: AnalyticsParams = {
    monster_key: monsterKey,
    monster_key_type: monsterKeyType,
    surface: surface
  };

  if (query) {
    params.search_query = query;
  }

  trackEvent('monster_clicked', params);
}

/**
 * Track filter usage
 */
export function trackFilterUsage(filterType: string, filterValue: string, surface?: string): void {
  const params: AnalyticsParams = {
    filter_type: filterType,
    filter_value: filterValue,
    surface: surface
  };

  trackEvent('filter_used', params);
}
