# Shadowtag Omega V2 - Coding Constitution

## 1. Architectural Integrity
* **Clean Architecture:** Strictly separate concerns.
    * **Controllers:** Handle HTTP request/response only.
    * **Services:** Contain all business logic.
    * **Repositories:** Handle direct database access.
* **Unidirectional Data Flow:** Data flows down; events bubble up. Never mutate state directly.
* **API Layer:** All external API calls must go through the `@/lib/api-client` wrapper.

## 2. Security Mandates (Non-Negotiable)
* **Zero-Trust:** Never commit `.env` files, API keys, or credentials.
* **SQL Safety:** Never use string concatenation for queries. Use the ORM's parameterization methods.
* **Input Validation:** All API inputs must be validated using Zod schemas before processing.

## 3. Tech Stack Hard-Constraints
* **Styling:** Use Tailwind CSS utility classes. Avoid CSS-in-JS or `.css` modules unless absolutely necessary.
* **State Management:**
    * **Server State:** Use React Query.
    * **Client State:** Use Zustand.
    * **Redux:** Strictly Forbidden for new features.
* **Testing:** Utility functions require Unit Tests (Vitest). Components require Integration Tests (React Testing Library).

## 4. Code Quality Standards
* **Functional Style:** Prefer `map`, `filter`, `reduce` over imperative loops (`for`, `while`).
* **Naming:**
    * Booleans: `is[Condition]`, `has[Condition]`, `should[Action]`.
    * Interfaces: Do *not* prefix with `I` (e.g., use `User`, not `IUser`).
