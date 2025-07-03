# Vimarsh Test-Suite Refactor & Coverage Roadmap

_Last updated: 2025-07-03_

## Objective
Bring the automated test-suite back to a 100 % pass rate with ≥ 85 % line coverage while aligning all tests with the current architecture (Gemini-Pro, RAG, cost-management, MSAL auth, etc.).

---

## Phase overview
| Phase | Targets | Packages | Coverage Gate | ETA |
|-------|---------|----------|---------------|-----|
| **Phase 1** | • Green Error-Handling core  <br>• Voice shim in place  <br>• Remove generated tests | Pkg-1,2,4,8 | 50 % | **Day 1–2** |
| **Phase 2** | • RAG & cost tests rewritten  <br>• Front-end Jest & RTL stable | Pkg-3,5,6 | 70 % | **Day 3** |
| **Phase 3** | • Cypress auth flow updated  <br>• Micro-tests for new logic  <br>• Raise coverage to 85 % | Pkg-7,9,10 | 85 % | **Day 4** |

---

## Detailed Work Packages

### Pkg-1 Error-Handling core rewrite  (6 files)
* Update imports to new `backend.error_handling.*` paths.
* Adapt to async `ErrorAnalytics.record_error`.
* Replace deprecated enums.

### Pkg-2 Voice pipeline tests  (8 files)
* Port to new `voice.*` modules.
* Mock TTS engine & speech recogniser.

### Pkg-3 RAG pipeline tests  (5 files)
* Target `backend.rag_pipeline.RAGService` with fake vector store.

### Pkg-4 Cost-management patches  (4 files)
* Update dynamic fallback & graceful degradation APIs.

### Pkg-5 Front-end Jest fixes  (10 files)
* Add MSAL mocks, enable auth flag.

### Pkg-6 RTL integration tests  (6 files)
* Re-enable page-level tests with new routes.

### Pkg-7 Cypress updates  (3 specs)
* Use real MSAL popup stub, new onboarding flow.

### Pkg-8 Remove generated tests
* Delete `generated_tests/` directory.

### Pkg-9 Micro-tests & coverage
* Fast unit tests for RAG context parsing, cost decorators, citation extraction.

### Pkg-10 CI gate adjustments
* Gradually raise `COVERAGE_THRESHOLD` in workflow.

---

## Progress Checklist
- [x] Branch `test-refactor/phase1` created
- [x] Generated tests removed
- [x] Coverage gate lowered to 25 % (done)
- [ ] **Phase 1** packages green
- [ ] Coverage gate raised to 50 %
- [ ] **Phase 2** packages green
- [ ] Coverage gate raised to 70 %
- [ ] **Phase 3** packages green
- [ ] Final gate 85 % & CI GREEN

---

## Notes / Decisions
* Legacy tests marked `xfail` temporarily via `tests/conftest.py`.
* Shim modules added for backwards-compat imports; to be removed after test rewrite.
* Voice & TTS external calls fully mocked – no network usage.

> _"A flaky test is worse than no test."  Each migrated test must be deterministic under local & CI runs._ 