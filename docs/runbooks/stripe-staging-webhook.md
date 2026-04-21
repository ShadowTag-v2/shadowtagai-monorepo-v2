# Stripe Staging Webhook Configuration

## Current Production Webhook
- ID: `we_1TNKSjEHnWpykeMiQZqmpy3X`
- URL: `https://counselconduit-api.run.app/webhooks/stripe`
- Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`

## Setting Up Staging Webhook

### Step 1: Create Test Mode Webhook in Stripe Dashboard
1. Go to [Stripe Webhooks](https://dashboard.stripe.com/test/webhooks)
2. Toggle to **Test mode** (top-right)
3. Add endpoint:
   - URL: `https://counselconduit-staging-767252945109.us-central1.run.app/webhooks/stripe`
   - Events: Same as production
4. Copy the signing secret → add to Secret Manager:
```bash
echo -n "whsec_test_..." | gcloud secrets create STRIPE_WEBHOOK_SECRET_STAGING \
  --data-file=- --project=shadowtag-omega-v4
```

### Step 2: Configure Staging Service
```bash
gcloud run services update counselconduit-staging \
  --project=shadowtag-omega-v4 --region=us-central1 \
  --update-secrets="STRIPE_WEBHOOK_SECRET=STRIPE_WEBHOOK_SECRET_STAGING:latest"
```

### Step 3: Test with Stripe CLI
```bash
stripe listen --forward-to https://counselconduit-staging-767252945109.us-central1.run.app/webhooks/stripe
stripe trigger checkout.session.completed
```

## Key Separation Rules
- **NEVER** use production Stripe keys in staging
- Staging uses `sk_test_*` keys ONLY
- Webhook signing secrets are DIFFERENT per environment
- Test clock objects exist only in test mode
