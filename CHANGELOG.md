# Changelog

All notable changes to CloudModX are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI: backend lint and tests, frontend build, Terraform format and validation, a Docker Compose smoke test of the full stack, and a secret scan of the whole git history.
- `backend/requirements-dev.txt` with the test client (`httpx2`) and linter (`ruff`) needed to run the test suite.
- Contributing guide, security policy, issue and pull request templates, and Dependabot configuration.

### Changed
- Pydantic schemas use `model_config = ConfigDict(...)` instead of the deprecated `class Config`.
- Removed unused imports across the backend.

### Fixed
- README now gives the correct frontend dev server address (`http://localhost:3000`).
- README test instructions now install the development requirements, so the tests run on a clean machine.

## 2026-10-16

### Added
- MIT License.
- `artifact_bucket_force_destroy` Terraform variable so `terraform destroy` can remove a non-empty artifact bucket.
- Regression test for rolling back with the default environment.
- README: step-by-step application deployment on EC2, configuration reference and accurate teardown instructions.

### Fixed
- Deploy and rollback now use the same default environment, so `POST /api/v1/modules/{id}/rollback` works after a deploy that does not specify one.
- The module rollback endpoint also reads `environment` from a JSON body, as sent by the web UI.
- Removed a hardcoded S3 bucket name; artifacts are stored locally unless `ARTIFACT_BUCKET_NAME` is set.
- SQL statement logging is off by default (`SQL_ECHO=true` to enable).
- Corrected setup documentation (Terraform version, lifecycle stages, environment files) and brought the Terraform README up to date.

## 2026-10-15

### Fixed
- Sanitized Terraform variables (no default database password), fixed the Docker Compose database connection, and hardened production configuration validation.

## [0.1.0] - 2026-10-08

### Added
- Initial release of the CloudModX Internal Developer Platform:
  - module lifecycle management (draft, review, approved, active, archived);
  - module versions with artifact uploads to Amazon S3;
  - deployment tracking with failure diagnostics and one-click rollback;
  - audit logging of platform actions;
  - React dashboard with release pipeline visualization and documentation hub;
  - FastAPI backend with PostgreSQL and Alembic migrations;
  - Terraform for VPC, EC2, RDS PostgreSQL, S3 and CloudWatch on AWS;
  - Docker Compose stack for local development.
