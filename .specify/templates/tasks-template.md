---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions
- Each implementation task MUST explicitly state files modified, files created
  and files deleted. If it creates files, include the justification for not
  modifying an existing file instead.

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management
- [ ] T010 Confirm affected Django app boundaries, URL names, templates, static
  assets and settings either reuse the existing architecture or document a
  perception-driven departure with no-regression validation
- [ ] T011 If UI is affected, inventory reusable Mision Emprende components,
  visual tokens, help patterns and responsive states from the baseline screens
- [ ] T012 Identify the visible or functional improvement most likely to affect
  client/jury approval and define how it will be validated in the demo
- [ ] T013 If UI is affected, identify mobile and tablet real-use interfaces;
  define validation coverage for mobile `360-767px`, tablet portrait
  `768-1023px`, tablet landscape `1024-1279px` and desktop `1280px+`, including
  tablet touch targets of at least `44x44px`
- [ ] T014 If a screen was not previously identified for mobile responsivity,
  consult the developer on which interfaces apply before planning or
  implementing responsive changes
- [ ] T015 If mobile-consumed flows are affected, define mobile viewport
  validation before approval
- [ ] T016 If UI is affected, define how user actions will show visible feedback
  in under `300ms`, how flows move forward/backward, and how errors explain next
  steps
- [ ] T017 Inventory existing files that could own this change before creating
  any new file; document which files will be modified, created and deleted
- [ ] T018 Identify replaced logic, templates, views, CSS classes, JS or files
  that must be removed in the same change so no inactive consumers remain

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T019 [P] [US1] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T020 [P] [US1] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create [Entity1] model in src/models/[entity1].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T022 [P] [US1] Create [Entity2] model in src/models/[entity2].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T023 [US1] Implement [Service] in src/services/[service].py (depends on T021, T022);
  files modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T024 [US1] Implement [endpoint/feature] in src/[location]/[file].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T025 [US1] Add validation and actionable error handling
- [ ] T026 [US1] If UI is affected, implement responsive Mision Emprende visual
  treatment, visible states and contextual help in the relevant template/static files
- [ ] T027 [US1] If UI is affected, enforce one dominant primary action, no more
  than three simultaneous decisions and consistent behavior for equivalent actions
- [ ] T028 [US1] If an internal pattern changes for better demo perception,
  document the benefit and no-regression evidence in plan.md or quickstart.md
- [ ] T029 [US1] Remove or update replaced functions, views, templates, CSS
  classes, JS and files so no inactive code remains
- [ ] T030 [US1] Add logging or operational feedback for user story 1 operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T031 [P] [US2] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T032 [P] [US2] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 2

- [ ] T033 [P] [US2] Create [Entity] model in src/models/[entity].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T034 [US2] Implement [Service] in src/services/[service].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T035 [US2] Implement [endpoint/feature] in src/[location]/[file].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T036 [US2] Integrate with User Story 1 components (if needed)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T037 [P] [US3] Contract test for [endpoint] in tests/contract/test_[name].py
- [ ] T038 [P] [US3] Integration test for [user journey] in tests/integration/test_[name].py

### Implementation for User Story 3

- [ ] T039 [P] [US3] Create [Entity] model in src/models/[entity].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T040 [US3] Implement [Service] in src/services/[service].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]
- [ ] T041 [US3] Implement [endpoint/feature] in src/[location]/[file].py; files
  modified: [list]; files created: [list with justification]; files deleted: [list]

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Validate UI against `home_estudiante.html` and
  `seleccion_modalidad.html` quality bar when screens changed
- [ ] TXXX Verify responsive behavior, focus states, active/disabled states,
  help overlays/tooltips and absence of text overflow on affected screens
- [ ] TXXX Verify mobile `360-767px`, tablet portrait `768-1023px`, tablet
  landscape `1024-1279px` and desktop `1280px+`; confirm tablet touch targets
  are at least `44x44px`
- [ ] TXXX Verify every flow identified as consumed on mobile passes mobile
  viewport validation before approval
- [ ] TXXX Confirm developer consultation is documented before responsive work
  on any screen not previously identified for mobile responsivity
- [ ] TXXX Verify critical game flows in tablet portrait and landscape, including
  rotation during an active session without hidden controls, layout jumps or
  progress loss
- [ ] TXXX Verify every user action shows visible feedback in under `300ms`,
  each flow has clear forward/backward movement, errors are actionable, and each
  screen has one dominant primary action with no more than three simultaneous
  decisions
- [ ] TXXX Verify existing Django URLs, templates, forms, sessions, teams,
  timers, coevaluation/final-result flows and OpenAI fallback behavior affected
  by the change
- [ ] TXXX Verify no inactive functions, views, templates, CSS classes, JS or
  files remain after replacements
- [ ] TXXX Review generated Django migrations before applying them and confirm
  they do not duplicate or conflict with earlier migrations
- [ ] TXXX Validate that the final demo path improves or preserves
  client/jury perception and satisfaction
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Internal patterns MAY change for significant visual or functional demo
  improvement, but every such change must include no-regression evidence
- Stop before any task that increases regression risk, changes data contracts,
  adds significant dependencies or alters existing flows unless explicit
  developer authorization is documented
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
