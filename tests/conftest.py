"""
Pytest Configuration
====================
Configuration file for pytest test suite.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set environment variables for testing
os.environ["PROJECT_ROOT"] = project_root
os.environ["AIRFLOW_HOME"] = project_root
os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = os.path.join(project_root, "dags")
os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
