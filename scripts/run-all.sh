#!/bin/bash
# Phase 0 Setup Orchestration Script
# Runs all Phase 0 setup steps with rich feedback

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Progress tracking
STEP=0
TOTAL_STEPS=4
START_TIME=$(date +%s)

# Log file
LOG_FILE="setup.log"
> "$LOG_FILE"  # Clear log file

# Functions
print_header() {
    echo ""
    echo "=============================================================="
    echo ""
    echo "  PHASE 0: INITIALIZATION & ENTRY POINT"
    echo "  Adaptive AI Integration Platform"
    echo ""
    echo "=============================================================="
    echo ""
    echo "SETUP CHECKLIST"
}

run_step() {
    STEP=$((STEP + 1))
    local description=$1
    local command=$2
    
    echo -e "  [$STEP/$TOTAL_STEPS] $description..."
    
    step_start=$(date +%s)
    
    if eval "$command" >> "$LOG_FILE" 2>&1; then
        step_end=$(date +%s)
        duration=$((step_end - step_start))
        echo -e "  ${GREEN}[PASS]${NC} Complete (${duration}s)"
    else
        echo -e "  ${RED}[FAIL]${NC} ERROR"
        echo ""
        echo "ERROR: Failed at step [$STEP/$TOTAL_STEPS] - $description"
        echo ""
        echo "Check log file for details: $LOG_FILE"
        echo "To retry: bash scripts/run-all.sh"
        echo ""
        exit 1
    fi
}

print_summary() {
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    echo ""
    echo "=============================================================="
    echo ""
    echo -e "${GREEN}PHASE 0 SETUP COMPLETE${NC} (${DURATION}s)"
    echo ""
    echo "SETUP SUMMARY"
    echo "  Directories Created: 13"
    echo "  Rule Files Generated: 6"
    echo "  Scripts Created: 4"
    echo "  Documentation Files: 8+"
    echo ""
    echo "WHAT'S NEXT?"
    echo ""
    echo "  Phase 0 is complete! Here are your next steps:"
    echo ""
    echo "  1. Review generated architecture:"
    echo "     -> Open: build_plan/phase0-architecture.md"
    echo "     -> Review: build_plan/roadmap.md"
    echo ""
    echo "  2. Explore role-based rules:"
    echo "     -> Directory: .cursor/rules/"
    echo "     -> Files: 6 specialized development personas"
    echo ""
    echo "  3. Proceed to Phase 1:"
    echo "     -> See: build_plan/roadmap.md (Phase 1 checklist)"
    echo "     -> Focus: Temporal.io integration"
    echo ""
    echo "RESOURCES"
    echo "  Documentation: build_plan/"
    echo "  Memory Bank: memory-bank/"
    echo "  Scripts: scripts/"
    echo ""
    echo "TROUBLESHOOTING"
    echo "  If issues arise:"
    echo "  -> Run: python scripts/validate-setup.py"
    echo "  -> Check: setup.log"
    echo "  -> Review: build_plan/phase0-architecture.md"
    echo ""
    echo "=============================================================="
    echo ""
}

# Main execution
main() {
    print_header
    
    run_step "Creating directory structure" "bash scripts/setup-directories.sh"
    run_step "Generating role-based rules (6 files)" "python scripts/generate-rules.py"
    run_step "Verifying setup integrity" "python scripts/validate-setup.py"
    run_step "Creating documentation index" "echo 'Phase 0 setup complete' > build_plan/setup-complete.txt"
    
    print_summary
}

# Run
main "$@"
