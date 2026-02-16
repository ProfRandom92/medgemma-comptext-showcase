# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in MedGemma × CompText, please report it responsibly to the security team.

### How to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please:

1. Email the security contact at: `medgemma-security@anthropic.com` (or maintainer)
2. Include:
   - Description of the vulnerability
   - Steps to reproduce (if applicable)
   - Potential impact
   - Suggested fix (if you have one)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Release**: Target within 2 weeks for critical issues
- **Disclosure**: Coordinated 30-day disclosure after patch release

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**: Regularly run `pip install --upgrade -r requirements.txt`
2. **Use HTTPS**: Always use HTTPS when transmitting patient data
3. **Environment Variables**: Never commit `.env` files with secrets
4. **Access Control**: Restrict access to deployed instances
5. **Audit Logs**: Enable and monitor audit logging in production

### For Developers

1. **Input Validation**: All user input must be validated before processing
2. **Secrets Management**: Never hardcode API keys, credentials, or tokens
3. **Dependency Scanning**: Run `pip audit` before committing
4. **Code Review**: All code changes must be reviewed before merging
5. **Testing**: Include security tests in test suite

## Security Updates

### Supported Versions

| Version | Status | Until |
|---------|--------|-------|
| 1.0.x   | Supported | Feb 25, 2026 |

Critical security updates will be issued for the current release version.

### Receiving Updates

Subscribe to security advisories:
- Watch the [GitHub Security Advisories](https://github.com/ProfRandom92/medgemma-comptext-showcase/security/advisories)
- Enable email notifications for releases

## Known Security Considerations

### HIPAA/GDPR Compliance

- Patient data should never be transmitted in plaintext
- Implement field-level encryption for sensitive data at rest
- Enable audit logging for all data access
- Use edge-native processing to minimize cloud transmission

### Data Privacy

- This project includes compression techniques that preserve clinical context while reducing data exposure
- Edge-native deployment means no raw patient data is sent to cloud services
- Always anonymize or pseudonymize patient data before analysis

## Security Contact

For security issues, please contact: `security@example.com`

## Acknowledgments

We thank the security researchers who responsibly disclose vulnerabilities to help us keep MedGemma safe.
