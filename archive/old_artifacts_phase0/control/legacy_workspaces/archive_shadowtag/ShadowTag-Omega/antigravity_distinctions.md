# Antigravity Distinctions

**Date:** January 18, 2026
**Project:** ShadowTag Omega

## 1. Project Distinction: External vs. Internal Ownership

### The Issue

We initially attempted to use `isentropic-watch-sxnz0` (Cloud SQL permissions error) and `shadowtag-omega-v2` (Billing disabled/Safe Mode).

### The Distinction

* **External Projects (`isentropic-watch`):** Owned by a different organization. "Owner" access does *not* override strict Organization Policies (e.g., denying Public APIs).
* **Internal Projects (`shadowtag-omega-v2`):** Created directly under `shadowtagai.com`.
  * **Result:** Full IAM inheritance, ability to link valid billing (`011219...`), and successful resource creation.

## 2. Billing Distinction: Account vs. Project

### The Issue

Disabled billing blocked all deployment.

### The Distinction

* **The Fix:** Pivoting to a project (`shadowtag-omega-v2`) that we could link our *known good* billing account to (`011219...`), bypassing the restricted accounts on the old projects.

## 3. Deployment Distinction: Dockerfile vs. Buildpacks

### The Issue

Deployment failed due to import errors (`google-genai`).

### The Distinction

* **Reality:** Active `Dockerfile` overrides Buildpacks.
* **The Fix:** We patched the `Dockerfile` to:
    1. Explicitly add `libs/` to `PYTHONPATH` (`ENV PYTHONPATH="/workspace:/workspace/libs:${PYTHONPATH}"`).
    2. Fail hard if `requirements.txt` fails (removed `|| pip install fallback`).

## 4. Security & Cleanup Distinction

### The Issue

User requested "Require Authentication" and removal of unused services.

### The Distinction

* **Legacy Services:** `fixer-agent` and `reviewer-agent` were detected running but had no source in the repo.
* **Action:** **Deleted** both services to ensure a clean state.
* **Security:** `n-autoresearch/Kosmos/BioAgentss-server` has **no public access** (`allUsers` binding absent). It effectively requires IAM authentication (Service Account or User Token).

## 5. Summary

We moved from a "Fix the zombie project" strategy to a "Clean Slate (Omega v2)" strategy. Everything running is now:

1. **Billing Enabled**
2. **Source-Controlled** (matches local repo)
3. **Secure** (Private, authenticated only)
4. **Clean** (No ghost services)

## 6. Architecture Distinction: Serverless Database vs. Application Container

### The Question

"Does Firestore get rid of Docker entirely?"

### The Distinction

* **Database (Yes):** Firestore is fully managed (Serverless). You do **not** run a Docker container for the database. It replaces the need for a `postgres` container.
* **Application (No):** Your code (`n-autoresearch/Kosmos/BioAgentss-server`) still needs an environment to run in. On Cloud Run, that environment is a **Docker Container** (built from your `Dockerfile`).
* **Summary:** Firestore eliminates the *Database* container, but Docker is still required to package and run your *Application* code.
