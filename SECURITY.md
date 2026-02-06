# Security

## Vulnerability Patches

### SQLite JDBC Remote Code Execution (Patched)
- **CVE**: Remote code execution vulnerability when JDBC URL is attacker controlled
- **Affected Versions**: >= 3.6.14.1, < 3.41.2.2
- **Patched Version**: 3.41.2.2 (currently in use)
- **Status**: ✅ PATCHED

## Security Features

### Authentication & Authorization
- **Password Storage**: BCrypt hashing with automatic salt generation
- **Password Handling**: Sensitive data cleared from memory after use
- **Session Management**: Thread-safe session handling with synchronized access
- **Role-Based Access**: Admin and User roles with appropriate permissions

### Data Protection
- **SQL Injection Prevention**: All queries use prepared statements with parameter binding
- **Input Validation**: User input validated before processing
- **Database Security**: Foreign key constraints and unique constraints enforced

### Code Security
- **Static Analysis**: CodeQL security scanning with zero alerts
- **Code Review**: Security-focused code review completed
- **Thread Safety**: Volatile and synchronized access for shared resources

## Security Best Practices

### For Administrators
1. **Change Default Password**: Immediately change the default admin password after installation
2. **User Management**: Regularly review user accounts and deactivate unused accounts
3. **Database Backup**: Keep regular backups of the database file in a secure location
4. **Access Control**: Limit physical access to the computer running the application
5. **Updates**: Keep Java runtime and dependencies up to date

### For Developers
1. **Dependency Updates**: Regularly check for security updates to dependencies
2. **Code Review**: Review all code changes for security implications
3. **Testing**: Run security tests before deploying updates
4. **Documentation**: Keep security documentation up to date

## Reporting Security Issues

If you discover a security vulnerability, please report it by:
1. Creating a GitHub Security Advisory in the repository
2. Do NOT open a public issue for security vulnerabilities
3. Provide detailed information about the vulnerability
4. Allow time for the maintainers to address the issue before public disclosure

## Security Checklist for Deployment

- [ ] Changed default admin password
- [ ] Reviewed and configured user accounts
- [ ] Database file has appropriate file system permissions
- [ ] Application runs with minimal system privileges
- [ ] Regular backup schedule established
- [ ] Java runtime is up to date
- [ ] All dependencies are at patched versions
- [ ] CodeQL security scan passed
- [ ] Application deployed on trusted hardware

## Known Limitations

1. **Single Database Connection**: The application uses a single database connection, suitable for desktop applications with limited concurrent access
2. **Local Storage**: Database is stored locally without encryption at rest
3. **Network**: Application is not designed for remote access

## Security Updates Log

| Date | Version | Description |
|------|---------|-------------|
| 2026-02-06 | 1.0 | Initial release with security features |
| 2026-02-06 | 1.0.1 | Updated sqlite-jdbc to 3.41.2.2 to patch RCE vulnerability |
