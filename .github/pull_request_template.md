## Summary

<!-- What does this pull request change, and why? Link any related issue, e.g. "Closes #12". -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Infrastructure (Terraform)
- [ ] Refactor / maintenance

## Checklist

- [ ] `ruff check .` and `python -m pytest tests` pass (from `backend/`)
- [ ] `npm run build` passes (from `frontend/`), if the frontend changed
- [ ] `terraform fmt -recursive` and `terraform validate` pass, if infrastructure changed
- [ ] Tests added or updated for changed backend behaviour
- [ ] An Alembic migration is included for database model changes
- [ ] README or `docs/` updated if setup, configuration or API behaviour changed
- [ ] No secrets, `.env` or `terraform.tfvars` files are included
