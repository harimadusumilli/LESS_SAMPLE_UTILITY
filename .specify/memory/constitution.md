<!--
Sync Impact Report
- Version change: template → 1.0.0
- Modified principles: placeholder template → Code Quality, Comprehensive Testing, UX Consistency, Safe Integration, Maintainable Delivery
- Added sections: Additional Quality Constraints, Development Workflow and Review
- Removed sections: placeholder guidance comments only
- Templates requiring updates: .specify/templates/plan-template.md ✅ verified, .specify/templates/spec-template.md ✅ verified, .specify/templates/tasks-template.md ✅ verified
- Follow-up TODOs: none
-->

# LESS Constitution

## Core Principles

### I. Code Quality is Non-Negotiable
All code MUST be clean, readable and maintainable. Code reviews MUST enforce consistent style, meaningful naming, minimal duplication, and explicit intent. Technical debt MAY only be accepted with a documented mitigation plan.

Rationale: High code quality reduces bugs, accelerates future work, and preserves team confidence in every change.

### II. Comprehensive Testing is Mandatory
Every feature MUST include automated tests before merge. Unit tests MUST cover boundaries and failure modes, while integration tests MUST validate cross-component behavior for user-facing flows. Regression protection MUST be preserved by automated test suites and cycle-gating PRs.

Rationale: Testing standards protect product quality, prevent regressions, and make delivery predictable.

### III. User Experience Consistency is Required
User-facing behavior MUST be consistent across screens, flows, and error handling. Design decisions MUST prioritize clarity, accessibility, and predictable feedback. UX changes MUST be validated against existing patterns or approved design guidance.

Rationale: Consistent UX reduces user friction, improves trust, and prevents subtle failures caused by inconsistent interactions.

### IV. Safe Integration and Release Discipline
Changes MUST be integrated incrementally with clear rollback or remediation paths. Feature branches MUST stay current with mainline changes, and releases MUST satisfy automated validation before deployment. Hotfixes MUST be minimized and justified.

Rationale: Integration discipline preserves system stability and makes deployments reliable.

### V. Maintainable Delivery and Continuous Improvement
Work MUST include documentation updates, meaningful commit messages, and explicit acceptance criteria. Post-merge reviews MUST capture lessons learned and identify opportunities to improve code quality, tests, and UX consistency.

Rationale: Maintainable delivery ensures the project stays sustainable and improves over time.

## Additional Quality Constraints

- All work MUST comply with the repository's chosen language and style guidelines.
- Changes MUST include measurable acceptance criteria and documented test coverage expectations.
- Cross-cutting concerns such as accessibility, localization, and performance MUST be considered for any user-facing feature.
- No implementation MAY be merged without at least one approving review from a designated team member.

## Development Workflow and Review

- Feature work MUST begin with a clear spec or plan that references these principles.
- Every PR MUST include a summary of how it satisfies code quality, testing, and UX consistency principles.
- Reviews MUST verify that tests exist, run successfully, and cover the new behavior.
- Compliance reviews MUST occur at major milestones and before release gate decisions.

## Governance

This constitution is authoritative for project practices. All design, development, and review activity MUST align with these principles. Amendments require a documented proposal, an explicit rationale, and approval from the project maintainers or governance group.

Version changes follow semantic versioning:
- MAJOR for backward-incompatible governance or principle redefinitions.
- MINOR for new principles or materially expanded mandatory guidance.
- PATCH for wording clarifications, typo fixes, and non-semantic refinements.

Compliance review expectations:
- Every PR MUST reference the constitution where applicable.
- Milestone reviews MUST explicitly confirm conformity with code quality, testing, and UX consistency.
- If a violation is accepted, it MUST be documented and revisited in a follow-up improvement task.

**Version**: 1.0.0 | **Ratified**: 2026-04-07 | **Last Amended**: 2026-04-07
