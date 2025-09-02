# Lit.js Component Testing

This directory contains unit tests for the Lit.js components in the Foe Foundry project.

## Overview

The testing setup includes:
- **Vitest** as the test runner with TypeScript support
- **Mock data stores** to replace the real API calls
- **Component logic tests** for core functionality
- **Integration tests** to verify interface compatibility

## Running Tests

```bash
# Run all tests once
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Test Structure

```
tests/
├── components/          # Component-specific tests
├── data/               # Data layer tests  
├── integration/        # Integration tests
├── mocks/             # Mock implementations
└── setup.ts           # Test environment setup
```

## Mock Data Stores

The mock data stores replace the real API calls for testing:

### MockPowerStore
- Implements the `PowerStore` interface
- Provides test data for power loadouts
- Supports custom test data setup

### MockMonsterStore  
- Implements the `MonsterStore` interface
- Provides test data for monsters and statblocks
- Supports custom test data setup

## Writing Tests

### Basic Component Test

```typescript
import { describe, it, expect } from 'vitest';

describe('Component Name', () => {
  it('should have expected behavior', () => {
    // Test logic here
    expect(true).toBe(true);
  });
});
```

### Using Mock Stores

```typescript
import { MockPowerStore } from '../mocks/index.js';

describe('Component with Data', () => {
  let mockStore: MockPowerStore;

  beforeEach(() => {
    mockStore = new MockPowerStore();
  });

  it('should work with mock data', async () => {
    const loadouts = await mockStore.getPowerLoadouts('test-monster');
    expect(loadouts).not.toBeNull();
  });
});
```

### Custom Test Data

```typescript
// Set up custom mock data
mockStore.setMockData('custom-monster', [
  {
    key: 'custom-loadout',
    name: 'Custom Loadout',
    // ... other properties
  }
]);

// Clear mock data after test
mockStore.clearMockData();
```

## CI/CD Integration

Tests are automatically run in the GitHub Actions workflow:
- JavaScript tests run before Python tests
- Tests must pass for CI to succeed
- Coverage reports are generated

## Best Practices

1. **Test core logic** rather than DOM manipulation
2. **Use mock stores** instead of real API calls
3. **Test interface compatibility** to ensure mocks match real implementations
4. **Set up and tear down** test data properly
5. **Keep tests focused** on single responsibilities

## Extending Tests

To add tests for new components:

1. Create a new test file in `tests/components/`
2. Import necessary mocks from `tests/mocks/`
3. Write focused tests for core functionality
4. Add integration tests if the component uses data stores

## Troubleshooting

If tests fail to run:
1. Check that all dependencies are installed: `npm ci`
2. Verify TypeScript configuration in `tsconfig.test.json`
3. Check Vitest configuration in `vitest.config.mjs`
4. Ensure mock setup is correct in `tests/setup.ts`