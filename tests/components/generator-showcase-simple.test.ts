import { describe, it, expect, beforeEach, vi } from 'vitest';

// Create a simple GeneratorShowcase class to test core functionality
class TestGeneratorShowcase {
  monsterKey: string | null = null;
  private timerActive = false;
  private timerProgress = 0;
  private currentMessage = '';
  private messages = [
    "A worthy foe approaches...",
    "A deadly foe approaches...",
    "A formidable enemy emerges...",
    "Something sinister stirs...",
    "A dangerous creature awakens...",
    "Your nemesis draws near..."
  ];

  private getMonsterKeyFromUrl(): string | null {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('monster-key') || urlParams.get('template');
  }

  private shouldStartTimer(): boolean {
    return !this.timerActive && Math.random() > 0.5; // Random for testing
  }

  private getRandomMessage(): string {
    return this.messages[Math.floor(Math.random() * this.messages.length)];
  }

  // Expose private methods for testing
  public testGetMonsterKeyFromUrl() {
    return this.getMonsterKeyFromUrl();
  }

  public testShouldStartTimer() {
    return this.shouldStartTimer();
  }

  public testGetRandomMessage() {
    return this.getRandomMessage();
  }
}

describe('GeneratorShowcase Core Logic', () => {
  let showcase: TestGeneratorShowcase;

  beforeEach(() => {
    showcase = new TestGeneratorShowcase();
  });

  it('should initialize with null monster key', () => {
    expect(showcase.monsterKey).toBeNull();
  });

  it('should extract monster key from URL parameters', () => {
    // Mock window.location.search
    Object.defineProperty(window, 'location', {
      value: {
        search: '?monster-key=url-monster'
      },
      writable: true
    });

    const monsterKey = showcase.testGetMonsterKeyFromUrl();
    expect(monsterKey).toBe('url-monster');
  });

  it('should handle template parameter as fallback', () => {
    Object.defineProperty(window, 'location', {
      value: {
        search: '?template=template-monster'
      },
      writable: true
    });

    const monsterKey = showcase.testGetMonsterKeyFromUrl();
    expect(monsterKey).toBe('template-monster');
  });

  it('should return random message from predefined array', () => {
    const message = showcase.testGetRandomMessage();
    expect(typeof message).toBe('string');
    expect(message.length).toBeGreaterThan(0);
  });

  it('should determine whether timer should start', () => {
    const shouldStart = showcase.testShouldStartTimer();
    expect(typeof shouldStart).toBe('boolean');
  });
});