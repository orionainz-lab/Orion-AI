# Scripts Directory

**Purpose**: Setup automation and utility scripts for Phase 0 initialization

## Contents

- `setup-directories.sh` - Creates project directory structure
- `generate-rules.py` - Generates 9 role-based .cursor/rules files
- `validate-setup.py` - Validates Phase 0 setup completion
- `run-all.sh` - Orchestrates complete Phase 0 setup

## Usage

### Complete Setup
```bash
bash scripts/run-all.sh
```

### Individual Scripts
```bash
# Create directories
bash scripts/setup-directories.sh

# Generate rule files
python scripts/generate-rules.py

# Validate setup
python scripts/validate-setup.py
```

## Requirements

- Python 3.11+
- Bash 5.0+
- Write permissions in project directory

---

**Phase**: 0 - Initialization  
**Status**: Setup scripts to be implemented
