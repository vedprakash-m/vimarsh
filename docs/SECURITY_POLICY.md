# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Vimarsh, please help us maintain a secure environment by reporting it responsibly.

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. Send a detailed report to: `security@vimarsh.vedprakash.net`
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 7 days
- **Regular Updates**: Every 7 days until resolution
- **Resolution Timeline**: Critical issues within 30 days, others within 90 days

### Security Best Practices

This project follows these security practices:

- ✅ **Secrets Management**: All sensitive data stored in Azure Key Vault
- ✅ **Pre-push Hooks**: Automated secret scanning before commits
- ✅ **Dependency Scanning**: Regular vulnerability checks
- ✅ **Secure Defaults**: No hardcoded credentials or fallbacks
- ✅ **Input Validation**: Comprehensive sanitization and validation
- ✅ **Authentication**: Azure Entra ID integration with role-based access

### Scope

This security policy covers:
- The main Vimarsh application
- Backend Azure Functions
- Frontend React application
- Infrastructure as Code (Bicep templates)
- CI/CD pipelines

### Bug Bounty

While we don't currently offer monetary rewards, we will:
- Credit you in our security acknowledgments (with your permission)
- Provide a detailed response about the fix
- Consider you for beta testing of new security features

Thank you for helping keep Vimarsh secure! 🙏
