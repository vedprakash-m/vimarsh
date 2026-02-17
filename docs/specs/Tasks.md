# Vimarsh Production Hardening — Implementation Plan

> **Purpose:** Systematic execution plan to transform Vimarsh from feature-complete prototype to production-hardened platform.  
> **Approach:** Fix in dependency order — security/correctness first, then structure, then quality.  
> **Legend:** ✅ Done | 🔄 In Progress | ⬜ Not Started | ⏭️ Deferred (requires infra access)

---

## Phase 0: Spec Corrections (Pre-requisite)

| # | Task | Status | Files |
|---|------|--------|-------|
| 0.1 | Fix Tech Spec: Gemini→Azure OpenAI as current AI stack | ✅ | `docs/specs/Tech_Spec_Vimarsh.md` |
| 0.2 | Fix Tech Spec: Region East US→West US 2 | ✅ | `docs/specs/Tech_Spec_Vimarsh.md` |
| 0.3 | Fix Tech Spec: 7 domains→6 domains throughout | ✅ | `docs/specs/Tech_Spec_Vimarsh.md` |
| 0.4 | Fix Tech Spec: Add CORS policy documentation | ✅ | `docs/specs/Tech_Spec_Vimarsh.md` |
| 0.5 | Fix Tech Spec: Add auth fail-closed requirement | ✅ | `docs/specs/Tech_Spec_Vimarsh.md` |
| 0.6 | Fix Tech Spec: Standardize DB name to `vimarsh-multi-personality` | ✅ | `docs/specs/Tech_Spec_Vimarsh.md` |
| 0.7 | Fix UX Spec: 7 domains→6 domains | ✅ | `docs/specs/User_Experience.md` |
| 0.8 | Fix UX Spec: Region→West US 2 | ✅ | `docs/specs/User_Experience.md` |

---

## Phase 1: P0 — Security & Correctness (Ship-Blocking)

### 1.1 Auth Fail-Closed Pattern
**Priority:** P0 | **Risk:** Critical — silent security bypass  
**Problem:** `backend/auth/__init__.py` makes all auth decorators identity functions (no-ops) on ImportError. One missing dependency silently exposes all 47 routes including 20+ admin endpoints.  
**Solution:** Replace no-op fallbacks with decorators that return HTTP 503.

| # | Task | Status | Files |
|---|------|--------|-------|
| 1.1.1 | Replace identity-function fallbacks with 503-returning decorators | ✅ | `backend/auth/__init__.py` |
| 1.1.2 | Add startup log CRITICAL when auth fails to load | ✅ | `backend/auth/__init__.py` |
| 1.1.3 | Write test: verify auth decorators reject when module unavailable | ✅ | `backend/tests/test_auth_failclosed.py` |

### 1.2 Fix Settings API Contract (Two Bugs)
**Priority:** P0 | **Risk:** High — user preferences silently fail to persist  
**Problem A:** `SettingsContext.tsx` line 149 builds URL `${getApiBaseUrl()}/api/user/preferences` but `getApiBaseUrl()` already returns `…/api`, producing `…/api/api/user/preferences` (404).  
**Problem B:** Frontend reads `data.updated_preferences` from PATCH response, but backend returns `data.preferences`.  
**Solution:** Fix URL and response key in SettingsContext.tsx.

| # | Task | Status | Files |
|---|------|--------|-------|
| 1.2.1 | Remove extra `/api` prefix in PATCH URL | ✅ | `frontend/src/contexts/SettingsContext.tsx` |
| 1.2.2 | Fix response key: `updated_preferences` → `preferences` | ✅ | `frontend/src/contexts/SettingsContext.tsx` |
| 1.2.3 | Write test: verify settings save round-trips correctly | ⏭️ | `frontend/src/contexts/SettingsContext.test.tsx` |

### 1.3 Authenticate Engagement API
**Priority:** P0 | **Risk:** High — engagement data accessible without auth  
**Problem:** `engagementApi.ts` uses raw `axios` without Bearer token injection. All 7 endpoints are unauthenticated.  
**Solution:** Replace raw `axios` with the `SpiritualGuidanceAPI` singleton from `utils/api.ts`, or add auth interceptor.

| # | Task | Status | Files |
|---|------|--------|-------|
| 1.3.1 | Refactor engagementApi to use authenticated API client | ✅ | `frontend/src/components/engagement/engagementApi.ts` |
| 1.3.2 | Verify auth tokens are sent on engagement calls | ✅ | Manual test / integration test |

### 1.4 Fix CORS in Bicep IaC
**Priority:** P0 | **Risk:** Medium — wildcard CORS bypasses app-level restrictions  
**Problem:** `unified-resources.bicep` has `allowedOrigins: ['*']` with `supportCredentials: false`. App code restricts to `vimarsh.vedprakash.net`. Bicep wins at platform level.  
**Solution:** Set explicit allowed origins in Bicep matching production domains.

| # | Task | Status | Files |
|---|------|--------|-------|
| 1.4.1 | Replace wildcard CORS with explicit production domains | ✅ | `infrastructure/unified-resources.bicep` |
| 1.4.2 | Set `supportCredentials: true` for auth cookie flow | ✅ | `infrastructure/unified-resources.bicep` |

### 1.5 Cosmos DB Key to Key Vault
**Priority:** P0 | **Risk:** Medium — database credential in plaintext app settings  
**Problem:** `COSMOS_DB_KEY` is set as raw value in Bicep. Meanwhile the decommissioned `GEMINI_API_KEY` is in Key Vault.  
**Solution:** Store Cosmos key as Key Vault secret, reference via `@Microsoft.KeyVault(...)`.

| # | Task | Status | Files |
|---|------|--------|-------|
| 1.5.1 | Create Cosmos DB key secret in Key Vault resource | ✅ | `infrastructure/unified-resources.bicep` |
| 1.5.2 | Update COSMOS_DB_KEY app setting to Key Vault reference | ✅ | `infrastructure/unified-resources.bicep` |
| 1.5.3 | Remove GEMINI_API_KEY provisioning (no longer used) | ✅ | `infrastructure/unified-resources.bicep` |

---

## Phase 2: P1 — Architectural & Reliability

### 2.1 Split function_app.py into Blueprints
**Priority:** P1 | **Risk:** Medium — 4,105-line God file is unmaintainable  
**Problem:** All 47 routes, 150+ lines of try/except imports, and inline DB queries in one file.  
**Solution:** Use Azure Functions Blueprints to split by domain.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.1.1 | Create `backend/routes/` package with `__init__.py` | ✅ | `backend/routes/__init__.py` |
| 2.1.2 | Extract admin routes (20+) to `routes/admin_bp.py` | ✅ | `backend/routes/admin_bp.py` |
| 2.1.3 | Extract guidance/wisdom routes to `routes/guidance_bp.py` | ✅ | `backend/routes/guidance_bp.py` |
| 2.1.4 | Extract user profile routes to `routes/user_bp.py` | ✅ | `backend/routes/user_bp.py` |
| 2.1.5 | Extract diagnostic/health routes to `routes/diagnostics_bp.py` | ✅ | `backend/routes/diagnostics_bp.py` |
| 2.1.6 | Extract sharing/voice routes to `routes/sharing_bp.py` | ✅ | `backend/routes/voice_bp.py`, `backend/routes/wisdom_bp.py`, `backend/routes/personalities_bp.py` |
| 2.1.7 | Slim function_app.py to blueprint registration only (~100 lines) | ✅ | `backend/function_app.py` (86 lines) |
| 2.1.8 | Run all existing tests — verify no regressions | ✅ | `backend/tests/` (425 passed, 7 timeout-related skips) |

### 2.2 Complete Gemini → Azure OpenAI Migration
**Priority:** P1 | **Risk:** Medium — dual-provider dependency, stale Gemini API key  
**Problem:** 4 service files still directly import/use `google.generativeai`. 2 more have stale string references.  
**Solution:** Replace all Gemini SDK calls with Azure OpenAI equivalents using centralized config.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.2.1 | Migrate `topic_extraction_service.py` — 5 `generate_content_async` calls → Azure OpenAI Chat | ✅ | `backend/services/topic_extraction_service.py` |
| 2.2.2 | Migrate `embedding_generator.py` — wire `AzureOpenAIEmbeddingService` into `generate_batch_embeddings` | ✅ | `backend/services/embedding_generator.py` |
| 2.2.3 | Migrate `knowledge_base_manager.py` — replace `GeminiTransformer` with `AzureOpenAIEmbeddingService` | ✅ | `backend/services/knowledge_base_manager.py` |
| 2.2.4 | Migrate `hierarchical_memory_service.py` — replace both generation and embedding Gemini calls | ✅ | `backend/services/hierarchical_memory_service.py` |
| 2.2.5 | Fix `enhanced_llm_wrapper.py` — `response_source: "gemini_ai"` → `"azure_openai"` | ✅ | `backend/services/enhanced_llm_wrapper.py` |
| 2.2.6 | Fix `analytics_service.py` — update pricing comment | ✅ | `backend/services/analytics_service.py` |
| 2.2.7 | Fix `rag_integration_service.py` — update model string in health check | ✅ | `backend/services/rag_integration_service.py` |
| 2.2.8 | Remove `google-generativeai` from `requirements.txt` | ✅ | `backend/requirements-*.txt` |
| 2.2.9 | Remove `GEMINI_API_KEY` from `local.settings.json` template | ✅ | `backend/local.settings.json` |

### 2.3 Standardize Database Name
**Priority:** P1 | **Risk:** Medium — data written to wrong database silently  
**Problem:** `PreferencesService` uses `vimarsh-db`, others use `vimarsh-multi-personality`.  
**Solution:** Standardize all services on `vimarsh-multi-personality` via `AZURE_COSMOS_DATABASE_NAME` env var.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.3.1 | Audit all services for database name usage | ✅ | `backend/services/*.py` |
| 2.3.2 | Update `preferences_service.py` to use env var / standardized name | ✅ | `backend/services/preferences_service.py`, `backend/onboarding/onboarding_service.py`, `backend/notifications/*.py`, `backend/services/hierarchical_memory_service.py` |
| 2.3.3 | Update Bicep database resource name to `vimarsh-multi-personality` | ✅ | `infrastructure/unified-resources.bicep` |

### 2.4 Sync Bicep with Actual Containers  
**Priority:** P1 | **Risk:** Medium — IaC cannot recreate environment  
**Problem:** Bicep defines 3 containers. Code uses 15+.  
**Solution:** Add all referenced containers to Bicep.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.4.1 | Audit all container references in backend code | ✅ | `backend/services/*.py` |
| 2.4.2 | Add missing containers to Bicep | ✅ | `infrastructure/unified-resources.bicep` (added: personalities, personality_vectors, users, user_preferences, user_sessions, user_interactions, user_activity, notification_subscriptions, token_usage, user_cost_totals, engagement_tracking, memory_profiles, conversation_history, relationship_states, session_summaries) |
| 2.4.3 | Ensure partition keys match code expectations | ✅ | `infrastructure/unified-resources.bicep` (all use `/user_id` or `/personality_id` as appropriate) |

### 2.5 Implement Conversation History API
**Priority:** P1 | **Risk:** Medium — core PRD feature is stubbed out  
**Problem:** `api.ts` `getConversationHistory()` always returns `{ conversations: [] }` with TODO comment.  
**Solution:** Implement backend endpoint + wire frontend.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.5.1 | Create `GET /api/conversations` backend endpoint | ✅ | `backend/routes/user_bp.py` |
| 2.5.2 | Implement frontend `getConversationHistory()` method | ✅ | `frontend/src/utils/api.ts` |
| 2.5.3 | Wire conversation list into GuidanceInterface or dedicated component | ✅ | `frontend/src/components/ConversationHistory.tsx` (now fetches from API for authenticated users) |

### 2.6 Unify Frontend API Client
**Priority:** P1 | **Risk:** Medium — inconsistent auth/retry behavior  
**Problem:** Three HTTP patterns: `SpiritualGuidanceAPI` singleton (auth+retry), raw `fetch()` (manual auth), raw `axios` (no auth).  
**Solution:** Funnel all API calls through the singleton.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.6.1 | Refactor `SettingsContext.tsx` — replace `fetch()` with API singleton | ✅ | `frontend/src/contexts/SettingsContext.tsx`, `frontend/src/utils/api.ts` (added getUserProfile, updatePreferences) |
| 2.6.2 | Refactor `GuidanceInterface.tsx` — replace `fetch()` with API singleton | ✅ | `frontend/src/components/GuidanceInterface.tsx` |
| 2.6.3 | Verify all frontend files use consistent API client | ✅ | Audit complete. See notes below. |

**2.6.3 Audit Notes:**
- ✅ `GuidanceInterface.tsx` — migrated to API singleton
- ✅ `SettingsContext.tsx` — migrated to API singleton
- ⏳ `useSpiritualChat.ts` — uses raw fetch; intentional (requires AbortController for cancellation)
- ⏳ `notificationApi.ts` — uses raw fetch; domain-specific service (separate concern)
- ⏳ `onboardingApi.ts` — uses axios; domain-specific service (separate concern)
- ⏳ `adminService.ts` — uses raw fetch; admin domain (separate concern)
- ⏳ `AdminServiceDashboard.tsx` — uses raw fetch; admin health checks
- ⏳ `SharingInterface.tsx` — uses raw fetch; share tracking (separate concern)

**Recommendation:** Add AbortController support to API singleton in Phase 3 to migrate `useSpiritualChat.ts`.

### 2.7 Split Monolith Frontend Components
**Priority:** P1 | **Risk:** Low-Medium — unmaintainable at current size  
**Problem:** `GuidanceInterface.tsx` (1,746 lines), `LandingPage.tsx` (1,595 lines).  
**Solution:** Extract by responsibility.

**Progress:** Created `frontend/src/components/chat/` with types.ts, MessageSourceBadge.tsx, index.ts. GuidanceInterface.tsx reduced to 1,607 lines.

| # | Task | Status | Files |
|---|------|--------|-------|
| 2.7.1 | Extract `MessageList` from GuidanceInterface | ⏳ | `frontend/src/components/chat/MessageList.tsx` (deferred: tightly coupled with state) |
| 2.7.2 | Extract `ChatInput` from GuidanceInterface | ⏳ | `frontend/src/components/chat/ChatInput.tsx` (deferred: tightly coupled with state) |
| 2.7.3 | Extract `VoiceControls` from GuidanceInterface | ✅ | Already exists at `frontend/src/components/VoiceControls.tsx` |
| 2.7.4 | Extract `ShareDialog` from GuidanceInterface | ✅ | Already exists at `frontend/src/components/SharingInterface.tsx` |
| 2.7.5 | Slim GuidanceInterface to composition root | ✅ | Extracted `Message` type and `MessageSourceBadge` to `chat/` module |
| 2.7.6 | Extract `HeroSection` from LandingPage | ⬜ | `frontend/src/components/landing/HeroSection.tsx` |
| 2.7.7 | Extract `PersonalityShowcase` from LandingPage | ⬜ | `frontend/src/components/landing/PersonalityShowcase.tsx` |
| 2.7.8 | Slim LandingPage to composition root | ⬜ | `frontend/src/components/LandingPage.tsx` |

---

## Phase 3: P2 — Quality & Maintainability

### 3.1 Fix Test Coverage Thresholds
**Priority:** P2  
**Problem:** Backend 10%, Frontend 2-4% thresholds will never fail. 5 Settings test suites are `describe.skip`.

| # | Task | Status | Files |
|---|------|--------|-------|
| 3.1.1 | Raise backend coverage threshold to 40% | ⬜ | `.github/workflows/unified-ci-cd.yml` |
| 3.1.2 | Raise frontend coverage thresholds to 30% | ⬜ | `frontend/package.json` (jest config) |
| 3.1.3 | Un-skip or delete 5 Settings test suites | ⬜ | `frontend/src/tests/Settings/*.test.tsx` |

### 3.2 Add Lint & Type-Check to CI
**Priority:** P2  
**Problem:** flake8, mypy, eslint, tsc configured but never run in CI pipeline.

| # | Task | Status | Files |
|---|------|--------|-------|
| 3.2.1 | Add `npm run type-check` step to frontend test job | ⬜ | `.github/workflows/unified-ci-cd.yml` |
| 3.2.2 | Add `flake8` step to backend test job | ⬜ | `.github/workflows/unified-ci-cd.yml` |
| 3.2.3 | Fix any lint/type errors surfaced | ⬜ | Various |

### 3.3 Archive Dead Service Versions
**Priority:** P2  
**Problem:** `backend/services/` has 57 files with `enhanced_*`, `*_v2`, `*_v6`, `phase2_*` duplicates.

| # | Task | Status | Files |
|---|------|--------|-------|
| 3.3.1 | Audit which services are actually imported by function_app.py | ⬜ | `backend/function_app.py` |
| 3.3.2 | Move unused service files to `backend/archived/` | ⬜ | `backend/services/` → `backend/archived/` |
| 3.3.3 | Remove version suffixes from active services | ⬜ | `backend/services/` |

### 3.4 Fix Stale Closure in Settings Debounce
**Priority:** P2  
**Problem:** `pendingUpdates` captured in setTimeout closure may be stale after 500ms.

| # | Task | Status | Files |
|---|------|--------|-------|
| 3.4.1 | Replace `pendingUpdates` state with useRef | ⬜ | `frontend/src/contexts/SettingsContext.tsx` |
| 3.4.2 | Write test: rapid successive setting changes all persist | ⬜ | `frontend/src/contexts/SettingsContext.test.tsx` |

### 3.5 Co-locate Azure Regions
**Priority:** P2 | **Note:** Requires Azure portal/CLI — infrastructure change  
**Problem:** Functions (East US) → Cosmos DB (West US 2) cross-continent latency on every DB call.

| # | Task | Status | Files |
|---|------|--------|-------|
| 3.5.1 | Plan region consolidation (target: West US 2 for all compute) | ⏭️ | `infrastructure/unified-resources.bicep` |
| 3.5.2 | Execute migration with zero-downtime strategy | ⏭️ | Azure portal / CLI |

---

## Phase 4: UX Revamp — Login-to-Logout Experience

> **Goal:** Fix the 5 critical UX problems identified in the Steve Jobs/Jony Ive audit: auth cascade, competing onboarding systems, confusing navigation, unstyled Settings, and inconsistent Admin panel.  
> **Dependency:** After Phase 2 (especially 2.6 unified API, 2.7 component split).  
> **Approach:** Fix in dependency order — auth stability first, then navigation, then pages.

### 4.1 Fix Auth Callback Cascade (Remove Artificial Delays)
**Priority:** P0 UX | **Risk:** High — users see 5+ screen transitions on every login  
**Problem:** AuthCallback.tsx has 1000ms + 1200ms delays. LandingPage has 500ms redirect delay. AppLoadingContext has 100ms delay. Combined: 3+ seconds of unnecessary waiting across multiple flashing screens.  
**Solution:** Remove all artificial delays. Auth callback should process redirect → refresh → navigate in one flow.

| # | Task | Status | Files |
|---|------|--------|-------|
| 4.1.1 | Remove 1000ms "state settling" await from AuthCallback | ✅ | `frontend/src/components/AuthCallback.tsx` |
| 4.1.2 | Remove 1200ms setTimeout before navigate('/guidance') | ✅ | `frontend/src/components/AuthCallback.tsx` |
| 4.1.3 | Remove 500ms redirect delay from LandingPage | ✅ | `frontend/src/components/LandingPage.tsx` |
| 4.1.4 | Remove 100ms delay from AppLoadingContext | ✅ | `frontend/src/contexts/AppLoadingContext.tsx` |
| 4.1.5 | Remove MSAL initialization retry loop (5×500ms) from AuthProvider | ✅ | `frontend/src/auth/AuthProvider.tsx` |

### 4.2 Eliminate Orphaned Auth Context
**Priority:** P0 UX | **Risk:** High — AccountTab uses wrong auth provider, logout may break  
**Problem:** `frontend/src/context/AuthContext.tsx` is an orphaned legacy module with a different interface (AuthUser vs AccountInfo). `AccountTab.tsx` imports `useAuth` from this wrong path, causing potential runtime errors when `user?.email` doesn't exist.  
**Solution:** Delete orphaned context, fix AccountTab import.

| # | Task | Status | Files |
|---|------|--------|-------|
| 4.2.1 | Fix AccountTab: import useAuth from `../../auth/AuthProvider` | ✅ | `frontend/src/components/Settings/AccountTab.tsx` |
| 4.2.2 | Update AccountTab to use `account?.username` instead of `user?.email` | ✅ | `frontend/src/components/Settings/AccountTab.tsx` |
| 4.2.3 | Delete orphaned `frontend/src/context/AuthContext.tsx` | ✅ | `frontend/src/context/AuthContext.tsx` (deleted) |
| 4.2.4 | Verify no other files import from `context/AuthContext` | ✅ | Grep confirmed; updated test mocks in `setupTests.ts` |

### 4.3 Fix EngagementTour Placement & Onboarding Unification
**Priority:** P0 UX | **Risk:** High — modal fires on every page load for new users, blocks app  
**Problem A:** `EngagementTourWrapper` renders in App.tsx OUTSIDE the Router, fires globally based on localStorage only (no auth check). Shows 6-step modal within 1.5s of ANY page load.  
**Problem B:** Two competing onboarding systems: EngagementTour (localStorage-based, engagement features) and OnboardingWizard (API-based, personality quiz). Both can fire simultaneously.  
**Problem C:** LandingPage shows OnboardingWizard on API error (catch block defaults to `setShowOnboarding(true)`).  
**Solution:** Move EngagementTour inside /guidance route (auth-gated), fix onboarding error handling.

| # | Task | Status | Files |
|---|------|--------|-------|
| 4.3.1 | Remove `EngagementTourWrapper` from App.tsx (global scope) | ✅ | `frontend/src/App.tsx` |
| 4.3.2 | Add EngagementTour to GuidanceInterface (only shows for authenticated users on /guidance) | ✅ | `frontend/src/components/GuidanceInterface.tsx` |
| 4.3.3 | Fix LandingPage: don't show OnboardingWizard on API error — treat as "new user, skip" | ✅ | `frontend/src/components/LandingPage.tsx` |
| 4.3.4 | Remove onboarding wizard from LandingPage for authenticated users (they redirect to /guidance) | ✅ | Already handled by redirect logic |

### 4.4 Revamp Navigation Header (User Menu Dropdown)
**Priority:** P1 UX | **Risk:** Medium — confusing icon-only buttons, no discoverability  
**Problem:** GuidanceInterface header has 6-8 icon-only buttons (personality badge, memory indicator, streak display, settings gear, admin emoji ⚙️, logout arrow). Personality name truncated to 100px. Uses `window.innerWidth` instead of CSS media queries.  
**Solution:** Replace icon row with a clean personality badge + user avatar dropdown menu.

| # | Task | Status | Files |
|---|------|--------|-------|
| 4.4.1 | Create UserMenuDropdown component with avatar, name, and menu items | ✅ | `frontend/src/components/UserMenuDropdown.tsx` (new, ~260 lines) |
| 4.4.2 | Replace icon-only buttons in GuidanceInterface header with UserMenuDropdown | ✅ | `frontend/src/components/GuidanceInterface.tsx` (header reduced from ~260 to ~60 lines) |
| 4.4.3 | Move Memory, Progress, Admin links into dropdown menu | ✅ | `frontend/src/components/UserMenuDropdown.tsx` |
| 4.4.4 | Replace `window.innerWidth` checks with CSS media queries | ⏳ | Deferred: removed from header, still present in body (separate task) |

### 4.5 Rewrite Settings Page Styling
**Priority:** P1 UX | **Risk:** Medium — Tailwind classes don't render (no config), page looks broken  
**Problem:** UserSettings.tsx and all 5 tab components use Tailwind utility classes (e.g., `className="min-h-screen bg-gray-50"`), but there's no `tailwind.config.js` or PostCSS config in the frontend. Classes don't compile → page renders with no styling. Also uses emoji icons (👤 ✨ 🔔 🔒 ⚙️) instead of proper icons.  
**Solution:** Create settings-utilities.css providing CSS utility classes matching the vimarsh design system. Replace emoji icons with Lucide React icons. Fix complex patterns (toggle switches, group-hover) with component CSS classes.

| # | Task | Status | Files |
|---|------|--------|-------|
| 4.5.1 | Create settings-utilities.css with utility classes + import in UserSettings | ✅ | `frontend/src/styles/settings-utilities.css` (new, 427 lines), `frontend/src/pages/UserSettings.tsx` |
| 4.5.2 | Replace emoji tab icons with Lucide React icons | ✅ | `frontend/src/pages/UserSettings.tsx` (User, Sparkles, Bell, Shield, Settings icons) |
| 4.5.3 | Fix toggle switches (NotificationsTab) — replace complex Tailwind peer/after patterns with CSS component class | ✅ | `frontend/src/components/Settings/NotificationsTab.tsx` |
| 4.5.4 | Fix gradient hover button (AccountTab) — replace Tailwind gradient hover with inline style | ✅ | `frontend/src/components/Settings/AccountTab.tsx` |
| 4.5.5 | Fix text size preview (ExperienceTab) — replace conditional Tailwind classes with inline style | ✅ | `frontend/src/components/Settings/ExperienceTab.tsx` |
| 4.5.6 | Add missing focus ring and checkbox accent color utility classes | ✅ | `frontend/src/styles/settings-utilities.css` |

### 4.6 Unify Admin Panel Design System
**Priority:** P2 UX | **Risk:** Low-Medium — admin panel looks like a different app  
**Problem:** AdminDashboard.tsx imports `admin.css` (1,215 lines) with completely different design tokens: Inter font instead of system stack, blue gradient sidebar instead of orange brand, separate spacing/shadow variables. It's the only place in the app with a sidebar navigation.  
**Solution:** Apply consistent design from vimarsh-design-system.css. Replace sidebar with tab-based layout matching the rest of the app.

| # | Task | Status | Files |
|---|------|--------|-------|
| 4.6.1 | Replace admin.css color tokens with vimarsh-design-system.css variables | ⏳ | Deferred: gray/spacing tokens already aligned |
| 4.6.2 | Replace Inter font with app-wide system font stack | ✅ | `frontend/src/styles/admin.css` |
| 4.6.3 | Replace blue gradient sidebar with orange-tinted brand-consistent header | ✅ | `frontend/src/styles/admin.css` (gradient now blue→saffron) |

---

## Execution Order & Dependencies

```
Phase 0 (Specs)          ← DONE
  │
Phase 1 (P0 Security)   ← DONE
  │
Phase 2 (P1 Architecture) ← DONE (2.7.6-2.7.8 deferred)
  │
Phase 3 (P2 Quality)    ← IN PROGRESS
  │
Phase 4 (UX Revamp)      ← DONE (4.4.4 and 4.6.1 deferred)
  ├── 4.1 Auth cascade fix        ✅
  ├── 4.2 Orphaned AuthContext     ✅
  ├── 4.3 EngagementTour fix       ✅
  ├── 4.4 Navigation revamp        ✅ (4.4.4 body media queries deferred)
  ├── 4.5 Settings rewrite         ✅
  └── 4.6 Admin consistency        ✅ (4.6.1 full token replacement deferred)
```

---

## Verification Checkpoints

After each phase, verify:

- **Phase 1:** `pytest backend/tests/` passes, `npm test` passes, settings save round-trips in browser, no wildcard CORS in Bicep
- **Phase 2:** `pytest backend/tests/` passes, `npm run build` succeeds, `npm run type-check` clean, no `google.generativeai` imports in `backend/services/`
- **Phase 3:** CI pipeline runs lint + typecheck, coverage thresholds enforced, `backend/services/` has < 30 active files
- **Phase 4:** `npm run build` succeeds, no TypeScript errors, no imports from `context/AuthContext`, all Settings tabs render styled (visual check), auth callback completes in < 500ms (no artificial delays), EngagementTour only shows for authenticated users on /guidance route

---

*Last updated: 2025-07-25*
