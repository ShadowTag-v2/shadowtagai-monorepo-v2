import re
import os

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Create lib/analytics.ts
analytics_ts = """export function trackEvent(eventName: string, params?: Record<string, string | number | boolean>) {
  if (typeof window !== "undefined" && typeof window.gtag === "function") {
    window.gtag("event", eventName, params);
  }
}
declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
  }
}
"""
with open('src/lib/analytics.ts', 'w') as f:
    f.write(analytics_ts)

# Find all blocks based on /* ===== Name ===== */
# Wait, let's use regex to split by /* =====
blocks = re.split(r'/\* ===== (.*?) ===== \*/', content)

# blocks[0] is imports and anything before the first comment
# blocks[1] is the name of the first comment
# blocks[2] is the content of the first comment
# and so on...

components = []

for i in range(1, len(blocks), 2):
    name = blocks[i].strip()
    code = blocks[i+1].strip()
    
    if name.startswith("GA4 CUSTOM EVENTS"):
        continue
    
    if name == "PAGE":
        continue
        
    # Extract function name from code
    match = re.search(r'function\s+([A-Z][a-zA-Z0-9_]*)', code)
    if match:
        comp_name = match.group(1)
        components.append(comp_name)
        
        # Add necessary imports
        imports = []
        if 'trackEvent' in code:
            imports.append('import { trackEvent } from "@/lib/analytics";')
        
        hooks = []
        for hook in ['useState', 'useEffect', 'useRef', 'useCallback']:
            if hook + '(' in code or hook + ' ' in code or hook + '<' in code:
                hooks.append(hook)
        
        if hooks:
            imports.append(f'import {{ {", ".join(hooks)} }} from "react";')
            
        imports_str = '\n'.join(imports)
        if imports_str:
            imports_str = '"use client";\n\n' + imports_str + '\n\n'
        elif 'use client' in code or hooks:
            imports_str = '"use client";\n\n'
        else:
            imports_str = ''
            
        file_content = f"{imports_str}export {code}\n"
        
        with open(f'src/components/home/{comp_name}.tsx', 'w') as f:
            f.write(file_content)

# Now create the new page.tsx
page_imports = []
for comp in components:
    page_imports.append(f'import {{ {comp} }} from "@/components/home/{comp}";')

page_imports_str = '\n'.join(page_imports)

new_page_content = f'''"use client";

{page_imports_str}

export default function Home() {{
  return (
    <>
      <ScrollProgress />
      <NavBar />
      <main>
        <HeroSection />
        <StatsBar />
        <PlatformSection />
        <HowItWorks />
        <ModelRouting />
        <PricingSection />
        <EmailCapture />
        <HeppnerSection />
        <AboutSection />
      </main>
      <Footer />
    </>
  );
}}
'''

with open('src/app/page.tsx', 'w') as f:
    f.write(new_page_content)

print(f"Extracted components: {components}")
