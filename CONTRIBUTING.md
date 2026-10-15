# Contributing to CloudModX

Thanks for your interest in improving CloudModX. This guide explains how to set up the project, make a change and open a pull request.

## Ways to contribute

- **Report a bug**: open an issue with the *Bug report* template.
- **Suggest a feature**: open an issue with the *Feature request* template.
- **Fix something**: pick an open issue (or open one first for larger changes) and send a pull request.
- **Security problems**: do **not** open a public issue. Follow [SECURITY.md](SECURITY.md).

## Development setup

Follow **Section 4** of the [README](README.md) to run the stack locally, either fully in Docker Compose or with the backend and frontend running on your machine.

Install the backend development tools (test client and linter):

```bash
cd backend
pip install -r requirements-dev.txt
```

## Before you open a pull request

Run the same checks that CI runs. All of them must pass.

```bash
# Backend: lint and tests (from backend/)
ruff check .
python -m pytest tests -v

# Frontend: production build (from frontend/)
npm ci
npm run build

# Terraform, if you changed infrastructure/ (from infrastructure/terraform/)
terraform fmt -recursive
terraform init -backend=false
terraform validate
```

## Guidelines

- **Keep pull requests focused.** One fix or feature per pull request is easier to review.
- **Add or update tests** for backend behaviour you change. Tests live in `backend/tests/` and run against an in-memory SQLite database.
- **Database changes** need an Alembic migration in `backend/alembic/versions/`.
- **Update the docs** (README or `docs/`) when you change setup steps, configuration or API behaviour.
- **Never commit secrets.** `.env`, `terraform.tfvars` and Terraform state files are gitignored, and CI scans every commit for leaked keys.

## Commit messages

Use short, descriptive messages in the imperative mood. Prefixes in the style of [Conventional Commits](https://www.conventionalcommits.org/) are welcome:

```
feat: add environment filter to deployments page
fix: use module environment as rollback default
docs: clarify host-run setup
```

## License

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).
