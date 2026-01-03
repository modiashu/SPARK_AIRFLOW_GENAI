"""
Integration Tests for Airflow DAG
==================================
Tests for the hello_world_dag.py Airflow DAG.

Run with: pytest tests/test_dag.py
"""

import os
import sys
from datetime import datetime
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set required Airflow environment variables before importing
os.environ["AIRFLOW_HOME"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = os.path.join(os.environ["AIRFLOW_HOME"], "dags")
os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "False"

from airflow.models import DagBag

def test_dag_loaded():
    """Test that the DAG is loaded without errors."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    
    # Check for import errors
    assert len(dagbag.import_errors) == 0, \
        f"DAG import errors: {dagbag.import_errors}"
    
    # Check that our DAG is present
    assert "hello_world_spark_airflow" in dagbag.dags, \
        "DAG 'hello_world_spark_airflow' not found"

def test_dag_structure():
    """Test the DAG structure and configuration."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    assert dag is not None
    
    # Check DAG properties
    assert dag.dag_id == "hello_world_spark_airflow"
    assert dag.schedule_interval is None  # Manual trigger
    assert dag.catchup is False
    assert dag.default_args["owner"] == "data-engineering-team"
    assert dag.default_args["retries"] == 2

def test_dag_has_expected_tasks():
    """Test that DAG has all expected tasks."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    expected_tasks = [
        "start_pipeline",
        "validate_environment",
        "run_spark_job",
        "validate_output",
        "end_pipeline"
    ]
    
    actual_tasks = list(dag.task_ids)
    
    for task_id in expected_tasks:
        assert task_id in actual_tasks, f"Task '{task_id}' not found in DAG"

def test_task_dependencies():
    """Test that task dependencies are correctly defined."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    # Get tasks
    start = dag.get_task("start_pipeline")
    validate_env = dag.get_task("validate_environment")
    run_spark = dag.get_task("run_spark_job")
    validate_output = dag.get_task("validate_output")
    end = dag.get_task("end_pipeline")
    
    # Check dependencies: start → validate_env → run_spark → validate_output → end
    assert validate_env in start.downstream_list
    assert run_spark in validate_env.downstream_list
    assert validate_output in run_spark.downstream_list
    assert end in validate_output.downstream_list

def test_task_operators():
    """Test that tasks use the correct operators."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    from airflow.operators.python import PythonOperator
    from airflow.operators.bash import BashOperator
    
    # Check operator types
    assert isinstance(dag.get_task("start_pipeline"), PythonOperator)
    assert isinstance(dag.get_task("validate_environment"), PythonOperator)
    assert isinstance(dag.get_task("run_spark_job"), BashOperator)
    assert isinstance(dag.get_task("validate_output"), PythonOperator)
    assert isinstance(dag.get_task("end_pipeline"), PythonOperator)

def test_dag_tags():
    """Test that DAG has appropriate tags."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    expected_tags = ['spark', 'hello-world', 'learning', 'etl']
    
    for tag in expected_tags:
        assert tag in dag.tags, f"Tag '{tag}' not found in DAG"

def test_no_cycles():
    """Test that DAG has no cycles."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    # Airflow automatically detects cycles during DAG parsing
    # If DAG loaded successfully, there are no cycles
    assert dag is not None

def test_task_retries():
    """Test that tasks have retry configuration."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    for task in dag.tasks:
        # Check that retries are configured
        assert task.retries == 2, f"Task {task.task_id} should have 2 retries"

def test_execution_timeout():
    """Test that tasks have execution timeout."""
    dagbag = DagBag(dag_folder="dags", include_examples=False)
    dag = dagbag.get_dag("hello_world_spark_airflow")
    
    for task in dag.tasks:
        assert task.execution_timeout is not None, \
            f"Task {task.task_id} should have execution timeout"

def test_validate_environment_files():
    """Test that required files exist for DAG execution."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check input data
    input_file = os.path.join(project_root, "data", "input", "sample_sales_data.csv")
    assert os.path.exists(input_file), "Input data file missing"
    
    # Check Spark job script
    spark_job = os.path.join(project_root, "spark_jobs", "hello_world_spark.py")
    assert os.path.exists(spark_job), "Spark job script missing"
    
    # Check output directory
    output_dir = os.path.join(project_root, "data", "output")
    assert os.path.exists(output_dir), "Output directory missing"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
