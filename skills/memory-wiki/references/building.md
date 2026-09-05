# Building profile

## Seed requirements

Elicit or preserve:

- problem and user-visible outcome;
- acceptance criteria;
- target repository;
- compatibility, security, performance, and migration constraints;
- suspected components and unknowns;
- external implementations or papers worth comparing;
- explicit non-goals.

Keep the original seed unchanged after initialization.

## Research boundaries

Use the project wiki for external knowledge: algorithms, standards, documentation, papers, and architecture notes about comparison repositories.

Treat the target repository as live source code, not as wiki material. Read its code, tests, glossary, and ADRs directly. Do not build a generated graph of the current repository unless a measured retrieval problem justifies it.

Never edit the target repository while project status is `seed`, `scoped`, `researching`, `distilled`, or `critiqued`. Begin implementation after the project reaches `ready`.

## Guideline

Write `guideline.md` as an executable implementation plan containing:

1. current behavior and evidence;
2. desired behavior and acceptance criteria;
3. chosen design and rejected alternatives;
4. affected interfaces, modules, data, and dependencies;
5. compatibility and migration strategy;
6. failure modes, security, and observability;
7. ordered implementation tasks;
8. tests and verification for each task;
9. documentation or ADR changes;
10. open questions that block implementation.

Distinguish facts observed in the target repository from external patterns and agent inferences.

## Reflection

Check:

- every acceptance criterion maps to implementation and verification;
- the design fits current repository conventions;
- external patterns are adapted rather than copied blindly;
- interfaces and ownership boundaries are explicit;
- rollback, migration, and failure behavior are addressed where relevant;
- tests cover regression and negative paths;
- no open blocking question is hidden in prose.

## Decision review

Resolve tradeoffs from code, evidence, repository constraints, and prior user direction when possible. Ask the user only about product behavior, compatibility tolerance, operational cost, API taste, migration appetite, or accepted risk when the choice is material and cannot be inferred safely.

## Implementation

After the plan passes critique and lint and reaches `ready`:

1. Reinspect the live repository because it may have changed since planning.
2. Implement in small coherent milestones.
3. Test in proportion to risk after each milestone.
4. Record deviations and their rationale in `critique.md` or an ADR.
5. Mark `implemented` only after changes exist; mark `verified` only after acceptance criteria pass.
