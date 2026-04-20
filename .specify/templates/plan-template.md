# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Document how the plan satisfies each constitutional principle:

- **Percepcion del Cliente/Jurado como Criterio Final**: Explain how the plan
  improves or preserves the demo perception, visual quality, functional clarity
  and expected satisfaction of the client/jury.
- **Identidad Inmersiva y Experiencia Asistida**: If the feature touches UI,
  explain how it preserves or raises the visual and interaction quality of
  `home_estudiante.html` and `seleccion_modalidad.html`, including responsive
  behavior, visible states and contextual help. Include the required breakpoint
  plan for mobile and tablet as real-use devices: mobile `360-767px`, tablet
  portrait `768-1023px`, tablet landscape `1024-1279px` and desktop `1280px+`.
  Identify flows consumed on mobile from the specification and confirm they will
  be tested in a mobile viewport before approval. If the screen was not already
  identified for mobile responsivity, record the developer consultation that
  defines which interfaces apply before planning or implementing the responsive
  change. Confirm tablet touch targets are at least `44x44px`, critical game
  flows are tested in both tablet orientations, and layout remains stable when
  rotating during an active session.
- **Impacto Visual y Funcional sobre Patrones Internos**: Identify any internal
  pattern, code organization or architecture choice that will be changed because
  it materially improves client/jury perception. Document why the improvement
  takes priority and how the existing system remains unbroken.
- **No Regresion Verificada**: List automated tests or reproducible manual checks
  for affected roles, URLs, templates, data, timers, teams, coevaluation, final
  results and OpenAI behavior when applicable.
- **Evolucion Guiada por Demostracion**: Document benefits, risks and evidence
  for relevant departures from internal patterns. Record explicit developer
  authorization only when the departure increases regression risk, changes data
  contracts, adds significant dependencies or alters existing flows.
- **Usabilidad Funcional y Sin Friccion**: Explain how user actions receive
  visible feedback in under `300ms`, how every flow supports clear forward and
  backward movement, how errors explain what happened and what to do next, how
  equivalent actions stay consistent across screens, and how each screen limits
  the experience to one dominant primary action and no more than three
  simultaneous decisions.
- **Higiene de Codigo**: List the existing files inspected before proposing any
  new file. For every new file, justify why no existing app, component, template,
  CSS or JS file can own the change. Identify replaced logic that will be
  deleted in the same change, confirm no unused functions, views, templates, CSS
  classes or files will remain, and describe how generated Django migrations
  will be reviewed for redundant or conflicting operations before applying them.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
