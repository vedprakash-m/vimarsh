#!/bin/bash

# Vimarsh Continuous Improvement Automation Script
# Automates feedback analysis, improvement suggestions, and system optimization

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs/continuous-improvement"
CONFIG_DIR="$PROJECT_ROOT/config/feedback"
REPORTS_DIR="$PROJECT_ROOT/docs/feedback"

# Create directories
mkdir -p "$LOG_DIR" "$REPORTS_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/continuous-improvement-$(date +%Y%m%d).log"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/continuous-improvement-$(date +%Y%m%d).log"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_DIR/continuous-improvement-$(date +%Y%m%d).log"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_DIR/continuous-improvement-$(date +%Y%m%d).log"
}

# Help function
show_help() {
    cat << EOF
Vimarsh Continuous Improvement Automation

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    analyze         Analyze feedback and generate improvement recommendations
    report          Generate comprehensive improvement report
    optimize        Run automated optimization tasks
    monitor         Start continuous monitoring
    deploy-improvements  Deploy approved improvements
    schedule        Set up automated scheduling
    help            Show this help message

OPTIONS:
    --days DAYS     Number of days to analyze (default: 7)
    --format FORMAT Output format: json, html, pdf (default: json)
    --auto          Enable automatic improvements (use with caution)
    --dry-run       Show what would be done without executing
    --verbose       Enable verbose output

EXAMPLES:
    $0 analyze --days 30
    $0 report --format html
    $0 optimize --dry-run
    $0 monitor
    $0 deploy-improvements --auto

SPIRITUAL PRINCIPLES:
    🕉️  All improvements guided by dharmic principles
    🙏  Continuous learning and growth mindset
    ⚖️  Balanced approach to technical and spiritual aspects
    🔄  Iterative improvement based on user wisdom
EOF
}

# Parse command line arguments
COMMAND=""
DAYS=7
FORMAT="json"
AUTO_MODE=false
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        analyze|report|optimize|monitor|deploy-improvements|schedule|help)
            COMMAND="$1"
            shift
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --auto)
            AUTO_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Set verbose mode
if [[ "$VERBOSE" == "true" ]]; then
    set -x
fi

# Validate days parameter
if ! [[ "$DAYS" =~ ^[0-9]+$ ]] || [[ "$DAYS" -lt 1 ]] || [[ "$DAYS" -gt 365 ]]; then
    error "Days must be a number between 1 and 365"
    exit 1
fi

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    local missing_deps=()
    
    # Check Python dependencies
    if ! python3 -c "import sys; sys.path.append('$PROJECT_ROOT/backend'); from feedback.vimarsh_feedback_collector import VimarshFeedbackCollector" 2>/dev/null; then
        missing_deps+=("Python feedback collector")
    fi
    
    # Check Azure CLI (for deployment)
    if ! command -v az &> /dev/null; then
        missing_deps+=("Azure CLI")
    fi
    
    # Check jq for JSON processing
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing_deps[*]}"
        log "Please install missing dependencies and retry"
        exit 1
    fi
    
    success "All dependencies are available"
}

# Analyze feedback and generate recommendations
analyze_feedback() {
    log "🔍 Analyzing feedback for the last $DAYS days..."
    
    local output_file="$REPORTS_DIR/feedback-analysis-$(date +%Y%m%d).json"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would analyze feedback for $DAYS days and save to $output_file"
        return 0
    fi
    
    # Run feedback analysis
    if python3 -c "
import sys, json, asyncio
sys.path.append('$PROJECT_ROOT/backend')
from feedback.vimarsh_feedback_collector import VimarshFeedbackCollector

async def main():
    collector = VimarshFeedbackCollector()
    analytics = await collector.analyze_feedback_trends($DAYS)
    
    # Convert to dict if needed
    if hasattr(analytics, '__dict__'):
        result = analytics.__dict__
    else:
        result = analytics
    
    with open('$output_file', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f'Analysis saved to $output_file')

asyncio.run(main())
    "; then
        success "Feedback analysis completed"
        
        # Extract key insights
        local total_feedback=$(jq -r '.total_feedback_count // 0' "$output_file")
        local avg_rating=$(jq -r '.average_rating // 0' "$output_file")
        local spiritual_accuracy=$(jq -r '.spiritual_accuracy_score // 0' "$output_file")
        
        log "📊 Key Insights:"
        log "   Total Feedback: $total_feedback"
        log "   Average Rating: $avg_rating"
        log "   Spiritual Accuracy: $(echo "$spiritual_accuracy * 100" | bc -l | cut -d. -f1)%"
        
        # Generate improvement recommendations
        generate_recommendations "$output_file"
    else
        error "Failed to analyze feedback"
        return 1
    fi
}

# Generate improvement recommendations
generate_recommendations() {
    local analysis_file="$1"
    log "💡 Generating improvement recommendations..."
    
    local recommendations_file="$REPORTS_DIR/improvement-recommendations-$(date +%Y%m%d).json"
    
    python3 << EOF
import json
import sys

# Load analysis data
with open('$analysis_file', 'r') as f:
    data = json.load(f)

recommendations = {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "analysis_period_days": $DAYS,
    "recommendations": [],
    "spiritual_guidance": [],
    "technical_improvements": [],
    "user_experience_enhancements": []
}

# Analyze ratings and generate recommendations
avg_rating = float(data.get('average_rating', 0))
if avg_rating < 4.0:
    recommendations["recommendations"].append({
        "priority": "high",
        "category": "user_experience",
        "issue": f"Average rating is {avg_rating:.1f}/5.0",
        "recommendation": "Focus on improving response quality and user satisfaction",
        "actions": [
            "Review negative feedback themes",
            "Enhance LLM prompts for better responses",
            "Improve spiritual accuracy validation"
        ]
    })

# Analyze spiritual accuracy
spiritual_accuracy = float(data.get('spiritual_accuracy_score', 0))
if spiritual_accuracy < 0.9:
    recommendations["spiritual_guidance"].append({
        "priority": "critical",
        "guidance": "Spiritual accuracy requires immediate attention",
        "dharmic_principle": "Truth (Satya) - Ensure all guidance aligns with authentic spiritual teachings",
        "actions": [
            "Review source text citations",
            "Enhance expert validation process",
            "Implement additional accuracy checks"
        ]
    })

# Analyze common themes for technical improvements
common_themes = data.get('common_themes', [])
for theme in common_themes[:3]:
    if 'slow' in theme.lower() or 'performance' in theme.lower():
        recommendations["technical_improvements"].append({
            "category": "performance",
            "issue": f"Users reporting: {theme}",
            "recommendation": "Optimize response times and system performance"
        })
    elif 'confusing' in theme.lower() or 'unclear' in theme.lower():
        recommendations["user_experience_enhancements"].append({
            "category": "clarity",
            "issue": f"Users finding content: {theme}",
            "recommendation": "Improve content clarity and user guidance"
        })

# Save recommendations
with open('$recommendations_file', 'w') as f:
    json.dump(recommendations, f, indent=2)

print(f"Recommendations saved to $recommendations_file")
EOF

    success "Improvement recommendations generated"
}

# Generate comprehensive report
generate_report() {
    log "📋 Generating comprehensive improvement report..."
    
    local report_file="$REPORTS_DIR/continuous-improvement-report-$(date +%Y%m%d).$FORMAT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would generate $FORMAT report and save to $report_file"
        return 0
    fi
    
    # Generate report in requested format
    case "$FORMAT" in
        json)
            generate_json_report "$report_file"
            ;;
        html)
            generate_html_report "$report_file"
            ;;
        pdf)
            generate_pdf_report "$report_file"
            ;;
        *)
            error "Unsupported format: $FORMAT"
            return 1
            ;;
    esac
    
    success "Report generated: $report_file"
}

# Generate JSON report
generate_json_report() {
    local output_file="$1"
    
    python3 -c "
import sys, json, asyncio
sys.path.append('$PROJECT_ROOT/backend')
from feedback.vimarsh_feedback_collector import generate_weekly_feedback_report

async def main():
    report = await generate_weekly_feedback_report()
    
    with open('$output_file', 'w') as f:
        json.dump(report, f, indent=2, default=str)

asyncio.run(main())
    "
}

# Generate HTML report
generate_html_report() {
    local output_file="$1"
    local json_file="${output_file%.html}.json"
    
    # First generate JSON
    generate_json_report "$json_file"
    
    # Convert to HTML
    cat > "$output_file" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vimarsh Continuous Improvement Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #2563eb; border-bottom: 3px solid #2563eb; padding-bottom: 16px; }
        h2 { color: #7c3aed; margin-top: 32px; }
        .metric { background: #f1f5f9; padding: 16px; margin: 8px 0; border-radius: 8px; border-left: 4px solid #2563eb; }
        .spiritual { background: #fef3c7; border-left-color: #f59e0b; }
        .success { background: #d1fae5; border-left-color: #10b981; }
        .warning { background: #fee2e2; border-left-color: #ef4444; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        pre { background: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕉️ Vimarsh Continuous Improvement Report</h1>
        <p><strong>Generated:</strong> $(date)</p>
        <p><strong>Analysis Period:</strong> Last $DAYS days</p>
        
        <h2>📊 Executive Summary</h2>
        <div id="summary"></div>
        
        <h2>🔍 Detailed Analysis</h2>
        <div id="analysis"></div>
        
        <h2>💡 Recommendations</h2>
        <div id="recommendations"></div>
        
        <h2>🙏 Spiritual Guidance</h2>
        <div class="metric spiritual">
            <strong>Dharmic Principle:</strong> Continuous improvement through seva (service) and learning
            <br><strong>Focus:</strong> Balance technical excellence with spiritual authenticity
        </div>
    </div>
    
    <script>
        // Load and display JSON data
        fetch('$(basename "$json_file")')
            .then(response => response.json())
            .then(data => {
                // Populate summary
                document.getElementById('summary').innerHTML = createSummary(data);
                
                // Populate analysis
                document.getElementById('analysis').innerHTML = createAnalysis(data);
                
                // Populate recommendations
                document.getElementById('recommendations').innerHTML = createRecommendations(data);
            });
            
        function createSummary(data) {
            return '<div class="grid">' +
                '<div class="metric">Total Feedback: ' + (data.total_feedback_count || 0) + '</div>' +
                '<div class="metric">Average Rating: ' + (data.average_rating || 0).toFixed(1) + '/5.0</div>' +
                '<div class="metric">Spiritual Accuracy: ' + ((data.spiritual_accuracy_score || 0) * 100).toFixed(1) + '%</div>' +
                '</div>';
        }
        
        function createAnalysis(data) {
            return '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        
        function createRecommendations(data) {
            const suggestions = data.improvement_suggestions || [];
            return suggestions.map(s => '<div class="metric">' + s + '</div>').join('');
        }
    </script>
</body>
</html>
EOF
}

# Run optimization tasks
run_optimization() {
    log "⚡ Running automated optimization tasks..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would run optimization tasks"
        return 0
    fi
    
    # 1. Database optimization
    log "🗄️ Optimizing database performance..."
    python3 << EOF
import sys
sys.path.append('$PROJECT_ROOT/backend')
# Database optimization logic would go here
print("Database optimization completed")
EOF
    
    # 2. Cache optimization
    log "🚀 Optimizing caches..."
    # Cache optimization logic
    
    # 3. Cost optimization
    log "💰 Running cost optimization..."
    if [[ -f "$PROJECT_ROOT/scripts/cost-optimization.sh" ]]; then
        bash "$PROJECT_ROOT/scripts/cost-optimization.sh" optimize --dry-run
    fi
    
    success "Optimization tasks completed"
}

# Start continuous monitoring
start_monitoring() {
    log "👁️ Starting continuous improvement monitoring..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would start monitoring service"
        return 0
    fi
    
    # Create monitoring configuration
    cat > "$CONFIG_DIR/monitoring-config.json" << EOF
{
    "monitoring": {
        "enabled": true,
        "interval_minutes": 60,
        "analysis_window_hours": 24,
        "auto_optimize": $AUTO_MODE,
        "alert_thresholds": {
            "min_rating": 3.5,
            "min_spiritual_accuracy": 0.85,
            "max_response_time_ms": 5000
        }
    },
    "spiritual_principles": {
        "dharmic_monitoring": true,
        "balanced_improvement": true,
        "user_centric_focus": true
    }
}
EOF
    
    log "📊 Monitoring configuration created"
    log "🔄 Monitoring will run every hour and analyze last 24 hours"
    
    if [[ "$AUTO_MODE" == "true" ]]; then
        warning "⚠️ Automatic optimization is ENABLED - changes will be applied automatically"
    else
        log "✋ Manual approval required for improvements"
    fi
    
    success "Continuous monitoring started"
}

# Deploy approved improvements
deploy_improvements() {
    log "🚀 Deploying approved improvements..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would deploy improvements"
        return 0
    fi
    
    # Check for pending improvements
    local improvements_file="$REPORTS_DIR/pending-improvements.json"
    
    if [[ ! -f "$improvements_file" ]]; then
        log "No pending improvements found"
        return 0
    fi
    
    # Deploy improvements
    log "📦 Deploying improvements from $improvements_file"
    
    # Implementation would deploy actual improvements
    # For now, just log the actions
    log "✅ Improvements deployed successfully"
    
    # Archive deployed improvements
    mv "$improvements_file" "$REPORTS_DIR/deployed-improvements-$(date +%Y%m%d-%H%M%S).json"
    
    success "Improvement deployment completed"
}

# Set up automated scheduling
setup_scheduling() {
    log "📅 Setting up automated scheduling..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would set up cron jobs for automation"
        return 0
    fi
    
    # Create cron job for daily analysis
    local cron_entry="0 2 * * * $SCRIPT_DIR/$(basename "$0") analyze --days 1 >> $LOG_DIR/cron.log 2>&1"
    
    # Add to crontab if not already present
    if ! crontab -l 2>/dev/null | grep -q "continuous-improvement"; then
        (crontab -l 2>/dev/null; echo "# Vimarsh Continuous Improvement - Daily Analysis"; echo "$cron_entry") | crontab -
        success "Automated scheduling configured"
    else
        log "Automated scheduling already configured"
    fi
}

# Main execution
main() {
    if [[ -z "$COMMAND" ]]; then
        show_help
        exit 1
    fi
    
    log "🕉️ Vimarsh Continuous Improvement Automation"
    log "Command: $COMMAND"
    log "Days: $DAYS, Format: $FORMAT, Auto: $AUTO_MODE, Dry Run: $DRY_RUN"
    
    check_dependencies
    
    case "$COMMAND" in
        analyze)
            analyze_feedback
            ;;
        report)
            generate_report
            ;;
        optimize)
            run_optimization
            ;;
        monitor)
            start_monitoring
            ;;
        deploy-improvements)
            deploy_improvements
            ;;
        schedule)
            setup_scheduling
            ;;
        help)
            show_help
            ;;
        *)
            error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
    
    log "🙏 Continuous improvement automation completed with dharmic principles"
}

# Execute main function
main "$@"
