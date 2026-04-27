# ShadowTag OS: Omega Thread Transfer Manifest

> "You've got to start with the customer experience and work back toward the technology - not the other way around." — Steve Jobs

## The State of the Board (Review & Analysis)

In this session, we transcended basic syntax and operated as The Board (IQ Lock: 160).

We addressed the **"reams left on the table"**:

1. **Orchestrator Stability:** We fixed the critical deployment pipelines (Temporal worker images and run paths).
2. **Data Ingestion Resilience:** We discovered that `langextract` updated its API signature from `model_name` to `model_id`. We corrected this. Furthermore, encountering PDF EOF errors (`Stream has ended unexpectedly`), we didn't just suppress the error; we enabled **graceful degradation**. Now, if a PDF fails midway through reading, it salvages whatever text was successfully parsed and pushes it to the LLM anyway, ensuring maximum data liquidity.
3. **UI/UX Component Assembly:** We started building a Dark Luxury Web3 experience.

### Why our UI approach is different (The Distinction)

Instead of just cobbling together React components, we recognized the **A2UI + Google Stitch** paradigm.

- We constructed the base layer statically (`page.tsx`, `HeroContent.tsx`, `GlowButton.tsx`) to act as the pristine container.
- Moving forward, the *internal dashboard flows* will be dynamically constructed via **A2UI**, rendering CopilotKit agentic streams into native mobile/web interfaces without brittle hardcoding. We don't build pages anymore; we build engines that render pages based on context.

---

## The Thread Codebase (Re-Punched and Re-Considered)

### 1. `apps/shadowtag-web/components/ui/GlowButton.tsx`

```tsx
import React, { ReactNode } from 'react';

interface GlowButtonProps {
  variant: "dark" | "light";
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export default function GlowButton({ variant, children, className = "", onClick }: GlowButtonProps) {
  const baseClasses = "relative overflow-hidden rounded-full border-[0.6px] border-white/20 px-[29px] py-[11px] text-[14px] font-medium transition-transform hover:scale-[1.02] active:scale-[0.98]";
  const variantClasses = variant === "dark" ? "bg-black text-white" : "bg-white text-black";

  return (
    <button className={`${baseClasses} ${variantClasses} ${className}`} onClick={onClick}>
      <div className="absolute top-0 left-[10%] right-[10%] h-[1px] bg-gradient-to-r from-transparent via-white/80 to-transparent blur-[2px]"></div>
      <span className="relative z-10">{children}</span>
    </button>
  );
}
```

### 2. `apps/shadowtag-web/components/hero/Navbar.tsx`

```tsx
import React from 'react';
import { ChevronDown } from 'lucide-react';
import GlowButton from '../ui/GlowButton';

export default function Navbar() {
  const navLinks = ["Get Started", "Developers", "Features", "Resources"];

  return (
    <nav className="absolute top-0 w-full flex justify-between items-center z-50 px-6 py-4 md:px-[120px] md:py-[20px]">
      {/* Left: Logo */}
      <div className="text-white font-bold tracking-widest text-xl w-[187px] h-[25px] flex items-center">
        LOGOIPSUM
      </div>

      {/* Center: Nav links */}
      <div className="hidden md:flex gap-[30px]">
        {navLinks.map((link) => (
          <a key={link} href="#" className="text-white text-[14px] font-medium flex items-center gap-[14px] hover:text-white/80 transition-colors">
            {link}
            <ChevronDown size={14} />
          </a>
        ))}
      </div>

      {/* Right: CTA */}
      <GlowButton variant="dark">Join Waitlist</GlowButton>
    </nav>
  );
}
```

### 3. `apps/shadowtag-web/components/hero/HeroContent.tsx`

```tsx
import React from 'react';
import GlowButton from '../ui/GlowButton';

export default function HeroContent() {
  return (
    <div className="flex flex-col items-center justify-center h-full pt-[200px] md:pt-[280px] pb-[102px] gap-[40px] relative z-10 px-4">
      {/* Badge */}
      <div className="rounded-[20px] bg-white/10 border border-white/20 px-3 py-1 flex items-center gap-2 backdrop-blur-sm">
        <div className="w-1 h-1 bg-white rounded-full animate-pulse"></div>
        <span className="text-white/60 text-[13px]">Early access available from</span>
        <span className="text-white font-medium text-[13px]">May 1, 2026</span>
      </div>

      {/* Heading */}
      <h1 className="text-[36px] md:text-[56px] leading-[1.28] font-medium max-w-[613px] text-center bg-gradient-to-br from-white via-white/80 to-white/0 text-transparent bg-clip-text">
        Web3 at the Speed of Experience
      </h1>

      {/* Subtitle */}
      <p className="text-[15px] font-normal text-white/70 max-w-[680px] text-center mt-[-16px]">
        Powering seamless experiences and real-time connections, EOS is the base for creators who move with purpose, leveraging resilience, speed, and scale to shape the future.
      </p>

      {/* CTA */}
      <GlowButton variant="light">Join Waitlist</GlowButton>
    </div>
  );
}
```

### 4. `apps/shadowtag-web/app/page.tsx`

```tsx
import React from 'react';
import Navbar from '../components/hero/Navbar';
import HeroContent from '../components/hero/HeroContent';

export default function Web3HeroPage() {
  return (
    <main className="min-h-screen relative overflow-hidden w-full bg-black font-sans">
      {/* Video Background */}
      <video
        className="absolute inset-0 w-full h-full object-cover -z-20"
        src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260217_030345_246c0224-10a4-422c-b324-070b7c0eceda.mp4"
        muted
        autoPlay
        playsInline
        loop
      />

      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black/50 -z-10" />

      {/* Content Layer */}
      <Navbar />
      <HeroContent />
    </main>
  );
}
```

### 5. `apps/shadowtag-web/app/globals.css` (Font Update)

```css
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@400,500,600,700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #05020A;
  --foreground: #F4F0FF;
}

body {
  background-color: #02040A; /* void */
  color: #E2E8F0; /* starlight */
  font-family: 'General Sans', ui-sans-serif, system-ui, -apple-system, sans-serif;
}

.glass-panel {
  background: rgba(14, 11, 22, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid #2A2438;
}
```

### 6. `shadowtag-omega-v4/scripts/ingest_drive_docs.py` (Excerpts & Updates)

```python
# Project Context locked
PROJECT_ID = "shadowtag-omega-v4"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

# Using the requested model exactly for maximum inference depth
MODEL_ID = "gemini-2.5-flash-thinking-exp-01-21"

def extract_text_from_pdf(filepath: str) -> str:
    """Extracts text from a PDF file with graceful degradation."""
    try:
        reader = PdfReader(filepath)
        text = ""
        for i, page in enumerate(reader.pages):
            if i > 50:
                break
            extracted = page.extract_text()
            if extracted:
                text += str(extracted) + "\n"
        return text
    except Exception as e:
        # Graceful degradation logic implemented
        logger.warning(f"Partial or total failure reading PDF {filepath}. Reason: {type(e).__name__} - {e}")
        # Return whatever text we managed to extract before the EOF/parsing error
        return text
```

---
*Ready for handoff to the next session loop.*
