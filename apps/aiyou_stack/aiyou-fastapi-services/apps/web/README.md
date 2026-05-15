# Antigravity Web Interface

This is the Next.js frontend for the Antigravity Agentic System.

## Stack

- **Framework**: Next.js 15 (App Router)

- **Language**: TypeScript

- **Styling**: Tailwind CSS

- **API Integration**: Auto-generated clients from FastAPI OpenAPI specs

## Development

1. Ensure the FastAPI backend is running (usually port 8000).

2. Run the development server:

   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000).

## API Client Generation

To update the API client after backend changes:

```bash
npm run generate:client

```

(Note: Ensure `openapi-ts` is configured in `package.json`)
