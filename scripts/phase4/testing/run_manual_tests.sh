#!/bin/bash

# ================================================================
# Phase 4.2/4.3 Manual Testing Script
# ================================================================
# Purpose: Run all manual tests for real-time and Temporal integration
# Usage: ./run_manual_tests.sh
# ================================================================

set -e

echo "================================================================"
echo "PHASE 4.2/4.3 MANUAL TESTING"
echo "================================================================"

# Navigate to project root
cd "$(dirname "$0")/../../.."
PROJECT_ROOT=$(pwd)

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python not found${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[INFO] Using Python: $PYTHON_CMD${NC}"

# ================================================================
# PRE-FLIGHT CHECKS
# ================================================================

echo -e "\n${YELLOW}=== PRE-FLIGHT CHECKS ===${NC}"

# Check 1: Supabase running
echo -n "Checking Supabase connection... "
TESTS_RUN=$((TESTS_RUN + 1))
if curl -s http://127.0.0.1:54321/rest/v1/ > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    echo -e "${YELLOW}[HINT] Start Supabase: cd docker && docker-compose up -d${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Check 2: Temporal running
echo -n "Checking Temporal connection... "
TESTS_RUN=$((TESTS_RUN + 1))
if curl -s http://localhost:7233/ > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    echo -e "${YELLOW}[HINT] Start Temporal: cd docker && docker-compose up -d${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Check 3: Frontend dependencies
echo -n "Checking frontend dependencies... "
TESTS_RUN=$((TESTS_RUN + 1))
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    echo -e "${YELLOW}[HINT] Install dependencies: cd frontend && npm install${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Check 4: Environment variables
echo -n "Checking frontend .env.local... "
TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "frontend/.env.local" ]; then
    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    echo -e "${YELLOW}[HINT] Create frontend/.env.local with Supabase credentials${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ================================================================
# TEST 1: SEED TEST DATA
# ================================================================

echo -e "\n${YELLOW}=== TEST 1: SEED TEST DATA ===${NC}"
echo "This test will insert sample proposals into Supabase"
echo "Location: scripts/phase4/testing/seed_test_data.sql"
echo ""
echo -e "${YELLOW}[ACTION REQUIRED] Please run the SQL script manually:${NC}"
echo "  1. Open Supabase Dashboard: http://127.0.0.1:54323"
echo "  2. Go to SQL Editor"
echo "  3. Copy/paste the contents of: scripts/phase4/testing/seed_test_data.sql"
echo "  4. Click 'Run'"
echo ""
read -p "Press Enter after you've run the SQL script..."

TESTS_RUN=$((TESTS_RUN + 1))
echo -e "${GREEN}PASS (Manual)${NC} - Test data seeded"
TESTS_PASSED=$((TESTS_PASSED + 1))

# ================================================================
# TEST 2: FRONTEND STARTUP
# ================================================================

echo -e "\n${YELLOW}=== TEST 2: FRONTEND STARTUP ===${NC}"
echo "Starting Next.js development server..."

# Check if server is already running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}Frontend already running on http://localhost:3000${NC}"
else
    echo -e "${YELLOW}[INFO] Starting frontend in background...${NC}"
    cd frontend
    npm run dev > /dev/null 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for server to start
    echo "Waiting for server to start..."
    sleep 10
    
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC} - Frontend started (PID: $FRONTEND_PID)"
        TESTS_RUN=$((TESTS_RUN + 1))
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} - Frontend failed to start"
        TESTS_RUN=$((TESTS_RUN + 1))
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
fi

# ================================================================
# TEST 3: DASHBOARD STATS
# ================================================================

echo -e "\n${YELLOW}=== TEST 3: DASHBOARD STATS ===${NC}"
echo -e "${YELLOW}[ACTION REQUIRED] Manual verification:${NC}"
echo "  1. Open: http://localhost:3000"
echo "  2. Verify stats cards show:"
echo "     - Total Proposals (should be > 0)"
echo "     - Approved count"
echo "     - Pending count"
echo "     - Rejected count"
echo "  3. Verify 'System Status' shows all green"
echo ""
read -p "Do the stats look correct? (y/n): " -n 1 -r
echo ""

TESTS_RUN=$((TESTS_RUN + 1))
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}PASS${NC} - Dashboard stats working"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC} - Dashboard stats not working"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ================================================================
# TEST 4: MATRIX GRID DATA
# ================================================================

echo -e "\n${YELLOW}=== TEST 4: MATRIX GRID DATA ===${NC}"
echo -e "${YELLOW}[ACTION REQUIRED] Manual verification:${NC}"
echo "  1. Open: http://localhost:3000/matrix"
echo "  2. Verify proposals are displayed"
echo "  3. Verify status badges (pending, approved, rejected)"
echo "  4. Verify action buttons on pending proposals"
echo "  5. Try sorting and filtering"
echo ""
read -p "Is the Matrix Grid displaying data correctly? (y/n): " -n 1 -r
echo ""

TESTS_RUN=$((TESTS_RUN + 1))
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}PASS${NC} - Matrix Grid data loading"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC} - Matrix Grid data not loading"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ================================================================
# TEST 5: PROPOSAL MODAL
# ================================================================

echo -e "\n${YELLOW}=== TEST 5: PROPOSAL MODAL ===${NC}"
echo -e "${YELLOW}[ACTION REQUIRED] Manual verification:${NC}"
echo "  1. Click on any proposal row in the Matrix Grid"
echo "  2. Verify modal opens with:"
echo "     - Status badge"
echo "     - Event information"
echo "     - Metadata (JSON)"
echo "  3. Click outside or close button to dismiss"
echo ""
read -p "Does the proposal modal work correctly? (y/n): " -n 1 -r
echo ""

TESTS_RUN=$((TESTS_RUN + 1))
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}PASS${NC} - Proposal modal working"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC} - Proposal modal not working"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ================================================================
# TEST 6: REALTIME SUBSCRIPTIONS
# ================================================================

echo -e "\n${YELLOW}=== TEST 6: REALTIME SUBSCRIPTIONS ===${NC}"
echo "Testing Supabase Realtime with INSERT/UPDATE/DELETE..."
echo "Keep the Matrix Grid open in your browser!"
echo ""
echo -e "${YELLOW}[INFO] Running realtime test script...${NC}"

TESTS_RUN=$((TESTS_RUN + 1))
if $PYTHON_CMD scripts/phase4/testing/test_realtime_subscriptions.py; then
    echo ""
    echo -e "${YELLOW}[ACTION REQUIRED] Did you see the following in the Matrix Grid?${NC}"
    echo "  1. New proposal appeared instantly"
    echo "  2. Status changed to 'approved'"
    echo "  3. Proposal disappeared after delete"
    echo "  4. Toast notifications appeared"
    echo ""
    read -p "Did realtime updates work? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}PASS${NC} - Realtime subscriptions working"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAIL${NC} - Realtime subscriptions not working"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${RED}FAIL${NC} - Realtime test script failed"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ================================================================
# TEST 7: TEMPORAL SIGNAL API
# ================================================================

echo -e "\n${YELLOW}=== TEST 7: TEMPORAL SIGNAL API ===${NC}"
echo "This will start a test workflow and wait for signals..."
echo -e "${YELLOW}[INFO] Starting Temporal test workflow...${NC}"
echo ""
echo "NOTE: This test will run in background. You'll test signals via the UI."
echo ""

TESTS_RUN=$((TESTS_RUN + 1))

# Start the Temporal test in background with timeout
timeout 60s $PYTHON_CMD scripts/phase4/testing/test_temporal_signal.py &
TEMPORAL_TEST_PID=$!

echo "Workflow started (PID: $TEMPORAL_TEST_PID)"
echo ""
echo -e "${YELLOW}[ACTION REQUIRED] Test Approve/Reject buttons:${NC}"
echo "  1. In Matrix Grid, find a PENDING proposal"
echo "  2. Click the green checkmark (Approve) button"
echo "  3. Verify:"
echo "     - Toast notification appears"
echo "     - Status badge changes to 'approved'"
echo "  4. Find another PENDING proposal"
echo "  5. Click the red X (Reject) button"
echo "  6. Verify status changes to 'rejected'"
echo ""
read -p "Did the Approve/Reject actions work? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}PASS${NC} - Temporal signal API working"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC} - Temporal signal API not working"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Kill the background Temporal test
kill $TEMPORAL_TEST_PID 2>/dev/null || true

# ================================================================
# TEST 8: NOTIFICATION TOASTS
# ================================================================

echo -e "\n${YELLOW}=== TEST 8: NOTIFICATION TOASTS ===${NC}"
echo -e "${YELLOW}[ACTION REQUIRED] Manual verification:${NC}"
echo "  1. Trigger various actions (approve, reject, export CSV)"
echo "  2. Verify toast notifications appear in top-right"
echo "  3. Verify they auto-dismiss after 5 seconds"
echo "  4. Verify you can manually close them"
echo "  5. Verify correct colors (green=success, red=error)"
echo ""
read -p "Are notifications working correctly? (y/n): " -n 1 -r
echo ""

TESTS_RUN=$((TESTS_RUN + 1))
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}PASS${NC} - Notification system working"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAIL${NC} - Notification system not working"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# ================================================================
# TEST SUMMARY
# ================================================================

echo ""
echo "================================================================"
echo "TEST SUMMARY"
echo "================================================================"
echo "Tests Run:    $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}ALL TESTS PASSED! ✅${NC}"
    echo ""
    echo "Phase 4.2 features are fully functional:"
    echo "  ✅ Dashboard with real stats"
    echo "  ✅ Matrix Grid with real data"
    echo "  ✅ Realtime subscriptions"
    echo "  ✅ Temporal signal API"
    echo "  ✅ Approve/Reject actions"
    echo "  ✅ Proposal modal"
    echo "  ✅ Notification toasts"
    exit 0
else
    echo -e "${RED}SOME TESTS FAILED ❌${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "  1. Check Supabase/Temporal are running"
    echo "  2. Verify environment variables"
    echo "  3. Check browser console for errors"
    echo "  4. Review test output for hints"
    exit 1
fi
