# EnergyHub Development Principles

> Build EnergyHub so it is understandable, reliable, safe to change, and enjoyable to extend.

---

# Product Before Code

Code is not the product.

The product is the experience homeowners receive.

Every technical decision should improve reliability, comfort, understanding, or maintainability rather than simply adding functionality.

---

# Documentation Before Implementation

Significant features should follow this path:

```text
Idea
    ↓
Discussion
    ↓
Decision
    ↓
Documentation
    ↓
Implementation
    ↓
Real-System Testing
    ↓
Documentation Update
    ↓
Git Commit
```

Documentation is part of development, not work performed after development.

Small fixes do not require unnecessary design documents.

The amount of documentation should match the importance and complexity of the change.

---

# Git Is the Project Source of Truth

The repository represents the reviewable state of EnergyHub.

It contains:

- production code;
- architecture documentation;
- development documentation;
- selected current Home Assistant configuration;
- hardware knowledge;
- development tools.

Runtime state and temporary experiments do not automatically belong in Git.

---

# Home Assistant and Git Have Different Roles

EnergyHub application code flows from Git to Home Assistant:

```text
Git Repository
        ↓
deploy-to-ha.ps1
        ↓
sync-to-ha.ps1
        ↓
Home Assistant Add-on
        ↓
Manual Restart
        ↓
Test
```

Selected Home Assistant configuration flows in the opposite direction:

```text
Home Assistant
        ↓
sync-from-ha.ps1
        ↓
homeassistant/live/
        ↓
Review Changes
        ↓
Git Commit
```

These workflows should remain separate and explicit.

The complete Home Assistant `.storage` directory must never be committed.

---

# Production Quality Repository

The repository should contain:

- production-ready code;
- selected current configuration;
- useful development tools;
- verified hardware knowledge;
- maintained documentation.

Temporary experiments should remain outside production paths until they become useful and understood.

---

# Small, Understandable Commits

Each commit should represent one logical change or coherent milestone.

Commit messages should explain intent.

Good:

```text
feat: add mode-aware grid import estimation
```

Good:

```text
docs: document recovery strategy
```

Poor:

```text
fixed stuff
```

Before committing:

```text
Deploy or Sync
        ↓
Test
        ↓
Inspect Logs
        ↓
Review Git Diff
        ↓
Commit
```

---

# Clear Responsibility Boundaries

Each subsystem should have one clear responsibility.

Current examples:

- Telemetry Service;
- Grid History;
- Grid Confidence;
- Daily Summary;
- Health Services;
- Hybrid Decision Engine;
- Panic Decision Engine;
- Inverter Controller;
- Operating Mode;
- Grid Import;
- MQTT Integration.

A subsystem should not silently take ownership of unrelated behavior.

---

# Keep `main.py` as an Orchestrator

`main.py` may initialize, connect, and coordinate services.

It should not become the permanent home of:

- decision formulas;
- protocol mappings;
- historical calculations;
- recovery policy;
- MQTT Discovery definitions.

Logic that develops its own state, rules, persistence, or tests should normally move into a focused service.

---

# Separate Decisions from Execution

Decision services answer:

```text
What should EnergyHub do?
```

The Inverter Controller answers:

```text
How should the physical inverter do it?
```

Example:

```text
Hybrid Decision
        ↓
Request Hybrid
        ↓
Inverter Controller
        ↓
PowMr Commands
        ↓
Verification
```

Decision services should not directly send vendor-specific commands.

---

# Hardware Independence Is a Direction

EnergyHub 1.0 currently supports one real installation:

- PowMr 10.2M;
- PI30MAX;
- JK BMS;
- Home Assistant.

We should avoid unnecessary vendor coupling in high-level logic.

However, EnergyHub should not pretend a complete multi-vendor abstraction layer already exists.

Current priority:

```text
Reliable Real Installation
        ↓
Clear Responsibility Boundaries
        ↓
Reusable Services
        ↓
Real Multi-Vendor Requirements
        ↓
Validated Abstractions
```

Do not introduce abstraction merely because it may be useful someday.

---

# Explainability

Important behavior should be understandable from:

- state;
- reason;
- logs;
- documentation.

EnergyHub should answer:

```text
What happened?
Why did it happen?
What did EnergyHub do?
Did it succeed?
Is user action required?
```

Simple, explicit code is preferred over clever code.

---

# Decision Logging

Important architectural decisions should be documented in the Decision Log.

The purpose is not to record every coding choice.

The purpose is to preserve decisions that future development may otherwise accidentally reverse.

---

# Technical Debt Must Be Visible

Technical debt should not accumulate silently.

Known compromises belong in:

- Backlog;
- Project State;
- code comments when technically appropriate.

Completed work should not remain indefinitely in the Backlog as if it were still planned.

Temporary solutions should have a clear reason and future direction.

---

# Test on the Real System

EnergyHub controls physical hardware.

Simulation and isolated testing are useful, but they are not sufficient.

The normal development loop is:

```text
Implement
    ↓
Deploy
    ↓
Restart Add-on
    ↓
Inspect Startup
    ↓
Inspect Logs
    ↓
Verify Home Assistant Entities
    ↓
Verify Physical Behavior
```

Testing should confirm both software state and real inverter behavior.

---

# Read Before Write

When working with physical hardware:

```text
Understand Read Commands
        ↓
Verify Current State
        ↓
Test Write Command
        ↓
Verify ACK
        ↓
Read Back State
        ↓
Confirm Physical Behavior
```

Write operations should be introduced cautiously.

---

# Verify Physical State

A successful command does not always prove the inverter reached the intended state.

Where read-back is available:

```text
Command
    ↓
ACK
    ↓
Read Back
    ↓
Verify
```

EnergyHub should not claim a confirmed Operating Mode before appropriate verification.

---

# Safe and Bounded Recovery

Automatic recovery is allowed only when the action is:

- understood;
- safe;
- bounded;
- verifiable;
- appropriate for the detected failure.

Infinite retry loops are prohibited.

EnergyHub must never automatically restart the inverter.

When safe automatic recovery is not possible:

```text
Detect
    ↓
Report
    ↓
Require Human Attention
```

Detailed recovery policy belongs in `13-Recovery-Strategy.md`.

---

# Preserve Manual Control

Automation should reduce homeowner decisions without removing meaningful control.

Users should be able to:

- disable Autopilot;
- request supported operating strategies;
- enable or disable Away Mode;
- inspect important reasons and state;
- recover manually when automatic recovery is inappropriate.

---

# Automation Must Respect Ownership

An automation should automatically stop a household load only when that automation previously started it.

Current example:

```text
EnergyHub starts first-floor heat pump
        ↓
Ownership helper becomes ON
        ↓
EnergyHub may later stop it
```

If the user started the load manually, EnergyHub should not assume ownership.

---

# Continuous Refactoring

Refactoring is encouraged when it improves:

- readability;
- responsibility boundaries;
- testability;
- reliability;
- maintainability.

Refactoring should preserve behavior unless behavior change is intentional and documented.

Do not refactor large working subsystems merely to achieve theoretical architectural purity.

---

# Long-Term Thinking

Long-term design matters.

But every design decision should balance:

```text
Current Real Need
+
Reliability
+
Maintainability
+
Future Direction
```

The question is not only:

```text
Will this make sense in five years?
```

It is also:

```text
Does this solve the real problem clearly today?
```

---

# Feature Design Checklist

Before implementation:

- What real problem does this solve?
- Who benefits?
- Does it reduce homeowner decisions or improve understanding?
- Which subsystem owns it?
- Is similar logic already implemented elsewhere?
- What data does it require?
- What happens if the data is missing or stale?
- What happens if the feature fails?
- Is there a safe fallback?
- Is automatic recovery appropriate?
- Is recovery bounded and verifiable?
- Can the decision be explained?
- Does Home Assistant or EnergyHub own the behavior?
- Does documentation need updating?

Before completion:

- Has the code been deployed?
- Has startup behavior been checked?
- Have logs been inspected?
- Have Home Assistant entities been verified?
- Has physical behavior been verified where applicable?
- Have failure cases been considered?
- Has the Git diff been reviewed?
- Has documentation been updated?
- Is completed work removed from the Backlog where appropriate?

---

# Definition of Done

A feature is complete only when:

- it solves the intended problem;
- it works reliably on the real system;
- responsibility ownership is clear;
- important decisions are explainable;
- failure behavior is understood;
- recovery is safe where applicable;
- Home Assistant integration works where applicable;
- documentation reflects the implementation;
- obsolete Backlog items are updated;
- the Git diff has been reviewed;
- the change has been committed.

Only then is the feature considered finished.

---

# Development Principle

EnergyHub development should follow this direction:

```text
Understand the Real Problem
        ↓
Choose the Correct Owner
        ↓
Document the Decision
        ↓
Implement the Smallest Clear Solution
        ↓
Test on the Real System
        ↓
Verify Failure Behavior
        ↓
Update Documentation
        ↓
Review and Commit
```

The goal is not to create the most complex energy-management platform.

The goal is to create a platform that can safely become more capable without becoming difficult to understand.