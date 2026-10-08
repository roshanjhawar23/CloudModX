# Database Schema & Data Models

CloudModX uses PostgreSQL 15 on Amazon RDS managed with SQLAlchemy ORM.

## Schema Overview

### 1. `users`
- `id` (PK, Integer, autoincrement)
- `name` (VARCHAR 100, NOT NULL)
- `email` (VARCHAR 255, UNIQUE, NOT NULL)
- `role` (VARCHAR 50, default 'developer')
- `created_at`, `updated_at` (TIMESTAMP with TZ)

### 2. `modules`
- `id` (PK, Integer, autoincrement)
- `name` (VARCHAR 150, NOT NULL, indexed)
- `description` (TEXT)
- `owner_id` (FK -> users.id, CASCADE)
- `technology` (VARCHAR 100, NOT NULL)
- `architecture` (VARCHAR 100, NOT NULL)
- `environment` (VARCHAR 50, default 'development')
- `status` (VARCHAR 50, default 'draft', indexed)
- `repository_url` (VARCHAR 255)
- `created_at`, `updated_at` (TIMESTAMP with TZ)

### 3. `module_versions`
- `id` (PK, Integer, autoincrement)
- `module_id` (FK -> modules.id, CASCADE)
- `version` (VARCHAR 50, NOT NULL, indexed)
- `release_notes` (TEXT)
- `artifact_id` (FK -> artifacts.id, SET NULL)
- `created_at` (TIMESTAMP with TZ)

### 4. `artifacts`
- `id` (PK, Integer, autoincrement)
- `module_id` (FK -> modules.id, CASCADE)
- `version` (VARCHAR 50, NOT NULL)
- `filename` (VARCHAR 255, NOT NULL)
- `storage_provider` (VARCHAR 50, default 's3')
- `storage_path` (VARCHAR 500, NOT NULL)
- `size_bytes` (BIGINT, default 0)
- `checksum` (VARCHAR 64)
- `created_at` (TIMESTAMP with TZ)

### 5. `deployments`
- `id` (PK, Integer, autoincrement)
- `module_id` (FK -> modules.id, CASCADE)
- `version_id` (FK -> module_versions.id, CASCADE)
- `environment` (VARCHAR 50, default 'dev')
- `status` (VARCHAR 50, default 'queued', indexed)
- `deployed_by` (FK -> users.id, SET NULL)
- `started_at`, `completed_at` (TIMESTAMP with TZ)
- `error_message` (TEXT)
- `created_at` (TIMESTAMP with TZ)

### 6. `audit_logs`
- `id` (PK, Integer, autoincrement)
- `user_id` (FK -> users.id, SET NULL)
- `action` (VARCHAR 100, NOT NULL, indexed)
- `resource_type` (VARCHAR 50, NOT NULL, indexed)
- `resource_id` (VARCHAR 100)
- `details` (TEXT / JSON)
- `created_at` (TIMESTAMP with TZ)
