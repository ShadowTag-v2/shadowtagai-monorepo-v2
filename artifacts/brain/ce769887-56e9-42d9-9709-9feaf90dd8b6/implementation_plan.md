# Stitch Design Workflow Integration

The goal is to adopt the Stitch capabilities to supercharge UI rapid prototyping and iterative planning processes.

## Proposed Changes

We are introducing the `stitch-skills` suite and integrating it seamlessly within the `Cor.Ideate` planning layer. This is not strictly a code-level application implementation but rather an environment and workflow implementation to enable AI-assisted UI design before entering the explicit coding phase.

### `external_sdks/stitch-skills` & `external_sdks/pickle-rick-extension`

These are newly adopted external repositories that offer advanced AI behavior looping (Pickle Rick) and generative UI (Stitch).

#### Setup
-   Ensure all required skills (`stitch-loop`, `react:components`, `design-md`) are globally available logic templates.

### Workflow Integration (`Cor.Ideate` Strategy)

-   We will simulate `Cor.Ideate` utilizing the `design-md` process.
-   When `Cor.Ideate` analyzes UI goals (e.g., "Analyze the top 3 e-commerce checkout flows..."), we fetch web context, study established layouts, and propose varying structural directions for user choice.
-   Once a specific UI flow is chosen, the `react:components` and `stitch-loop` logic is employed to render or iterate on actual code.

## Verification Plan

### Test Initial Cor.Ideate Run
We will verify that the workflow behaves correctly by acting as the agent executing the `design-md` or `stitch-loop` skill.

1.  **Mock Task:** Act on a prompt from the user such as "Look at current trends in SaaS pricing pages and generate 3 options for my product."
2.  **Action:** Utilize the terminal or programmatic interface to generate the appropriate `DESIGN.md` output based on the Stitch skill configuration.
3.  **Result:** Ensure output matches Stitch expected formatting, containing colors, tokens, typography, layout instructions, and reasoning.

### Veo 3 Integration and React Application
-   **Clone Repo:** Download the `veo-3-nano-banana-gemini-api-quickstart` repository into the `external_sdks/` directory. (Completed)
-   **Bootstrap Dashboard:** The `stitch_dashboard` directory requires a Next.js backbone. We will copy the `package.json`, `app/`, `components/`, and `lib/` directory backbone from the Veo 3 quickstart into `stitch_dashboard/` to serve as our base Next.js React application.
-   **React Components:** Execute the `react:components` Stitch logic on our `stitch_dashboard/page.tsx` (the 3-button 'Barney Style' layout) to generate structured Tailwind-based UI components.
-   **Pitch Deck Integration:** Hook the newly scaffolded dashboard layout into the Veo 3 Video capabilities, integrating a component representing the "Pitch Deck" feature natively powered by the newly copied Veo 3 `/api/veo/generate` code structures.

## Pitch Deck Studio Architectural Expansion (Phase 2)

Based on the newly ingested `nano-banana-hackathon-kit`, `gemini-image-editing-nextjs-quickstart`, and `gemini-cli`, the next evolutionary stage of the Pitch Deck Studio module (`/composer`) will incorporate:

1. **Iterative Asset Editing (`gemini-image-editing-nextjs-quickstart`)**
   - **Capability:** Moving beyond one-shot generation, we will integrate the conversation-state persistence from this quickstart.
   - **Function:** Users can generate a pitch deck slide or video frame, then use natural language to iteratively edit it (e.g., "make the background darker", "move the logo left") while maintaining context over the asset.

2. **Consistent Brand Storytelling (`nano-banana-hackathon-kit`)**
   - **Capability:** Utilizing Gemini 2.5 Flash Image Preview (Nano Banana).
   - **Function:** Enforces thematic consistency across the entire Pitch Deck. It allows character preservation and product fusion, enabling the deck to maintain the exact same corporate mascot or product visualization precisely mapped across multiple generated media assets.

3. **Orchestrated Data Scaffolding (`gemini-cli`)**
   - **Capability:** Agentic CLI capabilities with MCP server networking.
   - **Function:** Before the media is even generated, we can employ headless execution of the `gemini-cli` via our backend to ingest live repos, real-world data, or financial context. This ensures the Pitch Deck isn't just visually stunning, but functionally accurate based on ground-truth data retrieved autonomously.
