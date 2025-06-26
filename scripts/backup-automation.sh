#!/bin/bash

# Vimarsh Backup Automation Setup
# Sets up cron jobs for automated backup and monitoring

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CRON_FILE="/tmp/vimarsh-backup-cron"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() { echo -e "${GREEN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Help function
show_help() {
    cat << EOF
Vimarsh Backup Automation Setup

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    install             Install backup automation cron jobs
    uninstall           Remove backup automation cron jobs
    status              Show current cron job status
    test                Test backup automation scripts
    help                Show this help message

OPTIONS:
    --environment ENV   Target environment (dev, staging, prod)
    --email EMAIL       Email for backup notifications
    --dry-run          Show what would be done without executing

EXAMPLES:
    $0 install --environment prod --email admin@vimarsh.app
    $0 status
    $0 test --environment dev

EOF
}

# Install cron jobs
install_cron_jobs() {
    local environment="$1"
    local email="${2:-admin@vimarsh.app}"
    
    info "Installing backup automation for environment: $environment"
    
    # Create log directory
    mkdir -p "$PROJECT_ROOT/logs/backup"
    
    # Create cron job configuration
    cat > "$CRON_FILE" << EOF
# Vimarsh Backup Automation - Environment: $environment
# Generated on: $(date)

# Set environment variables
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=$email

# Daily backup at 2 AM
0 2 * * * $PROJECT_ROOT/scripts/disaster-recovery.sh backup --environment $environment >> $PROJECT_ROOT/logs/backup/daily-backup.log 2>&1

# Weekly validation on Sundays at 3 AM
0 3 * * 0 $PROJECT_ROOT/scripts/disaster-recovery.sh validate --environment $environment >> $PROJECT_ROOT/logs/backup/weekly-validation.log 2>&1

# Monthly DR test on first Sunday at 4 AM (non-production only)
EOF

    if [[ "$environment" != "prod" ]]; then
        cat >> "$CRON_FILE" << EOF
0 4 1-7 * 0 $PROJECT_ROOT/scripts/disaster-recovery.sh test-dr --environment $environment >> $PROJECT_ROOT/logs/backup/monthly-dr-test.log 2>&1
EOF
    fi
    
    cat >> "$CRON_FILE" << EOF

# Daily status check at 6 AM
0 6 * * * $PROJECT_ROOT/scripts/disaster-recovery.sh status --environment $environment >> $PROJECT_ROOT/logs/backup/daily-status.log 2>&1

# Cleanup old logs (keep 30 days)
0 1 * * * find $PROJECT_ROOT/logs/backup -name "*.log" -mtime +30 -delete

EOF
    
    # Install cron jobs
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would install the following cron jobs:"
        cat "$CRON_FILE"
    else
        crontab "$CRON_FILE"
        info "Backup automation cron jobs installed successfully"
        info "Logs will be written to: $PROJECT_ROOT/logs/backup/"
        info "Email notifications will be sent to: $email"
    fi
    
    # Clean up temporary file
    rm -f "$CRON_FILE"
}

# Uninstall cron jobs
uninstall_cron_jobs() {
    info "Removing Vimarsh backup automation cron jobs..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        info "DRY RUN: Would remove Vimarsh backup cron jobs"
        return 0
    fi
    
    # Get current crontab
    if crontab -l 2>/dev/null > "$CRON_FILE"; then
        # Remove Vimarsh backup automation lines
        grep -v "Vimarsh Backup Automation" "$CRON_FILE" | \
        grep -v "disaster-recovery.sh" | \
        grep -v "# Generated on:" | \
        crontab -
        
        info "Backup automation cron jobs removed successfully"
    else
        warn "No existing crontab found"
    fi
    
    # Clean up temporary file
    rm -f "$CRON_FILE"
}

# Show cron job status
show_cron_status() {
    info "Current Vimarsh backup automation status:"
    echo
    
    if crontab -l 2>/dev/null | grep -q "disaster-recovery.sh"; then
        echo "✓ Backup automation is ACTIVE"
        echo
        echo "Active cron jobs:"
        crontab -l 2>/dev/null | grep -A 20 "Vimarsh Backup Automation" || true
    else
        echo "✗ Backup automation is NOT ACTIVE"
        echo
        echo "To install backup automation, run:"
        echo "  $0 install --environment [ENV] --email [EMAIL]"
    fi
    
    echo
    echo "Recent backup logs:"
    if [[ -d "$PROJECT_ROOT/logs/backup" ]]; then
        ls -la "$PROJECT_ROOT/logs/backup" | head -10
    else
        echo "No backup logs found"
    fi
}

# Test backup automation
test_backup_automation() {
    local environment="$1"
    
    info "Testing backup automation for environment: $environment"
    
    # Test disaster recovery script
    info "Testing disaster recovery script..."
    if "$PROJECT_ROOT/scripts/disaster-recovery.sh" validate --environment "$environment" --dry-run; then
        echo "✓ Disaster recovery script test passed"
    else
        error "✗ Disaster recovery script test failed"
        return 1
    fi
    
    # Test log directory creation
    info "Testing log directory..."
    mkdir -p "$PROJECT_ROOT/logs/backup"
    if [[ -d "$PROJECT_ROOT/logs/backup" ]]; then
        echo "✓ Log directory test passed"
    else
        error "✗ Log directory test failed"
        return 1
    fi
    
    # Test cron syntax
    info "Testing cron syntax..."
    local test_cron_file="/tmp/vimarsh-test-cron"
    cat > "$test_cron_file" << EOF
# Test cron job
0 2 * * * echo "test" >> /tmp/vimarsh-test.log
EOF
    
    # Test cron syntax by trying to parse it
    if command -v crontab >/dev/null 2>&1; then
        # Some systems support -T flag for syntax testing
        if crontab -T "$test_cron_file" 2>/dev/null; then
            echo "✓ Cron syntax test passed"
        else
            # Fallback: check basic cron syntax manually
            if grep -q "^[0-9*/-]* [0-9*/-]* [0-9*/-]* [0-9*/-]* [0-9*/-]* " "$test_cron_file"; then
                echo "✓ Cron syntax test passed (manual validation)"
            else
                error "✗ Cron syntax test failed"
                return 1
            fi
        fi
    else
        warn "Crontab not available, skipping syntax test"
    fi
    
    rm -f "$test_cron_file"
    
    info "All backup automation tests passed successfully"
}

# Parse command line arguments
COMMAND=""
ENVIRONMENT=""
EMAIL=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        install|uninstall|status|test|help)
            COMMAND="$1"
            shift
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --email)
            EMAIL="$2"
            shift 2
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

if [[ "$COMMAND" == "install" || "$COMMAND" == "test" ]] && [[ -z "$ENVIRONMENT" ]]; then
    error "Environment is required for $COMMAND command"
    show_help
    exit 1
fi

# Main execution
case "$COMMAND" in
    install)
        install_cron_jobs "$ENVIRONMENT" "$EMAIL"
        ;;
    uninstall)
        uninstall_cron_jobs
        ;;
    status)
        show_cron_status
        ;;
    test)
        test_backup_automation "$ENVIRONMENT"
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
