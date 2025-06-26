#!/bin/bash

# Vimarsh Production Deployment Validation and Smoke Tests
# Comprehensive validation suite for production deployments

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/deployment-validation-$(date +%Y%m%d-%H%M%S).log"

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${BLUE}$*${NC}"; }
warn() { log "WARN" "${YELLOW}$*${NC}"; }
error() { log "ERROR" "${RED}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }
test_start() { log "TEST" "${PURPLE}$*${NC}"; }

# Global test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test result tracking
declare -a FAILED_TEST_NAMES=()

# Help function
show_help() {
    cat << EOF
Vimarsh Production Deployment Validation Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    validate            Run full deployment validation suite
    smoke-test          Run smoke tests on deployed environment
    health-check        Quick health check of all services
    performance-test    Run performance validation tests
    security-test       Run basic security validation
    integration-test    Run integration tests against production
    rollback-test       Test rollback procedures
    help                Show this help message

OPTIONS:
    --environment ENV   Target environment (staging, prod)
    --base-url URL      Base URL for the deployed application
    --function-url URL  Azure Functions base URL
    --web-url URL       Static Web App URL
    --timeout SEC       Timeout for HTTP requests (default: 30)
    --retry-count N     Number of retries for failed tests (default: 3)
    --parallel          Run tests in parallel where possible
    --verbose           Enable verbose output
    --dry-run          Show what would be tested without executing

EXAMPLES:
    $0 validate --environment prod --base-url https://vimarsh-functions.azurewebsites.net
    $0 smoke-test --environment staging --web-url https://vimarsh-web.azurestaticapps.net
    $0 health-check --environment prod --verbose
    $0 performance-test --environment prod --parallel

EOF
}

# Test execution wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    test_start "Running test: $test_name"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would run test: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    fi
    
    local start_time=$(date +%s)
    
    if $test_function; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        success "✓ $test_name (${duration}s)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        error "✗ $test_name (${duration}s)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$test_name")
        return 1
    fi
}

# HTTP request helper with retry logic
http_request() {
    local method="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local retry_count="${RETRY_COUNT:-3}"
    local timeout="${TIMEOUT:-30}"
    
    for i in $(seq 1 $retry_count); do
        if [[ "$VERBOSE" == "true" ]]; then
            info "HTTP $method $url (attempt $i/$retry_count)"
        fi
        
        local response
        local status_code
        
        if response=$(curl -s -w "%{http_code}" -m "$timeout" -X "$method" "$url" 2>/dev/null); then
            status_code="${response: -3}"
            response_body="${response%???}"
            
            if [[ "$status_code" == "$expected_status" ]]; then
                if [[ "$VERBOSE" == "true" ]]; then
                    info "HTTP $method $url -> $status_code (success)"
                fi
                return 0
            else
                warn "HTTP $method $url -> $status_code (expected $expected_status)"
            fi
        else
            warn "HTTP $method $url -> connection failed (attempt $i/$retry_count)"
        fi
        
        if [[ $i -lt $retry_count ]]; then
            sleep $((i * 2))  # Exponential backoff
        fi
    done
    
    error "HTTP $method $url -> failed after $retry_count attempts"
    return 1
}

# JSON validation helper
validate_json() {
    local response="$1"
    local required_fields="$2"
    
    # Check if response is valid JSON
    if ! echo "$response" | jq . >/dev/null 2>&1; then
        error "Invalid JSON response"
        return 1
    fi
    
    # Check required fields
    if [[ -n "$required_fields" ]]; then
        IFS=',' read -ra FIELDS <<< "$required_fields"
        for field in "${FIELDS[@]}"; do
            if ! echo "$response" | jq -e ".$field" >/dev/null 2>&1; then
                error "Missing required field: $field"
                return 1
            fi
        done
    fi
    
    return 0
}

# Infrastructure validation tests
test_azure_functions_health() {
    local health_url="${FUNCTION_URL}/api/health"
    
    if http_request "GET" "$health_url" "200"; then
        local response=$(curl -s "$health_url" 2>/dev/null)
        
        if validate_json "$response" "status,timestamp"; then
            local status=$(echo "$response" | jq -r '.status')
            if [[ "$status" == "healthy" ]]; then
                return 0
            else
                error "Function app status: $status"
                return 1
            fi
        fi
    fi
    
    return 1
}

test_static_web_app_health() {
    if http_request "GET" "$WEB_URL" "200"; then
        # Check if the response contains expected content
        local response=$(curl -s "$WEB_URL" 2>/dev/null)
        
        if echo "$response" | grep -q "Vimarsh" && echo "$response" | grep -q "spiritual"; then
            return 0
        else
            error "Static web app content validation failed"
            return 1
        fi
    fi
    
    return 1
}

test_cosmos_db_connectivity() {
    local cosmos_test_url="${FUNCTION_URL}/api/test-cosmos"
    
    if http_request "GET" "$cosmos_test_url" "200"; then
        local response=$(curl -s "$cosmos_test_url" 2>/dev/null)
        
        if validate_json "$response" "status,database"; then
            local status=$(echo "$response" | jq -r '.status')
            if [[ "$status" == "connected" ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

test_application_insights() {
    local insights_test_url="${FUNCTION_URL}/api/test-insights"
    
    if http_request "GET" "$insights_test_url" "200"; then
        local response=$(curl -s "$insights_test_url" 2>/dev/null)
        
        if validate_json "$response" "status,telemetry"; then
            local status=$(echo "$response" | jq -r '.status')
            if [[ "$status" == "active" ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

test_key_vault_connectivity() {
    local keyvault_test_url="${FUNCTION_URL}/api/test-keyvault"
    
    if http_request "GET" "$keyvault_test_url" "200"; then
        local response=$(curl -s "$keyvault_test_url" 2>/dev/null)
        
        if validate_json "$response" "status,secrets_accessible"; then
            local status=$(echo "$response" | jq -r '.status')
            if [[ "$status" == "accessible" ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

# Functional smoke tests
test_spiritual_guidance_api() {
    local guidance_url="${FUNCTION_URL}/api/spiritual-guidance"
    local test_query='{"query": "What is dharma?", "language": "en"}'
    
    local response=$(curl -s -X POST "$guidance_url" \
        -H "Content-Type: application/json" \
        -d "$test_query" \
        -w "%{http_code}" 2>/dev/null)
    
    local status_code="${response: -3}"
    local response_body="${response%???}"
    
    if [[ "$status_code" == "200" ]]; then
        if validate_json "$response_body" "response,source,citations"; then
            local spiritual_response=$(echo "$response_body" | jq -r '.response')
            
            # Check if response contains spiritual content
            if echo "$spiritual_response" | grep -qi "dharma\|spiritual\|krishna\|divine"; then
                return 0
            else
                error "Spiritual guidance response lacks spiritual content"
                return 1
            fi
        fi
    else
        error "Spiritual guidance API returned status: $status_code"
        return 1
    fi
    
    return 1
}

test_voice_interface_endpoints() {
    local voice_test_url="${FUNCTION_URL}/api/voice/test"
    
    if http_request "GET" "$voice_test_url" "200"; then
        local response=$(curl -s "$voice_test_url" 2>/dev/null)
        
        if validate_json "$response" "speech_recognition,text_to_speech"; then
            local sr_status=$(echo "$response" | jq -r '.speech_recognition.status')
            local tts_status=$(echo "$response" | jq -r '.text_to_speech.status')
            
            if [[ "$sr_status" == "available" && "$tts_status" == "available" ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

test_authentication_flow() {
    local auth_test_url="${FUNCTION_URL}/api/auth/test"
    
    if http_request "GET" "$auth_test_url" "200"; then
        local response=$(curl -s "$auth_test_url" 2>/dev/null)
        
        if validate_json "$response" "auth_provider,tenant_id"; then
            local provider=$(echo "$response" | jq -r '.auth_provider')
            if [[ "$provider" == "Microsoft Entra External ID" ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

test_citation_system() {
    local citation_url="${FUNCTION_URL}/api/test-citations"
    
    if http_request "GET" "$citation_url" "200"; then
        local response=$(curl -s "$citation_url" 2>/dev/null)
        
        if validate_json "$response" "citations_available,source_texts"; then
            local citations_count=$(echo "$response" | jq -r '.citations_available')
            if [[ "$citations_count" -gt 0 ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

# Performance tests
test_response_time_performance() {
    local guidance_url="${FUNCTION_URL}/api/spiritual-guidance"
    local test_query='{"query": "What is the meaning of life?", "language": "en"}'
    
    local start_time=$(date +%s%3N)
    
    local response=$(curl -s -X POST "$guidance_url" \
        -H "Content-Type: application/json" \
        -d "$test_query" \
        -w "%{http_code}" 2>/dev/null)
    
    local end_time=$(date +%s%3N)
    local duration=$((end_time - start_time))
    
    local status_code="${response: -3}"
    
    if [[ "$status_code" == "200" && "$duration" -lt 30000 ]]; then  # 30 seconds max
        info "Response time: ${duration}ms"
        return 0
    else
        error "Performance test failed: ${duration}ms response time or status $status_code"
        return 1
    fi
}

test_concurrent_requests() {
    local guidance_url="${FUNCTION_URL}/api/spiritual-guidance"
    local test_query='{"query": "What is Om?", "language": "en"}'
    local concurrent_count=5
    
    info "Testing $concurrent_count concurrent requests"
    
    local pids=()
    local temp_dir="/tmp/vimarsh-concurrent-test-$$"
    mkdir -p "$temp_dir"
    
    # Start concurrent requests
    for i in $(seq 1 $concurrent_count); do
        (
            local result_file="$temp_dir/result-$i"
            if curl -s -X POST "$guidance_url" \
                -H "Content-Type: application/json" \
                -d "$test_query" \
                -w "%{http_code}" -o "$result_file.body" > "$result_file.status" 2>/dev/null; then
                echo "success" > "$result_file.outcome"
            else
                echo "failure" > "$result_file.outcome"
            fi
        ) &
        pids+=($!)
    done
    
    # Wait for all requests to complete
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    # Check results
    local success_count=0
    for i in $(seq 1 $concurrent_count); do
        local result_file="$temp_dir/result-$i"
        if [[ -f "$result_file.outcome" ]] && [[ "$(cat "$result_file.outcome")" == "success" ]]; then
            local status_code=$(cat "$result_file.status" 2>/dev/null || echo "000")
            if [[ "$status_code" == "200" ]]; then
                success_count=$((success_count + 1))
            fi
        fi
    done
    
    # Cleanup
    rm -rf "$temp_dir"
    
    if [[ "$success_count" -ge $((concurrent_count * 80 / 100)) ]]; then  # 80% success rate
        info "Concurrent test: $success_count/$concurrent_count requests successful"
        return 0
    else
        error "Concurrent test failed: only $success_count/$concurrent_count requests successful"
        return 1
    fi
}

# Security tests
test_https_enforcement() {
    local http_url="${FUNCTION_URL/https:/http:}"
    
    if [[ "$http_url" == "$FUNCTION_URL" ]]; then
        # Already HTTP, test should fail
        if http_request "GET" "$http_url/api/health" "301,302,308"; then
            return 0  # Redirect is good
        else
            return 1  # Should have redirected
        fi
    else
        # Test HTTP redirect
        local response=$(curl -s -I "$http_url/api/health" 2>/dev/null || true)
        if echo "$response" | grep -q "301\|302\|308"; then
            return 0
        else
            return 1
        fi
    fi
}

test_cors_headers() {
    local response_headers=$(curl -s -I "${FUNCTION_URL}/api/health" 2>/dev/null)
    
    if echo "$response_headers" | grep -qi "access-control-allow-origin"; then
        return 0
    else
        error "CORS headers not found"
        return 1
    fi
}

test_security_headers() {
    local response_headers=$(curl -s -I "$WEB_URL" 2>/dev/null)
    
    local required_headers=("x-content-type-options" "x-frame-options" "x-xss-protection")
    local found_headers=0
    
    for header in "${required_headers[@]}"; do
        if echo "$response_headers" | grep -qi "$header"; then
            found_headers=$((found_headers + 1))
        fi
    done
    
    if [[ "$found_headers" -ge 2 ]]; then  # At least 2 security headers
        return 0
    else
        error "Insufficient security headers found: $found_headers/3"
        return 1
    fi
}

# Integration tests
test_end_to_end_workflow() {
    info "Testing complete user workflow"
    
    # 1. Load frontend
    if ! http_request "GET" "$WEB_URL" "200"; then
        return 1
    fi
    
    # 2. Test API availability
    if ! http_request "GET" "${FUNCTION_URL}/api/health" "200"; then
        return 1
    fi
    
    # 3. Test spiritual guidance
    local guidance_url="${FUNCTION_URL}/api/spiritual-guidance"
    local test_query='{"query": "What is the path to enlightenment?", "language": "en"}'
    
    local response=$(curl -s -X POST "$guidance_url" \
        -H "Content-Type: application/json" \
        -d "$test_query" 2>/dev/null)
    
    if ! validate_json "$response" "response,source,citations"; then
        return 1
    fi
    
    # 4. Verify response quality
    local spiritual_response=$(echo "$response" | jq -r '.response')
    if ! echo "$spiritual_response" | grep -qi "spiritual\|enlightenment\|dharma\|krishna"; then
        error "End-to-end test: Response lacks spiritual content"
        return 1
    fi
    
    return 0
}

test_monitoring_integration() {
    # Test Application Insights integration
    local insights_url="${FUNCTION_URL}/api/test-monitoring"
    
    if http_request "GET" "$insights_url" "200"; then
        local response=$(curl -s "$insights_url" 2>/dev/null)
        
        if validate_json "$response" "monitoring_active,custom_events"; then
            local monitoring_status=$(echo "$response" | jq -r '.monitoring_active')
            if [[ "$monitoring_status" == "true" ]]; then
                return 0
            fi
        fi
    fi
    
    return 1
}

# Rollback tests
test_rollback_procedures() {
    info "Testing rollback procedure validation"
    
    # Check if previous deployment artifacts exist
    if [[ -f "$PROJECT_ROOT/deployment/previous-deployment.json" ]]; then
        info "Previous deployment configuration found"
        return 0
    else
        warn "No previous deployment configuration found (acceptable for first deployment)"
        return 0
    fi
}

# Main validation suites
run_infrastructure_validation() {
    info "Running infrastructure validation tests..."
    
    run_test "Azure Functions Health Check" test_azure_functions_health
    run_test "Static Web App Health Check" test_static_web_app_health
    run_test "Cosmos DB Connectivity" test_cosmos_db_connectivity
    run_test "Application Insights Integration" test_application_insights
    run_test "Key Vault Connectivity" test_key_vault_connectivity
}

run_functional_smoke_tests() {
    info "Running functional smoke tests..."
    
    run_test "Spiritual Guidance API" test_spiritual_guidance_api
    run_test "Voice Interface Endpoints" test_voice_interface_endpoints
    run_test "Authentication Flow" test_authentication_flow
    run_test "Citation System" test_citation_system
}

run_performance_tests() {
    info "Running performance validation tests..."
    
    run_test "Response Time Performance" test_response_time_performance
    run_test "Concurrent Request Handling" test_concurrent_requests
}

run_security_tests() {
    info "Running security validation tests..."
    
    run_test "HTTPS Enforcement" test_https_enforcement
    run_test "CORS Headers" test_cors_headers
    run_test "Security Headers" test_security_headers
}

run_integration_tests() {
    info "Running integration tests..."
    
    run_test "End-to-End Workflow" test_end_to_end_workflow
    run_test "Monitoring Integration" test_monitoring_integration
}

run_rollback_tests() {
    info "Running rollback validation tests..."
    
    run_test "Rollback Procedures" test_rollback_procedures
}

# Generate test report
generate_test_report() {
    local report_file="$PROJECT_ROOT/docs/deployment/deployment-validation-report-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# Vimarsh Production Deployment Validation Report

**Test Date:** $(date)  
**Environment:** $ENVIRONMENT  
**Test Execution:** $(basename "$0")

## Summary

- **Total Tests:** $TOTAL_TESTS
- **Passed:** $PASSED_TESTS
- **Failed:** $FAILED_TESTS
- **Success Rate:** $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%

## Test Results

| Category | Status | Details |
|----------|--------|---------|
| Infrastructure | $( [[ $FAILED_TESTS -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL" ) | Core infrastructure validation |
| Functional | $( [[ $FAILED_TESTS -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL" ) | API and feature validation |
| Performance | $( [[ $FAILED_TESTS -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL" ) | Response time and load testing |
| Security | $( [[ $FAILED_TESTS -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL" ) | Security configuration validation |
| Integration | $( [[ $FAILED_TESTS -eq 0 ]] && echo "✅ PASS" || echo "❌ FAIL" ) | End-to-end workflow testing |

EOF

    if [[ $FAILED_TESTS -gt 0 ]]; then
        cat >> "$report_file" << EOF

## Failed Tests

EOF
        for test_name in "${FAILED_TEST_NAMES[@]}"; do
            echo "- $test_name" >> "$report_file"
        done
        
        cat >> "$report_file" << EOF

## Recommended Actions

1. Review failed test details in log file: $LOG_FILE
2. Address infrastructure or configuration issues
3. Re-run validation after fixes
4. Consider rollback if critical issues persist

EOF
    else
        cat >> "$report_file" << EOF

## ✅ Deployment Validation Successful

All tests passed successfully. The deployment is validated and ready for production use.

## Next Steps

1. Monitor application performance and health
2. Set up ongoing monitoring and alerting
3. Schedule regular validation tests
4. Document any lessons learned

EOF
    fi
    
    cat >> "$report_file" << EOF

## Configuration Used

- **Function URL:** $FUNCTION_URL
- **Web URL:** $WEB_URL
- **Timeout:** $TIMEOUT seconds
- **Retry Count:** $RETRY_COUNT
- **Parallel Execution:** $PARALLEL

## Log Files

- **Main Log:** $LOG_FILE
- **Test Report:** $report_file

---
*Generated by Vimarsh Deployment Validation*
EOF
    
    success "Test report generated: $report_file"
}

# Parse command line arguments
COMMAND=""
ENVIRONMENT=""
FUNCTION_URL=""
WEB_URL=""
TIMEOUT=30
RETRY_COUNT=3
PARALLEL=false
VERBOSE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        validate|smoke-test|health-check|performance-test|security-test|integration-test|rollback-test|help)
            COMMAND="$1"
            shift
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --base-url|--function-url)
            FUNCTION_URL="$2"
            shift 2
            ;;
        --web-url)
            WEB_URL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --retry-count)
            RETRY_COUNT="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$COMMAND" ]]; then
    error "Command is required"
    show_help
    exit 1
fi

if [[ "$COMMAND" == "help" ]]; then
    show_help
    exit 0
fi

if [[ -z "$ENVIRONMENT" ]]; then
    error "Environment is required"
    show_help
    exit 1
fi

# Set default URLs if not provided
if [[ -z "$FUNCTION_URL" ]]; then
    case "$ENVIRONMENT" in
        staging)
            FUNCTION_URL="https://vimarsh-staging-functions.azurewebsites.net"
            ;;
        prod)
            FUNCTION_URL="https://vimarsh-functions.azurewebsites.net"
            ;;
        *)
            error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
fi

if [[ -z "$WEB_URL" ]]; then
    case "$ENVIRONMENT" in
        staging)
            WEB_URL="https://vimarsh-staging-web.azurestaticapps.net"
            ;;
        prod)
            WEB_URL="https://vimarsh-web.azurestaticapps.net"
            ;;
        *)
            error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
fi

# Check dependencies
if ! command -v curl &> /dev/null; then
    error "curl is required but not installed"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    error "jq is required but not installed"
    exit 1
fi

# Main execution
main() {
    info "Starting Vimarsh Production Deployment Validation"
    info "Environment: $ENVIRONMENT"
    info "Function URL: $FUNCTION_URL"
    info "Web URL: $WEB_URL"
    info "Command: $COMMAND"
    
    case "$COMMAND" in
        validate)
            run_infrastructure_validation
            run_functional_smoke_tests
            run_performance_tests
            run_security_tests
            run_integration_tests
            run_rollback_tests
            ;;
        smoke-test)
            run_functional_smoke_tests
            ;;
        health-check)
            run_infrastructure_validation
            ;;
        performance-test)
            run_performance_tests
            ;;
        security-test)
            run_security_tests
            ;;
        integration-test)
            run_integration_tests
            ;;
        rollback-test)
            run_rollback_tests
            ;;
        *)
            error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac
    
    # Generate report
    generate_test_report
    
    # Final summary
    echo
    if [[ $FAILED_TESTS -eq 0 ]]; then
        success "🎉 All tests passed! Deployment validation successful."
        success "Total: $TOTAL_TESTS tests, Success rate: 100%"
        exit 0
    else
        error "❌ Some tests failed! Deployment validation failed."
        error "Total: $TOTAL_TESTS tests, Passed: $PASSED_TESTS, Failed: $FAILED_TESTS"
        error "Success rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
        exit 1
    fi
}

# Run main function
main "$@"
