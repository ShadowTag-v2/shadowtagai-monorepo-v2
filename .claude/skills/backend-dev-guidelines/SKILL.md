# Backend Development Guidelines

**Purpose:** Enforce Node.js/TypeScript/Express patterns for Pnkln backend services
**Enforcement:** `"suggest"`
**Priority:** `"high"`
**Version:** 1.0.0

---

## Overview

This skill provides best practices for building scalable, maintainable backend services using Pnkln's tech stack. It covers architecture patterns, error handling, testing, and deployment practices.

**Tech Stack:**
- **Runtime:** Node.js 20+ with TypeScript 5+
- **Framework:** Express.js with async/await
- **Database:** PostgreSQL with Prisma ORM
- **Package Manager:** pnpm (not npm/yarn)
- **Process Manager:** PM2 for microservices
- **Testing:** Jest with ≥98% coverage requirement
- **Monitoring:** Sentry for error tracking

---

## Architecture Pattern

### Layered Architecture (Standard)

```
Routes → Controllers → Services → Repositories → Database

Example file structure:
backend/
├── src/
│   ├── routes/          # API endpoint definitions
│   │   └── user.routes.ts
│   ├── controllers/     # Request/response handling
│   │   └── user.controller.ts
│   ├── services/        # Business logic
│   │   └── user.service.ts
│   ├── repositories/    # Data access layer
│   │   └── user.repository.ts
│   ├── models/          # TypeScript interfaces
│   │   └── user.model.ts
│   ├── middleware/      # Express middleware
│   │   └── auth.middleware.ts
│   └── utils/           # Helper functions
│       └── crypto.util.ts
├── prisma/
│   └── schema.prisma    # Database schema
├── tests/
│   ├── unit/
│   └── integration/
├── package.json
└── tsconfig.json
```

---

## Code Examples

### 1. Route Definition

```typescript
// src/routes/user.routes.ts
import { Router } from 'express';
import { UserController } from '../controllers/user.controller';
import { authenticate } from '../middleware/auth.middleware';
import { validateRequest } from '../middleware/validation.middleware';
import { createUserSchema } from '../schemas/user.schema';

const router = Router();
const userController = new UserController();

// Public routes
router.post(
  '/register',
  validateRequest(createUserSchema),
  userController.register
);

// Protected routes
router.get(
  '/profile',
  authenticate,
  userController.getProfile
);

router.put(
  '/profile',
  authenticate,
  validateRequest(updateUserSchema),
  userController.updateProfile
);

export default router;
```

### 2. Controller (Request/Response Handling)

```typescript
// src/controllers/user.controller.ts
import { Request, Response, NextFunction } from 'express';
import { UserService } from '../services/user.service';
import * as Sentry from '@sentry/node';

export class UserController {
  private userService: UserService;

  constructor() {
    this.userService = new UserService();
  }

  register = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { email, password, name } = req.body;

      // Delegate business logic to service
      const user = await this.userService.createUser({ email, password, name });

      res.status(201).json({
        success: true,
        data: {
          id: user.id,
          email: user.email,
          name: user.name
        }
      });
    } catch (error) {
      Sentry.captureException(error, {
        tags: { controller: 'UserController', action: 'register' }
      });
      next(error); // Pass to error middleware
    }
  };

  getProfile = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const userId = req.user!.id; // Set by authenticate middleware

      const user = await this.userService.getUserById(userId);

      if (!user) {
        return res.status(404).json({
          success: false,
          error: 'User not found'
        });
      }

      res.status(200).json({
        success: true,
        data: user
      });
    } catch (error) {
      Sentry.captureException(error, {
        tags: { controller: 'UserController', action: 'getProfile' }
      });
      next(error);
    }
  };
}
```

### 3. Service (Business Logic)

```typescript
// src/services/user.service.ts
import { UserRepository } from '../repositories/user.repository';
import { hashPassword, verifyPassword } from '../utils/crypto.util';
import { CreateUserDTO, User } from '../models/user.model';

export class UserService {
  private userRepository: UserRepository;

  constructor() {
    this.userRepository = new UserRepository();
  }

  async createUser(data: CreateUserDTO): Promise<User> {
    // Validate business rules
    const existingUser = await this.userRepository.findByEmail(data.email);
    if (existingUser) {
      throw new Error('Email already registered');
    }

    // Hash password (using Argon2id - see security-enforcement skill)
    const hashedPassword = await hashPassword(data.password);

    // Delegate data persistence to repository
    const user = await this.userRepository.create({
      ...data,
      password: hashedPassword
    });

    return user;
  }

  async getUserById(id: string): Promise<User | null> {
    return this.userRepository.findById(id);
  }

  async authenticateUser(email: string, password: string): Promise<User> {
    const user = await this.userRepository.findByEmail(email);

    if (!user) {
      throw new Error('Invalid credentials');
    }

    const isValidPassword = await verifyPassword(password, user.password);

    if (!isValidPassword) {
      throw new Error('Invalid credentials');
    }

    return user;
  }
}
```

### 4. Repository (Data Access)

```typescript
// src/repositories/user.repository.ts
import { PrismaClient } from '@prisma/client';
import { User, CreateUserDTO } from '../models/user.model';

export class UserRepository {
  private prisma: PrismaClient;

  constructor() {
    this.prisma = new PrismaClient();
  }

  async create(data: CreateUserDTO): Promise<User> {
    return this.prisma.user.create({
      data: {
        email: data.email,
        password: data.password,
        name: data.name
      }
    });
  }

  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({
      where: { id }
    });
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.prisma.user.findUnique({
      where: { email }
    });
  }

  async update(id: string, data: Partial<User>): Promise<User> {
    return this.prisma.user.update({
      where: { id },
      data
    });
  }

  async delete(id: string): Promise<void> {
    await this.prisma.user.delete({
      where: { id }
    });
  }
}
```

---

## Error Handling

### Global Error Middleware

```typescript
// src/middleware/error.middleware.ts
import { Request, Response, NextFunction } from 'express';
import * as Sentry from '@sentry/node';

export class AppError extends Error {
  statusCode: number;
  isOperational: boolean;

  constructor(message: string, statusCode: number = 500) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;

    Error.captureStackTrace(this, this.constructor);
  }
}

export const errorHandler = (
  error: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  let statusCode = 500;
  let message = 'Internal server error';

  if (error instanceof AppError) {
    statusCode = error.statusCode;
    message = error.message;
  }

  // Log to Sentry (all errors)
  Sentry.captureException(error, {
    tags: {
      path: req.path,
      method: req.method
    },
    extra: {
      body: req.body,
      query: req.query,
      params: req.params
    }
  });

  // Don't leak error details in production
  const isDevelopment = process.env.NODE_ENV === 'development';

  res.status(statusCode).json({
    success: false,
    error: message,
    ...(isDevelopment && { stack: error.stack })
  });
};

// Usage in app.ts
app.use(errorHandler);
```

---

## Testing

### Unit Tests (Jest)

```typescript
// tests/unit/user.service.test.ts
import { UserService } from '../../src/services/user.service';
import { UserRepository } from '../../src/repositories/user.repository';

jest.mock('../../src/repositories/user.repository');

describe('UserService', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockUserRepository = new UserRepository() as jest.Mocked<UserRepository>;
    userService = new UserService();
    (userService as any).userRepository = mockUserRepository;
  });

  describe('createUser', () => {
    it('should create a new user with hashed password', async () => {
      const createUserDTO = {
        email: 'test@example.com',
        password: 'SecurePass123!',
        name: 'Test User'
      };

      mockUserRepository.findByEmail.mockResolvedValue(null);
      mockUserRepository.create.mockResolvedValue({
        id: '123',
        email: createUserDTO.email,
        name: createUserDTO.name,
        password: 'hashed-password',
        createdAt: new Date()
      });

      const result = await userService.createUser(createUserDTO);

      expect(result.email).toBe(createUserDTO.email);
      expect(mockUserRepository.create).toHaveBeenCalledWith(
        expect.objectContaining({
          email: createUserDTO.email,
          name: createUserDTO.name,
          password: expect.not.stringContaining('SecurePass123!')
        })
      );
    });

    it('should throw error if email already exists', async () => {
      const createUserDTO = {
        email: 'existing@example.com',
        password: 'SecurePass123!',
        name: 'Test User'
      };

      mockUserRepository.findByEmail.mockResolvedValue({
        id: '456',
        email: createUserDTO.email,
        name: 'Existing User',
        password: 'hashed',
        createdAt: new Date()
      });

      await expect(userService.createUser(createUserDTO)).rejects.toThrow(
        'Email already registered'
      );
    });
  });
});
```

### Integration Tests

```typescript
// tests/integration/user.routes.test.ts
import request from 'supertest';
import app from '../../src/app';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

describe('User Routes', () => {
  beforeAll(async () => {
    // Setup test database
    await prisma.$connect();
  });

  afterAll(async () => {
    // Cleanup
    await prisma.user.deleteMany();
    await prisma.$disconnect();
  });

  describe('POST /api/users/register', () => {
    it('should register a new user', async () => {
      const response = await request(app)
        .post('/api/users/register')
        .send({
          email: 'newuser@example.com',
          password: 'SecurePass123!',
          name: 'New User'
        })
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.email).toBe('newuser@example.com');
      expect(response.body.data.password).toBeUndefined(); // Never return password
    });

    it('should return 400 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users/register')
        .send({
          email: 'invalid-email',
          password: 'SecurePass123!',
          name: 'Test User'
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('email');
    });
  });
});
```

---

## Package Manager: pnpm

### Installation

```bash
# Install pnpm globally
npm install -g pnpm

# Install dependencies
pnpm install

# Add new dependency
pnpm add express
pnpm add -D @types/express typescript

# Remove dependency
pnpm remove express
```

### package.json Scripts

```json
{
  "name": "pnkln-backend-service",
  "version": "1.0.0",
  "scripts": {
    "dev": "tsx watch src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "test:integration": "jest --testPathPattern=integration",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts",
    "db:migrate": "prisma migrate dev",
    "db:generate": "prisma generate",
    "db:studio": "prisma studio"
  },
  "dependencies": {
    "express": "^4.18.2",
    "prisma": "^5.7.0",
    "@prisma/client": "^5.7.0",
    "@sentry/node": "^7.85.0",
    "argon2": "^0.31.2"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/jest": "^29.5.10",
    "@types/node": "^20.10.0",
    "jest": "^29.7.0",
    "supertest": "^6.3.3",
    "tsx": "^4.6.2",
    "typescript": "^5.3.2"
  }
}
```

---

## API Design Standards

### RESTful Conventions

```typescript
GET    /api/v1/users           # List users
GET    /api/v1/users/:id       # Get user by ID
POST   /api/v1/users           # Create user
PUT    /api/v1/users/:id       # Update user (full)
PATCH  /api/v1/users/:id       # Update user (partial)
DELETE /api/v1/users/:id       # Delete user
```

### Response Format (Standard)

```typescript
// Success response
{
  "success": true,
  "data": { /* payload */ },
  "meta": {  // Optional
    "page": 1,
    "limit": 20,
    "total": 100
  }
}

// Error response
{
  "success": false,
  "error": "Error message",
  "code": "VALIDATION_ERROR"  // Optional error code
}
```

---

## Environment Configuration

### .env.development

```bash
NODE_ENV=development
PORT=3000
DATABASE_URL="postgresql://dev:devpass@localhost:5432/pnkln_dev"
JWT_SECRET="dev-secret-change-in-production"
SENTRY_DSN="https://dev@sentry.io/123456"
```

### Loading Config

```typescript
// src/config/index.ts
import dotenv from 'dotenv';

dotenv.config({ path: `.env.${process.env.NODE_ENV}` });

export const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  database: {
    url: process.env.DATABASE_URL!
  },
  auth: {
    jwtSecret: process.env.JWT_SECRET!,
    jwtExpiry: '7d'
  },
  sentry: {
    dsn: process.env.SENTRY_DSN
  }
};

// Validate required env vars
const required = ['DATABASE_URL', 'JWT_SECRET'];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}
```

---

## Best Practices Checklist

- [ ] Use layered architecture (Routes → Controllers → Services → Repositories)
- [ ] All async operations use `async/await` (no callbacks)
- [ ] All errors captured with Sentry.captureException()
- [ ] All database queries use Prisma (no raw SQL without parameterization)
- [ ] All endpoints have input validation (Zod or Joi)
- [ ] All routes protected with authentication middleware (except public endpoints)
- [ ] Test coverage ≥98% (run `pnpm test` to verify)
- [ ] No secrets in code (use environment variables)
- [ ] API versioning (/api/v1/)
- [ ] Consistent response format (success/error structure)
- [ ] Use pnpm (not npm/yarn)
- [ ] TypeScript strict mode enabled

---

## Common Mistakes

❌ **Mixing business logic in controllers**
```typescript
// Bad: Business logic in controller
router.post('/register', async (req, res) => {
  const hashedPassword = await argon2.hash(req.body.password);
  const user = await prisma.user.create({ ... });
});
```

❌ **No error handling**
```typescript
// Bad: Unhandled promise rejection
router.get('/users/:id', async (req, res) => {
  const user = await userService.getUser(req.params.id);
  res.json(user);
});
```

❌ **Returning sensitive data**
```typescript
// Bad: Password in response
res.json({ id: user.id, email: user.email, password: user.password });
```

✅ **Correct patterns**
```typescript
// Good: Controller delegates to service
router.post('/register', userController.register);

// Good: Error handling
try {
  const user = await userService.getUser(id);
  res.json(user);
} catch (error) {
  Sentry.captureException(error);
  next(error);
}

// Good: Exclude sensitive fields
res.json({ id: user.id, email: user.email });
```

---

**Last Updated:** 2025-11-15
**Maintained By:** Pnkln Backend Team
**Stack:** Node.js 20+ TypeScript 5 + Express + Prisma + pnpm + PM2
