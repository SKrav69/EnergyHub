# EnergyHub Decision Log

> Important architectural and product decisions are documented here.

This document explains why significant decisions were made.

Future contributors—including ourselves—should be able to understand the reasoning behind the platform.

---

# 2026-06-27

## Repository Philosophy

Decision

GitHub becomes the single source of truth.

Reason

Documentation, architecture and production code should always remain synchronized.

---

## Documentation Before Code

Decision

Every significant feature starts with discussion and documentation before implementation.

Reason

Good architecture prevents technical debt and improves long-term maintainability.

---

## Human-Centric Design

Decision

EnergyHub optimizes for people rather than kilowatt-hours.

Reason

The goal is not maximum efficiency.

The goal is maximum comfort, simplicity and peace of mind.

---

## Autonomous Home

Decision

EnergyHub is positioned as the Operating System for Autonomous Homes.

Reason

The project extends beyond energy management.

Its purpose is to coordinate the entire smart home ecosystem.

---

## Home Assistant

Decision

Home Assistant is infrastructure—not the product.

Reason

EnergyHub should remain independent from the underlying home automation platform.

Future versions may support additional backends.

---

## Progressive Automation

Decision

Automation should be introduced gradually.

Reason

Users build trust over time.

The homeowner always decides how much control to delegate.

---

## Calm Technology

Decision

Silence is considered a feature.

Reason

Technology should reduce mental effort instead of constantly demanding attention.

---

## Modular Architecture

Decision

Business logic must remain independent from hardware.

Reason

Hardware changes over time.

EnergyHub should continue working regardless of the specific inverter, battery or communication protocol.

---

## BMS Integration

Decision

Postpone Bluetooth BMS integration.

Reason

Current inverter telemetry already provides sufficient information for the Foundation stage.

The architecture already supports adding BMS support later.

---

## Repository Content

Decision

Only production-quality code belongs in the main repository.

Reason

Experimental research should not increase repository complexity.

Useful experiments become documented examples before entering the repository.

---

## Knowledge Base

Decision

Documentation is treated as part of the product.

Reason

Architecture, philosophy and engineering decisions should survive multiple generations of code.

The Knowledge Base is maintained with the same discipline as the source code.
