# Spiral Charter (`SP-001`)

- **Spiral ID**: SP-001
- **Project / Product Name**: PulseMetrics SaaS
- **Primary Surface**: Web App / SaaS
- **Lifecycle Mode**: greenfield
- **Rigor Tier**: standard
- **Status**: ACTIVE
- **Updated (UTC)**: 2026-11-21T12:00:00Z
- **Owner**: Lead Architect
- **Spiral Exit Verdict**: PASS

## 1. Objectives, Scope & Explicit Non-Goals

- **Primary Objective**: Launch developer analytics workspace with p95 API latency <= 200 ms and WCAG 2.1 AA contrast compliance.
- **Target Vertical Slice(s)**:
  - Slice 1: Tenant-isolated ingestion -> PostgreSQL daily rollup -> Server-rendered analytics dashboard.
- **Non-Goals / Out of Scope (Anti-Goals)**:
  - Multi-region active-active sharding and custom query DSL deferred to later Spirals.

## 2. Constraints & Operating Mode

- **Spiral Budget**: Timebox 2 weeks, max 1 database engine, max 0 external client state managers.
- **Tech Stack & Platform Envelope**: Next.js App Router, PostgreSQL 16 with RLS, Python 3 stdlib tooling.

## 3. Alternatives & Simplest High-Craft Option

- **Linked Simplicity Record**: `simplicity-interrogation-record.md`
- **Selection Rationale**: Option A (Simplest High-Craft modular monolith + PostgreSQL 16 materialized views) delivers equal p95 query speed with 10x lower ops surface than Kafka + ClickHouse.

## 4. Cross-Quadrant Gate Ledger & Q4 Spiral Exit

- **Linked Artifacts**:
  - Simplicity Record: [Simplicity Interrogation Record](simplicity-interrogation-record.md)
  - Risk & Spike Register: [Risk & Spike Register](risk-spike-register.md)
  - Phase 3A Foundation Gate: [System Foundation Gate](system-foundation-gate.md)
- **Spiral Exit Verdict**: PASS
