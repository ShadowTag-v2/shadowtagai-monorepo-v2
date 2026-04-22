# CounselConduit Pricing — v2.0 (Hard Redesign)

## Position
Premium SaaS pricing leveraging emotional arbitrage — the gap between AI cost ($0.02/query) and perceived value ($149-$999/mo).

## Tier Structure

### Attorney Tiers (Lawyer → Us)
| Tier | Price | Target |
|------|-------|--------|
| Solo | $299/mo | Solo practitioners, 1 attorney |
| Practice | $599/mo | Small firms, 2-10 attorneys |
| Enterprise | $999/mo | Mid-size firms, 10+ attorneys |

### Client Pass-Through (Client → Lawyer)
- Lawyer sets their own pricing on the client portal
- Stripe Connect handles the split
- We never touch client-lawyer fee arrangement

### Consumer (Direct B2C)
| Tier | Price | Margin |
|------|-------|--------|
| Pro Monthly | $149/mo | 95% |
| Pro Annual | $1,428/yr ($119/mo) | 95% |
| Enterprise | $20,000/mo | 69-71% |

### Beta
- Coupon: `3wseBY7Z` (50% off, 3 months, max 100 redemptions)

## Commercial Logic
- Emotional arbitrage: charge for safety, not compute
- Auto-bump on usage (Claude Code billing model)
- BYOK lowers buyer friction
- Clean upgrade path: Solo → Practice → Enterprise
- All LLM API costs absorbed in subscription margin

## Revenue Projections
| Year | Firms | ARPU/mo | ARR |
|------|-------|---------|-----|
| Y1 | 200 | $999 | $2.4M |
| Y2 | 800 | $1,100 | $10.6M |
| Y3 | 1,500 | $1,200 | $21.6M |

## Next Steps
1. Wire pricing assumptions into live calculator
2. Back with retriever-eval and usage telemetry
3. Implement auto-bump tier detection in `stripe_handler.py`
