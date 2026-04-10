# Test Generator 🧪

**AI-Powered Test Suite Creation for Quality & Testing**

The Test Generator is a comprehensive testing system that writes the tests you've been avoiding. It creates unit, integration, and E2E tests using Claude's Agent SDK to catch bugs before users do.

## 🌟 Key Features

- **Test Creation**: Automated generation of comprehensive test suites
- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Verify components work together correctly
- **E2E Tests**: Validate complete user workflows
- **Test Coverage**: Track and improve code coverage
- **Bug Prevention**: Catch issues before they reach production

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Test Types](#test-types)
- [CLI Usage](#cli-usage)
- [Test Templates](#test-templates)
- [Test Utilities](#test-utilities)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## 🚀 Installation

The Test Generator is already set up in this project with all dependencies:

```bash
# Dependencies are already installed
# To reinstall if needed:
npm install
```

**Included packages:**

- `jest` - Testing framework
- `ts-jest` - TypeScript support for Jest
- `@types/jest` - TypeScript definitions
- `@anthropic-ai/claude-agent-sdk` - AI-powered test generation

## ⚡ Quick Start

### 1. Run Existing Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- tests/unit/example.test.ts
```

### 2. Generate New Tests

```bash
# Generate unit tests for a file
npx ts-node tools/test-generator/index.ts src/example.ts

# Generate integration tests
npx ts-node tools/test-generator/index.ts -t integration src/example.ts

# Generate E2E tests
npx ts-node tools/test-generator/index.ts -t e2e src/example.ts

# Specify custom output location
npx ts-node tools/test-generator/index.ts -o tests/custom/my-test.ts src/example.ts
```

### 3. Check Coverage

```bash
# Generate coverage report
npm run test:coverage

# Open HTML coverage report
open coverage/lcov-report/index.html
```

## 🧪 Test Types

### Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Location**: `tests/unit/`

**When to use**:

- Testing pure functions
- Testing class methods
- Testing business logic
- Testing utilities and helpers

**Example**:

```typescript
describe('add function', () => {
  it('should add two numbers correctly', () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

### Integration Tests

**Purpose**: Verify multiple components work together

**Location**: `tests/integration/`

**When to use**:

- Testing data flow between components
- Testing API endpoints with database
- Testing service interactions
- Testing complex workflows

**Example**:

```typescript
describe('Calculator Integration', () => {
  it('should handle chained operations', () => {
    calculator.add(10, 5);
    calculator.subtract(20, 8);
    expect(calculator.getHistory()).toHaveLength(2);
  });
});
```

### E2E Tests

**Purpose**: Validate complete user workflows

**Location**: `tests/e2e/`

**When to use**:

- Testing full user journeys
- Testing critical business flows
- Testing UI interactions
- Testing system integration

**Example**:

```typescript
describe('User Registration Flow', () => {
  it('should complete full registration', async () => {
    await fillRegistrationForm();
    await submitForm();
    expect(await getUserStatus()).toBe('registered');
  });
});
```

## 💻 CLI Usage

The Test Generator CLI provides powerful options for test creation:

```bash
test-generator [options] <file-path>
```

### Options

| Option | Alias | Description | Default |
|--------|-------|-------------|---------|
| `--type` | `-t` | Test type: unit, integration, e2e | `unit` |
| `--output` | `-o` | Output path for test file | Auto-generated |
| `--coverage` | `-c` | Show coverage after generation | `false` |
| `--framework` | `-f` | Testing framework: jest, vitest, mocha | `jest` |
| `--help` | `-h` | Show help message | - |

### Examples

```bash
# Basic unit test generation
test-generator src/utils/math.ts

# Generate integration tests with coverage
test-generator -t integration -c src/api/users.ts

# Generate E2E tests with custom output
test-generator -t e2e -o tests/e2e/auth-flow.test.ts src/auth/login.ts

# Use different framework
test-generator -f vitest src/utils/validation.ts
```

## 📝 Test Templates

The Test Generator includes templates for common testing patterns:

### Available Templates

1. **Unit Test Template** - Basic unit testing structure
2. **Integration Test Template** - Multi-component testing
3. **E2E Test Template** - End-to-end user flows
4. **Async Test Template** - Testing async operations
5. **Mock Template** - Mocking external dependencies
6. **API Test Template** - Testing REST APIs
7. **Database Test Template** - Testing database operations

### Using Templates

Templates are located in `tools/test-generator/templates.ts`. You can use them directly:

```typescript
import { getTemplate } from './tools/test-generator/templates';

const unitTemplate = getTemplate('unit');
const integrationTemplate = getTemplate('integration');
```

## 🛠️ Test Utilities

The project includes comprehensive test utilities in `tests/utils/test-helpers.ts`:

### Mock Helpers

```typescript
import { createMock, createSpy } from '../utils/test-helpers';

const mockFunction = createMock<(x: number) => number>();
const spy = createSpy(object, 'methodName');
```

### Async Utilities

```typescript
import { waitFor, sleep } from '../utils/test-helpers';

await waitFor(() => condition === true, 5000);
await sleep(1000);
```

### Test Data Generators

```typescript
import { testData } from '../utils/test-helpers';

const randomEmail = testData.randomEmail();
const randomString = testData.randomString(10);
const randomNumber = testData.randomNumber(1, 100);
```

### Fixture Builder

```typescript
import { FixtureBuilder } from '../utils/test-helpers';

const userFixture = new FixtureBuilder({
  name: 'Test User',
  email: 'redacted@shadowtag-v4.local',
});

const user = userFixture.with({ name: 'John' }).build();
const users = userFixture.buildMany(5);
```

### Performance Testing

```typescript
import { performance } from '../utils/test-helpers';

const { result, duration } = await performance.measure(async () => {
  return await slowOperation();
});

await performance.assertTiming(() => operation(), 1000);
```

## ⚙️ Configuration

### Jest Configuration

Located in `jest.config.js`:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

### TypeScript Configuration

Located in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "strict": true,
    "types": ["jest", "@types/node"]
  },
  "include": ["src/**/*", "tests/**/*", "tools/**/*"]
}
```

## ✅ Best Practices

### 1. Test Structure (AAA Pattern)

```typescript
it('should do something', () => {
  // Arrange - Set up test data
  const input = 'test';

  // Act - Execute the code under test
  const result = functionUnderTest(input);

  // Assert - Verify the results
  expect(result).toBe('expected');
});
```

### 2. Descriptive Test Names

```typescript
// ✅ Good
it('should return 404 when user does not exist', () => { });

// ❌ Bad
it('test 1', () => { });
```

### 3. Test Independence

```typescript
// Each test should be independent
beforeEach(() => {
  // Reset state before each test
  resetDatabase();
  clearCache();
});
```

### 4. Mock External Dependencies

```typescript
import { jest } from '@jest/globals';

jest.mock('external-api', () => ({
  fetch: jest.fn().mockResolvedValue({ data: 'mocked' }),
}));
```

### 5. Test Edge Cases

```typescript
describe('divide', () => {
  it('should divide two numbers', () => { });
  it('should handle division by zero', () => { });
  it('should handle negative numbers', () => { });
  it('should handle decimal results', () => { });
});
```

## 📚 Examples

### Example 1: Testing a Simple Function

**Source** (`src/example.ts`):

```typescript
export function add(a: number, b: number): number {
  return a + b;
}
```

**Test** (`tests/unit/example.test.ts`):

```typescript
describe('add', () => {
  it('should add two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('should handle negative numbers', () => {
    expect(add(-2, -3)).toBe(-5);
  });
});
```

### Example 2: Testing Async Functions

```typescript
describe('fetchUser', () => {
  it('should fetch user data', async () => {
    const user = await fetchUser('123');
    expect(user.id).toBe('123');
  });

  it('should handle errors', async () => {
    await expect(fetchUser('')).rejects.toThrow();
  });
});
```

### Example 3: Testing Classes

```typescript
describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  it('should track operation history', () => {
    calculator.add(5, 3);
    expect(calculator.getHistory()).toContain(8);
  });
});
```

## 🔧 Troubleshooting

### Tests Not Running

**Problem**: Tests don't execute

**Solution**:

```bash
# Clear Jest cache
npx jest --clearCache

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Import Errors

**Problem**: Cannot find module errors

**Solution**: Check `tsconfig.json` paths and ensure files are included:

```json
{
  "include": ["src/**/*", "tests/**/*"]
}
```

### Coverage Not Generated

**Problem**: Coverage report empty

**Solution**: Ensure source files are in `src/` directory and check `collectCoverageFrom` in `jest.config.js`:

```javascript
collectCoverageFrom: [
  'src/**/*.{js,ts}',
  '!src/**/*.test.{js,ts}',
]
```

### TypeScript Errors in Tests

**Problem**: Type errors in test files

**Solution**: Install type definitions:

```bash
npm install --save-dev @types/jest @jest/globals
```

## 📊 Coverage Goals

The project enforces minimum coverage thresholds:

- **Branches**: 70%
- **Functions**: 70%
- **Lines**: 70%
- **Statements**: 70%

To check current coverage:

```bash
npm run test:coverage
```

## 🎯 Use Cases

### 1. Test Writing

Generate comprehensive tests for new or existing code

### 2. Coverage Improvement

Identify untested code and create tests for it

### 3. Bug Prevention

Create tests before fixing bugs to ensure they don't return

### 4. Test Automation

Automate repetitive test creation tasks

### 5. Quality Assurance

Maintain high code quality standards

### 6. Test Implementation

Quickly implement test suites for entire modules

## 🚀 Next Steps

1. **Write Your First Test**: Create a simple function and generate tests
2. **Improve Coverage**: Run coverage report and test uncovered code
3. **Automate Testing**: Set up CI/CD to run tests automatically
4. **Add Custom Templates**: Create templates for your specific use cases
5. **Integrate with Git**: Add pre-commit hooks to run tests

## 📖 Additional Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [TypeScript Testing Best Practices](https://typescript-testing.guide/)
- [Test-Driven Development Guide](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Claude Agent SDK Documentation](https://docs.anthropic.com/claude/docs)

## 🤝 Contributing

To add new test templates or utilities:

1. Add templates to `tools/test-generator/templates.ts`
2. Add utilities to `tests/utils/test-helpers.ts`
3. Update this documentation
4. Create example tests

## 📝 License

This Test Generator is part of the shadowtag_v4-fastapi-services project.

---

**Built with ❤️ using Claude Agent SDK**

*Testing expert who creates comprehensive test suites. Writes the tests you've been avoiding. Unit, integration, E2E - catches bugs before users do.*
