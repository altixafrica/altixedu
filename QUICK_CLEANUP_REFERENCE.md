# Quick Cleanup Reference - Files to Delete

## CRITICAL - Delete Immediately (Break build/configuration)
```
frontend/next.config.ts
frontend/next-env.d.ts
frontend/tailwind.config.ts
frontend/.next/
frontend/tsconfig.tsbuildinfo
.encryption_key (and remove from git history)
```

## HIGH PRIORITY - Code/Components
```
frontend/app/  (entire directory - old Next.js structure)
altixedu/comprehensive_check.py (old version, replaced by _v2)
altixedu/test_endpoints.py (old test file)
```

## MEDIUM PRIORITY - Cleanup & Security
```
altixedu/accounts/  (duplicate of apps/accounts/)
altixedu/migration_output.txt (temporary file)
server.log (log file - add to .gitignore)
altixedu/setup_government_features.py (one-time setup script)
altixedu/setup_ministry_admins.py (one-time setup script)
```

## LOW PRIORITY - Optional Archival
```
CHANGES_APPLIED_COMPLETE_LIST.md → Move to docs/archive/
PRODUCTION_READINESS_100_PERCENT.md → Move to docs/archive/
PRODUCTION_READINESS_STATUS.md → Move to docs/archive/
PRODUCTION_CHECKLIST.md → Move to docs/archive/
PRODUCTION_99_PERCENT_READY.md → Move to docs/archive/
SESSION_COMPLETION_SUMMARY.md → Move to docs/archive/
PHASE_4_IMPLEMENTATION.md → Move to docs/archive/
IMAGE_REQUIREMENTS.md → Move to docs/archive/
FRONTEND_EXPECTATIONS.txt → Move to docs/archive/
check_production_readiness.sh → Delete or archive
comprehensive_readiness_check.sh → Delete or archive
```

## CONDITIONAL - Verify Before Deleting
```
altixedu/apps/bursars/  (if not used anywhere)
tests_all_features.py (decide if test-related files should be consolidated)
validate_code.py (check if still needed)
quick_validation.py (check if still needed)
test_ministry_admin.sh → Move to tests/ or delete
test_phase4_endpoints.sh → Move to tests/ or delete
```

## Configuration Fixes (Not Deletions)
```
frontend/tsconfig.json - REMOVE Next.js plugin reference (lines 14-16):
  "plugins": [
    {
      "name": "next"
    }
  ],

.gitignore - ADD these entries:
  .encryption_key
  *.sqlite3
  server.log
  .env
  *.db
  *.sqlite
```

## Total Impact
- **~47 files/directories to remove**
- **~500MB+ storage reclaimed** (mostly from .next/ and node_modules cleanup)
- **Estimated cleanup time: 2-3 hours** including testing

## Order of Execution (Safest)
1. Add entries to .gitignore first
2. Delete frontend Next.js files (next.config.ts, next-env.d.ts, tailwind.config.ts, .next/)
3. Fix tsconfig.json (remove Next.js plugin)
4. Run `npm run build` in frontend to verify no breaks
5. Delete Django backend test/temp files
6. Delete duplicate apps
7. Move documentation files to archive
8. Run `python manage.py check` to verify

---

For detailed analysis, see: CLEANUP_ANALYSIS.md
