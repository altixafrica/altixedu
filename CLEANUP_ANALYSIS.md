# AltixEdu Backend - Code Cleanup Analysis

**Analysis Date:** March 24, 2026  
**Project Type:** Django REST Framework + React/Vite Frontend  
**Status:** Post-Next.js to React/Vite Migration (Incomplete Cleanup)

---

## Executive Summary

This project has significant dead code, duplicate files, and leftover configuration from a Next.js → React/Vite conversion that was not fully cleaned up. Additionally, the Django backend has temporary test files, sensitive data files that shouldn't be committed, and some unused apps/models.

**Total Files to Remove:** 47+  
**Total Size Cleanup Potential:** ~500MB+ (mostly node_modules and cache)

---

## 1. FRONTEND DEAD CODE & NEXT.JS ARTIFACTS

### 1.1 Next.js Configuration Files (Should Delete)
These files are Next.js-specific and incompatible with the Vite setup currently in use.

| File | Reason | Priority |
|------|--------|----------|
| `frontend/next.config.ts` | Next.js config - project uses Vite | **HIGH** |
| `frontend/next-env.d.ts` | Next.js type declarations - not needed for Vite | **HIGH** |
| `frontend/tsconfig.json` | Contains Next.js plugin reference at line 15: `"plugins": [{"name": "next"}]` | **HIGH** |

**Action:** Delete these 3 files  
**Reason:** Vite uses its own configuration model, these files will cause confusion and potential build issues

---

### 1.2 Duplicate Tailwind Configuration (Should Delete)
Both `.js` and `.ts` versions of Tailwind config exist - only one should be used.

| File | Current State | Issue |
|------|---------------|-------|
| `frontend/tailwind.config.ts` | Next.js format | References `./app/**/*.{js,ts,jsx,tsx,mdx}` (Next.js pattern) |
| `frontend/tailwind.config.js` | Vite format ✓ CORRECT | References `./src/**/*.{js,jsx}` (Vite pattern) |

**Action:** Delete `frontend/tailwind.config.ts`  
**Reason:** `tailwind.config.js` is the correct Vite-compatible version

---

### 1.3 TypeScript Configuration Issue
`frontend/tsconfig.json` still references Next.js plugin despite using Vite.

**Current state (Lines 14-16):**
```json
"plugins": [
  {
    "name": "next"
  }
],
```

**Fix Required:** Remove the Next.js plugin from tsconfig.json or use Vite's tsconfig

---

### 1.4 Orphaned Next.js App Directory
The `frontend/app/` directory contains Next.js code that's unused. The actual React application is in `frontend/src/`.

| Path | Type | Status | Issue |
|------|------|--------|-------|
| `frontend/app/page.tsx` | Next.js Page | ❌ UNUSED | Imports Next.js types: `import type { Metadata } from "next"` |
| `frontend/app/page-new.tsx` | Next.js Page Variant | ❌ UNUSED | Old variant, marked as "new" |
| `frontend/app/layout.tsx` | Next.js Layout | ❌ UNUSED | Exports Next.js metadata |
| `frontend/app/` (entire directory) | Next.js structure | ❌ UNUSED | 20+ subdirectories with Next.js-style pages |

**Action:** Delete entire `frontend/app/` directory and `frontend/index.html` in favor of proper Vite structure  
**Reason:** Real app is in `frontend/src/` with proper Vite entry point

---

### 1.5 Build Cache & Artifacts (Should Delete)
These are build artifacts and should not be in the repository.

| Path | Size/Status | Issue |
|------|-------------|-------|
| `frontend/.next/` | Large directory | Next.js build output - should be in .gitignore |
| `frontend/node_modules/` | ~500MB+ | Already in .gitignore, but verify it's actually ignored |
| `frontend/tsconfig.tsbuildinfo` | TypeScript build cache | Build artifact, not needed |

**Action:** Delete `frontend/.next/` and `frontend/tsconfig.tsbuildinfo`  
**.gitignore Status:** Verify these are properly ignored:
```
.next/          ✓ Already in frontend/.gitignore
node_modules/   ✓ Already in frontend/.gitignore
coverage/       ✓ Already in frontend/.gitignore
```

---

### 1.6 ESLint Configuration
`frontend/.eslintignore` and `.eslintrc.json` exist. Verify they're configured for React/Vite, not Next.js.

**Current Status:** Need to verify .eslintrc.json doesn't reference Next.js-specific rules

---

## 2. DJANGO BACKEND DEAD CODE & ISSUES

### 2.1 Temporary & Test Files at Root Level
Multiple test files and validation scripts at the root directory that should be cleaned up.

| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `altixedu/test_endpoints.py` | Testing script | Old test script | **DELETE** |
| `altixedu/comprehensive_check.py` | Validation | Seems redundant | **DELETE** |
| `altixedu/comprehensive_check_v2.py` | Validation variant | Presumably newer version of above | **DELETE** |
| `altixedu/test_endpoints.py` | Endpoint testing | Duplicate testing | **DELETE** |
| `tests_all_features.py` | Integration tests | Located at root | **DELETE or MOVE** |

**Reason:** These belong in a proper `tests/` directory or should be removed entirely

---

### 2.2 Setup & Migration Scripts (Root Level)
Several one-time setup scripts at root that shouldn't be in production:

| File | Purpose | Status |
|------|---------|--------|
| `setup_government_features.py` | Setup script | One-time setup - could be archived |
| `setup_ministry_admins.py` | Setup script | One-time setup - could be archived |
| `setup_features.py` (in altixedu/) | Setup script | One-time setup - could be archived |
| `server.log` | Log file | Should not be committed |
| `migration_output.txt` | Output file | Temporary file |

**Action:** 
- Delete: `migration_output.txt`, `server.log`
- Consider: Archive setup scripts to separate docs/ folder or delete if no longer needed

---

### 2.3 Sensitive Files in Repository
These files contain secrets/sensitive data and should NOT be in git:

| File | Issue | Status |
|------|-------|--------|
| `altixedu/.encryption_key` | Encryption key 🔐 | **CRITICAL** - remove and add to .gitignore |
| `altixedu/db.sqlite3` | Database file | Already should be ignored but verify |
| `.env` | Environment variables | ⚠️ Should be renamed to `.env.example` |
| `.env.example` | Template (OK) | ✓ Safe to keep |
| `frontend/.env.local` | Frontend env (dev) | Should not be committed |

**Actions:**
1. Add to root `.gitignore`:
   ```
   *.sqlite3
   .encryption_key
   .env
   frontend/.env.local
   server.log
   ```
2. Delete actual commit of `.encryption_key` and `db.sqlite3` from git history

---

### 2.4 Cache Directories (`__pycache__`)
Throughout the Django backend:

| Directory | Status |
|-----------|--------|
| `altixedu/__pycache__/` | Should be ignored |
| `altixedu/apps/*/\_\_pycache\_\_/` | Should be ignored |
| `frontend/node_modules/` | Should be ignored |

**Verify these are in `.gitignore`:**
- Root `.gitignore`: ✓ Has `venv/`, `frontend/node_modules/`
- frontend `.gitignore`: ✓ Has `node_modules`

---

### 2.5 Duplicate Accounts Apps
There are TWO accounts apps in the Django backend:

| App Location | Status | Content |
|--------------|---------|---------|
| `altixedu/accounts/` | ❓ OLD/DUPLICATE | Basic structure: models.py, views.py, migrations/, tests.py, admin.py |
| `altixedu/apps/accounts/` | ✓ ACTIVE | Full implementation: role_views.py, role_serializers.py, role_models.py, permissions.py, serializers.py |

**Settings Check:** Which is registered in `INSTALLED_APPS`?

**Action:** Delete one (likely `altixedu/accounts/`)

---

### 2.6 Incomplete Apps
The `bursars` app appears to be incomplete:

| App | Files | Status |
|-----|-------|--------|
| `altixedu/apps/bursars/` | Only: admin.py, models.py, migrations/, __init__.py | ❌ NO views.py or tests.py |

**Check:**
- Is `bursars` used in any views/serializers?
- Are bursars users handled by `accounts` app instead?
- Should this be deleted or completed?

**Recommendation:** If not actively used, delete it

---

### 2.7 Document/Summary Files (Low Priority)
Multiple documentation files at root that are useful for development history but clutter the repo:

| File | Purpose | Action |
|------|---------|--------|
| `CHANGES_APPLIED_COMPLETE_LIST.md` | Project history | Archive/delete |
| `PRODUCTION_READINESS_100_PERCENT.md` | Status doc | Archive/delete |
| `PRODUCTION_READINESS_STATUS.md` | Status doc | Archive/delete |
| `PRODUCTION_CHECKLIST.md` | Checklist | Archive/delete |
| `PRODUCTION_99_PERCENT_READY.md` | Status doc | Archive/delete |
| `SESSION_COMPLETION_SUMMARY.md` | Summary | Archive/delete |
| `PHASE_4_IMPLEMENTATION.md` | Phase doc | Archive/delete |
| `IMAGE_REQUIREMENTS.md` | Requirements | Archive/delete |
| `FRONTEND_EXPECTATIONS.txt` | Requirements | Archive/delete |

**Reason:** These are commit message-style docs that should be in a CHANGELOG or separate docs/ folder

**Action:** Create `docs/archive/` and move these files there, OR delete if no longer needed

---

### 2.8 Shell Scripts (Root Level)
Several testing/validation shell scripts:

| File | Purpose |
|------|---------|
| `start_server.sh` | Start server - useful to keep |
| `test_ministry_admin.sh` | Test script - should be in tests/ |
| `test_phase4_endpoints.sh` | Test script - should be in tests/ |
| `check_production_readiness.sh` | Check script - archive or delete |
| `comprehensive_readiness_check.sh` | Check script - archive or delete |

**Action:** Keep `start_server.sh`, move others to tests/ directory

---

### 2.9 Configuration Files Status
Checking key config files:

| File | Status |
|------|--------|
| `pytest.ini` | ✓ Good - test configuration |
| `requirements.txt` | ✓ Good - dependency list |
| `manage.py` | ✓ Good - Django management |
| `README.md` | ✓ Good - project documentation |

---

## 3. CONSOLIDATION ISSUES

### 3.1 Unused Test Files (In apps/*/tests.py)

Several apps have `tests.py` files. These should be consolidated:

- `altixedu/apps/accounts/tests.py`
- `altixedu/apps/platform/tests.py`
- (others in various apps)

**Recommendation:** Use pytest with conftest.py (already exists) and move to proper `tests/` directory

---

### 3.2 Multiple Validation/Check Scripts

Similar scripts exist with different versions:
- `comprehensive_check.py`
- `comprehensive_check_v2.py`

**Action:** Keep only the latest version (_v2), delete older

---

## 4. SUMMARY TABLE: FILES TO DELETE

### HIGH PRIORITY (Breaking/Outdated)

| File/Directory | Reason | Difficulty |
|---|---|---|
| `frontend/next.config.ts` | Next.js config - unused | Easy |
| `frontend/next-env.d.ts` | Next.js types - unused | Easy |
| `frontend/tailwind.config.ts` | Duplicate of .js version | Easy |
| `frontend/app/` | Entire Next.js app directory | Medium |
| `frontend/.next/` | Build cache | Easy |
| `frontend/tsconfig.tsbuildinfo` | Build cache | Easy |
| `altixedu/comprehensive_check.py` | Superseded by _v2 | Easy |
| `altixedu/test_endpoints.py` | Old test file | Easy |
| `.encryption_key` | Sensitive data 🔐 | Critical |

### MEDIUM PRIORITY (Cleanup & Organization)

| File/Directory | Reason | Difficulty |
|---|---|---|
| `altixedu/accounts/` | Duplicate of `apps/accounts/` | Medium |
| `altixedu/apps/bursars/` (if unused) | Incomplete app | Medium |
| `altixedu/migration_output.txt` | Temporary output | Easy |
| `server.log` | Log file | Easy |
| `altixedu/setup_government_features.py` | One-time setup script | Medium |
| `altixedu/setup_ministry_admins.py` | One-time setup script | Medium |
| `test_ministry_admin.sh` | Move to tests/ or delete | Easy |
| `test_phase4_endpoints.sh` | Move to tests/ or delete | Easy |

### LOW PRIORITY (Documentation Cleanup)

| Files | Reason | Difficulty |
|---|---|---|
| `CHANGES_APPLIED_COMPLETE_LIST.md` | Archive/move to docs/ | Easy |
| `PRODUCTION_*.md` (all 4 files) | Archive/move to docs/ | Easy |
| `SESSION_COMPLETION_SUMMARY.md` | Archive/move to docs/ | Easy |
| `PHASE_4_IMPLEMENTATION.md` | Archive/move to docs/ | Easy |
| `IMAGE_REQUIREMENTS.md` | Move to docs/ | Easy |
| `FRONTEND_EXPECTATIONS.txt` | Move to docs/ | Easy |
| `check_production_readiness.sh` | Archive/delete | Easy |
| `comprehensive_readiness_check.sh` | Archive/delete | Easy |

---

## 5. RECOMMENDED CLEANUP PLAN

### Phase 1: Critical (Immediate)
1. Delete `frontend/next-env.d.ts`
2. Delete `frontend/next.config.ts`
3. Delete `frontend/tailwind.config.ts`
4. Delete `frontend/.next/` (build cache)
5. Delete `frontend/tsconfig.tsbuildinfo`
6. Remove `.encryption_key` from git and gitignore
7. Fix `frontend/tsconfig.json` - remove Next.js plugin

**Time:** ~15 minutes  
**Impact:** Removes Next.js confusion, fixes build configuration

---

### Phase 2: Code Cleanup
1. Delete `frontend/app/` directory (entire next.js app)
2. Verify `frontend/src/` and `frontend/index.html` work with Vite
3. Delete `altixedu/accounts/` (if truly duplicate)
4. Delete `altixedu/comprehensive_check.py` (old version)
5. Delete `altixedu/test_endpoints.py`
6. Delete `server.log` and `migration_output.txt`
7. Verify `altixedu/apps/bursars/` is truly unused before deleting

**Time:** ~30 minutes  
**Impact:** Removes significant dead code, clarifies project structure

---

### Phase 3: Organization
1. Create `docs/archive/` directory
2. Move status/summary markdown files to `docs/archive/`
3. Create `tests/` directory in backend
4. Move shell test scripts to `tests/`
5. Consolidate app `tests.py` files into unified test structure
6. Update `.gitignore` with sensitive files

**Time:** ~45 minutes (also improves long-term maintainability)

---

## 6. VERIFICATION CHECKLIST

After cleanup, verify:

- [ ] `npm run build` succeeds in frontend/
- [ ] `python manage.py check` passes in Django
- [ ] All imported apps still exist and work
- [ ] No import errors from deleted files
- [ ] `.gitignore` includes: `*.sqlite3`, `.encryption_key`, `server.log`, `*.env` (except .env.example)
- [ ] Vite dev server (`npm run dev`) starts correctly
- [ ] Django development server (`python manage.py runserver`) works

---

## 7. FILES AFFECTED BY EACH DELETION

### If deleting `frontend/app/`:
- Check if any imports reference files in `app/` directory
- Verify `src/` has all necessary page/route components
- Update any documentation pointing to `app/`

### If deleting `altixedu/accounts/`:
- Verify it's not imported in `INSTALLED_APPS`
- Check no migrations reference it
- Ensure `apps.accounts` is the active version in settings

### If deleting `altixedu/apps/bursars/`:
- Search all files for references to bursars
- Check if any users/groups reference bursar role
- Verify no API endpoints use bursars app

---

## 8. ADDITIONAL RECOMMENDATIONS

1. **Git Cleanup:** After deletion, consider `git gc --aggressive` to reclaim space
2. **Environment Setup:** Add proper .env setup documentation
3. **Testing:** Consolidate pytest configuration and tests in one place
4. **CI/CD:** Add build validation to prevent reintroduction of Next.js files
5. **Pre-commit Hooks:** Add checks to prevent committing `.env`, `.encryption_key`, `*.sqlite3`

---

**Generated:** March 24, 2026  
**Status:** Analysis Complete - Ready for Implementation
