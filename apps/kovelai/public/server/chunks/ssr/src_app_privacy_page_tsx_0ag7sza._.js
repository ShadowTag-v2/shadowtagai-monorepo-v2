module.exports=[88202,a=>{"use strict";var b=a.i(87924),c=a.i(46271),d=a.i(39432),e=a.i(72131),f=a.i(6742),g=a.i(69737),h=a.i(48291);function i({children:a,className:f="",delay:g=0}){let h=(0,e.useRef)(null),j=(0,d.useInView)(h,{once:!0,margin:"-80px"});return(0,b.jsx)(c.motion.div,{ref:h,initial:{opacity:0,y:32},animate:j?{opacity:1,y:0}:{opacity:0,y:32},transition:{duration:.6,delay:g,ease:[.22,1,.36,1]},className:f,children:a})}let j=[{id:"collection",title:"1. Information We Collect",content:`KovelAI collects the minimum information necessary to provide our services:

• **Account Information:** Firm name, administrator email, and billing details provided during registration.
• **Session Metadata:** Timestamp, duration, and token count for billing and compliance audit purposes. Session content is never stored.
• **Usage Analytics:** Aggregated, anonymized platform usage metrics via Google Analytics 4 with IP anonymization enabled.

**What We Do NOT Collect:**
• Client search queries or AI conversation content
• Browser history or browsing behavior
• Documents, files, or case materials
• Any personally identifiable information (PII) of your clients`},{id:"retention",title:"2. Zero-Retention Architecture",content:`KovelAI operates a zero-retention architecture for all privileged session data:

• All AI inference occurs in ephemeral compute instances that are cryptographically shredded upon session termination.
• No client queries, responses, or session content is written to persistent storage at any point.
• Session metadata (timestamps, token counts) is retained for 90 days for billing reconciliation, then permanently deleted.
• Infrastructure logs are retained for 30 days for security monitoring, contain no session content, and are automatically purged.`},{id:"sharing",title:"3. Information Sharing",content:`KovelAI does not sell, rent, or trade your information. We share data only in these limited circumstances:

• **Service Providers:** Google Cloud Platform (infrastructure), Stripe (payment processing). All providers are bound by data processing agreements.
• **Legal Compliance:** We may disclose information if required by law, subpoena, or court order — however, our zero-retention architecture means we physically cannot produce session content that was never stored.
• **Business Transfer:** In the event of a merger or acquisition, your data would be subject to the same privacy protections.`},{id:"security",title:"4. Security Measures",content:`• AES-256 encryption at rest for all persistent data
• TLS 1.3 for all data in transit
• SOC 2 Type II certified infrastructure
• RBAC with MFA enforcement for all administrator accounts
• 15-minute session token rotation
• Cloud Armor WAF with 4 active security rules
• Immutable audit trails with tamper-evident checksums
• Penetration testing conducted annually by independent security firms`},{id:"rights",title:"5. Your Rights",content:`Depending on your jurisdiction, you may have the following rights:

• **Access:** Request a copy of the personal data we hold about you.
• **Correction:** Request correction of inaccurate personal data.
• **Deletion:** Request deletion of your personal data (subject to legal retention obligations).
• **Portability:** Request your data in a structured, machine-readable format.
• **Objection:** Object to processing of your personal data for specific purposes.

**GDPR (EU/EEA):** We process data under legitimate interest (Article 6(1)(f)) and contractual necessity (Article 6(1)(b)). DPA available upon request.
**CCPA (California):** We do not sell personal information. California residents may exercise their rights by contacting privacy@kovelai.com.`},{id:"contact",title:"6. Contact & Updates",content:`For privacy inquiries, data subject requests, or to report a concern:

• **Email:** privacy@kovelai.com
• **Mail:** ShadowTagAI, Inc. — Privacy Team

This policy is effective as of January 1, 2026 and was last updated on May 4, 2026. We will notify registered users of material changes via email at least 30 days before they take effect.`}];a.s(["default",0,function(){let[a,c]=(0,e.useState)(!1),d=(0,e.useCallback)(()=>c(!0),[]),k=(0,e.useCallback)(()=>c(!1),[]);return(0,b.jsxs)(b.Fragment,{children:[(0,b.jsx)("a",{href:"#main-content",className:"skip-nav",children:"Skip to main content"}),(0,b.jsx)(h.default,{onOpenModal:d}),(0,b.jsx)("main",{id:"main-content",className:"pt-24 pb-16",children:(0,b.jsx)("section",{className:"py-16",children:(0,b.jsxs)("div",{className:"max-w-[800px] mx-auto px-4 sm:px-6 lg:px-8",children:[(0,b.jsx)(i,{children:(0,b.jsxs)("div",{className:"text-center mb-16",children:[(0,b.jsx)("div",{className:"inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8",children:(0,b.jsx)("span",{className:"text-sm font-medium text-[#d0c5b5]",children:"🔒 Privacy Policy"})}),(0,b.jsxs)("h1",{className:"text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-[#d7e3fc] mb-6",children:["Your Privacy,"," ",(0,b.jsx)("span",{className:"bg-gradient-to-r from-[#e6c487] to-[#c9a96e] bg-clip-text text-transparent",children:"By Design"})]}),(0,b.jsx)("p",{className:"text-lg text-[#d0c5b5] leading-relaxed max-w-2xl mx-auto",children:"KovelAI's zero-retention architecture means your clients' privileged data is never stored, never indexed, and never accessible — even to us."})]})}),j.map((a,c)=>(0,b.jsx)(i,{delay:.05*c,className:"mb-12",children:(0,b.jsxs)("div",{className:"glass-card",children:[(0,b.jsx)("h2",{className:"text-xl font-semibold text-[#d7e3fc] mb-4",children:a.title}),(0,b.jsx)("div",{className:"text-sm text-[#d0c5b5] leading-relaxed whitespace-pre-line",children:a.content})]})},a.id)),(0,b.jsx)(i,{delay:.3,children:(0,b.jsx)("div",{className:"text-center mt-16",children:(0,b.jsx)("a",{href:"/",className:"btn-ghost text-base py-3 px-8",children:"← Back to Home"})})})]})})}),(0,b.jsx)(g.default,{onOpenModal:d}),(0,b.jsx)(f.default,{isOpen:a,onClose:k})]})}])}];

//# sourceMappingURL=src_app_privacy_page_tsx_0ag7sza._.js.map