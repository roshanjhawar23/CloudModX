# Security Policy

## Supported versions

CloudModX is maintained on the `main` branch. Security fixes are applied there only.

## Reporting a vulnerability

**Please do not report security problems in public issues, discussions or pull requests.**

Report them privately through GitHub:

1. Go to the repository's **Security** tab.
2. Click **Report a vulnerability**.
3. Describe the problem, the affected files or endpoints, and steps to reproduce it.

You can expect an acknowledgement within 7 days. If the report is confirmed, a fix will be prepared and you will be credited in the release notes unless you prefer otherwise.

## Scope and known limitations

CloudModX is a portfolio and demonstration project. Please keep these known limitations in mind:

- **No authentication or authorization.** The API does not implement user login. Do not deploy it publicly with real or sensitive data.
- **HTTP only.** The default EC2 deployment serves plain HTTP on port 80. Add TLS (for example an ALB with ACM, or a reverse proxy with Let's Encrypt) before any real use.
- **Demo-oriented AWS defaults.** RDS automated backups are off and deletion protection is disabled to keep costs low (see `infrastructure/terraform/variables.tf`).

Reports about these documented limitations are still welcome if you find a concrete way they can be exploited beyond what is described here.

## Handling secrets

- Never commit `.env`, `terraform.tfvars`, Terraform state files or AWS credentials. They are gitignored.
- CI runs a secret scan ([gitleaks](https://github.com/gitleaks/gitleaks)) over the full git history on every push and pull request.
- The EC2 instance uses an IAM role for S3 access; no static AWS keys are needed or stored.
