# Control Manifest

- **Boundary 1 (`web -> api`)**: Authenticated HTTPS JSON over `/api/v1/*` validated via strict request schemas.
- **Boundary 2 (`api -> postgres`)**: Parameterized SQL queries only; tenant isolation enforced via `SET LOCAL app.org_id` + RLS.
- **Core Invariants**:
  - Zero cross-tenant reads (`org_id` mandatory on all tenant tables).
  - Idempotency key required on all ingestion `POST` endpoints.
