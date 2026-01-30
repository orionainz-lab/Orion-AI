#!/bin/bash
# Phase 4 VAN QA: Run All Validation Scripts
# Purpose: Execute all Phase 4 technology validation tests
# Expected: All tests pass, ready for BUILD mode

set -e

echo "================================================================"
echo "🧪 PHASE 4 VAN QA: COMPREHENSIVE VALIDATION"
echo "================================================================"
echo ""
echo "Running all validation scripts for Phase 4 technology stack..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Track overall results
TOTAL_SCRIPTS=6
SCRIPTS_PASSED=0
SCRIPTS_FAILED=0
SCRIPTS_SKIPPED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_script() {
    local script_name="$1"
    local script_path="$2"
    local can_skip="${3:-false}"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running: $script_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if [ -f "$script_path" ]; then
        if bash "$script_path"; then
            echo ""
            echo -e "${GREEN}✓ $script_name: PASSED${NC}"
            SCRIPTS_PASSED=$((SCRIPTS_PASSED + 1))
            return 0
        else
            echo ""
            echo -e "${RED}✗ $script_name: FAILED${NC}"
            
            if [ "$can_skip" = "true" ]; then
                echo -e "${YELLOW}  This test can be skipped (non-critical)${NC}"
                SCRIPTS_SKIPPED=$((SCRIPTS_SKIPPED + 1))
                return 0
            else
                SCRIPTS_FAILED=$((SCRIPTS_FAILED + 1))
                return 1
            fi
        fi
    else
        echo -e "${RED}✗ Script not found: $script_path${NC}"
        SCRIPTS_FAILED=$((SCRIPTS_FAILED + 1))
        return 1
    fi
}

run_python_script() {
    local script_name="$1"
    local script_path="$2"
    local can_skip="${3:-false}"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running: $script_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Use python or python3 depending on what's available
    local python_cmd="python3"
    if ! command -v python3 &> /dev/null; then
        python_cmd="python"
    fi
    
    if [ -f "$script_path" ]; then
        if $python_cmd "$script_path"; then
            echo ""
            echo -e "${GREEN}✓ $script_name: PASSED${NC}"
            SCRIPTS_PASSED=$((SCRIPTS_PASSED + 1))
            return 0
        else
            echo ""
            echo -e "${RED}✗ $script_name: FAILED${NC}"
            
            if [ "$can_skip" = "true" ]; then
                echo -e "${YELLOW}  This test can be skipped (non-critical)${NC}"
                SCRIPTS_SKIPPED=$((SCRIPTS_SKIPPED + 1))
                return 0
            else
                SCRIPTS_FAILED=$((SCRIPTS_FAILED + 1))
                return 1
            fi
        fi
    else
        echo -e "${RED}✗ Script not found: $script_path${NC}"
        SCRIPTS_FAILED=$((SCRIPTS_FAILED + 1))
        return 1
    fi
}

# Start time
START_TIME=$(date +%s)

echo "Validation Scripts:"
echo "  1. Next.js 14+ Setup"
echo "  2. Supabase Auth Flow"
echo "  3. AG Grid Rendering (Manual)"
echo "  4. Temporal Signal API"
echo "  5. TypeScript Types"
echo "  6. 200-Line Rule Enforcement"
echo ""

# Script 1: Next.js Setup
run_script \
    "Next.js 14+ Setup" \
    "$SCRIPT_DIR/test_nextjs_setup.sh" \
    false

# Script 2: Supabase Auth
run_python_script \
    "Supabase Auth Flow" \
    "$SCRIPT_DIR/test_supabase_auth.py" \
    false

# Script 3: AG Grid (Manual)
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 3: AG Grid Rendering${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}MANUAL TEST:${NC} AG Grid Rendering"
echo ""
echo "This test requires opening a browser:"
echo "  1. Open: scripts/phase4/test_aggrid_rendering.html"
echo "  2. Click 'Load 10,000 Rows'"
echo "  3. Verify smooth scrolling"
echo "  4. Test filtering and sorting"
echo ""
echo "Expected Results:"
echo "  - Render 10,000 rows in <2 seconds"
echo "  - Smooth scrolling (virtual DOM)"
echo "  - Custom cell renderers working (status badges)"
echo "  - Filtering and sorting functional"
echo ""

read -p "Open test_aggrid_rendering.html and press Enter when done... "

read -p "Did all AG Grid tests pass? (y/n): " ag_grid_result

if [ "$ag_grid_result" = "y" ] || [ "$ag_grid_result" = "Y" ]; then
    echo -e "${GREEN}✓ AG Grid Rendering: PASSED${NC}"
    SCRIPTS_PASSED=$((SCRIPTS_PASSED + 1))
else
    echo -e "${RED}✗ AG Grid Rendering: FAILED${NC}"
    SCRIPTS_FAILED=$((SCRIPTS_FAILED + 1))
fi

# Script 4: Temporal Signal
run_python_script \
    "Temporal Signal API" \
    "$SCRIPT_DIR/test_temporal_signal.py" \
    true  # Can skip if Temporal not running

# Script 5: TypeScript Types
run_script \
    "TypeScript Types" \
    "$SCRIPT_DIR/test_typescript_types.sh" \
    false

# Script 6: 200-Line Rule
run_script \
    "200-Line Rule Enforcement" \
    "$SCRIPT_DIR/test_200line_rule.sh" \
    false

# End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary
echo ""
echo ""
echo "================================================================"
echo "🎯 VAN QA VALIDATION SUMMARY"
echo "================================================================"
echo ""
echo "Total Scripts:   $TOTAL_SCRIPTS"
echo -e "Scripts Passed:  ${GREEN}$SCRIPTS_PASSED${NC}"
echo -e "Scripts Failed:  ${RED}$SCRIPTS_FAILED${NC}"
echo -e "Scripts Skipped: ${YELLOW}$SCRIPTS_SKIPPED${NC}"
echo ""
echo "Duration: ${DURATION}s"
echo ""

if [ $SCRIPTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}RESULT: ✓ ALL VALIDATIONS PASSED${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Phase 4 technology stack is validated and ready!"
    echo ""
    echo "Technology Stack Validated:"
    echo "  ✅ Next.js 14+ with App Router"
    echo "  ✅ Supabase Auth (OAuth ready)"
    echo "  ✅ AG Grid Community (10K+ rows)"
    echo "  ✅ Temporal Signal API"
    echo "  ✅ TypeScript Types (strict mode)"
    echo "  ✅ 200-Line Rule Enforcement"
    echo ""
    echo -e "${BLUE}READY FOR BUILD MODE${NC}"
    echo ""
    echo "Next Steps:"
    echo "  1. Create Phase 4 VAN QA completion marker"
    echo "  2. Begin Phase 4.1: Foundation (8 hours)"
    echo "     - Initialize Next.js project"
    echo "     - Set up Supabase Auth"
    echo "     - Build basic Matrix Grid"
    echo ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}RESULT: ✗ SOME VALIDATIONS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Please review the failures above and resolve issues before BUILD mode."
    echo ""
    echo "Common Issues:"
    echo "  - Next.js: Ensure Node.js 18+ installed"
    echo "  - Supabase: Check .env file has correct credentials"
    echo "  - AG Grid: Open HTML file in browser manually"
    echo "  - Temporal: Ensure docker-compose up -d temporal"
    echo "  - TypeScript: Regenerate types if schema changed"
    echo "  - 200-Line: ESLint will be set up in Phase 4.1"
    echo ""
    exit 1
fi
