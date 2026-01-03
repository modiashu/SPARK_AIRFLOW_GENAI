#!/bin/bash

# ============================================================================
# Run Spark Job Directly (Without Airflow)
# ============================================================================
# This script runs the Spark job directly for testing purposes.
# Useful for debugging the Spark job without going through Airflow.
# ============================================================================

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
        print_info "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
fi

export PROJECT_ROOT="$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

print_info "Running Spark job..."
print_info "Project Root: $PROJECT_ROOT"

python3 "$PROJECT_ROOT/spark_jobs/hello_world_spark.py"

print_success "Spark job completed!"
print_info "Check output in: $PROJECT_ROOT/data/output/"
