# EnergyHub Development Principles

> Build a platform that is easy to understand, easy to maintain and enjoyable to extend.

---

# Product Before Code

Code is not the product.

The product is the experience homeowners receive.

Every technical decision should improve the product rather than simply adding functionality.

---

# Documentation First

Every significant feature starts with documentation.

Ideas become design.

Design becomes architecture.

Architecture becomes implementation.

Code is the final step—not the first.

---

# Development Workflow

Every feature follows the same process:

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

Testing

↓

Git Commit

Skipping steps usually creates technical debt.

---

# GitHub Is the Single Source of Truth

The repository represents the current state of EnergyHub.

Documentation, architecture and production code belong in Git.

Temporary experiments do not.

---

# Production Quality Repository

The repository should contain:

* Production-ready code
* Well-documented examples
* Stable configurations
* Documentation

Experimental prototypes should remain outside the main repository until they become useful.

---

# Small, Understandable Commits

Each commit should represent one logical change.

Commit messages should explain intent rather than implementation details.

Good example:

```
feat: add inverter mode switching
```

Poor example:

```
fixed stuff
```

---

# Modular Architecture

Each subsystem should have a clear responsibility.

Examples:

* Inverter
* Battery
* Forecast
* Dashboard
* Notifications
* Automation Engine

Modules communicate through well-defined interfaces.

---

# Hardware Independence

Business logic should never depend directly on a specific hardware vendor.

Instead of:

```
POP02
```

The application should use:

```
set_mode("panic")
```

Vendor-specific commands belong inside hardware adapters.

---

# Explainability

Complex code should be easy to understand.

Simple code is usually better than clever code.

Future maintainability is more important than short-term optimization.

---

# Decision Logging

Every important architectural decision should be documented.

Future developers—including ourselves—should understand why decisions were made.

---

# Technical Debt

Technical debt should never accumulate silently.

Known compromises belong in the backlog.

Temporary solutions should be clearly marked.

---

# Testing Philosophy

Read operations are verified before write operations.

Automation is verified before being enabled.

Potentially dangerous operations should always be reversible.

---

# Continuous Refactoring

Improvement never stops.

Whenever code becomes simpler, more readable or more maintainable without changing behavior, refactoring is encouraged.

---

# Long-Term Thinking

Every design decision should answer one question:

Will this still make sense in five years?

If not, reconsider the design.

---

# Definition of Done

A feature is complete only when:

* It works reliably.
* It is documented.
* It follows the architecture.
* It is understandable.
* It has been committed to Git.
* It improves the homeowner's experience.

Only then is the feature considered finished.
