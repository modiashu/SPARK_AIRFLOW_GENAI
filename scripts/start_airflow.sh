#!/bin/bash

# ============================================================================
# Start Airflow Script
# ============================================================================
# This script starts the Airflow webserver and scheduler.
# Run this after completing setup.sh
# ============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    print_info "Loaded environment variables from .env"
else
    print_warning ".env file not found. Using defaults."
fi

# Set AIRFLOW_HOME
export AIRFLOW_HOME="$PROJECT_ROOT"

print_info "Starting Airflow..."
print_info "AIRFLOW_HOME: $AIRFLOW_HOME"
print_info "Project Root: $PROJECT_ROOT"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not activated. Activating..."
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Start Airflow in standalone mode (webserver + scheduler combined)
# This is simpler and more reliable for local development
print_info "Starting Airflow in standalone mode..."
nohup airflow standalone > "$PROJECT_ROOT/logs/airflow-standalone.log" 2>&1 &
AIRFLOW_PID=$!
echo $AIRFLOW_PID > "$PROJECT_ROOT/airflow-standalone.pid"

echo ""
print_success "Airflow started successfully!"
echo ""
print_info "Airflow PID: $AIRFLOW_PID"
echo ""
print_info "Access Airflow UI at: http://localhost:8080"
print_info "Default credentials: admin / admin"
echo ""
print_info "To view logs:"
echo "  tail -f $PROJECT_ROOT/logs/airflow-standalone.log"
echo ""
print_info "To stop Airflow, run: ./scripts/stop_airflow.sh"
echo ""
