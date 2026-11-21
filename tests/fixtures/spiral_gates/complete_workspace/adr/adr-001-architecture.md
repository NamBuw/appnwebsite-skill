# ADR-001: Modular Monolith with PostgreSQL Rollups

- **Status**: Accepted
- **Depends On**: None
- **Context**: PulseMetrics processes <= 2,000 events/min at launch with 2 engineers.
- **Decision**: Use a single Next.js + PostgreSQL 16 modular monolith with SQL materialized views instead of Kafka + ClickHouse + microservices.
- **Consequences**: Zero distributed ops overhead; horizontal escalation deferred until sustained ingestion > 10,000 events/sec.
