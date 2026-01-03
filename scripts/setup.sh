#!/bin/bash

# ============================================================================
# Setup Script for Spark-Airflow Hello World Project
# ============================================================================
# This script sets up the complete local development environment including:
# - UV virtual environment
# - Python dependencies
# - Apache Spark
# - Apache Airflow
# - Environment variables
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo ""
    echo "================================================================"
    echo "$1"
    echo "================================================================"
}

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_section "Spark-Airflow Hello World - Setup"
print_info "Project Root: $PROJECT_ROOT"

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================
print_section "Step 1: Checking Prerequisites"

# UV will handle Python installation, so we don't need to check for system Python
print_info "UV will install Python 3.11 if not available"

# Check for UV
if ! command -v uv &> /dev/null; then
    print_warning "UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        print_error "Failed to install UV. Please install it manually from https://github.com/astral-sh/uv"
        exit 1
    fi
fi
print_success "UV package manager found"

# Check Java (required for Spark)
if ! command -v java &> /dev/null; then
    print_error "Java is not installed. Spark requires Java 8 or 11."
    print_info "Install Java:"
    print_info "  macOS: brew install openjdk@11"
    print_info "  Linux: sudo apt-get install openjdk-11-jdk"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
print_success "Java $JAVA_VERSION found"

# ============================================================================
# Step 2: Create .env file from template
# ============================================================================
print_section "Step 2: Creating Environment Configuration"

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    print_info "Creating .env file from template..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    
    # Update PROJECT_ROOT in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|PROJECT_ROOT=\${PWD}|PROJECT_ROOT=$PROJECT_ROOT|g" "$PROJECT_ROOT/.env"
    else
        sed -i "s|PROJECT_ROOT=\${PWD}|PROJECT_ROOT=$PROJECT_ROOT|g" "$PROJECT_ROOT/.env"
    fi
    
    print_success ".env file created"
    print_info "You can customize settings in .env file if needed"
else
    print_info ".env file already exists"
fi

# ============================================================================
# Step 3: Create Virtual Environment with UV
# ============================================================================
print_section "Step 3: Setting up Python Virtual Environment"

if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    print_info "Creating virtual environment with Python 3.11..."
    uv venv .venv --python 3.11
    print_success "Virtual environment created with Python 3.11"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"
print_success "Virtual environment activated"

# ============================================================================
# Step 4: Install Python Dependencies
# ============================================================================
print_section "Step 4: Installing Python Dependencies"

print_info "Installing dependencies from pyproject.toml..."

# Standard way: use UV's sync command which reads pyproject.toml
if ! uv sync; then
    print_error "Failed to install dependencies"
    print_info ""
    print_info "Troubleshooting steps:"
    print_info "  1. Check network: ping files.pythonhosted.org"
    print_info "  2. If on VPN, ensure proxy is configured or disconnect VPN"
    print_info "  3. Clear proxy variables if not on VPN: unset HTTP_PROXY HTTPS_PROXY"
    print_info ""
    print_error "Setup failed. Please resolve the issue and try again."
    exit 1
fi

print_success "All dependencies installed successfully"

# ============================================================================
# Step 5: Verify Apache Spark (PySpark)
# ============================================================================
print_section "Step 5: Verifying Apache Spark"

print_info "PySpark 3.5.1 has been installed as a Python dependency"
print_info "This includes all necessary Spark binaries for local execution"
print_success "No separate Spark installation needed for this learning project!"
print_info ""
print_info "Note: For production environments, you would deploy to a Spark cluster"

# ============================================================================
# Step 6: Initialize Airflow
# ============================================================================
print_section "Step 6: Initializing Apache Airflow"

# Set AIRFLOW_HOME
export AIRFLOW_HOME="$PROJECT_ROOT"

print_info "Initializing Airflow database..."
airflow db init

print_info "Creating Airflow admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

print_success "Airflow initialized successfully"

# ============================================================================
# Step 7: Verify Setup
# ============================================================================
print_section "Step 7: Verifying Setup"

print_info "Checking directory structure..."
for dir in dags spark_jobs data/input data/output logs config scripts tests; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        print_success "✓ $dir/"
    else
        print_error "✗ $dir/ (missing)"
    fi
done

print_info "Checking required files..."
for file in pyproject.toml .env .gitignore; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        print_success "✓ $file"
    else
        print_error "✗ $file (missing)"
    fi
done

# ============================================================================
# Setup Complete
# ============================================================================
print_section "Setup Complete!"

echo ""
print_success "Environment setup completed successfully!"
echo ""
print_info "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo "  2. Start Airflow:"
echo "     ./scripts/start_airflow.sh"
echo "  3. Access Airflow UI:"
echo "     http://localhost:8080 (admin/admin)"
echo "  4. Trigger the DAG from Airflow UI or run:"
echo "     airflow dags trigger hello_world_spark_airflow"
echo ""
print_info "For more information, see README.md"
echo ""
