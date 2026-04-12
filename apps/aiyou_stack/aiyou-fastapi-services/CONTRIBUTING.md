# Contributing to Design System Builder

Thank you for your interest in contributing to the Design System Builder! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/shadowtag_v4-fastapi-services.git
   cd shadowtag_v4-fastapi-services
   ```

3. **Install dependencies**:

   ```bash
   npm install
   ```

4. **Create a branch** for your feature:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running the Project

```bash
# Development mode with auto-reload
npm run dev

# Build the project
npm run build

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Lint code
npm run lint

# Format code
npm run format
```

### Code Style

- We use **TypeScript** for type safety
- Follow the **ESLint** configuration
- Use **Prettier** for code formatting
- Write **descriptive commit messages**

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Tests should be in `tests/` directory
- Use Jest for testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## Contribution Guidelines

### Code Quality

1. **Type Safety**: Use TypeScript types and interfaces
2. **Error Handling**: Implement proper error handling
3. **Logging**: Use the Winston logger for all logging
4. **Documentation**: Document all public APIs
5. **Testing**: Write comprehensive tests

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(agent): add support for Angular components

fix(tokens): correct color lightening algorithm

docs(readme): update API documentation
```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**: `npm test`
4. **Lint your code**: `npm run lint`
5. **Format your code**: `npm run format`
6. **Update CHANGELOG.md** with your changes
7. **Submit PR** with clear description

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Project Structure

```
src/
├── agents/           # AI agent implementations
├── services/         # Business logic services
├── routes/           # API route handlers
├── types/            # TypeScript type definitions
├── config/           # Configuration files
├── utils/            # Utility functions
└── index.ts          # Application entry point

tests/                # Test files
```

## Adding New Features

### Adding a New Component Generator

1. Update `src/services/component-scaffolder.ts`
2. Add framework-specific template
3. Update types in `src/types/design-system.ts`
4. Add tests in `tests/`
5. Update documentation

### Adding a New API Endpoint

1. Add route in `src/routes/`
2. Update OpenAPI documentation
3. Add validation schemas
4. Add tests
5. Update README

### Adding Vertex AI Features

1. Update `src/services/vertex-workbench-integration.ts`
2. Add new methods
3. Update API routes
4. Add tests
5. Update documentation

## Code Review Process

All contributions go through code review:

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Merge** after approval

## Release Process

1. Update version in `package.json`
2. Update CHANGELOG.md
3. Create release tag
4. Publish to npm (maintainers only)

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the Code of Conduct

## Getting Help

- **Issues**: GitHub Issues for bugs and features
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Check README and docs/

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing! 🎉
