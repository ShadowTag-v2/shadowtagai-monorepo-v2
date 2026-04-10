# Stripe Integration - Quick Start

## ✅ Files Created

```
scripts/setup_stripe_products.py  # Creates Stripe products
api/routes/subscription.py        # Checkout API endpoints
public/pricing.html               # Pricing page
```

## 🚀 Setup (5 minutes)

### Step 1: Get Stripe Keys

1. Go to https://dashboard.stripe.com/register
2. Create account (or login)
3. Navigate to: Developers → API keys
4. Copy **Secret key** (starts with `sk_test_`)

### Step 2: Add to .env

```bash
echo 'STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE' >> .env
echo 'STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE' >> .env
```

### Step 3: Create Products

```bash
python3 scripts/setup_stripe_products.py
```

**Expected output:**

```
✅ Created: Cor2.0 Pro - Price ID: price_1ABC123
✅ Created: Cor2.0 Math Auditor - Price ID: price_1DEF456

Add to .env:
PRO_PRICE_ID=price_1ABC123
MATH_AUDITOR_PRICE_ID=price_1DEF456
```

### Step 4: Add Price IDs to .env

Copy the output and add to `.env`:

```bash
echo 'PRO_PRICE_ID=price_YOUR_PRO_ID' >> .env
echo 'MATH_AUDITOR_PRICE_ID=price_YOUR_MATH_ID' >> .env
```

### Step 5: Update main.py

Add this to your FastAPI app:

```python
from api.routes.subscription import router as subscription_router

app.include_router(subscription_router)
```

### Step 6: Test Locally

```bash
# Start server
uvicorn main:app --reload

# Open pricing page
open http://localhost:8000/public/pricing.html
```

## 🧪 Testing

### Test Checkout Flow

1. Click **Start Pro** button
2. Enter test email
3. Redirected to Stripe checkout
4. Use test card: `4242 4242 4242 4242`
5. Any future date, any CVC

### Test Webhook (Local)

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/api/subscription/webhook

# In another terminal, trigger test event
stripe trigger checkout.session.completed
```

## 📊 Expected Results (Week 1)

| Day | Action        | Result            |
| --- | ------------- | ----------------- |
| Mon | Deploy Stripe | Pricing page live |
| Tue | ProductHunt   | 50 signups        |
| Wed | Email drip    | 5 trials          |
| Thu | Follow-ups    | 2 paid ($40 MRR)  |
| Fri | Optimize      | 8% conversion     |

## 🐛 Troubleshooting

**Error: No module named 'stripe'**

```bash
pip3 install stripe
```

**Error: STRIPE_SECRET_KEY not found**

```bash
# Check .env exists
cat .env | grep STRIPE

# Load .env in Python
from dotenv import load_dotenv
load_dotenv()
```

**Error: Invalid price_id**

```bash
# Verify products created
stripe products list
stripe prices list
```

## 📈 Next Steps

1. ✅ Stripe integration complete
2. ⏭️ Email capture for free tier
3. ⏭️ ProductHunt launch
4. ⏭️ Analytics (Mixpanel/Amplitude)
5. ⏭️ Math Auditor outreach

---

**Status**: Ready to accept payments
**Revenue Target**: $200 MRR by Week 2
**Break-Even**: Month 4 (150 Pro users)
