"""Landing page generator for ShadowTag-v2 Intelligence Services.

Generates static HTML landing pages with:
- Hero section
- Pricing tables
- Feature comparisons
- CTA buttons
- Stripe checkout integration
"""

from . import PRICING_PLANS, PricingTier


def generate_landing_page(
    stripe_publishable_key: str = "pk_test_...",
    custom_domain: str = "shadowtag_v4-intelligence.com",
) -> str:
    """Generate complete landing page HTML.

    Args:
        stripe_publishable_key: Stripe publishable key
        custom_domain: Custom domain for branding

    Returns:
        Complete HTML page

    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShadowTag-v2 Intelligence - Multi-Source Intelligence Collection Platform</title>
    <meta name="description" content="Production-ready intelligence collection with ethical crawling, tier classification, and ML-powered insights. From $99/month.">

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
            text-align: center;
        }}

        .hero h1 {{
            font-size: 3.5rem;
            margin-bottom: 20px;
            font-weight: 700;
        }}

        .hero p {{
            font-size: 1.5rem;
            margin-bottom: 40px;
            opacity: 0.95;
        }}

        .hero .stats {{
            display: flex;
            justify-content: center;
            gap: 60px;
            margin-top: 60px;
        }}

        .hero .stat {{
            text-align: center;
        }}

        .hero .stat-number {{
            font-size: 3rem;
            font-weight: bold;
        }}

        .hero .stat-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}

        .cta-button {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 15px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: transform 0.2s;
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        /* Features Section */
        .features {{
            padding: 80px 0;
            background: #f9fafb;
        }}

        .features h2 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 60px;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
        }}

        .feature-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .feature-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #667eea;
        }}

        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 20px;
        }}

        /* Pricing Section */
        .pricing {{
            padding: 80px 0;
        }}

        .pricing h2 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 20px;
        }}

        .pricing-subtitle {{
            text-align: center;
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 60px;
        }}

        .pricing-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .pricing-card {{
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 15px;
            padding: 40px 30px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .pricing-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}

        .pricing-card.featured {{
            border-color: #667eea;
            border-width: 3px;
            position: relative;
        }}

        .pricing-card.featured::before {{
            content: "MOST POPULAR";
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            background: #667eea;
            color: white;
            padding: 5px 20px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }}

        .pricing-tier {{
            font-size: 1.2rem;
            color: #667eea;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .pricing-price {{
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .pricing-period {{
            color: #666;
            margin-bottom: 30px;
        }}

        .pricing-features {{
            list-style: none;
            margin: 30px 0;
            text-align: left;
        }}

        .pricing-features li {{
            padding: 10px 0;
            border-bottom: 1px solid #f3f4f6;
        }}

        .pricing-features li:before {{
            content: "✓ ";
            color: #10b981;
            font-weight: bold;
            margin-right: 10px;
        }}

        .pricing-cta {{
            display: block;
            width: 100%;
            background: #667eea;
            color: white;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .pricing-cta:hover {{
            background: #5568d3;
        }}

        .pricing-card.featured .pricing-cta {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        /* ROI Calculator */
        .roi-section {{
            background: #f9fafb;
            padding: 80px 0;
        }}

        .roi-section h2 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 40px;
        }}

        .roi-calculator {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .roi-calculator input {{
            width: 100%;
            padding: 15px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1.1rem;
            margin: 10px 0 30px 0;
        }}

        .roi-result {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-top: 30px;
        }}

        .roi-result h3 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}

        /* Footer */
        footer {{
            background: #1f2937;
            color: white;
            padding: 40px 0;
            text-align: center;
        }}

        footer a {{
            color: #667eea;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Intelligence Collection, Automated</h1>
            <p>Multi-source intelligence gathering with ethical crawling, ML-powered insights, and production-ready infrastructure</p>
            <a href="#pricing" class="cta-button">Start Free Trial</a>

            <div class="stats">
                <div class="stat">
                    <div class="stat-number">1000+</div>
                    <div class="stat-label">Items/Day</div>
                </div>
                <div class="stat">
                    <div class="stat-number">6</div>
                    <div class="stat-label">Source Types</div>
                </div>
                <div class="stat">
                    <div class="stat-number">95%</div>
                    <div class="stat-label">Compliance Rate</div>
                </div>
                <div class="stat">
                    <div class="stat-number">45min</div>
                    <div class="stat-label">Nightly Runtime</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="features">
        <div class="container">
            <h2>Everything You Need to Build Intelligence Pipelines</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📥</div>
                    <h3>Multi-Source Collection</h3>
                    <p>YouTube, Twitter, News, Reddit, Academic sources. Configurable rate limits and priorities.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">✅</div>
                    <h3>Ethical Compliance</h3>
                    <p>robots.txt respect, rate limiting, transparent user agents. 95%+ compliance out of the box.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🏆</div>
                    <h3>Tier Classification</h3>
                    <p>Automatic quality scoring. Tier 1 (high), Tier 2 (medium), Tier 3 (low) with multi-factor analysis.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Visualizations</h3>
                    <p>ASCII, Mermaid, and interactive charts. Tier distributions, source coverage, compliance trends.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>ML Anomaly Detection</h3>
                    <p>Predictive alerting, cost spike detection, source outage prediction. Professional tier and above.</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3>Production Ready</h3>
                    <p>Circuit breakers, retry logic, graceful degradation. <200ms overhead on 45-min runtime.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Pricing Section -->
    <section class="pricing" id="pricing">
        <div class="container">
            <h2>Simple, Transparent Pricing</h2>
            <p class="pricing-subtitle">Choose the plan that fits your needs. All plans include 14-day free trial.</p>

            <div class="pricing-grid">
                {_generate_pricing_cards()}
            </div>

            <p style="text-align: center; margin-top: 40px; color: #666;">
                All prices in USD. Annual billing saves 16% (2 months free). Enterprise includes custom SLAs and dedicated support.
            </p>
        </div>
    </section>

    <!-- ROI Calculator -->
    <section class="roi-section">
        <div class="container">
            <h2>Calculate Your ROI</h2>
            <div class="roi-calculator">
                <label>How many intelligence analysts do you have?</label>
                <input type="number" id="analysts" value="2" min="1" max="100">

                <label>Average hourly rate per analyst ($)</label>
                <input type="number" id="hourly-rate" value="75" min="1" max="500">

                <label>Hours spent on manual collection per week</label>
                <input type="number" id="hours-week" value="10" min="1" max="100">

                <div class="roi-result">
                    <h3 id="savings-result">$39,000/year saved</h3>
                    <p>With ShadowTag-v2 Intelligence, automate 80% of manual collection work</p>
                    <p style="margin-top: 20px;"><strong>ROI: 13x</strong> (Professional plan at $299/month)</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <p>&copy; 2025 ShadowTag-v2 Intelligence Services. Built on the PNKLN Core Stack™.</p>
            <p style="margin-top: 10px;">
                <a href="#">Documentation</a> |
                <a href="#">API Reference</a> |
                <a href="#">Privacy Policy</a> |
                <a href="#">Terms of Service</a>
            </p>
        </div>
    </footer>

    <script src="https://js.stripe.com/v3/"></script>
    <script>
        // Initialize Stripe
        const stripe = Stripe('{stripe_publishable_key}');

        // Pricing button handlers
        document.querySelectorAll('.pricing-cta').forEach(button => {{
            button.addEventListener('click', async (e) => {{
                const tier = e.target.dataset.tier;
                const period = e.target.dataset.period;

                // In production: Create checkout session via API
                console.log(`Selected: ${{tier}} - ${{period}}`);

                // Redirect to Stripe Checkout
                // const response = await fetch('/api/create-checkout-session', {{
                //     method: 'POST',
                //     headers: {{ 'Content-Type': 'application/json' }},
                //     body: JSON.stringify({{ tier, period }})
                // }});
                // const {{ sessionId }} = await response.json();
                // stripe.redirectToCheckout({{ sessionId }});
            }});
        }});

        // ROI Calculator
        function calculateROI() {{
            const analysts = parseInt(document.getElementById('analysts').value) || 2;
            const hourlyRate = parseInt(document.getElementById('hourly-rate').value) || 75;
            const hoursPerWeek = parseInt(document.getElementById('hours-week').value) || 10;

            const weeklyManualCost = analysts * hourlyRate * hoursPerWeek;
            const annualManualCost = weeklyManualCost * 52;
            const automationSavings = annualManualCost * 0.8; // 80% automation
            const ShadowTag-v2Cost = 299 * 12; // Professional plan
            const netSavings = automationSavings - ShadowTag-v2Cost;
            const roi = (netSavings / ShadowTag-v2Cost).toFixed(1);

            document.getElementById('savings-result').textContent =
                `$$${{netSavings.toLocaleString()}}/year saved`;

            document.querySelector('.roi-result p:last-child').innerHTML =
                `<strong>ROI: ${{roi}}x</strong> (Professional plan at $299/month)`;
        }}

        document.getElementById('analysts').addEventListener('input', calculateROI);
        document.getElementById('hourly-rate').addEventListener('input', calculateROI);
        document.getElementById('hours-week').addEventListener('input', calculateROI);
    </script>
</body>
</html>"""

    return html


def _generate_pricing_cards() -> str:
    """Generate pricing card HTML."""
    cards = []

    tier_order = [
        PricingTier.FREE,
        PricingTier.STARTER,
        PricingTier.PROFESSIONAL,
        PricingTier.ENTERPRISE,
    ]

    for tier in tier_order:
        plan = PRICING_PLANS[tier]
        featured = "featured" if tier == PricingTier.PROFESSIONAL else ""

        features = [
            f"Up to {plan.max_sources:,} sources"
            if plan.max_sources < 999
            else "Unlimited sources",
            f"{plan.max_items_per_day:,} items/day"
            if plan.max_items_per_day < 999999
            else "Unlimited items",
            f"{plan.max_api_calls_per_month:,} API calls/month"
            if plan.max_api_calls_per_month < 9999999
            else "Unlimited API calls",
        ]

        if plan.visualizations:
            features.append("Visualizations included")
        if plan.ml_anomaly_detection:
            features.append("ML anomaly detection")
        if plan.priority_support:
            features.append("Priority support")
        if plan.custom_integrations:
            features.append("Custom integrations")
        if plan.sla_guarantee:
            features.append(f"{plan.sla_guarantee}% SLA guarantee")

        features_html = "\n".join(f"<li>{f}</li>" for f in features)

        price_display = f"${int(plan.price_monthly)}" if plan.price_monthly > 0 else "Free"
        button_text = "Start Free Trial" if plan.price_monthly > 0 else "Get Started"

        card = f"""
                <div class="pricing-card {featured}">
                    <div class="pricing-tier">{plan.name}</div>
                    <div class="pricing-price">{price_display}</div>
                    <div class="pricing-period">{"/month" if plan.price_monthly > 0 else "Forever"}</div>
                    <ul class="pricing-features">
                        {features_html}
                    </ul>
                    <button class="pricing-cta" data-tier="{tier.value}" data-period="monthly">
                        {button_text}
                    </button>
                </div>"""

        cards.append(card)

    return "\n".join(cards)


def generate_documentation_site() -> str:
    """Generate documentation landing page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ShadowTag-v2 Intelligence - Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        h1 { color: #667eea; }
        h2 { margin-top: 40px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #1f2937;
            color: #f3f4f6;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }
        .endpoint {
            background: #f9fafb;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>ShadowTag-v2 Intelligence API Documentation</h1>

    <h2>Getting Started</h2>
    <p>Welcome to ShadowTag-v2 Intelligence! This guide will help you integrate our intelligence collection platform into your workflow.</p>

    <h3>Authentication</h3>
    <p>All API requests require an API key passed in the <code>X-API-Key</code> header:</p>
    <pre>curl -H "X-API-Key: your_api_key_here" https://api.shadowtag_v4-intelligence.com/v1/ingestion/summary</pre>

    <h2>Core Endpoints</h2>

    <div class="endpoint">
        <h3>GET /v1/ingestion/summary</h3>
        <p>Get quick overview of ingestion pipeline status.</p>
        <p><strong>Response:</strong></p>
        <pre>{
  "total_items": 1250,
  "tier_1_percentage": 22.5,
  "compliance_score": 96.8,
  "sources_active": 6
}</pre>
    </div>

    <div class="endpoint">
        <h3>POST /v1/ingestion/trigger</h3>
        <p>Manually trigger an ingestion run.</p>
        <p><strong>Request Body:</strong></p>
        <pre>{
  "max_items_per_source": 100,
  "priority_sources_only": false
}</pre>
    </div>

    <div class="endpoint">
        <h3>GET /v1/briefing/latest</h3>
        <p>Retrieve the most recent daily briefing.</p>
        <p><strong>Query Parameters:</strong></p>
        <ul>
            <li><code>format</code> - markdown, json, html (default: markdown)</li>
            <li><code>include_visualizations</code> - true/false (default: true)</li>
        </ul>
    </div>

    <h2>Rate Limits</h2>
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="background: #f3f4f6;">
            <th style="padding: 10px; text-align: left;">Tier</th>
            <th style="padding: 10px; text-align: left;">Rate Limit</th>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Free</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">10 requests/hour</td>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Starter</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">100 requests/hour</td>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">Professional</td>
            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">1000 requests/hour</td>
        </tr>
        <tr>
            <td style="padding: 10px;">Enterprise</td>
            <td style="padding: 10px;">Unlimited</td>
        </tr>
    </table>

    <h2>Webhooks</h2>
    <p>Configure webhooks to receive real-time notifications:</p>
    <ul>
        <li><code>ingestion.completed</code> - Nightly ingestion finished</li>
        <li><code>tier1.item.detected</code> - High-value item found</li>
        <li><code>compliance.violation</code> - Ethical compliance issue</li>
        <li><code>cost.threshold.exceeded</code> - Budget warning</li>
    </ul>

    <h2>Support</h2>
    <p>Need help? Contact us at <a href="mailto:support@shadowtag_v4-intelligence.com">support@shadowtag_v4-intelligence.com</a></p>
</body>
</html>"""


if __name__ == "__main__":
    # Generate landing page
    html = generate_landing_page()

    # Save to file
    with open("/tmp/ShadowTag-v2_landing_page.html", "w") as f:
        f.write(html)

    print("✓ Landing page generated: /tmp/ShadowTag-v2_landing_page.html")
    print("✓ Open in browser to preview")

    # Generate docs
    docs_html = generate_documentation_site()
    with open("/tmp/ShadowTag-v2_docs.html", "w") as f:
        f.write(docs_html)

    print("✓ Documentation page generated: /tmp/ShadowTag-v2_docs.html")
