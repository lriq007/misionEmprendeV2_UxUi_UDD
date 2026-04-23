# Tasks: Actualizacion Rompehielo Ruleta

**Input**: Design documents from `/specs/001-rompehielo-ruleta/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/rompehielo-json.md`, `quickstart.md`

**Tests**: Include Django automated coverage in `proyecIngSoft/etapasJuego/tests.py` plus manual validation updates in `specs/001-rompehielo-ruleta/quickstart.md` because the specification requires independent verification, responsive checks, rotation checks, repeated-tap handling, and error recovery.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently after the shared backend/bootstrap foundation is complete.

**Design Note**: `spec.md` defines a tablet-first ruleta UI, while `plan.md`, `research.md`, `data-model.md`, and `contracts/rompehielo-json.md` define a backend bootstrap slice on the existing `rompehielo` route. The task plan below reconciles both: shared phases establish the question catalog and JSON bootstrap, then each user story implements the UI behavior described in the specification on the existing Django template, CSS, and JS files.

## Phase 1: Setup (Shared Alignment)

**Purpose**: Align the documented implementation scope and verification surface before touching the Django app.

- [X] T001 Reconcile the UI scope from `specs/001-rompehielo-ruleta/spec.md` with the backend bootstrap scope in `specs/001-rompehielo-ruleta/plan.md`; files modified: `specs/001-rompehielo-ruleta/plan.md`; files created: none; files deleted: none
- [X] T002 Update the implementation and manual validation notes in `specs/001-rompehielo-ruleta/quickstart.md` to cover the existing Django paths `proyecIngSoft/etapasJuego/views.py`, `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`, `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`, and `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files modified: `specs/001-rompehielo-ruleta/quickstart.md`; files created: none; files deleted: none
- [X] T003 Capture the final ownership decision for `proyecIngSoft/etapasJuego/views.py`, `proyecIngSoft/etapasJuego/tests.py`, `proyecIngSoft/etapasJuego/services/__init__.py`, and `proyecIngSoft/etapasJuego/services/roulette.py` in `specs/001-rompehielo-ruleta/plan.md`; files modified: `specs/001-rompehielo-ruleta/plan.md`; files created: none; files deleted: none

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared question/bootstrap layer that all ruleta stories depend on.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [X] T004 Create the stateless question catalog and cycle-safe selection API in `proyecIngSoft/etapasJuego/services/roulette.py`; files modified: none; files created: `proyecIngSoft/etapasJuego/services/roulette.py` (new domain service is justified because no existing service owns rompehielo question selection or error payloads); files deleted: none
- [X] T005 [P] Export `RouletteEngine` from `proyecIngSoft/etapasJuego/services/__init__.py` only if the package facade is already consumed elsewhere; files modified: `proyecIngSoft/etapasJuego/services/__init__.py`; files created: none; files deleted: none
- [X] T006 Implement dual HTML/JSON handling for the existing `rompehielo` route in `proyecIngSoft/etapasJuego/views.py` using `specs/001-rompehielo-ruleta/contracts/rompehielo-json.md` as the contract source; files modified: `proyecIngSoft/etapasJuego/views.py`; files created: none; files deleted: none
- [X] T007 [P] Add shared backend coverage for `RouletteEngine`, HTML render mode, and `?format=json` bootstrap mode in `proyecIngSoft/etapasJuego/tests.py`; files modified: `proyecIngSoft/etapasJuego/tests.py`; files created: none; files deleted: none

**Checkpoint**: The existing `rompehielo` URL serves both template and JSON bootstrap, and the ruleta UI can consume a stable question source.

---

## Phase 3: User Story 1 - Guiar un turno de rompehielo (Priority: P1) 🎯 MVP

**Goal**: Replace the static rompehielo panel with a ruleta-centered turn flow that surfaces a dominant `Siguiente turno` action, rotates through questions without repetition per cycle, and keeps the timer/exit path intact.

**Independent Test**: Open `/etapasJuego/tablet/rompehielo/` on tablet-sized viewports, trigger multiple consecutive turns, and confirm the screen shows a central ruleta, a clear current question region, and a single dominant `Siguiente turno` action with visible feedback in under `300ms`.

### Tests for User Story 1

- [X] T008 [P] [US1] Add Django assertions in `proyecIngSoft/etapasJuego/tests.py` for the ruleta shell, dominant turn button, current-question region, and JSON question bootstrap consumed by the page; files modified: `proyecIngSoft/etapasJuego/tests.py`; files created: none; files deleted: none
- [X] T009 [P] [US1] Add manual MVP validation steps for repeated taps, question rotation, and timer continuity to `specs/001-rompehielo-ruleta/quickstart.md`; files modified: `specs/001-rompehielo-ruleta/quickstart.md`; files created: none; files deleted: none

### Implementation for User Story 1

- [X] T010 [P] [US1] Rebuild the main rompehielo markup around a ruleta stage, selected-question panel, and central `Siguiente turno` control in `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files modified: `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files created: none; files deleted: none
- [X] T011 [P] [US1] Redesign the ruleta layout, responsive breakpoints, and dominant primary-action styling in `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`; files modified: `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`; files created: none; files deleted: none
- [X] T012 [US1] Implement question bootstrap, non-repeating cycle state, button locking, and sub-`300ms` visual feedback in `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files modified: `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files created: none; files deleted: none
- [X] T013 [US1] Wire the template data hooks needed by `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js` from `proyecIngSoft/etapasJuego/views.py` and `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files modified: `proyecIngSoft/etapasJuego/views.py`, `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files created: none; files deleted: none
- [X] T014 [US1] Preserve the existing timeout overlay route to `etapa1` while removing the obsolete static question-list behavior in `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`, `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`, and `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files modified: `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`, `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`, `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files created: none; files deleted: none

**Checkpoint**: User Story 1 is complete when a group can run repeated turns from the existing route with a ruleta-based layout and no blocked next-step path.

---

## Phase 4: User Story 2 - Indicar la accion del participante actual (Priority: P2)

**Goal**: Show a clear, tablet-legible response instruction immediately after a question is selected without obscuring the question, timer, or primary action.

**Independent Test**: Trigger a turn on tablet portrait and tablet landscape and confirm the screen shows the selected question plus the instruction `Comparte con tus companeros la respuesta` in a visually distinct area that remains legible after rotation.

### Tests for User Story 2

- [X] T015 [P] [US2] Add assertions in `proyecIngSoft/etapasJuego/tests.py` for the response-instruction region and the DOM hooks needed to render instructional state after a question is selected; files modified: `proyecIngSoft/etapasJuego/tests.py`; files created: none; files deleted: none
- [X] T016 [P] [US2] Extend `specs/001-rompehielo-ruleta/quickstart.md` with manual checks for message visibility, overflow prevention, and rotation stability for the current-participant prompt; files modified: `specs/001-rompehielo-ruleta/quickstart.md`; files created: none; files deleted: none

### Implementation for User Story 2

- [X] T017 [P] [US2] Add a dedicated current-participant instruction block and accessible live-update region in `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files modified: `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files created: none; files deleted: none
- [X] T018 [P] [US2] Style the selected-question and response-instruction hierarchy for tablet-first readability in `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`; files modified: `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`; files created: none; files deleted: none
- [X] T019 [US2] Update `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js` to reveal and reset the `Comparte con tus companeros la respuesta` state immediately after each valid selection and after retry recovery; files modified: `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files created: none; files deleted: none

**Checkpoint**: User Story 2 is complete when the current participant gets a clear response instruction that stays readable across the target tablet states.

---

## Phase 5: User Story 3 - Transferir la tablet al siguiente companero (Priority: P3)

**Goal**: Add a separate handoff instruction that clearly tells the group when to pass the tablet, while preserving an obvious path to the next turn and the time-up exit.

**Independent Test**: Complete a turn and confirm the screen shows both the response instruction and a second, visually distinct handoff message `Entregale la tablet al siguiente companero` in a separate zone that remains readable from normal tabletop distance.

### Tests for User Story 3

- [X] T020 [P] [US3] Add assertions in `proyecIngSoft/etapasJuego/tests.py` for the handoff-instruction region, retry-safe state hooks, and continued access to the next-turn action; files modified: `proyecIngSoft/etapasJuego/tests.py`; files created: none; files deleted: none
- [X] T021 [P] [US3] Extend `specs/001-rompehielo-ruleta/quickstart.md` with manual checks for handoff clarity, repeated-turn continuity, and end-of-timer continuation to `etapa1`; files modified: `specs/001-rompehielo-ruleta/quickstart.md`; files created: none; files deleted: none

### Implementation for User Story 3

- [X] T022 [P] [US3] Add a distinct handoff message zone and persistent next-step affordance in `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files modified: `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`; files created: none; files deleted: none
- [X] T023 [P] [US3] Style the handoff zone so it is visually separate from the current-question and response-instruction areas in `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`; files modified: `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`; files created: none; files deleted: none
- [X] T024 [US3] Update `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js` to sequence the handoff message after the response prompt, preserve retry behavior, and keep the next-turn action ready when the current turn completes; files modified: `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files created: none; files deleted: none

**Checkpoint**: User Story 3 is complete when the screen clearly distinguishes the answer step from the handoff step without creating dead ends in the turn flow.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, regression validation, and demo-readiness across all stories.

- [X] T025 [P] Remove replaced placeholder copy, unused CSS selectors, and obsolete JS branches from `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`, `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`, and `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files modified: `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`, `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`, `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files created: none; files deleted: none
- [ ] T026 [P] Validate the updated rompehielo screen against the interaction and visual quality bar established by `proyecIngSoft/etapasJuego/templates/etapasJuego/seleccion_modalidad.html` and `proyecIngSoft/login/templates/login/home_estudiante.html`, then record any final adjustments in `specs/001-rompehielo-ruleta/quickstart.md`; files modified: `specs/001-rompehielo-ruleta/quickstart.md`; files created: none; files deleted: none
- [ ] T027 Run `python manage.py test etapasJuego` from `proyecIngSoft/manage.py` and record the final verification results in `specs/001-rompehielo-ruleta/quickstart.md`; files modified: `specs/001-rompehielo-ruleta/quickstart.md`; files created: none; files deleted: none
- [X] T028 Consultar con el desarrollador si la vista rompehielo tendrá soporte para celulares y registrar la decisión; files modified: `specs/001-rompehielo-ruleta/plan.md`; files created: none; files deleted: none
- [X] T029 Implementar la interfaz de errores para mostrar mensajes accionables y la lógica de reintento en la misma pantalla; files modified: `proyecIngSoft/etapasJuego/templates/etapasJuego/rompehielo.html`, `proyecIngSoft/etapasJuego/static/etapasJuego/css/rompehielo.css`, `proyecIngSoft/etapasJuego/static/etapasJuego/js/rompehielo.js`; files created: none; files deleted: none

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** has no dependencies and should complete first.
- **Phase 2: Foundational** depends on Phase 1 and blocks every user story because the ruleta UI needs a stable question/bootstrap contract.
- **Phase 3: US1** depends on Phase 2 and delivers the MVP.
- **Phase 4: US2** depends on US1 because the response instruction needs the selected-question flow in place.
- **Phase 5: US3** depends on US1 and benefits from US2 because the handoff message must be visually distinct from the answer prompt.
- **Phase 6: Polish** depends on all implemented stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and is the MVP scope.
- **US2 (P2)**: Starts after US1 establishes the selected-question UI.
- **US3 (P3)**: Starts after US1 establishes the turn flow; integrates cleanly after US2 defines the first instructional message.

### Within Each User Story

- Story tests and manual validation updates should land before or alongside implementation for the same story.
- Template structure should exist before the corresponding CSS and JS behavior are finalized.
- JS turn-state work depends on the foundational question/bootstrap contract from Phase 2.

## Parallel Opportunities

- **Setup**: `T002` and `T003` can run in parallel after `T001`.
- **Foundational**: `T005` and `T007` can run in parallel once `T004` is in place; `T006` depends on `T004`.
- **US1**: `T008` and `T009` can run in parallel; `T010` and `T011` can run in parallel; `T012` depends on `T010` plus Phase 2; `T013` depends on `T010` and `T012`.
- **US2**: `T015` and `T016` can run in parallel; `T017` and `T018` can run in parallel; `T019` depends on `T017`.
- **US3**: `T020` and `T021` can run in parallel; `T022` and `T023` can run in parallel; `T024` depends on `T022`.
- **Polish**: `T025` and `T026` can run in parallel; `T027` should run last.

## Implementation Strategy

### MVP First

1. Complete Phases 1 and 2 to stabilize the question source and dual-mode route.
2. Complete Phase 3 to deliver a functional ruleta turn flow on the existing `rompehielo` screen.
3. Stop and validate the MVP on tablet before layering additional guidance.

### Incremental Delivery

1. Add the current-participant prompt in Phase 4 without changing the core turn loop.
2. Add the handoff prompt in Phase 5 as a second guided layer.
3. Finish with cleanup and full regression checks in Phase 6.
