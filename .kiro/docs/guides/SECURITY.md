# Security Policy

## Supported Versions

The following versions of the Agentic SDLC Kit are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| 1.x     | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a security vulnerability, please report it privately.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to report
Please email [truongnat@gmail.com](mailto:truongnat@gmail.com) with a description of the vulnerability. We will acknowledge your email within 48 hours and provide a timeline for a fix.

### What kind of vulnerabilities to report?
- Remote Code Execution (RCE) via prompt injection
- Secrets leakage in logs or artifacts
- Authorization bypass in the dashboard
- Dependency vulnerabilities (if not caught by bots)

## Security Best Practices for Users
- **Sandboxing**: Always use the Docker container mode for executing agent-generated code (`agentic_sdlc/infrastructure/sandbox/`).
- **Secrets**: Never commit `.env` files. Use the `.env.template` as a guide.
- **Review**: Always review the `implementation_plan.md` before approving code execution in the `/orchestrator` workflow.
