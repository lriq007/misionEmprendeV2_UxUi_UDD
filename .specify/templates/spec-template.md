# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?
- If this changes UI, which interfaces are consumed on mobile or tablet as
  real-use devices while preserving the Mision Emprende baseline?
- If this changes UI, how does the screen behave at mobile `360-767px`, tablet
  portrait `768-1023px`, tablet landscape `1024-1279px` and desktop `1280px+`?
- If this screen was not previously identified for mobile responsivity, what did
  the developer confirm about whether mobile applies?
- Which flows are consumed on mobile and how will they be tested in a mobile
  viewport before approval?
- If this changes a critical game flow, what happens when a tablet rotates
  during an active session?
- What feedback appears within `300ms` after each user action?
- What route lets the user move forward or backward from every step?
- How do errors tell the user what happened and what to do next?
- If this touches backend data or flow, how are existing sessions, teams,
  templates, URLs and role-specific paths protected from regression?
- If this requires a new file, what existing files were checked first and why
  are they not the right owner for the change?
- If this replaces existing behavior, what old functions, views, templates, CSS,
  JS or files must be removed in the same change?
- If this creates Django migrations, what previous migrations could conflict or
  become redundant?
- What visible or functional outcome will most affect client/jury perception,
  and how could the feature fail that expectation during a demo?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]
- **FR-UX**: If user-facing UI is changed, the system MUST preserve the visual
  quality, interaction states, contextual help and responsive behavior expected
  from `home_estudiante.html` and `seleccion_modalidad.html`.
- **FR-RESPONSIVE**: If user-facing UI is changed, the system MUST treat mobile
  and tablet as real-use devices where applicable. It MUST support mobile
  `360-767px`, tablet portrait `768-1023px`, tablet landscape `1024-1279px` and
  desktop `1280px+`; tablet touch targets MUST be at least `44x44px`; flows
  consumed on mobile MUST be identified in this specification and tested in a
  mobile viewport before approval; critical game flows MUST remain stable across
  tablet rotation. If a screen was not previously identified for mobile
  responsivity, the developer MUST be consulted before planning or implementing
  the responsive change.
- **FR-FRICTION**: User actions MUST provide visible feedback in under `300ms`;
  every flow MUST provide clear forward and backward movement; errors MUST state
  what happened and what to do next; equivalent actions MUST behave consistently
  across screens; each screen MUST have one dominant primary action and no more
  than three simultaneous decisions.
- **FR-PERCEPTION**: The system MUST prioritize changes that significantly
  improve client/jury perception, provided no existing flow is broken.
- **FR-REGRESSION**: If backend behavior is changed, the system MUST protect
  existing Django app boundaries, URL/template/static conventions,
  model/migration flow, environment configuration and affected role paths from
  regression. Internal patterns MAY change when they materially improve the demo
  and pass no-regression validation.
- **FR-HYGIENE**: Before creating a file, the implementation MUST verify whether
  an existing file fulfills the same role and modify it instead when possible.
  The implementation MUST NOT leave unused functions, views, templates, CSS
  classes or files; replaced logic MUST be deleted in the same change, not
  commented out; new CSS or JS MUST go into the existing component or app file
  unless explicit responsibility or volume justification is documented; Django
  migrations MUST be reviewed before application for redundant or conflicting
  operations.

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
- **SC-UX**: [If UI applies, measurable visual/interaction validation, e.g.,
  "Primary flow is usable without horizontal overflow at mobile, tablet portrait,
  tablet landscape and desktop widths, with visible focus and help controls"]
- **SC-RESPONSIVE**: [If UI applies, mobile/tablet validation, e.g., "Flows
  consumed on mobile pass mobile viewport validation, critical game flow remains
  usable in tablet portrait and landscape, touch targets are at least 44x44px,
  and rotation during an active session does not hide controls or lose progress"]
- **SC-FRICTION**: [If UI applies, usability validation, e.g., "Every user
  action shows visible feedback in under 300ms, every step has forward/back
  movement, and errors include next-step guidance"]
- **SC-REG**: [Regression validation, e.g., "Existing role path [X] continues to
  complete successfully after the change"]
- **SC-HYGIENE**: [Code hygiene validation, e.g., "Implementation declares files
  modified, created and deleted; every new file has a justification; no unused
  replaced code, template, CSS class or file remains; migrations were reviewed
  before applying"]
- **SC-JURY**: [Client/jury perception validation, e.g., "Demo reviewer can
  understand and complete the primary flow without explanation and rates the
  visual/functional result as acceptable for approval"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
