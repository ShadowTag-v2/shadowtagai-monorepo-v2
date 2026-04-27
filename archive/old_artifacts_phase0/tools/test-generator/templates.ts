/**
 * Test Templates
 *
 * Reusable templates for different types of tests
 */

export const UNIT_TEST_TEMPLATE = `import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';

describe('{{MODULE_NAME}}', () => {
  beforeEach(() => {
    // Setup before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  describe('{{FUNCTION_NAME}}', () => {
    it('should handle happy path scenario', () => {
      // Arrange
      const input = /* ... */;
      const expected = /* ... */;

      // Act
      const result = {{FUNCTION_NAME}}(input);

      // Assert
      expect(result).toBe(expected);
    });

    it('should handle edge cases', () => {
      // Test edge cases
    });

    it('should throw error for invalid input', () => {
      // Test error handling
      expect(() => {{FUNCTION_NAME}}(null)).toThrow();
    });
  });
});
`;

export const INTEGRATION_TEST_TEMPLATE = `import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';

describe('{{MODULE_NAME}} Integration Tests', () => {
  beforeAll(async () => {
    // Setup test environment, database, etc.
  });

  afterAll(async () => {
    // Teardown test environment
  });

  describe('{{FEATURE_NAME}}', () => {
    it('should integrate components correctly', async () => {
      // Arrange
      const testData = /* ... */;

      // Act
      const result = await {{FUNCTION_NAME}}(testData);

      // Assert
      expect(result).toBeDefined();
      // Add specific assertions
    });

    it('should handle external dependencies', async () => {
      // Test with real or mocked external services
    });

    it('should maintain data consistency', async () => {
      // Test data integrity across operations
    });
  });
});
`;

export const E2E_TEST_TEMPLATE = `import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';

describe('{{FEATURE_NAME}} E2E Tests', () => {
  beforeAll(async () => {
    // Setup complete test environment
    // Start services, databases, etc.
  });

  afterAll(async () => {
    // Teardown everything
  });

  describe('User Flow: {{FLOW_NAME}}', () => {
    it('should complete full user journey', async () => {
      // Step 1: Initial action
      // Step 2: Intermediate actions
      // Step 3: Final verification

      // Assert end-to-end behavior
    });

    it('should handle errors gracefully in production-like scenario', async () => {
      // Test error scenarios in realistic context
    });

    it('should perform within acceptable time limits', async () => {
      // Performance testing
      const startTime = Date.now();

      // Execute operation

      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(5000); // 5 seconds max
    });
  });
});
`;

export const ASYNC_TEST_TEMPLATE = `import { describe, it, expect } from '@jest/globals';

describe('Async {{FUNCTION_NAME}}', () => {
  it('should handle async operations correctly', async () => {
    // Arrange
    const input = /* ... */;

    // Act
    const result = await {{FUNCTION_NAME}}(input);

    // Assert
    expect(result).toBeDefined();
  });

  it('should handle async errors', async () => {
    // Test async error handling
    await expect({{FUNCTION_NAME}}(null)).rejects.toThrow();
  });

  it('should timeout on long operations', async () => {
    // Test with timeout
    await expect(
      {{FUNCTION_NAME}}(/* ... */)
    ).rejects.toThrow('timeout');
  }, 1000);
});
`;

export const MOCK_TEMPLATE = `import { jest } from '@jest/globals';

// Mock external dependencies
jest.mock('{{MODULE_PATH}}', () => ({
  {{EXPORT_NAME}}: jest.fn(),
}));

describe('Tests with Mocks', () => {
  beforeEach(() => {
    // Clear mock calls before each test
    jest.clearAllMocks();
  });

  it('should use mocked dependency', () => {
    const mockFn = require('{{MODULE_PATH}}').{{EXPORT_NAME}};
    mockFn.mockReturnValue('mocked value');

    // Test code that uses the mock

    expect(mockFn).toHaveBeenCalledTimes(1);
  });
});
`;

export const API_TEST_TEMPLATE = `import { describe, it, expect } from '@jest/globals';

describe('API Tests: {{ENDPOINT_NAME}}', () => {
  const baseUrl = process.env.API_URL || 'http://localhost:3000';

  describe('GET {{ENDPOINT_PATH}}', () => {
    it('should return 200 for valid request', async () => {
      const response = await fetch(\`\${baseUrl}{{ENDPOINT_PATH}}\`);

      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data).toBeDefined();
    });

    it('should return 404 for non-existent resource', async () => {
      const response = await fetch(\`\${baseUrl}{{ENDPOINT_PATH}}/invalid-id\`);
      expect(response.status).toBe(404);
    });

    it('should validate response schema', async () => {
      const response = await fetch(\`\${baseUrl}{{ENDPOINT_PATH}}\`);
      const data = await response.json();

      // Validate response structure
      expect(data).toHaveProperty('id');
      expect(data).toHaveProperty('name');
    });
  });

  describe('POST {{ENDPOINT_PATH}}', () => {
    it('should create resource with valid data', async () => {
      const payload = {
        // Test data
      };

      const response = await fetch(\`\${baseUrl}{{ENDPOINT_PATH}}\`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.status).toBe(201);
    });

    it('should reject invalid data', async () => {
      const invalidPayload = {};

      const response = await fetch(\`\${baseUrl}{{ENDPOINT_PATH}}\`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(invalidPayload),
      });

      expect(response.status).toBe(400);
    });
  });
});
`;

export const DATABASE_TEST_TEMPLATE = `import { describe, it, expect, beforeAll, afterAll, beforeEach } from '@jest/globals';

describe('Database Tests: {{MODEL_NAME}}', () => {
  let connection: any;

  beforeAll(async () => {
    // Setup database connection
    connection = await setupTestDatabase();
  });

  afterAll(async () => {
    // Close database connection
    await connection.close();
  });

  beforeEach(async () => {
    // Clear test data before each test
    await clearTestData();
  });

  describe('CRUD Operations', () => {
    it('should create record', async () => {
      const data = {
        // Test data
      };

      const result = await {{MODEL_NAME}}.create(data);

      expect(result.id).toBeDefined();
      expect(result.name).toBe(data.name);
    });

    it('should read record', async () => {
      const created = await {{MODEL_NAME}}.create(/* ... */);
      const found = await {{MODEL_NAME}}.findById(created.id);

      expect(found).toBeDefined();
      expect(found.id).toBe(created.id);
    });

    it('should update record', async () => {
      const created = await {{MODEL_NAME}}.create(/* ... */);
      const updated = await {{MODEL_NAME}}.update(created.id, { name: 'New Name' });

      expect(updated.name).toBe('New Name');
    });

    it('should delete record', async () => {
      const created = await {{MODEL_NAME}}.create(/* ... */);
      await {{MODEL_NAME}}.delete(created.id);
      const found = await {{MODEL_NAME}}.findById(created.id);

      expect(found).toBeNull();
    });
  });

  describe('Validation', () => {
    it('should enforce required fields', async () => {
      await expect({{MODEL_NAME}}.create({})).rejects.toThrow();
    });

    it('should validate data types', async () => {
      const invalidData = { age: 'not a number' };
      await expect({{MODEL_NAME}}.create(invalidData)).rejects.toThrow();
    });
  });
});
`;

export const templates = {
  unit: UNIT_TEST_TEMPLATE,
  integration: INTEGRATION_TEST_TEMPLATE,
  e2e: E2E_TEST_TEMPLATE,
  async: ASYNC_TEST_TEMPLATE,
  mock: MOCK_TEMPLATE,
  api: API_TEST_TEMPLATE,
  database: DATABASE_TEST_TEMPLATE,
};

export function getTemplate(type: keyof typeof templates): string {
  return templates[type] || templates.unit;
}
