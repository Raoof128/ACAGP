# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

The ACAGP team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

To report a security vulnerability, please email:

**security@acagp-project.org**

Include the following information:

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Regular Updates**: Every 5-7 days until resolution
- **Fix Timeline**: Critical issues within 7 days, high severity within 14 days
- **Public Disclosure**: Coordinated with reporter after fix is deployed

### Response Process

1. **Receipt Acknowledgment**: We confirm receipt of your vulnerability report
2. **Validation**: We reproduce and validate the vulnerability
3. **Fix Development**: We develop and test a fix
4. **Coordinated Disclosure**: We work with you on disclosure timeline
5. **Release**: We release the security patch
6. **Public Disclosure**: We publish security advisory

## Security Best Practices

### For Developers

**Code Security:**
- Never commit secrets, API keys, or credentials to the repository
- Use environment variables for all sensitive configuration
- Validate and sanitize all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization
- Follow principle of least privilege

**Dependencies:**
- Regularly update dependencies (`pip-audit`, `npm audit`)
- Review security advisories for dependencies
- Use pinned versions in production
- Scan container images for vulnerabilities

**Testing:**
- Include security tests in test suites
- Test authentication and authorization logic
- Validate input sanitization
- Check for common vulnerabilities (OWASP Top 10)

### For Deployment

**Infrastructure:**
- Use HTTPS/TLS for all communications
- Enable database encryption at rest
- Implement network segmentation
- Use secrets management (AWS Secrets Manager, Azure Key Vault)
- Enable audit logging for all compliance-related actions
- Implement rate limiting and DDoS protection

**Access Control:**
- Use multi-factor authentication (MFA)
- Implement role-based access control (RBAC)
- Regular access reviews
- Rotate credentials regularly
- Use service accounts with minimal permissions

**Monitoring:**
- Enable security monitoring (GuardDuty, Defender for Cloud)
- Set up alerts for suspicious activities
- Log security events
- Regular security audits

## Known Security Considerations

### Authentication & Authorization

Current implementation uses JWT tokens for API authentication. For production deployments:

- Rotate JWT secrets regularly
- Implement token expiration
- Use refresh tokens
- Implement account lockout after failed attempts
- Consider OAuth 2.0 / OpenID Connect for enterprise deployments

### Data Protection

**Sensitive Data:**
- Compliance assessment results
- Organization configurations
- User credentials
- Evidence artifacts

**Protection Measures:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Access logging
- Data retention policies

### Compliance Considerations

As a compliance platform, ACAGP handles sensitive regulatory data:

- **APRA CPS 234**: Information security controls
- **OAIC Privacy Act**: Personal information handling
- **ISO 27001**: Information security management

Ensure your deployment meets applicable regulatory requirements for:
- Data residency (Australian data sovereignty)
- Audit trails (7-year retention for APRA)
- Access controls
- Incident response

## Security Updates

Subscribe to security updates:

- **GitHub Security Advisories**: Watch this repository
- **Mailing List**: security-announce@acagp-project.org
- **RSS Feed**: GitHub releases feed

## Vulnerability Disclosure Policy

### Timeline

- **0 days**: Vulnerability reported to security@acagp-project.org
- **2 days**: Acknowledgment sent to reporter
- **7 days**: Initial assessment and severity classification
- **30 days**: Fix developed and tested
- **45 days**: Patch released (or coordinated with reporter)
- **60 days**: Public disclosure (if fix is available)

### Severity Classification

| Severity | CVSS Score | Response Time | Example |
|----------|------------|---------------|---------|
| Critical | 9.0 - 10.0 | 7 days | Authentication bypass |
| High | 7.0 - 8.9 | 14 days | SQL injection |
| Medium | 4.0 - 6.9 | 30 days | XSS vulnerability |
| Low | 0.1 - 3.9 | 60 days | Information disclosure |

### Bug Bounty

Currently, we do not offer a paid bug bounty program. However, we recognize security researchers in:

- Security advisories
- Hall of Fame (README.md)
- Release notes

## Security Checklist for Production Deployment

- [ ] Change all default passwords and secrets
- [ ] Enable HTTPS/TLS with valid certificates
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Enable database encryption at rest
- [ ] Set up automated backups
- [ ] Enable security monitoring (GuardDuty, Defender)
- [ ] Configure log aggregation and retention
- [ ] Implement rate limiting
- [ ] Set up intrusion detection
- [ ] Enable MFA for all admin accounts
- [ ] Review and restrict IAM permissions
- [ ] Enable audit logging
- [ ] Set up security alerts
- [ ] Perform security scan (SAST, DAST)
- [ ] Review third-party dependencies
- [ ] Document incident response plan
- [ ] Train team on security procedures

## Security Contacts

- **General Security Issues**: security@acagp-project.org
- **Code of Conduct**: conduct@acagp-project.org
- **Project Maintainers**: maintainers@acagp-project.org

## Responsible Disclosure Recognition

We would like to thank the following security researchers who have responsibly disclosed vulnerabilities:

<!-- Hall of Fame will be listed here -->

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)
- [APRA CPS 234](https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf)
- [ASD Information Security Manual](https://www.cyber.gov.au/resources-business-and-government/essential-cyber-security/ism)

---

**Last Updated**: 2025-01-16
**Version**: 1.0.0
