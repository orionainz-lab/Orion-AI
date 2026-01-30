#!/bin/bash
# Phase 0: Directory Structure Setup
# Creates all required directories for the project

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories to create
DIRECTORIES=(
    "memory-bank"
    "memory-bank/creative"
    "memory-bank/reflection"
    "memory-bank/archive"
    "build_plan"
    "build_plan/adrs"
    "scripts"
    "services"
    "utils"
    ".cursor/rules"
    "temporal/workflows"
    "temporal/activities"
    "temporal/workers"
    "connectors/unified_schema"
    "connectors/adapters"
    "frontend/components"
    "frontend/app"
    "docker"
)

echo "Creating project directory structure..."

# Create each directory
for dir in "${DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${BLUE}[SKIP]${NC} $dir (already exists)"
    else
        mkdir -p "$dir"
        echo -e "${GREEN}[CREATED]${NC} $dir"
    fi
done

echo ""
echo -e "${GREEN}Directory structure setup complete!${NC}"
echo ""
echo "Total directories: ${#DIRECTORIES[@]}"
echo ""
