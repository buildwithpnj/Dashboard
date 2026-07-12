# Platform Security, Auth & Tenancy Isolation

This document outlines the authentication layer, role-based access controls (RBAC), and multi-tenancy isolation models implemented for the **Warborn Multi-Agent Platform Core**.

---

## 1. Authentication Configurations

The security engine is fully config-driven. The following variables are configured under Pydantic Settings (and parsed from your `.env` file):

- `AUTH_ENABLED` (Boolean, Default: `False`): Global flag enabling or disabling request authentication checks.
- `ADMIN_API_KEY` (String, Default: `warborn_admin_secret`): API Key token expected inside the `X-API-KEY` header for administrative tasks.
- `JWT_SECRET_KEY` (String, Default: `super_jwt_secret_key`): Secret signing key used to decode client JWT tokens.
- `DEFAULT_TENANT_ID` (String, Default: `default_tenant`): Scoped tenant ID assigned to callers when auth is disabled.

---

## 2. Multi-Tenant Scoping Filters

To ensure tenant data segregation, all user profile context lookups and conversation tracking histories are strictly partitioned:

- **Entity Database Scoping**: Models (`learner_profiles`, `sessions`, `family_profiles`, `checkin_runs`) include a `tenant_id` column.
- **Dynamic Repository Isolation**: Queries executed by the databases repositories automatically append `tenant_id` assertions (`filter(model_cls.tenant_id == tenant_id)`).
- **Composite Primary Keys**: Persistent user profile records are keyed using composite IDs (e.g. `f"{tenant_id}_{user_id}"`) to prevent primary key conflicts across tenants.

---

## 3. Role-Based Access Controls (RBAC)

FastAPI endpoints are protected by `RoleChecker` dependency injection checks checking for roles in the authenticated `UserPrincipal`:

| Endpoint Route | Required Roles | Header Options | Description |
| :--- | :--- | :--- | :--- |
| `POST /v1/coach/respond` | `admin` \| `user` | Bearer JWT \| `X-API-KEY` | Executes language coaching queries |
| `POST /v1/coach/feedback` | `admin` \| `user` | Bearer JWT \| `X-API-KEY` | Saves corrections feedback entries |
| `POST /v1/coach/lifeos/respond` | `admin` \| `user` | Bearer JWT \| `X-API-KEY` | Evaluates habits and sleep details |
| `POST /v1/coach/family/checkin` | `admin` \| `user` | Bearer JWT \| `X-API-KEY` | Processes elderly wellness updates |
| `GET /v1/admin/metrics` | `admin` | Bearer JWT (role:admin) \| `X-API-KEY` | Retreives admin telemetry data |
