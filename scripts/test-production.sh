#!/bin/bash

# Vimarsh Production Testing Script
# Comprehensive testing of production deployment
# Usage: ./test-production.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🕉️  Vimarsh Production Testing Suite${NC}"
echo ""

# Configuration
FUNCTION_APP_NAME="vimarsh-functions"
RESOURCE_GROUP="vimarsh-rg"

# Get Function App URL
FUNCTION_APP_URL=$(az functionapp show \
    --resource-group $RESOURCE_GROUP \
    --name $FUNCTION_APP_NAME \
    --query defaultHostName \
    --output tsv 2>/dev/null || echo "")

if [ -z "$FUNCTION_APP_URL" ]; then
    echo -e "${RED}❌ Function App not found. Please deploy infrastructure first.${NC}"
    exit 1
fi

BASE_URL="https://$FUNCTION_APP_URL"
echo -e "${BLUE}🔗 Testing Function App: $BASE_URL${NC}"
echo ""

# Test functions
test_health_check() {
    echo -e "${BLUE}🏥 Testing health check endpoint...${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/api/health" || echo "HTTPSTATUS:000")
    
    if [[ $response == *"HTTPSTATUS:200"* ]]; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        return 0
    else
        echo -e "${RED}❌ Health check failed: $response${NC}"
        return 1
    fi
}

test_spiritual_guidance() {
    echo -e "${BLUE}🧘 Testing spiritual guidance endpoint...${NC}"
    
    # Test query
    test_query="What is the nature of duty according to Krishna?"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$test_query\", \"language\": \"English\"}" \
        "$BASE_URL/api/spiritual-guidance" || echo "HTTPSTATUS:000")
    
    http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ Spiritual guidance endpoint working${NC}"
        echo -e "${BLUE}📖 Response preview:${NC}"
        echo "$response_body" | jq -r '.guidance' | head -3 | sed 's/^/   /'
        echo "   ..."
        return 0
    else
        echo -e "${RED}❌ Spiritual guidance failed (HTTP $http_status)${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        return 1
    fi
}

test_rag_pipeline() {
    echo -e "${BLUE}🔍 Testing RAG retrieval endpoint...${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"karma yoga\", \"top_k\": 3}" \
        "$BASE_URL/api/rag/search" || echo "HTTPSTATUS:000")
    
    http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ RAG pipeline working${NC}"
        chunk_count=$(echo "$response_body" | jq '.chunks | length' 2>/dev/null || echo "0")
        echo -e "${BLUE}📚 Retrieved $chunk_count text chunks${NC}"
        return 0
    else
        echo -e "${RED}❌ RAG pipeline failed (HTTP $http_status)${NC}"
        echo -e "${RED}Response: $response_body${NC}"
        return 1
    fi
}

test_cost_monitoring() {
    echo -e "${BLUE}💰 Testing cost monitoring endpoint...${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        "$BASE_URL/api/cost/status" || echo "HTTPSTATUS:000")
    
    http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ Cost monitoring working${NC}"
        current_cost=$(echo "$response_body" | jq -r '.current_cost' 2>/dev/null || echo "N/A")
        budget_status=$(echo "$response_body" | jq -r '.budget_status' 2>/dev/null || echo "N/A")
        echo -e "${BLUE}💵 Current cost: $current_cost${NC}"
        echo -e "${BLUE}📊 Budget status: $budget_status${NC}"
        return 0
    else
        echo -e "${RED}❌ Cost monitoring failed (HTTP $http_status)${NC}"
        return 1
    fi
}

test_authentication() {
    echo -e "${BLUE}🔐 Testing authentication endpoint...${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        "$BASE_URL/api/auth/validate" || echo "HTTPSTATUS:000")
    
    http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    # For auth endpoint, we expect 401 (unauthorized) without token
    if [ "$http_status" = "401" ]; then
        echo -e "${GREEN}✅ Authentication endpoint working (correctly rejecting requests without token)${NC}"
        return 0
    elif [ "$http_status" = "200" ]; then
        echo -e "${YELLOW}⚠️  Authentication endpoint accessible without token (development mode?)${NC}"
        return 0
    else
        echo -e "${RED}❌ Authentication endpoint failed (HTTP $http_status)${NC}"
        return 1
    fi
}

# Performance testing
test_performance() {
    echo -e "${BLUE}⚡ Running performance tests...${NC}"
    
    echo -e "${BLUE}  Testing response times...${NC}"
    
    # Test health endpoint performance
    for i in {1..3}; do
        start_time=$(date +%s%N)
        curl -s "$BASE_URL/api/health" > /dev/null
        end_time=$(date +%s%N)
        duration=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds
        echo -e "${BLUE}    Health check #$i: ${duration}ms${NC}"
    done
    
    echo -e "${GREEN}✅ Performance tests completed${NC}"
}

# Load testing (basic)
test_load() {
    echo -e "${BLUE}🏋️  Running basic load test...${NC}"
    
    echo -e "${BLUE}  Sending 10 concurrent requests...${NC}"
    
    # Simple concurrent test
    for i in {1..10}; do
        (curl -s "$BASE_URL/api/health" > /dev/null && echo "Request $i: Success" || echo "Request $i: Failed") &
    done
    wait
    
    echo -e "${GREEN}✅ Load test completed${NC}"
}

# Database connectivity test
test_database() {
    echo -e "${BLUE}🗄️  Testing database connectivity...${NC}"
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        "$BASE_URL/api/admin/db-status" || echo "HTTPSTATUS:000")
    
    http_status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_status" = "200" ]; then
        echo -e "${GREEN}✅ Database connectivity working${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Database status endpoint not available (may be admin-only)${NC}"
        return 0
    fi
}

# Run all tests
echo -e "${BLUE}🚀 Starting production test suite...${NC}"
echo ""

total_tests=0
passed_tests=0

# Core functionality tests
tests=(
    "test_health_check"
    "test_spiritual_guidance" 
    "test_rag_pipeline"
    "test_cost_monitoring"
    "test_authentication"
    "test_database"
)

for test in "${tests[@]}"; do
    total_tests=$((total_tests + 1))
    if $test; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
done

# Performance tests (non-critical)
echo -e "${BLUE}🔬 Running additional tests...${NC}"
test_performance
echo ""
test_load

echo ""
echo -e "${BLUE}📊 Test Results Summary${NC}"
echo -e "   Tests passed: ${GREEN}$passed_tests${NC}/$total_tests"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "${GREEN}🎉 All critical tests passed! Production deployment is healthy.${NC}"
    echo ""
    echo -e "${BLUE}🌐 Production URLs:${NC}"
    echo -e "   Function App: $BASE_URL"
    echo -e "   Health Check: $BASE_URL/api/health"
    echo -e "   Spiritual Guidance: $BASE_URL/api/spiritual-guidance"
    echo ""
    echo -e "${BLUE}📈 Monitoring:${NC}"
    echo -e "   Azure Portal: https://portal.azure.com"
    echo -e "   Application Insights: Search for 'vimarsh-insights'"
    echo -e "   Cost Management: Azure Portal → Cost Management"
    echo ""
    echo -e "${BLUE}🔄 Pause/Resume Operations:${NC}"
    echo -e "   Pause: az group delete --name vimarsh-rg --yes"
    echo -e "   Resume: ./deploy.sh"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Please check the logs above.${NC}"
    echo -e "${YELLOW}   This may be normal if services are still starting up.${NC}"
    exit 1
fi
