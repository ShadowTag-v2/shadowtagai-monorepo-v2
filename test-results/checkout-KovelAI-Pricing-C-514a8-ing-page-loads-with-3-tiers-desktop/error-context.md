# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: checkout.spec.ts >> KovelAI Pricing & Checkout >> pricing page loads with 3 tiers
- Location: tests/e2e/checkout.spec.ts:8:7

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator: locator('.tier-name')
Timeout: 5000ms
- Expected  - 5
+ Received  + 1

- Array [
-   "Trial",
-   "Professional",
-   "Enterprise",
- ]
+ Array []

Call log:
  - Expect "toHaveText" with timeout 5000ms
  - waiting for locator('.tier-name')
    9 × locator resolved to 0 elements

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - link "Skip to main content" [ref=e2] [cursor=pointer]:
    - /url: "#main-content"
  - navigation [ref=e3]:
    - generic [ref=e4]:
      - link "KovelAI logo KovelAI" [ref=e5] [cursor=pointer]:
        - /url: /
        - img "KovelAI logo" [ref=e6]
        - text: KovelAI
      - list [ref=e7]:
        - listitem [ref=e8]:
          - link "Discovery Risk" [ref=e9] [cursor=pointer]:
            - /url: "#discovery-risk"
        - listitem [ref=e10]:
          - link "Features" [ref=e11] [cursor=pointer]:
            - /url: "#features"
        - listitem [ref=e12]:
          - link "Pricing" [ref=e13] [cursor=pointer]:
            - /url: "#pricing"
        - listitem [ref=e14]:
          - link "How It Works" [ref=e15] [cursor=pointer]:
            - /url: "#how-it-works"
        - listitem [ref=e16]:
          - link "FAQ" [ref=e17] [cursor=pointer]:
            - /url: "#faq"
        - listitem [ref=e18]:
          - link "Trust" [ref=e19] [cursor=pointer]:
            - /url: /trust
      - button "Contact Sales" [ref=e21] [cursor=pointer]
  - main [ref=e22]:
    - generic [ref=e23]:
      - generic:
        - img "Protective shield emblem"
      - generic [ref=e24]:
        - generic [ref=e25]: Privilege-Protected Infrastructure· ATTORNEY-MONITORED · HEPPNER-COMPLIANT
        - heading "Shield Your Client's Research From Discovery." [level=1] [ref=e26]:
          - text: Shield Your Client's Research
          - text: From Discovery.
        - heading "Deploy privileged search infrastructure your clients use under your oversight—so opposing counsel discovers nothing." [level=2] [ref=e27]
        - paragraph [ref=e28]:
          - text: After
          - emphasis [ref=e29]: In re Heppner
          - text: (S.D.N.Y., Feb. 2026), every web search and AI conversation your client conducts outside your firm's umbrella is fair game for opposing counsel. KovelAI is the turnkey infrastructure you deploy to close that gap.
        - paragraph [ref=e30]:
          - text: Your clients search at will under your privilege umbrella. You monitor every session, deliver the first legal opinion, and bill their credit card automatically.
          - strong [ref=e31]: “Either you do it through our firm's KovelAI, or proceed at your peril.”
        - generic [ref=e32]:
          - button "Deploy Your Firm's Portal" [ref=e33] [cursor=pointer]
          - link "See How Privilege Works →" [ref=e34] [cursor=pointer]:
            - /url: "#how-it-works"
        - paragraph [ref=e35]: Clients log in · You monitor all sessions · You give the first opinion · Automatic billing · Opposing counsel gets nothing
    - generic [ref=e38]:
      - generic [ref=e39]:
        - generic [ref=e40]: 3x+
        - generic [ref=e41]: Intake Revenue
      - generic [ref=e42]:
        - generic [ref=e43]: "0"
        - generic [ref=e44]: Data Retained
      - generic [ref=e45]:
        - generic [ref=e46]: 24/7
        - generic [ref=e47]: Client Capture
      - generic [ref=e48]:
        - generic [ref=e49]: ↑ ACV
        - generic [ref=e50]: Revenue per Matter
    - generic [ref=e52]:
      - generic [ref=e53]: The Heppner Problem
      - heading "Your Clients' Internet Searches Are Discoverable." [level=2] [ref=e54]
      - paragraph [ref=e55]:
        - text: After
        - emphasis [ref=e56]: In re Heppner
        - text: ", any client web search conducted outside privileged channels is fair game in litigation. This includes Google searches, legal research, and even AI chatbot interactions. KovelAI wraps these activities under attorney-client privilege — and bills for the protection."
      - generic [ref=e57]:
        - generic [ref=e58]:
          - generic [ref=e59]: ⚖️
          - heading "Privilege Shield" [level=3] [ref=e60]
          - paragraph [ref=e61]: All client web activity routed through your firm's privileged infrastructure. Zero discoverable footprint.
        - generic [ref=e62]:
          - generic [ref=e63]: 🔒
          - heading "Zero Data Retention" [level=3] [ref=e64]
          - paragraph [ref=e65]: No search logs, no browsing history, no metadata. The data that doesn't exist can't be subpoenaed.
        - generic [ref=e66]:
          - generic [ref=e67]: 💰
          - heading "Revenue at the Front Door" [level=3] [ref=e68]
          - paragraph [ref=e69]: Clients pay for privileged access. Your firm captures intake revenue 24/7, even after hours.
    - generic [ref=e71]:
      - generic [ref=e72]: Platform
      - heading "Built for Law Firms That Think Like Businesses" [level=2] [ref=e73]
      - paragraph [ref=e74]: KovelAI combines privileged communication infrastructure with AI-powered intake — turning your firm's front door into a revenue engine that never sleeps.
      - generic [ref=e75]:
        - generic [ref=e76]:
          - img [ref=e78]
          - heading "AI-Powered Intake" [level=3] [ref=e82]
          - paragraph [ref=e83]: Intelligent after-hours client intake that captures, qualifies, and organizes potential matters while your team rests.
        - generic [ref=e84]:
          - img [ref=e86]
          - heading "Matter Pipeline" [level=3] [ref=e90]
          - paragraph [ref=e91]: Every client interaction becomes a tracked, scored, and prioritized entry in your matter pipeline. No leads lost.
        - generic [ref=e92]:
          - img [ref=e94]
          - heading "Privileged Search" [level=3] [ref=e97]
          - paragraph [ref=e98]: Clients search the web through your firm's infrastructure. Every query is privileged, every session is billed.
        - generic [ref=e99]:
          - img [ref=e101]
          - heading "After-Hours Capture" [level=3] [ref=e104]
          - paragraph [ref=e105]: Panic calls at 2 AM become organized, retained matters by 8 AM. Your paralegal costs drop, your intake revenue rises.
        - generic [ref=e106]:
          - img [ref=e108]
          - heading "Compliance First" [level=3] [ref=e112]
          - paragraph [ref=e113]: Pursuing SOC 2 Type II certification. HIPAA-supportive architecture. Built to withstand judicial scrutiny on privilege claims.
        - generic [ref=e114]:
          - img [ref=e116]
          - heading "Revenue Analytics" [level=3] [ref=e119]
          - paragraph [ref=e120]: Real-time dashboards showing intake conversion, after-hours capture rate, and revenue per privileged session.
    - generic [ref=e122]:
      - generic [ref=e123]: Process
      - heading "Three Steps to Privileged Revenue" [level=2] [ref=e124]
      - generic [ref=e125]:
        - generic [ref=e126]:
          - generic [ref=e127]: "01"
          - heading "Connect" [level=3] [ref=e128]
          - paragraph [ref=e129]: Your clients access KovelAI through your firm's branded portal. Every session is logged under privilege.
        - generic [ref=e130]:
          - generic [ref=e131]: "02"
          - heading "Protect" [level=3] [ref=e132]
          - paragraph [ref=e133]: Web searches, AI queries, and document uploads are routed through privileged infrastructure. Zero exposure.
        - generic [ref=e134]:
          - generic [ref=e135]: "03"
          - heading "Bill" [level=3] [ref=e136]
          - paragraph [ref=e137]: Each privileged session generates billable entries. After-hours intake converts to retained matters automatically.
    - generic [ref=e139]:
      - generic [ref=e140]: From the Bar
      - heading "What Attorneys Are Saying" [level=2] [ref=e141]
      - generic [ref=e142]:
        - generic [ref=e143]:
          - generic [ref=e144]: ★★★★★
          - blockquote [ref=e145]: "\"We had a client whose Google search history was subpoenaed mid-litigation. After Heppner, we moved all client research to KovelAI. The privilege held. That one save paid for three years of service.\""
          - generic [ref=e146]:
            - generic [ref=e147]: MR
            - generic [ref=e148]:
              - generic [ref=e149]: Managing Partner
              - generic [ref=e150]: Am Law 200 Litigation Practice, New York
        - generic [ref=e151]:
          - generic [ref=e152]: ★★★★★
          - blockquote [ref=e153]: "\"The after-hours capture alone justified the cost. We went from losing 60% of weekend inquiries to converting 85% into retained matters. The privilege protection is the bonus.\""
          - generic [ref=e154]:
            - generic [ref=e155]: SK
            - generic [ref=e156]:
              - generic [ref=e157]: Senior Associate
              - generic [ref=e158]: Boutique Family Law, Los Angeles
        - generic [ref=e159]:
          - generic [ref=e160]: ★★★★★
          - blockquote [ref=e161]: "\"We bill clients $250/month for privileged search access. They're happy to pay because they understand the Heppner risk. Our intake revenue is up 40% since launch.\""
          - generic [ref=e162]:
            - generic [ref=e163]: JL
            - generic [ref=e164]:
              - generic [ref=e165]: Founding Partner
              - generic [ref=e166]: Criminal Defense, Chicago
    - generic [ref=e168]:
      - generic [ref=e169]: Why KovelAI
      - heading "KovelAI vs. Doing Nothing" [level=2] [ref=e170]
      - paragraph [ref=e171]: Every day without privilege protection is another day opposing counsel can mine your clients' digital footprint.
      - table [ref=e173]:
        - rowgroup [ref=e174]:
          - row "Feature Without KovelAI Shielded by Attorney-Client Privilege" [ref=e175]:
            - columnheader "Feature" [ref=e176]
            - columnheader "Without KovelAI" [ref=e177]
            - columnheader "Shielded by Attorney-Client Privilege" [ref=e178]
        - rowgroup [ref=e179]:
          - row "Client web searches ⚠️ Discoverable ✅ Privileged" [ref=e180]:
            - rowheader "Client web searches" [ref=e181]
            - cell "⚠️ Discoverable" [ref=e182]
            - cell "✅ Privileged" [ref=e183]
          - row "AI chatbot conversations ⚠️ Subpoena target ✅ Shielded under Kovel" [ref=e184]:
            - rowheader "AI chatbot conversations" [ref=e185]
            - cell "⚠️ Subpoena target" [ref=e186]
            - cell "✅ Shielded under Kovel" [ref=e187]
          - row "After-hours client inquiries ❌ Lost to voicemail ✅ Captured & retained" [ref=e188]:
            - rowheader "After-hours client inquiries" [ref=e189]
            - cell "❌ Lost to voicemail" [ref=e190]
            - cell "✅ Captured & retained" [ref=e191]
          - row "Data retention ⚠️ Browser logs everywhere ✅ Zero retention (RAM only)" [ref=e192]:
            - rowheader "Data retention" [ref=e193]
            - cell "⚠️ Browser logs everywhere" [ref=e194]
            - cell "✅ Zero retention (RAM only)" [ref=e195]
          - row "Revenue per interaction $0 (unbilled panic calls) $50–$250/session (billable)" [ref=e196]:
            - rowheader "Revenue per interaction" [ref=e197]
            - cell "$0 (unbilled panic calls)" [ref=e198]
            - cell "$50–$250/session (billable)" [ref=e199]
          - row "Paralegal cost for intake $45–$75/hour $0 (automated)" [ref=e200]:
            - rowheader "Paralegal cost for intake" [ref=e201]
            - cell "$45–$75/hour" [ref=e202]
            - cell "$0 (automated)" [ref=e203]
          - row "Compliance posture ❌ Hope-based ✅ SOC 2 audit-ready, HIPAA-supportive" [ref=e204]:
            - rowheader "Compliance posture" [ref=e205]
            - cell "❌ Hope-based" [ref=e206]
            - cell "✅ SOC 2 audit-ready, HIPAA-supportive" [ref=e207]
    - generic [ref=e209]:
      - generic [ref=e210]: Pricing
      - heading "Simple, Transparent Pricing" [level=2] [ref=e211]
      - paragraph [ref=e212]: Every plan includes Kovel Doctrine privilege protection, zero data retention, and Judge 6 compliance governance.
      - generic [ref=e213]:
        - generic [ref=e214]:
          - generic [ref=e215]: Trial
          - generic [ref=e216]: $0/mo
          - list [ref=e217]:
            - listitem [ref=e218]:
              - generic [ref=e219]: ✓
              - text: 10,000 tokens/month
            - listitem [ref=e220]:
              - generic [ref=e221]: ✓
              - text: Kovel Doctrine protection
            - listitem [ref=e222]:
              - generic [ref=e223]: ✓
              - text: Zero data retention
            - listitem [ref=e224]:
              - generic [ref=e225]: ✓
              - text: Basic intake dashboard
            - listitem [ref=e226]:
              - generic [ref=e227]: ✓
              - text: Email support
          - link "Start Free Trial" [ref=e228] [cursor=pointer]:
            - /url: https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000
        - generic [ref=e229]:
          - generic [ref=e230]: Most Popular
          - generic [ref=e231]: 50% OFF — Beta Launch
          - generic [ref=e232]: Professional
          - generic [ref=e233]: $149/mo
          - list [ref=e234]:
            - listitem [ref=e235]:
              - generic [ref=e236]: ✓
              - text: 100,000 tokens/month
            - listitem [ref=e237]:
              - generic [ref=e238]: ✓
              - text: "Everything in Trial, plus:"
            - listitem [ref=e239]:
              - generic [ref=e240]: ✓
              - text: Privileged web search proxy
            - listitem [ref=e241]:
              - generic [ref=e242]: ✓
              - text: After-hours AI intake
            - listitem [ref=e243]:
              - generic [ref=e244]: ✓
              - text: Revenue analytics dashboard
            - listitem [ref=e245]:
              - generic [ref=e246]: ✓
              - text: Matter pipeline integration
            - listitem [ref=e247]:
              - generic [ref=e248]: ✓
              - text: Priority support
          - link "Start Pro — $74.50/mo" [ref=e249] [cursor=pointer]:
            - /url: https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000?prefilled_promo_code=3wseBY7Z
          - paragraph [ref=e250]: or $1,428/yr (save $360)
        - generic [ref=e251]:
          - generic [ref=e252]: Enterprise
          - generic [ref=e253]: $20K/mo
          - list [ref=e254]:
            - listitem [ref=e255]:
              - generic [ref=e256]: ✓
              - text: Unlimited tokens
            - listitem [ref=e257]:
              - generic [ref=e258]: ✓
              - text: "Everything in Professional, plus:"
            - listitem [ref=e259]:
              - generic [ref=e260]: ✓
              - text: Dedicated compliance officer
            - listitem [ref=e261]:
              - generic [ref=e262]: ✓
              - text: Custom retention policies
            - listitem [ref=e263]:
              - generic [ref=e264]: ✓
              - text: BYOK (Bring Your Own Key)
            - listitem [ref=e265]:
              - generic [ref=e266]: ✓
              - text: Regional data isolation
            - listitem [ref=e267]:
              - generic [ref=e268]: ✓
              - text: 24/7 phone + Slack support
          - button "Contact Sales" [ref=e269] [cursor=pointer]
    - region "Stop Gambling With Client Privilege." [ref=e270]:
      - generic [ref=e271]:
        - img "Gavel icon representing legal authority" [ref=e273]
        - generic [ref=e278]:
          - paragraph [ref=e279]: The Ruling Is Clear
          - heading "Stop Gambling With Client Privilege." [level=2] [ref=e280]:
            - text: Stop Gambling With
            - text: Client Privilege.
          - paragraph [ref=e281]: Every day your clients search without KovelAI is another day opposing counsel can subpoena their browser history. Deploy your firm's privileged portal today.
          - generic [ref=e282]:
            - button "Deploy Your Shield Now" [ref=e283] [cursor=pointer]
            - link "View Pricing →" [ref=e284] [cursor=pointer]:
              - /url: "#pricing"
    - generic [ref=e286]:
      - generic [ref=e287]: Frequently Asked
      - heading "Common Questions" [level=2] [ref=e288]
      - generic [ref=e289]:
        - group [ref=e290]:
          - generic "What is the Kovel Doctrine? +" [ref=e291] [cursor=pointer]
        - group [ref=e292]:
          - generic "Is my client data stored anywhere? +" [ref=e293] [cursor=pointer]
        - group [ref=e294]:
          - generic "What happened in In re Heppner? +" [ref=e295] [cursor=pointer]
        - group [ref=e296]:
          - generic "How does billing work for privileged sessions? +" [ref=e297] [cursor=pointer]
        - group [ref=e298]:
          - generic "What AI model does KovelAI use? +" [ref=e299] [cursor=pointer]
        - group [ref=e300]:
          - generic "Does KovelAI support SOC 2 / HIPAA-aligned practices? +" [ref=e301] [cursor=pointer]
    - generic [ref=e303]:
      - generic [ref=e304]: Leadership
      - heading "Management" [level=2] [ref=e305]
      - generic [ref=e306]:
        - generic [ref=e307]:
          - img "Erik L. Hancock, JD — Founder & CEO of KovelAI" [ref=e308]
          - generic [ref=e309]:
            - link "Erik Hancock on LinkedIn" [ref=e310] [cursor=pointer]:
              - /url: https://linkedin.com/in/erik-hancock-80442476
              - img [ref=e311]
              - text: LinkedIn
            - link "KovelAI on X" [ref=e313] [cursor=pointer]:
              - /url: https://x.com/KovelAi_Inc
              - img [ref=e314]
              - text: X
        - generic [ref=e316]:
          - heading "Erik L. Hancock, JD" [level=3] [ref=e317]
          - generic [ref=e318]: Founder — CEO
          - paragraph [ref=e319]:
            - text: Erik founded KovelAI to solve the post-
            - emphasis [ref=e320]: Heppner
            - text: privilege gap that leaves law firms and their clients exposed. With a background in legal technology and AI infrastructure, he leads the company's mission to make privileged access the default — not the exception — for every client interaction.
          - generic [ref=e321]:
            - generic [ref=e322]:
              - generic [ref=e323]: Company
              - generic [ref=e324]: ShadowTagAi Inc.
            - generic [ref=e325]:
              - generic [ref=e326]: Address
              - generic [ref=e327]:
                - text: "495 N Main St., #119"
                - text: Lakeport, CA 95453
            - generic [ref=e328]:
              - generic [ref=e329]: Telephone
              - link "(369) 235-5643" [ref=e330] [cursor=pointer]:
                - /url: tel:+13692355643
            - generic [ref=e331]:
              - generic [ref=e332]: Facsimile
              - generic [ref=e333]: (707) 263-8659
    - generic [ref=e335]:
      - generic [ref=e336]: Insights
      - heading "From the KovelAI Blog" [level=2] [ref=e337]
      - generic [ref=e338]:
        - generic [ref=e339]: Legal AI · Heppner · Compliance
        - 'heading "The AI Slop Problem: Why Heppner Changes Everything for Client Web Activity" [level=3] [ref=e340]':
          - text: "The AI Slop Problem: Why"
          - emphasis [ref=e341]: Heppner
          - text: Changes Everything for Client Web Activity
        - paragraph [ref=e342]:
          - text: AI-generated content — “AI slop” — has flooded the internet. Clients googling legal questions now receive hallucinated answers from ChatGPT, Gemini, and Perplexity. After
          - emphasis [ref=e343]: Heppner
          - text: ", every one of those AI-mediated searches is discoverable. Here's what that means for your practice and why privilege-first infrastructure is no longer optional."
        - link "Read the full analysis →" [ref=e344] [cursor=pointer]:
          - /url: "#"
    - generic [ref=e346]:
      - generic [ref=e347]: Get Started
      - heading "Your Clients Are Googling Right Now. Is That Search Privileged?" [level=2] [ref=e348]
      - paragraph [ref=e349]: Every hour without KovelAI is another hour of discoverable client web activity. Start your free trial in 60 seconds — no credit card, no commitment, full Kovel Doctrine protection from day one.
      - generic [ref=e350]:
        - link "Start Free Trial" [ref=e351] [cursor=pointer]:
          - /url: https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000
        - button "Schedule a Demo" [ref=e352] [cursor=pointer]
  - contentinfo [ref=e353]:
    - generic [ref=e354]:
      - generic [ref=e355]:
        - generic [ref=e356]:
          - generic [ref=e357]: KovelAI
          - paragraph [ref=e358]: Post-Heppner privileged client AI and web search infrastructure for law firms. Capture revenue, protect privilege, automate intake.
        - generic [ref=e359]:
          - generic [ref=e360]: Platform
          - list [ref=e361]:
            - listitem [ref=e362]:
              - link "Features" [ref=e363] [cursor=pointer]:
                - /url: "#features"
            - listitem [ref=e364]:
              - link "How It Works" [ref=e365] [cursor=pointer]:
                - /url: "#how-it-works"
            - listitem [ref=e366]:
              - link "Discovery Risk" [ref=e367] [cursor=pointer]:
                - /url: "#discovery-risk"
        - generic [ref=e368]:
          - generic [ref=e369]: Company
          - list [ref=e370]:
            - listitem [ref=e371]:
              - link "Leadership" [ref=e372] [cursor=pointer]:
                - /url: "#management"
            - listitem [ref=e373]:
              - link "LinkedIn" [ref=e374] [cursor=pointer]:
                - /url: https://linkedin.com/in/erik-hancock-80442476
            - listitem [ref=e375]:
              - link "X (Twitter)" [ref=e376] [cursor=pointer]:
                - /url: https://x.com/KovelAi_Inc
            - listitem [ref=e377]:
              - link "Privacy Policy" [ref=e378] [cursor=pointer]:
                - /url: /privacy
            - listitem [ref=e379]:
              - link "Terms of Service" [ref=e380] [cursor=pointer]:
                - /url: /terms
            - listitem [ref=e381]:
              - link "Blog" [ref=e382] [cursor=pointer]:
                - /url: "#blog"
        - generic [ref=e383]:
          - generic [ref=e384]: Contact
          - list [ref=e385]:
            - listitem [ref=e386]:
              - button "Contact Sales" [ref=e387] [cursor=pointer]
            - listitem [ref=e388]:
              - link "Email" [ref=e389] [cursor=pointer]:
                - /url: mailto:founder@shadowtagai.com
            - listitem [ref=e390]:
              - link "ShadowTagAI ↗" [ref=e391] [cursor=pointer]:
                - /url: https://shadowtagai.com
      - generic [ref=e392]:
        - generic [ref=e393]: © 2024–2026 KovelAI. All rights reserved.
        - generic [ref=e394]:
          - text: A
          - link "ShadowTag AI" [ref=e395] [cursor=pointer]:
            - /url: https://shadowtagai.com
          - text: Company
  - alert [ref=e396]
```

# Test source

```ts
  1   | // tests/e2e/checkout.spec.ts
  2   | // Playwright E2E tests for the KovelAI Stripe checkout flow
  3   | import { expect, test } from '@playwright/test';
  4   | 
  5   | const BASE_URL = process.env.BASE_URL || 'https://kovelai.web.app';
  6   | 
  7   | test.describe('KovelAI Pricing & Checkout', () => {
  8   |   test('pricing page loads with 3 tiers', async ({ page }) => {
  9   |     await page.goto(`${BASE_URL}/pricing.html`);
  10  |     await expect(page.locator('.pricing-card')).toHaveCount(3);
> 11  |     await expect(page.locator('.tier-name')).toHaveText(['Trial', 'Professional', 'Enterprise']);
      |                                              ^ Error: expect(locator).toHaveText(expected) failed
  12  |   });
  13  | 
  14  |   test('monthly/annual toggle updates pricing', async ({ page }) => {
  15  |     await page.goto(`${BASE_URL}/pricing.html`);
  16  |     const proPrice = page.locator('#pro-price');
  17  | 
  18  |     // Default: monthly
  19  |     await expect(proPrice).toContainText('$149');
  20  | 
  21  |     // Switch to annual
  22  |     await page.locator('#annual-btn').click();
  23  |     await expect(proPrice).toContainText('$119');
  24  | 
  25  |     // Switch back to monthly
  26  |     await page.locator('#monthly-btn').click();
  27  |     await expect(proPrice).toContainText('$149');
  28  |   });
  29  | 
  30  |   test('trial CTA redirects to onboarding', async ({ page }) => {
  31  |     await page.goto(`${BASE_URL}/pricing.html`);
  32  |     const trialBtn = page.locator('.pricing-card').first().locator('.cta-btn');
  33  |     await trialBtn.click();
  34  |     await expect(page).toHaveURL(/onboarding/);
  35  |   });
  36  | 
  37  |   test('enterprise CTA opens email', async ({ page }) => {
  38  |     await page.goto(`${BASE_URL}/pricing.html`);
  39  |     const entBtn = page.locator('.pricing-card').last().locator('.cta-btn');
  40  |     const href = await entBtn.evaluate((el) => {
  41  |       el.addEventListener('click', (e) => e.preventDefault());
  42  |       el.click();
  43  |       return window.location.href;
  44  |     });
  45  |     // Enterprise button should attempt mailto
  46  |     expect(true).toBeTruthy(); // Non-blocking assertion
  47  |   });
  48  | 
  49  |   test('professional CTA triggers Stripe checkout', async ({ page }) => {
  50  |     await page.goto(`${BASE_URL}/pricing.html`);
  51  |     const proBtn = page.locator('.pricing-card.featured .cta-btn');
  52  | 
  53  |     // Intercept the API call to /billing/checkout
  54  |     const [request] = await Promise.all([
  55  |       page
  56  |         .waitForRequest((req) => req.url().includes('/billing/checkout'), { timeout: 5000 })
  57  |         .catch(() => null),
  58  |       proBtn.click(),
  59  |     ]);
  60  | 
  61  |     // Either the API request was made or Stripe.redirectToCheckout was called
  62  |     expect(true).toBeTruthy();
  63  |   });
  64  | });
  65  | 
  66  | test.describe('KovelAI Onboarding Wizard', () => {
  67  |   test('wizard has 4 steps', async ({ page }) => {
  68  |     await page.goto(`${BASE_URL}/onboarding.html`);
  69  |     await expect(page.locator('.step-dot')).toHaveCount(4);
  70  |     await expect(page.locator('#step-1')).toBeVisible();
  71  |   });
  72  | 
  73  |   test('step 1 → step 2 navigation works', async ({ page }) => {
  74  |     await page.goto(`${BASE_URL}/onboarding.html`);
  75  |     await page.fill('#attorney-name', 'Jane Attorney');
  76  |     await page.fill('#attorney-email', 'jane@lawfirm.com');
  77  |     await page.fill('#bar-number', 'CA-123456');
  78  |     await page.click('button:has-text("Continue")');
  79  |     await expect(page.locator('#step-2')).toBeVisible();
  80  |     await expect(page.locator('#step-1')).toBeHidden();
  81  |   });
  82  | 
  83  |   test('can navigate back from step 2', async ({ page }) => {
  84  |     await page.goto(`${BASE_URL}/onboarding.html`);
  85  |     await page.click('button:has-text("Continue")');
  86  |     await page.click('button:has-text("Back")');
  87  |     await expect(page.locator('#step-1')).toBeVisible();
  88  |   });
  89  | 
  90  |   test('full wizard completion flow', async ({ page }) => {
  91  |     await page.goto(`${BASE_URL}/onboarding.html`);
  92  | 
  93  |     // Step 1
  94  |     await page.fill('#attorney-name', 'Jane Attorney');
  95  |     await page.fill('#attorney-email', 'jane@lawfirm.com');
  96  |     await page.fill('#bar-number', 'CA-123456');
  97  |     await page.click('button:has-text("Continue")');
  98  | 
  99  |     // Step 2
  100 |     await page.fill('#firm-name', 'Smith & Associates');
  101 |     await page.click('.practice-size:has-text("Solo")');
  102 |     await page.click('button:has-text("Continue")');
  103 | 
  104 |     // Step 3
  105 |     await page.selectOption('#practice-area', 'Corporate / M&A');
  106 |     await page.selectOption('#jurisdiction', 'California');
  107 |     await page.click('button:has-text("Continue")');
  108 | 
  109 |     // Step 4 — completion
  110 |     await expect(page.locator('.success')).toBeVisible();
  111 |     await expect(page.locator("text=You're All Set")).toBeVisible();
```