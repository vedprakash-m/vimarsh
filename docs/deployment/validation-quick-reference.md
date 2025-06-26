# Deployment Validation Quick Reference

## Quick Commands

### Full Deployment Validation
```bash
# Production validation (comprehensive)
./scripts/deployment-validation.sh validate --environment prod --verbose

# Staging validation
./scripts/deployment-validation.sh validate --environment staging

# Dry run (no actual tests)
./scripts/deployment-validation.sh validate --environment staging --dry-run
```

### Quick Health Checks
```bash
# Basic health check
./scripts/deployment-validation.sh health-check --environment prod

# Simple smoke tests (minimal dependencies)
python3 scripts/simple-smoke-test.py --environment prod --verbose
```

### Specific Test Categories
```bash
# Performance tests only
./scripts/deployment-validation.sh performance-test --environment prod

# Security tests only
./scripts/deployment-validation.sh security-test --environment prod

# Infrastructure tests only
./scripts/deployment-validation.sh smoke-test --environment staging
```

### Advanced Smoke Tests (requires aiohttp, PyYAML)
```bash
# Install dependencies
pip install -r scripts/requirements-testing.txt

# Run comprehensive smoke tests
python3 scripts/smoke-test-runner.py --environment prod --verbose

# Generate HTML report
python3 scripts/smoke-test-runner.py --environment staging --output-format html
```

## Test Categories and Coverage

### 1. Infrastructure Tests (5 tests)
- ✅ Azure Functions Health
- ✅ Static Web App Availability  
- ✅ Cosmos DB Connectivity
- ✅ Key Vault Access
- ✅ Application Insights Integration

### 2. Functional Tests (4 tests)
- ✅ Spiritual Guidance API
- ✅ Voice Interface Endpoints
- ✅ Authentication Flow
- ✅ Citation System

### 3. Performance Tests (2 tests)
- ✅ Response Time Performance
- ✅ Concurrent Request Handling

### 4. Security Tests (3 tests)
- ✅ HTTPS Enforcement
- ✅ CORS Headers
- ✅ Security Headers

### 5. Integration Tests (2 tests)
- ✅ End-to-End Workflow
- ✅ Monitoring Integration

### 6. Rollback Tests (1 test)
- ✅ Rollback Procedures

**Total: 17 comprehensive tests**

## Expected Endpoints

### Production URLs
```
Function App: https://vimarsh-functions.azurewebsites.net
Static Web App: https://vimarsh-web.azurestaticapps.net
```

### Staging URLs
```
Function App: https://vimarsh-staging-functions.azurewebsites.net  
Static Web App: https://vimarsh-staging-web.azurestaticapps.net
```

### Test Endpoints
```
GET  /api/health                    - Basic health check
GET  /api/test/cosmos              - Cosmos DB connectivity
GET  /api/test/keyvault            - Key Vault access
GET  /api/test/insights            - Application Insights
POST /api/spiritual-guidance       - Core functionality
GET  /api/voice/capabilities       - Voice interface
GET  /api/auth/config              - Authentication
```

## Success Criteria

### Infrastructure
- All Azure resources deployed and running
- Health endpoints return 200 status
- Database connectivity confirmed
- Key Vault accessible

### Performance
- Response times < 5 seconds
- Concurrent request handling working
- Voice processing < 3 seconds
- No memory leaks or resource exhaustion

### Security
- HTTPS enforcement active
- Security headers present
- CORS properly configured
- Authentication blocking unauthorized access

### Spiritual Content
- Dharmic responses maintained
- Sanskrit pronunciation working
- Citation system functional
- Expert review workflow active

## Troubleshooting

### Common Failures
1. **DNS Resolution Error**: Environment not deployed yet
2. **401/403 Errors**: Authentication configuration issue
3. **500 Errors**: Backend service failure
4. **Timeout Errors**: Performance degradation
5. **CORS Errors**: Frontend-backend integration issue

### Quick Fixes
```bash
# Check Azure resource status
az functionapp show --name vimarsh-functions --resource-group vimarsh-rg

# Check application logs
az functionapp logs tail --name vimarsh-functions --resource-group vimarsh-rg

# Restart function app
az functionapp restart --name vimarsh-functions --resource-group vimarsh-rg
```

## CI/CD Integration

### GitHub Actions Usage
```yaml
- name: Deployment Validation
  run: ./scripts/deployment-validation.sh validate --environment ${{ env.ENVIRONMENT }} --verbose

- name: Smoke Tests  
  run: python3 scripts/simple-smoke-test.py --environment ${{ env.ENVIRONMENT }} --output results.json
```

### Exit Codes
- `0`: All tests passed
- `1`: Some tests failed
- `2`: Configuration error
- `3`: Dependency missing

## Report Locations

```
Validation Reports: docs/deployment/deployment-validation-report-{timestamp}.md
Smoke Test Results: logs/smoke-test-results-{timestamp}.json
Simple Test Output: stdout or specified JSON file
```

## Environment Requirements

### Minimal (simple-smoke-test.py)
- Python 3.x
- requests library

### Full (smoke-test-runner.py)  
- Python 3.x
- aiohttp
- PyYAML
- requests

### Deployment Validation
- Bash shell
- curl
- Azure CLI (for some tests)
- jq (for JSON parsing)

## Support

For issues with deployment validation:

1. Check this quick reference
2. Review the full documentation: `docs/deployment/production-deployment-validation.md`
3. Run tests with `--verbose` flag for detailed output
4. Check Azure portal for resource status
5. Review Application Insights for errors
