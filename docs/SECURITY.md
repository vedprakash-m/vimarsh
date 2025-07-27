# Security & Secret Management Guidelines

## 🚨 Recent Security Incident

**Date**: July 26, 2025  
**Issue**: Azure AD Client ID exposed in commit `f94f6e8`  
**Exposed Value**: `e4bd74b8-****-****-****-************` (masked for security)  
**Status**: ✅ **RESOLVED** - Comprehensive security system deployed

### Immediate Actions Taken:
1. ✅ Removed `frontend/.env.production` from git tracking
2. ✅ Updated `.gitignore` to prevent future env file commits
3. ✅ Implemented comprehensive pre-push hook for secret detection
4. ✅ Created `.env.production.template` for safe deployment practices
5. ✅ **COMPLETED**: Security system deployed to prevent future incidents
6. 🔄 **NEXT**: Rotate exposed Azure AD Client ID in Azure Portal (manual action required)

## 🔒 Git Hooks Security System

### Pre-Push Hook Features:
- **Secret Pattern Detection**: 15+ types of API keys, tokens, and credentials
- **Sensitive File Detection**: Environment files, certificates, private keys
- **Comprehensive Scanning**: All files in push commits
- **Smart Exclusions**: Ignores binary files, node_modules, build artifacts
- **Emergency Override**: `SKIP_SECRET_SCAN=1 git push` for critical situations

### Detected Secret Types:
- Google API Keys (`AIzaSy...`)
- OpenAI API Keys (`sk-...`)
- GitHub Tokens (`gho_...`, `ghs_...`, `ghr_...`)
- GitLab Tokens (`glpat-...`)
- Slack Tokens (`xoxb-...`, `xoxp-...`)
- Azure Keys & Connection Strings
- AWS Access Keys (`AKIA...`)
- Generic passwords, secrets, tokens in code
- Environment variable patterns

### Sensitive Files Blocked:
- `.env*` files (except `.env.example`, `.env.development`)
- Certificate files (`*.pem`, `*.key`, `*.p12`, `*.pfx`)
- SSH keys (`id_rsa*`, `*.ppk`)
- Credential files (`credentials.json`, `service-account*.json`)
- Azure publish settings (`*.publishsettings`)

## 🛡️ Security Best Practices

### 1. Environment Variables
```bash
# ✅ GOOD - Use templates with placeholders
REACT_APP_CLIENT_ID=<REPLACE_WITH_AZURE_AD_CLIENT_ID>

# ❌ BAD - Real credentials in code
REACT_APP_CLIENT_ID=xxxxxxxx-****-****-****-************
```

### 2. Production Configuration
- Use `.env.production.template` with placeholders
- Inject real values during deployment via CI/CD
- Store secrets in Azure Key Vault
- Use Azure App Service environment variable configuration

### 3. Development Workflow
```bash
# Before making changes
git pull origin main

# After making changes
git add .
git commit -m "Your commit message"

# The pre-push hook will scan for secrets automatically
git push origin main
```

### 4. Emergency Procedures
If secrets are accidentally pushed:
1. **Immediately rotate** the exposed credentials
2. **Remove from git history** using `git filter-branch` or BFG Repo-Cleaner
3. **Update all deployment systems** with new credentials
4. **Review access logs** for potential unauthorized usage

## 🔧 Testing Secret Detection

Run the test script to verify the hook works:
```bash
# Run test (creates files with fake secrets)
bash test-secret-detection.sh

# Try to push (should be blocked)
git push origin main

# Clean up test files
git reset --soft HEAD~1
git reset HEAD test-secrets/
rm -rf test-secrets/
git clean -fd
```

## 📋 Deployment Checklist

### Before Deployment:
- [ ] All secrets removed from code
- [ ] Environment templates created with placeholders
- [ ] Production secrets stored in Azure Key Vault
- [ ] CI/CD pipeline configured for secret injection
- [ ] Pre-push hook tested and working

### During Deployment:
- [ ] Copy `.env.production.template` to `.env.production`
- [ ] Replace all placeholders with actual values
- [ ] Verify no secrets in git history
- [ ] Test application with injected credentials

### After Deployment:
- [ ] Verify secret detection hook on team machines
- [ ] Document any new secret patterns to detect
- [ ] Regular security audits of commit history

## ⚡ Quick Commands

```bash
# Test secret detection
bash test-secret-detection.sh

# Skip secret scan (emergency only)
SKIP_SECRET_SCAN=1 git push

# Check what files are ignored
git status --ignored

# Manually scan for secrets
grep -r "AIzaSy\|sk-\|gho_" . --exclude-dir=node_modules

# View hook logs
git config --get core.hooksPath
```

## 🆘 Emergency Contacts

**Security Issues**: ved.mishra@email.com  
**Azure Admin**: vedprakash.m@outlook.com  
**Repository**: https://github.com/vedprakash-m/vimarsh

---

**Remember**: Security is everyone's responsibility! 💪
