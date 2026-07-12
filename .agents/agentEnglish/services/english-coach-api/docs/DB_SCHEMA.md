# Database Schema - Warborn Platform Core

This document outlines the entity-relationship configurations and database table schemas implemented via SQLAlchemy for SQL storage (SQLite local / PostgreSQL production).

---

## 1. Table Definitions

### 1. `product_configs`
Stores stable prompt instructions and token budget constraints per agent product.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(50) | Primary Key | Unique product identifier (e.g. `english_coach`) |
| `name` | String(100) | Not Null | User-facing display name |
| `description` | String(255) | Nullable | Short summary description |
| `is_active` | Boolean | Default `True` | Flags active availability status |
| `prompt_template` | Text | Not Null | System prompt instruction base |
| `max_dynamic_tokens` | Integer | Default `500` | Dynamic context size budget limit |

### 2. `learner_profiles`
Persists user habits, preferences, and profile summaries.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(100) | Primary Key | Unique user/product composite key |
| `user_id` | String(100) | Not Null | Associated User ID |
| `product_id` | String(50) | Not Null | Associated Product ID |
| `summary` | Text | Not Null | Decoupled user background context summary |
| `metadata_json` | Text | Nullable | JSON string storing preferences |

### 3. `sessions`
Tracks individual conversation session groups.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(100) | Primary Key | Session UUID |
| `user_id` | String(100) | Not Null | Associated User ID |
| `product_id` | String(50) | Not Null | Associated Product ID |
| `is_active` | Boolean | Default `True` | Active status indicator |
| `created_at` | DateTime | Default UTC | Creation timestamp |
| `updated_at` | DateTime | Default UTC | Last message update timestamp |

### 4. `messages`
Audit message logs, tracking token spends, costs, and response latencies.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(100) | Primary Key | Message UUID |
| `session_id` | String(100) | Foreign Key | References `sessions.id` |
| `role` | String(20) | Not Null | `system` \| `user` \| `assistant` |
| `content` | Text | Not Null | Text message body content |
| `created_at` | DateTime | Default UTC | Message timestamp |
| `metadata_json` | Text | Nullable | JSON metadata (cost, token, latency) |

### 5. `approved_examples`
Valid correction inputs and reference translations used for few-shot prompt context injections.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(100) | Primary Key | Example ID |
| `product_id` | String(50) | Not Null | Associated Product ID |
| `input_text` | Text | Not Null | Original raw input from user |
| `natural_english` | Text | Not Null | Corrected conversational text |
| `professional_english` | Text | Not Null | Corrected formal business text |
| `tags_json` | Text | Not Null | JSON array list of categories |
| `created_at` | DateTime | Default UTC | Ingestion timestamp |

### 6. `family_profiles`
Escalation and language settings configs for family members checks.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(100) | Primary Key | User/Parent ID |
| `parent_name` | String(100) | Not Null | Parent's name |
| `preferred_language` | String(50) | Default `English` | E.g. `Hindi` \| `English` |
| `escalation_contacts_json` | Text | Not Null | JSON array containing alert contact list |
| `script_stage` | String(50) | Default `start` | Active check-in progress stage |

### 7. `checkin_runs`
Safety log storing wellness check-in results and emergency flags.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | String(100) | Primary Key | Run UUID |
| `user_id` | String(100) | Not Null | Associated User ID |
| `session_id` | String(100) | Not Null | Associated session |
| `status` | String(30) | Default `normal` | `normal` \| `flagged` \| `escalated` |
| `escalated_at` | DateTime | Nullable | Safety escalation trigger timestamp |
| `notes` | Text | Nullable | Safety details and analysis notes |
