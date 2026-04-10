# Musk First Principles Filter

**Pre-JR Engine Triage** - Run this BEFORE Purpose/Reasons/Brakes

## The Algorithm

> "The most common mistake of smart engineers is to optimize a thing that should not exist."
> — Elon Musk

---

## Step 1: Question Requirements (Make Less Dumb)

| Question                                     | Answer | Score (1-5) |
| -------------------------------------------- | ------ | ----------- |
| Who gave this requirement?                   |        |             |
| What's their bias/incentive?                 |        |             |
| What problem does this ACTUALLY solve?       |        |             |
| Is this inherited assumption or validated?   |        |             |
| Can we find first-hand evidence it's needed? |        |             |

**Pass threshold:** Average ≥ 3.0

---

## Step 2: Delete the Thing (10% Restore Rule)

| Component/Feature/Step | Proposed for Deletion | Deleted? | Restored? | Reason |
| ---------------------- | --------------------- | -------- | --------- | ------ |
|                        | Yes/No                | Y/N      | Y/N       |        |
|                        | Yes/No                | Y/N      | Y/N       |        |
|                        | Yes/No                | Y/N      | Y/N       |        |
|                        | Yes/No                | Y/N      | Y/N       |        |
|                        | Yes/No                | Y/N      | Y/N       |        |

**Restore Rate:** **\_\_** %

**Pass criteria:**

- Must attempt deletion on ≥3 items
- If restore rate < 10%, too timid → delete more
- If restore rate > 50%, too aggressive → keep more

---

## Step 3: Optimize Only After 1+2

| Item to Optimize | Passed Step 1? | Passed Step 2? | Optimization Action |
| ---------------- | -------------- | -------------- | ------------------- |
|                  | Y/N            | Y/N            |                     |

**Rule:** No optimization without passing both prior steps.

---

## Filter Result

- [ ] **PASS** - Proceed to JR Engine (Purpose/Reasons/Brakes)
- [ ] **FAIL** - Requirements too dumb / not deleted enough

**Signed:** ********\_\_******** **Date:** ****\_\_****

---

## Audit Trail

### What We Deleted

-

### What We Were Forced to Restore

-

### What We Stopped Ourselves from Optimizing

- ***

## Common Traps

1. **Optimization shame** - Engineers afraid to optimize even post-deletion
2. **Requirements worship** - Treating customer requests as sacred
3. **Invisible infrastructure** - Deleting reliability layers that prevent failure
4. **Analysis paralysis** - Filter becomes bureaucratic vs liberating

## Bootstrap Tension

Remember: Deletion discipline can conflict with "ship fast" pressure.

**Resolution:** Delete ruthlessly in design phase, ship aggressively in execution phase.
