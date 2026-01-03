#!/bin/bash

# ============================================================================
# Stop Airflow Script
# ============================================================================
# This script stops the Airflow webserver and scheduler.
# ============================================================================

# Don't exit on error - we want to try all cleanup steps
set +e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_info "Stopping Airflow..."

# Stop standalone mode if running
if [ -f "$PROJECT_ROOT/airflow-standalone.pid" ]; then
    STANDALONE_PID=$(cat "$PROJECT_ROOT/airflow-standalone.pid")
    if ps -p $STANDALONE_PID > /dev/null 2>&1; then
        print_info "Stopping Airflow standalone (PID: $STANDALONE_PID)..."
        kill $STANDALONE_PID 2>/dev/null || print_info "Could not kill PID $STANDALONE_PID"
        sleep 1
    fi
    rm -f "$PROJECT_ROOT/airflow-standalone.pid"
fi

# Stop webserver (legacy)
if [ -f "$PROJECT_ROOT/airflow-webserver.pid" ]; then
    WEBSERVER_PID=$(cat "$PROJECT_ROOT/airflow-webserver.pid")
    if ps -p $WEBSERVER_PID > /dev/null 2>&1; then
        print_info "Stopping webserver (PID: $WEBSERVER_PID)..."
        kill $WEBSERVER_PID 2>/dev/null || print_info "Could not kill PID $WEBSERVER_PID (may already be stopped)"
        sleep 1
    else
        print_info "Webserver process not running (PID: $WEBSERVER_PID)"
    fi
    rm -f "$PROJECT_ROOT/airflow-webserver.pid"
else
    print_info "Webserver PID file not found"
fi

# Stop scheduler
if [ -f "$PROJECT_ROOT/airflow-scheduler.pid" ]; then
    SCHEDULER_PID=$(cat "$PROJECT_ROOT/airflow-scheduler.pid")
    if ps -p $SCHEDULER_PID > /dev/null 2>&1; then
        print_info "Stopping scheduler (PID: $SCHEDULER_PID)..."
        kill $SCHEDULER_PID 2>/dev/null || print_info "Could not kill PID $SCHEDULER_PID (may already be stopped)"
        sleep 1
    else
        print_info "Scheduler process not running (PID: $SCHEDULER_PID)"
    fi
    rm -f "$PROJECT_ROOT/airflow-scheduler.pid"
else
    print_info "Scheduler PID file not found"
fi

# Kill any remaining Airflow processes (including gunicorn workers)
print_info "Cleaning up any remaining Airflow processes..."
pkill -f "airflow webserver" 2>/dev/null || true
pkill -f "airflow scheduler" 2>/dev/null || true
pkill -f "gunicorn.*airflow" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Force kill if still running
pkill -9 -f "airflow webserver" 2>/dev/null || true
pkill -9 -f "airflow scheduler" 2>/dev/null || true
pkill -9 -f "gunicorn.*airflow" 2>/dev/null || true

# Clean up PID files
rm -f "$PROJECT_ROOT/airflow-webserver.pid" "$PROJECT_ROOT/airflow-scheduler.pid"

print_success "Airflow stopped successfully"
