# Web3 Hero Section Architecture

Provide a brief description of the problem, any background context, and what the change accomplishes.
This plan scaffolds a responsive, full-screen Web3 Hero Section based on the "Unusual Machines" reference, using Next.js 14/15, Tailwind CSS, `lucide-react`, and General Sans typography in a Dark Luxury aesthetic.

## User Review Required

> [!IMPORTANT]
> Please review the proposed architecture and the A2UI/Stitch workflow synthesis below. Upon your approval, I will execute the component scaffolding and wire them into `apps/shadowtag-web/app/page.tsx`.

## Proposed Changes

The requested components will be developed in the `apps/shadowtag-web` frontend.

### `apps/shadowtag-web/components/ui/`
#### [NEW] `GlowButton.tsx`
A highly reusable, pill-shaped button component engineered to feature a distinct glowing light streak effect simulated via a `blur-[2px]` top-inner gradient.
* **Props**: `variant: "dark" | "light"`, `children: ReactNode`.
* **Styling**: Rounded-full, padding `px-[29px] py-[11px]`, transparent border `border-white/20`.

### `apps/shadowtag-web/components/hero/`
#### [NEW] `Navbar.tsx`
A responsive navigation bar overlaying the Hero video.
* **Layout**: Absolute top positioning, `z-50`, `flex justify-between items-center`.
* **Elements**: Features a textual "LOGOIPSUM" logo, hidden-on-mobile navigation links paired with `ChevronDown` from `lucide-react`, and a Dark variant `<GlowButton>` acting as the main CTA.

#### [NEW] `HeroContent.tsx`
The primary viewport-centered content block.
* **Layout**: Flex column, vertically/horizontally centered, padding rules applied for top spacing (`pt-[200px] md:pt-[280px]`).
* **Elements**:
  * An Early Access "Pill" Badge.
  * A gradient text headline via `bg-clip-text`.
  * Subtitle text with a tighter gap override (`mt-[-16px]`).
  * A Light variant `<GlowButton>` CTA.

### `apps/shadowtag-web/app/`
#### [MODIFY] `page.tsx`
The main assembly page.
* Features a `min-h-screen relative overflow-hidden bg-black` container.
* Embeds the specified background `<video>` at `-z-20`.
* Contains an overlay div `bg-black/50` at `-z-10`.
* Plugs in `<Navbar />` and `<HeroContent />` inside the relative `z-10` interactive layer.

---

## AI Design Workflow Synthesis (A2UI & Google Stitch)

Based on the provided transcripts, here is a breakdown of how exactly we should leverage **A2UI** and **Google Stitch** into the ShadowTag-v2 pipeline:

### 1. Divergent Design Exploration (Google Stitch)
Instead of starting with a blank canvas or repeatedly prompting code in Cursor to explore layouts, we should start in **Google Stitch**.
*   **The "YOLO" Workflow**: Use Stitch’s YOLO mode (max creative range) on existing components (e.g. taking our new `HeroContent.tsx` and passing it in) to quickly generate 15-16 divergent alternatives.
*   **Purpose**: Uncover novel "alpha" directions you wouldn't find in a standard brainstorm. This forces exploration before committing to a static path.
*   **Handoff**: Export the chosen design from Stitch to Google AI Studio to turn it into an interactive HTML prototype before passing it to development.

### 2. Generative Agent-Driven Interfaces (A2UI & CopilotKit)
When building interactive app flows (like forms, graphs, uploading dashboards), don't hardcode rigid components. Use **A2UI**.
*   **The Concept**: A2UI uses a declarative JSON spec enabling CopilotKit-powered agents to generate structural UI components dynamically depending on user context.
*   **The Architecture**: Your backend agent outputs an A2UI payload instead of HTML/JS, which CopilotKit parses to render native React widgets. This keeps the frontend highly secure (no arbitrary code execution) while feeling native and seamless.
*   **Agent-to-Agent (A2A)**: We can hook A2UI up to our existing A2A zero-trust protocols. An agent handles the visual layout generation, while another logic agent provides the data constraints.

**Actionable Next Step**: After building this static Hero block, our next milestone should be to use A2UI to dynamically generate the user dashboard forms/modals natively through `shadowtag_swarm`!
