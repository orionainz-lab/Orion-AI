#!/bin/bash
# Rate Limiting Load Test Runner

set -e

echo "=================================================="
echo "  RATE LIMITING LOAD TEST"
echo "=================================================="
echo ""

# Check if locust is installed
if ! command -v locust &> /dev/null; then
    echo "❌ Error: locust is not installed"
    echo "   Run: pip install locust"
    exit 1
fi

# Check environment variables
if [ -z "$SUPABASE_URL" ]; then
    echo "⚠️  Warning: SUPABASE_URL not set, loading from .env"
    if [ -f .env ]; then
        export $(cat .env | grep -v ^# | xargs)
    fi
fi

# Set test parameters
HOST="${1:-http://localhost:8000}"
USERS="${2:-50}"
SPAWN_RATE="${3:-10}"
RUN_TIME="${4:-60s}"

echo "Test Configuration:"
echo "  Host: $HOST"
echo "  Users: $USERS"
echo "  Spawn Rate: $SPAWN_RATE users/second"
echo "  Duration: $RUN_TIME"
echo ""

# Create results directory
mkdir -p test-results/load-tests

# Run locust
echo "Starting load test..."
echo ""

locust \
    -f scripts/load_tests/rate_limiting.py \
    --headless \
    --host="$HOST" \
    --users="$USERS" \
    --spawn-rate="$SPAWN_RATE" \
    --run-time="$RUN_TIME" \
    --html=test-results/load-tests/rate-limiting-report.html \
    --csv=test-results/load-tests/rate-limiting

echo ""
echo "=================================================="
echo "  TEST COMPLETE"
echo "=================================================="
echo ""
echo "Results saved to:"
echo "  - test-results/load-tests/rate-limiting-report.html"
echo "  - test-results/load-tests/rate-limiting_stats.csv"
echo ""
