# Production Deployment Validation and Smoke Tests

## Overview

This document describes the comprehensive deployment validation and smoke test infrastructure for the Vimarsh AI Agent platform. The validation suite ensures that all production deployments meet quality, performance, security, and functional requirements.

## Components

### 1. Deployment Validation Script (`scripts/deployment-validation.sh`)

A comprehensive bash script that validates all aspects of a production deployment.

#### Features:
- **Infrastructure Validation**: Verifies all Azure resources are deployed and configured correctly
- **Functional Testing**: Tests all API endpoints and core functionality
- **Performance Testing**: Validates response times and concurrent request handling
- **Security Testing**: Checks HTTPS enforcement, CORS, and security headers
- **Integration Testing**: Verifies end-to-end workflows and monitoring integration
- **Rollback Testing**: Validates rollback procedures

#### Usage:
```bash
# Full validation suite
./scripts/deployment-validation.sh validate --environment prod --verbose

# Quick health check
./scripts/deployment-validation.sh health-check --environment staging

# Performance testing only
./scripts/deployment-validation.sh performance-test --environment prod --parallel

# Dry run (no actual tests)
./scripts/deployment-validation.sh validate --environment staging --dry-run
```

#### Commands:
- `validate`: Complete deployment validation suite (17 tests)
- `smoke-test`: Basic smoke tests for quick validation
- `health-check`: Quick health check of all services
- `performance-test`: Performance validation tests
- `security-test`: Security validation tests
- `integration-test`: Integration tests
- `rollback-test`: Rollback procedure validation

### 2. Smoke Test Runner (`scripts/smoke-test-runner.py`)

Advanced Python-based smoke test runner with async support and comprehensive reporting.

#### Features:
- **Async Testing**: Parallel test execution for faster results
- **YAML Configuration**: Flexible test scenarios via `config/testing/smoke-test-config.yaml`
- **Multiple Output Formats**: JSON, HTML, and Markdown reports
- **Test Categories**: Health checks, infrastructure, spiritual guidance, voice interface, performance, security
- **Environment Support**: Staging and production configurations

#### Dependencies:
```bash
pip install -r scripts/requirements-testing.txt
```

#### Usage:
```bash
# Run all smoke tests
python3 scripts/smoke-test-runner.py --environment prod --verbose

# Generate HTML report
python3 scripts/smoke-test-runner.py --environment staging --output-format html

# Run specific test category
python3 scripts/smoke-test-runner.py --environment prod --categories health_checks,infrastructure
```

### 3. Simple Smoke Test Runner (`scripts/simple-smoke-test.py`)

Lightweight smoke test runner with minimal dependencies (only `requests`).

#### Features:
- **No External Dependencies**: Only requires Python standard library + requests
- **Quick Validation**: Essential smoke tests for rapid deployment validation
- **JSON Reporting**: Structured test results for CI/CD integration
- **Verbose Logging**: Detailed output for debugging

#### Usage:
```bash
# Basic smoke tests
python3 scripts/simple-smoke-test.py --environment staging --verbose

# Generate JSON report
python3 scripts/simple-smoke-test.py --environment prod --output results.json
```

### 4. Test Configuration (`config/testing/smoke-test-config.yaml`)

Centralized configuration for all smoke test scenarios.

#### Test Categories:
- **Health Checks**: Basic endpoint availability
- **Infrastructure**: Database, Key Vault, Application Insights connectivity
- **Spiritual Guidance**: Core AI functionality with spiritual context
- **Voice Interface**: Speech processing and TTS capabilities
- **Performance**: Response time and load testing
- **Security**: HTTPS enforcement and security headers

### 5. Backend Test Endpoints (`backend/test_endpoints.py`)

Dedicated test endpoints for deployment validation.

#### Endpoints:
- `/api/health`: Basic health check
- `/api/test/cosmos`: Cosmos DB connectivity test
- `/api/test/keyvault`: Key Vault access test
- `/api/test/insights`: Application Insights integration test
- `/api/test/performance`: Performance metrics endpoint
- `/api/test/security`: Security configuration validation

## Test Scenarios

### Infrastructure Tests
1. **Azure Functions Health**: Verify function app is running and responsive
2. **Static Web App Availability**: Confirm frontend is accessible
3. **Cosmos DB Connectivity**: Test database connection and query capability
4. **Key Vault Access**: Verify secret retrieval functionality
5. **Application Insights Integration**: Check telemetry collection

### Functional Tests
1. **Spiritual Guidance API**: Test core AI functionality with dharmic queries
2. **Voice Interface**: Test speech recognition and text-to-speech
3. **Authentication Flow**: Verify Entra External ID integration
4. **Citation System**: Test source text attribution
5. **Error Handling**: Validate graceful error responses

### Performance Tests
1. **Response Time**: Ensure API responses under 5 seconds
2. **Concurrent Requests**: Test handling of multiple simultaneous users
3. **Voice Processing**: Validate speech processing performance
4. **Database Queries**: Test vector search response times

### Security Tests
1. **HTTPS Enforcement**: Verify HTTP to HTTPS redirects
2. **CORS Configuration**: Check cross-origin request policies
3. **Security Headers**: Validate CSP, XSS protection headers
4. **Authentication**: Test unauthorized access blocking

### Integration Tests
1. **End-to-End Workflow**: Complete user journey from query to response
2. **Monitoring Integration**: Verify Application Insights data flow
3. **Cost Monitoring**: Test budget alerts and tracking
4. **Expert Review System**: Validate content routing for review

## Continuous Integration

### GitHub Actions Integration

The validation scripts integrate with GitHub Actions workflows:

```yaml
- name: Production Deployment Validation
  run: |
    ./scripts/deployment-validation.sh validate --environment prod --verbose
    
- name: Smoke Tests
  run: |
    python3 scripts/simple-smoke-test.py --environment prod --output smoke-test-results.json
```

### Pre-Production Checklist

Before promoting to production:

1. ✅ All infrastructure tests pass
2. ✅ Functional tests achieve 100% success rate
3. ✅ Performance tests meet SLA requirements
4. ✅ Security tests pass all validations
5. ✅ Integration tests confirm end-to-end functionality
6. ✅ Rollback procedures tested and validated

## Reporting

### Test Reports

All validation tools generate comprehensive reports:

1. **Deployment Validation Report**: 
   - Location: `docs/deployment/deployment-validation-report-{timestamp}.md`
   - Format: Markdown with test results, timing, and recommendations

2. **Smoke Test Results**:
   - Location: `logs/smoke-test-results-{timestamp}.json`
   - Format: JSON with detailed test outcomes and performance metrics

3. **Simple Smoke Test Results**:
   - Location: User-specified or default console output
   - Format: JSON with essential test results

### Monitoring Integration

Test results integrate with Application Insights for tracking:
- Deployment success rates
- Test execution times
- Failure patterns and trends
- Performance regression detection

## Troubleshooting

### Common Issues

1. **DNS Resolution Failures**: Environment not yet deployed
   - Solution: Verify resource deployment status
   - Check: Azure portal for resource availability

2. **Authentication Errors**: Missing or invalid credentials
   - Solution: Verify service principal permissions
   - Check: Key Vault access policies

3. **Performance Degradation**: Response times exceeding thresholds
   - Solution: Check Application Insights for bottlenecks
   - Action: Scale up resources if needed

4. **Security Test Failures**: Missing security headers or HTTPS issues
   - Solution: Review Azure Static Web Apps configuration
   - Check: Function App security settings

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Deployment validation debug
./scripts/deployment-validation.sh validate --environment staging --verbose

# Smoke test debug
python3 scripts/simple-smoke-test.py --environment staging --verbose
```

## Best Practices

1. **Pre-Deployment**: Always run validation in staging first
2. **Automated Testing**: Integrate into CI/CD pipelines
3. **Regular Monitoring**: Schedule periodic validation runs
4. **Documentation**: Keep test scenarios updated with new features
5. **Rollback Testing**: Regularly validate rollback procedures

## Spiritual Context Validation

Special attention to spiritual content validation:

1. **Dharmic Response Quality**: Verify responses maintain spiritual authenticity
2. **Sanskrit Pronunciation**: Test voice interface with Sanskrit terms
3. **Cultural Sensitivity**: Validate respectful handling of sacred content
4. **Expert Review Integration**: Confirm expert validation workflow
5. **Citation Accuracy**: Verify proper attribution to source texts

## Security and Compliance

The validation suite ensures:

1. **Data Protection**: No sensitive data in test payloads
2. **Privacy Compliance**: GDPR-compliant data handling
3. **Authentication Security**: Proper token validation
4. **Transport Security**: HTTPS enforcement and secure headers
5. **Access Control**: Proper authorization checks

## Performance Benchmarks

### Response Time Targets
- Health checks: < 1 second
- Spiritual guidance queries: < 5 seconds
- Voice processing: < 3 seconds
- Database queries: < 2 seconds

### Throughput Targets
- Concurrent users: 50 simultaneous requests
- Peak load: 100 requests per minute
- Voice processing: 10 concurrent voice sessions

### Availability Targets
- System uptime: 99.9%
- Health check success rate: 100%
- Functional test success rate: 95%

## Conclusion

The production deployment validation and smoke test infrastructure provides comprehensive coverage of all system components, ensuring reliable and secure deployments of the Vimarsh AI Agent platform. Regular execution of these tests maintains high quality and performance standards while preserving the spiritual authenticity and cultural sensitivity that are core to the platform's mission.
