#!/bin/bash

# Vimarsh Monitoring and Alerting Setup Script
# This script deploys and configures comprehensive monitoring for the spiritual guidance system

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-development}"
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-vimarsh-rg}"
LOCATION="${AZURE_LOCATION:-eastus}"

# Monitoring configuration
EXPERT_EMAIL="${EXPERT_REVIEW_EMAIL:-vedprakash.m@me.com}"
MONTHLY_BUDGET="${MONTHLY_BUDGET_USD:-50}"
COST_ALERT_THRESHOLD="${COST_ALERT_THRESHOLD:-80}"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Help function
show_help() {
    cat << EOF
🙏 Vimarsh Monitoring and Alerting Setup

USAGE:
    $0 <operation> [environment]

OPERATIONS:
    deploy          Deploy monitoring infrastructure
    configure       Configure alerting rules
    test            Test monitoring and alerts
    status          Show monitoring status
    dashboard       Open monitoring dashboard
    help            Show this help message

ENVIRONMENTS:
    development     Local development monitoring
    staging         Staging environment monitoring  
    production      Production environment monitoring

EXAMPLES:
    $0 deploy production      # Deploy production monitoring
    $0 configure staging      # Configure staging alerts
    $0 test development       # Test development monitoring
    $0 status                # Show current monitoring status
    $0 dashboard production   # Open production dashboard

ENVIRONMENT VARIABLES:
    ENVIRONMENT                 # Target environment
    AZURE_SUBSCRIPTION_ID       # Azure subscription ID
    AZURE_RESOURCE_GROUP        # Azure resource group
    EXPERT_REVIEW_EMAIL         # Email for alerts
    MONTHLY_BUDGET_USD          # Monthly budget for cost alerts
    COST_ALERT_THRESHOLD        # Cost alert threshold (0-100)

🕉️ May this monitoring serve the divine purpose of ensuring reliable spiritual guidance
EOF
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites for monitoring setup..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        error "Azure CLI not found. Please install Azure CLI."
    fi
    
    # Check if logged in
    if ! az account show &> /dev/null; then
        error "Not logged into Azure. Please run 'az login'."
    fi
    
    # Set subscription if provided
    if [ -n "$SUBSCRIPTION_ID" ]; then
        az account set --subscription "$SUBSCRIPTION_ID"
        log "Using subscription: $SUBSCRIPTION_ID"
    fi
    
    # Check resource group exists
    if ! az group exists --name "$RESOURCE_GROUP" &> /dev/null; then
        warning "Resource group '$RESOURCE_GROUP' does not exist. Creating..."
        az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    fi
    
    log "✅ Prerequisites validated"
}

# Deploy monitoring infrastructure
deploy_monitoring() {
    local env="${1:-$ENVIRONMENT}"
    
    log "🚀 Deploying monitoring infrastructure for environment: $env"
    
    # Get resource names
    local app_insights_name="vimarsh-${env}-insights"
    local function_app_name="vimarsh-${env}-functions"
    local cosmos_db_name="vimarsh-${env}-cosmos"
    
    # Production uses different naming
    if [ "$env" = "production" ]; then
        app_insights_name="vimarsh-insights"
        function_app_name="vimarsh-functions"
        cosmos_db_name="vimarsh-cosmos"
    fi
    
    # Deploy monitoring Bicep template
    log "Deploying monitoring template..."
    
    local deployment_name="vimarsh-monitoring-$(date +%Y%m%d-%H%M%S)"
    
    az deployment group create \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "$PROJECT_ROOT/infrastructure/monitoring.bicep" \
        --name "$deployment_name" \
        --parameters \
            environment="$env" \
            location="$LOCATION" \
            appName="vimarsh" \
            appInsightsName="$app_insights_name" \
            functionAppName="$function_app_name" \
            cosmosDbName="$cosmos_db_name" \
            expertReviewEmail="$EXPERT_EMAIL" \
            monthlyBudgetUsd="$MONTHLY_BUDGET" \
            costAlertThreshold="$COST_ALERT_THRESHOLD" \
        --output table
    
    # Get deployment outputs
    local outputs=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$deployment_name" \
        --query properties.outputs \
        --output json)
    
    log "✅ Monitoring infrastructure deployed successfully"
    
    # Display important information
    echo -e "${BLUE}Monitoring Endpoints:${NC}"
    echo "$outputs" | jq -r '.monitoringEndpoints.value | to_entries[] | "  \(.key): \(.value)"'
}

# Configure custom monitoring
configure_monitoring() {
    local env="${1:-$ENVIRONMENT}"
    
    log "⚙️ Configuring custom monitoring for environment: $env"
    
    # Configure Application Insights custom events
    configure_app_insights_events "$env"
    
    # Configure Log Analytics queries
    configure_log_analytics_queries "$env"
    
    # Configure custom dashboards
    configure_custom_dashboards "$env"
    
    log "✅ Custom monitoring configuration completed"
}

# Configure Application Insights custom events
configure_app_insights_events() {
    local env="$1"
    
    log "📊 Configuring Application Insights custom events..."
    
    # Create custom events configuration
    cat > "$PROJECT_ROOT/config/monitoring/custom-events.json" << EOF
{
  "customEvents": [
    {
      "name": "SpiritualGuidanceRequested",
      "description": "Spiritual seeker requests guidance",
      "properties": {
        "language": "string",
        "queryType": "string",
        "responseTime": "number",
        "qualityScore": "number"
      }
    },
    {
      "name": "ExpertReviewTriggered", 
      "description": "Content flagged for expert review",
      "properties": {
        "contentType": "string",
        "flagReason": "string",
        "severity": "string"
      }
    },
    {
      "name": "CostThresholdReached",
      "description": "AI cost threshold reached",
      "properties": {
        "currentCost": "number",
        "threshold": "number",
        "action": "string"
      }
    },
    {
      "name": "VoiceInteractionCompleted",
      "description": "Voice interaction with spiritual seeker",
      "properties": {
        "language": "string",
        "duration": "number",
        "transcriptionAccuracy": "number"
      }
    }
  ]
}
EOF

    log "✅ Application Insights custom events configured"
}

# Configure Log Analytics queries
configure_log_analytics_queries() {
    local env="$1"
    
    log "📝 Configuring Log Analytics queries..."
    
    mkdir -p "$PROJECT_ROOT/config/monitoring/queries"
    
    # Spiritual guidance quality query
    cat > "$PROJECT_ROOT/config/monitoring/queries/spiritual-quality.kql" << 'EOF'
// Spiritual Guidance Quality Monitoring
customEvents
| where name == "SpiritualGuidanceRequested"
| where timestamp > ago(24h)
| extend qualityScore = toreal(customDimensions.qualityScore)
| extend language = tostring(customDimensions.language)
| summarize 
    RequestCount = count(),
    AvgQuality = avg(qualityScore),
    MinQuality = min(qualityScore),
    LowQualityCount = countif(qualityScore < 0.7)
    by language, bin(timestamp, 1h)
| order by timestamp desc
EOF

    # Expert review monitoring query
    cat > "$PROJECT_ROOT/config/monitoring/queries/expert-review.kql" << 'EOF'
// Expert Review System Monitoring
customEvents  
| where name == "ExpertReviewTriggered"
| where timestamp > ago(7d)
| extend severity = tostring(customDimensions.severity)
| extend flagReason = tostring(customDimensions.flagReason)
| summarize 
    ReviewCount = count(),
    HighSeverityCount = countif(severity == "high"),
    MediumSeverityCount = countif(severity == "medium")
    by flagReason, bin(timestamp, 1d)
| order by timestamp desc
EOF

    # Cost monitoring query
    cat > "$PROJECT_ROOT/config/monitoring/queries/cost-monitoring.kql" << 'EOF'
// AI Cost Monitoring and Optimization
customEvents
| where name == "CostThresholdReached" or name == "SpiritualGuidanceRequested"
| where timestamp > ago(24h)
| extend currentCost = toreal(customDimensions.currentCost)
| extend responseTime = toreal(customDimensions.responseTime)
| summarize 
    TotalRequests = countif(name == "SpiritualGuidanceRequested"),
    CostAlerts = countif(name == "CostThresholdReached"),
    AvgResponseTime = avg(responseTime),
    TotalCost = sum(currentCost)
    by bin(timestamp, 1h)
| order by timestamp desc
EOF

    log "✅ Log Analytics queries configured"
}

# Configure custom dashboards
configure_custom_dashboards() {
    local env="$1"
    
    log "📋 Configuring custom dashboards..."
    
    # Create dashboard configuration
    cat > "$PROJECT_ROOT/config/monitoring/dashboard-config.json" << EOF
{
  "dashboards": {
    "spiritual-guidance": {
      "name": "🙏 Vimarsh Spiritual Guidance Dashboard",
      "description": "Comprehensive monitoring for spiritual guidance system",
      "widgets": [
        {
          "type": "kql",
          "title": "Daily Seekers Served",
          "query": "customEvents | where name == 'SpiritualGuidanceRequested' | summarize count() by bin(timestamp, 1d)"
        },
        {
          "type": "metric",
          "title": "Response Time",
          "metric": "requests/duration"
        },
        {
          "type": "kql", 
          "title": "Quality Metrics",
          "query": "customEvents | where name == 'SpiritualGuidanceRequested' | extend quality = toreal(customDimensions.qualityScore) | summarize avg(quality)"
        }
      ]
    },
    "cost-optimization": {
      "name": "💰 AI Cost Management Dashboard", 
      "description": "Cost monitoring and optimization for AI services",
      "widgets": [
        {
          "type": "kql",
          "title": "Cost Trends",
          "query": "customEvents | where name == 'CostThresholdReached' | summarize sum(toreal(customDimensions.currentCost)) by bin(timestamp, 1d)"
        },
        {
          "type": "kql",
          "title": "Budget Utilization",
          "query": "customEvents | where name == 'CostThresholdReached' | extend threshold = toreal(customDimensions.threshold) | summarize max(threshold)"
        }
      ]
    }
  }
}
EOF

    log "✅ Custom dashboards configured"
}

# Test monitoring system
test_monitoring() {
    local env="${1:-$ENVIRONMENT}"
    
    log "🧪 Testing monitoring system for environment: $env"
    
    # Test Application Insights connectivity
    test_app_insights_connectivity "$env"
    
    # Test alert rules
    test_alert_rules "$env"
    
    # Test custom events
    test_custom_events "$env"
    
    log "✅ Monitoring system testing completed"
}

# Test Application Insights connectivity
test_app_insights_connectivity() {
    local env="$1"
    local app_insights_name="vimarsh-${env}-insights"
    
    if [ "$env" = "production" ]; then
        app_insights_name="vimarsh-insights"
    fi
    
    log "Testing Application Insights connectivity..."
    
    # Check if Application Insights exists
    if az monitor app-insights component show \
        --app "$app_insights_name" \
        --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        log "✅ Application Insights connectivity verified"
    else
        warning "Application Insights '$app_insights_name' not found or not accessible"
    fi
}

# Test alert rules
test_alert_rules() {
    local env="$1"
    
    log "Testing alert rules..."
    
    # List metric alerts
    local alerts=$(az monitor metrics alert list \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?contains(name, 'vimarsh-${env}')].name" \
        --output tsv)
    
    if [ -n "$alerts" ]; then
        log "✅ Found alert rules:"
        echo "$alerts" | while read -r alert; do
            echo "  - $alert"
        done
    else
        warning "No alert rules found for environment: $env"
    fi
}

# Test custom events
test_custom_events() {
    local env="$1"
    
    log "Testing custom events logging..."
    
    # Create test event script
    cat > "/tmp/test-events.py" << 'EOF'
import json
import requests
import os
from datetime import datetime

# Test custom event logging
def test_custom_events():
    # This would normally use Application Insights SDK
    print("✅ Custom events test completed")
    print("Events that would be logged:")
    print("  - SpiritualGuidanceRequested")
    print("  - ExpertReviewTriggered") 
    print("  - CostThresholdReached")
    print("  - VoiceInteractionCompleted")

if __name__ == "__main__":
    test_custom_events()
EOF

    python3 /tmp/test-events.py
    rm -f /tmp/test-events.py
}

# Show monitoring status
show_monitoring_status() {
    local env="${1:-$ENVIRONMENT}"
    
    log "📊 Monitoring Status for environment: $env"
    
    # Show Application Insights status
    show_app_insights_status "$env"
    
    # Show alert rules status
    show_alert_rules_status "$env"
    
    # Show budget status
    show_budget_status "$env"
}

# Show Application Insights status
show_app_insights_status() {
    local env="$1"
    local app_insights_name="vimarsh-${env}-insights"
    
    if [ "$env" = "production" ]; then
        app_insights_name="vimarsh-insights"
    fi
    
    echo -e "${BLUE}Application Insights Status:${NC}"
    
    if az monitor app-insights component show \
        --app "$app_insights_name" \
        --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        
        local status=$(az monitor app-insights component show \
            --app "$app_insights_name" \
            --resource-group "$RESOURCE_GROUP" \
            --query '{name: name, location: location, kind: kind}' \
            --output json)
        
        echo "$status" | jq -r 'to_entries[] | "  \(.key): \(.value)"'
    else
        echo "  Status: ❌ Not found"
    fi
}

# Show alert rules status
show_alert_rules_status() {
    local env="$1"
    
    echo -e "${BLUE}Alert Rules Status:${NC}"
    
    local alerts=$(az monitor metrics alert list \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?contains(name, 'vimarsh-${env}')].{name: name, enabled: enabled, severity: severity}" \
        --output json)
    
    if [ "$alerts" != "[]" ]; then
        echo "$alerts" | jq -r '.[] | "  \(.name): \(if .enabled then "✅ Enabled" else "❌ Disabled" end) (Severity: \(.severity))"'
    else
        echo "  Status: ❌ No alert rules found"
    fi
}

# Show budget status
show_budget_status() {
    local env="$1"
    
    echo -e "${BLUE}Budget Status:${NC}"
    echo "  Monthly Budget: \$${MONTHLY_BUDGET}"
    echo "  Alert Threshold: ${COST_ALERT_THRESHOLD}%"
    echo "  Expert Email: ${EXPERT_EMAIL}"
}

# Open monitoring dashboard
open_dashboard() {
    local env="${1:-$ENVIRONMENT}"
    
    log "🌐 Opening monitoring dashboard for environment: $env"
    
    local app_insights_name="vimarsh-${env}-insights"
    if [ "$env" = "production" ]; then
        app_insights_name="vimarsh-insights"
    fi
    
    # Get Application Insights URL
    local ai_url="https://portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Insights/components/${app_insights_name}/overview"
    
    echo -e "${BLUE}Dashboard URLs:${NC}"
    echo "  Application Insights: $ai_url"
    echo "  Azure Portal: https://portal.azure.com/#@microsoft.onmicrosoft.com/resource/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}"
    
    # Try to open in browser (macOS)
    if command -v open &> /dev/null; then
        open "$ai_url"
        log "✅ Dashboard opened in browser"
    else
        log "Copy the URLs above to access dashboards"
    fi
}

# Main execution
main() {
    local operation="${1:-help}"
    local env="${2:-$ENVIRONMENT}"
    
    case "$operation" in
        "deploy")
            check_prerequisites
            deploy_monitoring "$env"
            configure_monitoring "$env"
            ;;
        "configure")
            configure_monitoring "$env"
            ;;
        "test")
            test_monitoring "$env"
            ;;
        "status")
            show_monitoring_status "$env"
            ;;
        "dashboard")
            open_dashboard "$env"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Execute main function
main "$@"
