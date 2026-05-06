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
  - link "Skip to main content" [ref=e2]:
    - /url: "#main-content"
  - navigation [ref=e3]:
    - generic [ref=e4]:
      - link "KovelAI logo KovelAI" [ref=e5]:
        - /url: /
        - img "KovelAI logo" [ref=e6]
        - text: KovelAI
      - generic [ref=e7]:
        - button "Contact Sales" [ref=e8] [cursor=pointer]
        - button "Toggle navigation" [ref=e9]: ☰
  - main [ref=e10]:
    - generic [ref=e11]:
      - generic:
        - img "Protective shield emblem"
      - generic [ref=e12]:
        - generic [ref=e13]: Privilege-Protected Infrastructure· ATTORNEY-MONITORED · HEPPNER-COMPLIANT
        - heading "Shield Your Client's Research From Discovery." [level=1] [ref=e14]:
          - text: Shield Your Client's Research
          - text: From Discovery.
        - heading "Deploy privileged search infrastructure your clients use under your oversight—so opposing counsel discovers nothing." [level=2] [ref=e15]
        - paragraph [ref=e16]:
          - text: After
          - emphasis [ref=e17]: In re Heppner
          - text: (S.D.N.Y., Feb. 2026), every web search and AI conversation your client conducts outside your firm's umbrella is fair game for opposing counsel. KovelAI is the turnkey infrastructure you deploy to close that gap.
        - paragraph [ref=e18]:
          - text: Your clients search at will under your privilege umbrella. You monitor every session, deliver the first legal opinion, and bill their credit card automatically.
          - strong [ref=e19]: “Either you do it through our firm's KovelAI, or proceed at your peril.”
        - generic [ref=e20]:
          - button "Deploy Your Firm's Portal" [ref=e21] [cursor=pointer]
          - link "See How Privilege Works →" [ref=e22] [cursor=pointer]:
            - /url: "#how-it-works"
        - paragraph [ref=e23]: Clients log in · You monitor all sessions · You give the first opinion · Automatic billing · Opposing counsel gets nothing
    - generic [ref=e26]:
      - generic [ref=e27]:
        - generic [ref=e28]: 3x+
        - generic [ref=e29]: Intake Revenue
      - generic [ref=e30]:
        - generic [ref=e31]: "0"
        - generic [ref=e32]: Data Retained
      - generic [ref=e33]:
        - generic [ref=e34]: 24/7
        - generic [ref=e35]: Client Capture
      - generic [ref=e36]:
        - generic [ref=e37]: ↑ ACV
        - generic [ref=e38]: Revenue per Matter
    - generic [ref=e40]:
      - generic [ref=e41]: The Heppner Problem
      - heading "Your Clients' Internet Searches Are Discoverable." [level=2] [ref=e42]
      - paragraph [ref=e43]:
        - text: After
        - emphasis [ref=e44]: In re Heppner
        - text: ", any client web search conducted outside privileged channels is fair game in litigation. This includes Google searches, legal research, and even AI chatbot interactions. KovelAI wraps these activities under attorney-client privilege — and bills for the protection."
      - generic [ref=e45]:
        - generic [ref=e46]:
          - generic [ref=e47]: ⚖️
          - heading "Privilege Shield" [level=3] [ref=e48]
          - paragraph [ref=e49]: All client web activity routed through your firm's privileged infrastructure. Zero discoverable footprint.
        - generic [ref=e50]:
          - generic [ref=e51]: 🔒
          - heading "Zero Data Retention" [level=3] [ref=e52]
          - paragraph [ref=e53]: No search logs, no browsing history, no metadata. The data that doesn't exist can't be subpoenaed.
        - generic [ref=e54]:
          - generic [ref=e55]: 💰
          - heading "Revenue at the Front Door" [level=3] [ref=e56]
          - paragraph [ref=e57]: Clients pay for privileged access. Your firm captures intake revenue 24/7, even after hours.
    - generic [ref=e59]:
      - generic [ref=e60]: Platform
      - heading "Built for Law Firms That Think Like Businesses" [level=2] [ref=e61]
      - paragraph [ref=e62]: KovelAI combines privileged communication infrastructure with AI-powered intake — turning your firm's front door into a revenue engine that never sleeps.
      - generic [ref=e63]:
        - generic [ref=e64]:
          - img [ref=e66]
          - heading "AI-Powered Intake" [level=3] [ref=e70]
          - paragraph [ref=e71]: Intelligent after-hours client intake that captures, qualifies, and organizes potential matters while your team rests.
        - generic [ref=e72]:
          - img [ref=e74]
          - heading "Matter Pipeline" [level=3] [ref=e78]
          - paragraph [ref=e79]: Every client interaction becomes a tracked, scored, and prioritized entry in your matter pipeline. No leads lost.
        - generic [ref=e80]:
          - img [ref=e82]
          - heading "Privileged Search" [level=3] [ref=e85]
          - paragraph [ref=e86]: Clients search the web through your firm's infrastructure. Every query is privileged, every session is billed.
        - generic [ref=e87]:
          - img [ref=e89]
          - heading "After-Hours Capture" [level=3] [ref=e92]
          - paragraph [ref=e93]: Panic calls at 2 AM become organized, retained matters by 8 AM. Your paralegal costs drop, your intake revenue rises.
        - generic [ref=e94]:
          - img [ref=e96]
          - heading "Compliance First" [level=3] [ref=e100]
          - paragraph [ref=e101]: Pursuing SOC 2 Type II certification. HIPAA-supportive architecture. Built to withstand judicial scrutiny on privilege claims.
        - generic [ref=e102]:
          - img [ref=e104]
          - heading "Revenue Analytics" [level=3] [ref=e107]
          - paragraph [ref=e108]: Real-time dashboards showing intake conversion, after-hours capture rate, and revenue per privileged session.
    - generic [ref=e110]:
      - generic [ref=e111]: Process
      - heading "Three Steps to Privileged Revenue" [level=2] [ref=e112]
      - generic [ref=e113]:
        - generic [ref=e114]:
          - generic [ref=e115]: "01"
          - heading "Connect" [level=3] [ref=e116]
          - paragraph [ref=e117]: Your clients access KovelAI through your firm's branded portal. Every session is logged under privilege.
        - generic [ref=e118]:
          - generic [ref=e119]: "02"
          - heading "Protect" [level=3] [ref=e120]
          - paragraph [ref=e121]: Web searches, AI queries, and document uploads are routed through privileged infrastructure. Zero exposure.
        - generic [ref=e122]:
          - generic [ref=e123]: "03"
          - heading "Bill" [level=3] [ref=e124]
          - paragraph [ref=e125]: Each privileged session generates billable entries. After-hours intake converts to retained matters automatically.
    - generic [ref=e127]:
      - generic [ref=e128]: From the Bar
      - heading "What Attorneys Are Saying" [level=2] [ref=e129]
      - generic [ref=e130]:
        - generic [ref=e131]:
          - generic [ref=e132]: ★★★★★
          - blockquote [ref=e133]: "\"We had a client whose Google search history was subpoenaed mid-litigation. After Heppner, we moved all client research to KovelAI. The privilege held. That one save paid for three years of service.\""
          - generic [ref=e134]:
            - generic [ref=e135]: MR
            - generic [ref=e136]:
              - generic [ref=e137]: Managing Partner
              - generic [ref=e138]: Am Law 200 Litigation Practice, New York
        - generic [ref=e139]:
          - generic [ref=e140]: ★★★★★
          - blockquote [ref=e141]: "\"The after-hours capture alone justified the cost. We went from losing 60% of weekend inquiries to converting 85% into retained matters. The privilege protection is the bonus.\""
          - generic [ref=e142]:
            - generic [ref=e143]: SK
            - generic [ref=e144]:
              - generic [ref=e145]: Senior Associate
              - generic [ref=e146]: Boutique Family Law, Los Angeles
        - generic [ref=e147]:
          - generic [ref=e148]: ★★★★★
          - blockquote [ref=e149]: "\"We bill clients $250/month for privileged search access. They're happy to pay because they understand the Heppner risk. Our intake revenue is up 40% since launch.\""
          - generic [ref=e150]:
            - generic [ref=e151]: JL
            - generic [ref=e152]:
              - generic [ref=e153]: Founding Partner
              - generic [ref=e154]: Criminal Defense, Chicago
    - generic [ref=e156]:
      - generic [ref=e157]: Why KovelAI
      - heading "KovelAI vs. Doing Nothing" [level=2] [ref=e158]
      - paragraph [ref=e159]: Every day without privilege protection is another day opposing counsel can mine your clients' digital footprint.
      - table [ref=e161]:
        - rowgroup [ref=e162]:
          - row "Feature Without KovelAI Shielded by Attorney-Client Privilege" [ref=e163]:
            - columnheader "Feature" [ref=e164]
            - columnheader "Without KovelAI" [ref=e165]
            - columnheader "Shielded by Attorney-Client Privilege" [ref=e166]
        - rowgroup [ref=e167]:
          - row "Client web searches ⚠️ Discoverable ✅ Privileged" [ref=e168]:
            - rowheader "Client web searches" [ref=e169]
            - cell "⚠️ Discoverable" [ref=e170]
            - cell "✅ Privileged" [ref=e171]
          - row "AI chatbot conversations ⚠️ Subpoena target ✅ Shielded under Kovel" [ref=e172]:
            - rowheader "AI chatbot conversations" [ref=e173]
            - cell "⚠️ Subpoena target" [ref=e174]
            - cell "✅ Shielded under Kovel" [ref=e175]
          - row "After-hours client inquiries ❌ Lost to voicemail ✅ Captured & retained" [ref=e176]:
            - rowheader "After-hours client inquiries" [ref=e177]
            - cell "❌ Lost to voicemail" [ref=e178]
            - cell "✅ Captured & retained" [ref=e179]
          - row "Data retention ⚠️ Browser logs everywhere ✅ Zero retention (RAM only)" [ref=e180]:
            - rowheader "Data retention" [ref=e181]
            - cell "⚠️ Browser logs everywhere" [ref=e182]
            - cell "✅ Zero retention (RAM only)" [ref=e183]
          - row "Revenue per interaction $0 (unbilled panic calls) $50–$250/session (billable)" [ref=e184]:
            - rowheader "Revenue per interaction" [ref=e185]
            - cell "$0 (unbilled panic calls)" [ref=e186]
            - cell "$50–$250/session (billable)" [ref=e187]
          - row "Paralegal cost for intake $45–$75/hour $0 (automated)" [ref=e188]:
            - rowheader "Paralegal cost for intake" [ref=e189]
            - cell "$45–$75/hour" [ref=e190]
            - cell "$0 (automated)" [ref=e191]
          - row "Compliance posture ❌ Hope-based ✅ SOC 2 audit-ready, HIPAA-supportive" [ref=e192]:
            - rowheader "Compliance posture" [ref=e193]
            - cell "❌ Hope-based" [ref=e194]
            - cell "✅ SOC 2 audit-ready, HIPAA-supportive" [ref=e195]
    - generic [ref=e197]:
      - generic [ref=e198]: Pricing
      - heading "Simple, Transparent Pricing" [level=2] [ref=e199]
      - paragraph [ref=e200]: Every plan includes Kovel Doctrine privilege protection, zero data retention, and Judge 6 compliance governance.
      - generic [ref=e201]:
        - generic [ref=e202]:
          - generic [ref=e203]: Trial
          - generic [ref=e204]: $0/mo
          - list [ref=e205]:
            - listitem [ref=e206]:
              - generic [ref=e207]: ✓
              - text: 10,000 tokens/month
            - listitem [ref=e208]:
              - generic [ref=e209]: ✓
              - text: Kovel Doctrine protection
            - listitem [ref=e210]:
              - generic [ref=e211]: ✓
              - text: Zero data retention
            - listitem [ref=e212]:
              - generic [ref=e213]: ✓
              - text: Basic intake dashboard
            - listitem [ref=e214]:
              - generic [ref=e215]: ✓
              - text: Email support
          - link "Start Free Trial" [ref=e216] [cursor=pointer]:
            - /url: https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000
        - generic [ref=e217]:
          - generic [ref=e218]: Most Popular
          - generic [ref=e219]: 50% OFF — Beta Launch
          - generic [ref=e220]: Professional
          - generic [ref=e221]: $149/mo
          - list [ref=e222]:
            - listitem [ref=e223]:
              - generic [ref=e224]: ✓
              - text: 100,000 tokens/month
            - listitem [ref=e225]:
              - generic [ref=e226]: ✓
              - text: "Everything in Trial, plus:"
            - listitem [ref=e227]:
              - generic [ref=e228]: ✓
              - text: Privileged web search proxy
            - listitem [ref=e229]:
              - generic [ref=e230]: ✓
              - text: After-hours AI intake
            - listitem [ref=e231]:
              - generic [ref=e232]: ✓
              - text: Revenue analytics dashboard
            - listitem [ref=e233]:
              - generic [ref=e234]: ✓
              - text: Matter pipeline integration
            - listitem [ref=e235]:
              - generic [ref=e236]: ✓
              - text: Priority support
          - link "Start Pro — $74.50/mo" [ref=e237] [cursor=pointer]:
            - /url: https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000?prefilled_promo_code=3wseBY7Z
          - paragraph [ref=e238]: or $1,428/yr (save $360)
        - generic [ref=e239]:
          - generic [ref=e240]: Enterprise
          - generic [ref=e241]: $20K/mo
          - list [ref=e242]:
            - listitem [ref=e243]:
              - generic [ref=e244]: ✓
              - text: Unlimited tokens
            - listitem [ref=e245]:
              - generic [ref=e246]: ✓
              - text: "Everything in Professional, plus:"
            - listitem [ref=e247]:
              - generic [ref=e248]: ✓
              - text: Dedicated compliance officer
            - listitem [ref=e249]:
              - generic [ref=e250]: ✓
              - text: Custom retention policies
            - listitem [ref=e251]:
              - generic [ref=e252]: ✓
              - text: BYOK (Bring Your Own Key)
            - listitem [ref=e253]:
              - generic [ref=e254]: ✓
              - text: Regional data isolation
            - listitem [ref=e255]:
              - generic [ref=e256]: ✓
              - text: 24/7 phone + Slack support
          - button "Contact Sales" [ref=e257] [cursor=pointer]
    - region "Stop Gambling With Client Privilege." [ref=e258]:
      - generic [ref=e259]:
        - img "Gavel icon representing legal authority" [ref=e261]
        - generic [ref=e266]:
          - paragraph [ref=e267]: The Ruling Is Clear
          - heading "Stop Gambling With Client Privilege." [level=2] [ref=e268]:
            - text: Stop Gambling With
            - text: Client Privilege.
          - paragraph [ref=e269]: Every day your clients search without KovelAI is another day opposing counsel can subpoena their browser history. Deploy your firm's privileged portal today.
          - generic [ref=e270]:
            - button "Deploy Your Shield Now" [ref=e271] [cursor=pointer]
            - link "View Pricing →" [ref=e272] [cursor=pointer]:
              - /url: "#pricing"
    - generic [ref=e274]:
      - generic [ref=e275]: Frequently Asked
      - heading "Common Questions" [level=2] [ref=e276]
      - generic [ref=e277]:
        - group [ref=e278]:
          - generic "What is the Kovel Doctrine? +" [ref=e279] [cursor=pointer]
        - group [ref=e280]:
          - generic "Is my client data stored anywhere? +" [ref=e281] [cursor=pointer]
        - group [ref=e282]:
          - generic "What happened in In re Heppner? +" [ref=e283] [cursor=pointer]
        - group [ref=e284]:
          - generic "How does billing work for privileged sessions? +" [ref=e285] [cursor=pointer]
        - group [ref=e286]:
          - generic "What AI model does KovelAI use? +" [ref=e287] [cursor=pointer]
        - group [ref=e288]:
          - generic "Does KovelAI support SOC 2 / HIPAA-aligned practices? +" [ref=e289] [cursor=pointer]
    - generic [ref=e291]:
      - generic [ref=e292]: Leadership
      - heading "Management" [level=2] [ref=e293]
      - generic [ref=e294]:
        - generic [ref=e295]:
          - img "Erik L. Hancock, JD — Founder & CEO of KovelAI" [ref=e296]
          - generic [ref=e297]:
            - link "Erik Hancock on LinkedIn" [ref=e298]:
              - /url: https://linkedin.com/in/erik-hancock-80442476
              - img [ref=e299]
              - text: LinkedIn
            - link "KovelAI on X" [ref=e301]:
              - /url: https://x.com/KovelAi_Inc
              - img [ref=e302]
              - text: X
        - generic [ref=e304]:
          - heading "Erik L. Hancock, JD" [level=3] [ref=e305]
          - generic [ref=e306]: Founder — CEO
          - paragraph [ref=e307]:
            - text: Erik founded KovelAI to solve the post-
            - emphasis [ref=e308]: Heppner
            - text: privilege gap that leaves law firms and their clients exposed. With a background in legal technology and AI infrastructure, he leads the company's mission to make privileged access the default — not the exception — for every client interaction.
          - generic [ref=e309]:
            - generic [ref=e310]:
              - generic [ref=e311]: Company
              - generic [ref=e312]: ShadowTagAi Inc.
            - generic [ref=e313]:
              - generic [ref=e314]: Address
              - generic [ref=e315]:
                - text: "495 N Main St., #119"
                - text: Lakeport, CA 95453
            - generic [ref=e316]:
              - generic [ref=e317]: Telephone
              - link "(369) 235-5643" [ref=e318]:
                - /url: tel:+13692355643
            - generic [ref=e319]:
              - generic [ref=e320]: Facsimile
              - generic [ref=e321]: (707) 263-8659
    - generic [ref=e323]:
      - generic [ref=e324]: Insights
      - heading "From the KovelAI Blog" [level=2] [ref=e325]
      - generic [ref=e326]:
        - generic [ref=e327]: Legal AI · Heppner · Compliance
        - 'heading "The AI Slop Problem: Why Heppner Changes Everything for Client Web Activity" [level=3] [ref=e328]':
          - text: "The AI Slop Problem: Why"
          - emphasis [ref=e329]: Heppner
          - text: Changes Everything for Client Web Activity
        - paragraph [ref=e330]:
          - text: AI-generated content — “AI slop” — has flooded the internet. Clients googling legal questions now receive hallucinated answers from ChatGPT, Gemini, and Perplexity. After
          - emphasis [ref=e331]: Heppner
          - text: ", every one of those AI-mediated searches is discoverable. Here's what that means for your practice and why privilege-first infrastructure is no longer optional."
        - link "Read the full analysis →" [ref=e332]:
          - /url: "#"
    - generic [ref=e334]:
      - generic [ref=e335]: Get Started
      - heading "Your Clients Are Googling Right Now. Is That Search Privileged?" [level=2] [ref=e336]
      - paragraph [ref=e337]: Every hour without KovelAI is another hour of discoverable client web activity. Start your free trial in 60 seconds — no credit card, no commitment, full Kovel Doctrine protection from day one.
      - generic [ref=e338]:
        - link "Start Free Trial" [ref=e339] [cursor=pointer]:
          - /url: https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000
        - button "Schedule a Demo" [ref=e340] [cursor=pointer]
  - contentinfo [ref=e341]:
    - generic [ref=e342]:
      - generic [ref=e343]:
        - generic [ref=e344]:
          - generic [ref=e345]: KovelAI
          - paragraph [ref=e346]: Post-Heppner privileged client AI and web search infrastructure for law firms. Capture revenue, protect privilege, automate intake.
        - generic [ref=e347]:
          - generic [ref=e348]: Platform
          - list [ref=e349]:
            - listitem [ref=e350]:
              - link "Features" [ref=e351]:
                - /url: "#features"
            - listitem [ref=e352]:
              - link "How It Works" [ref=e353]:
                - /url: "#how-it-works"
            - listitem [ref=e354]:
              - link "Discovery Risk" [ref=e355]:
                - /url: "#discovery-risk"
        - generic [ref=e356]:
          - generic [ref=e357]: Company
          - list [ref=e358]:
            - listitem [ref=e359]:
              - link "Leadership" [ref=e360]:
                - /url: "#management"
            - listitem [ref=e361]:
              - link "LinkedIn" [ref=e362]:
                - /url: https://linkedin.com/in/erik-hancock-80442476
            - listitem [ref=e363]:
              - link "X (Twitter)" [ref=e364]:
                - /url: https://x.com/KovelAi_Inc
            - listitem [ref=e365]:
              - link "Privacy Policy" [ref=e366]:
                - /url: /privacy
            - listitem [ref=e367]:
              - link "Terms of Service" [ref=e368]:
                - /url: /terms
            - listitem [ref=e369]:
              - link "Blog" [ref=e370]:
                - /url: "#blog"
        - generic [ref=e371]:
          - generic [ref=e372]: Contact
          - list [ref=e373]:
            - listitem [ref=e374]:
              - button "Contact Sales" [ref=e375] [cursor=pointer]
            - listitem [ref=e376]:
              - link "Email" [ref=e377]:
                - /url: mailto:founder@shadowtagai.com
            - listitem [ref=e378]:
              - link "ShadowTagAI ↗" [ref=e379]:
                - /url: https://shadowtagai.com
      - generic [ref=e380]:
        - generic [ref=e381]: © 2024–2026 KovelAI. All rights reserved.
        - generic [ref=e382]:
          - text: A
          - link "ShadowTag AI" [ref=e383]:
            - /url: https://shadowtagai.com
          - text: Company
  - alert [ref=e384]
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