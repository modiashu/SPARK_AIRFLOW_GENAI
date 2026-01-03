"""
Hello World Spark-Airflow DAG
==============================
A comprehensive Airflow DAG demonstrating how to orchestrate a Spark job.

This DAG showcases:
- Task dependencies and sequencing
- Using BashOperator to run Spark jobs
- Using PythonOperator for pre/post-processing
- Error handling and retries
- Logging and monitoring

DAG Structure:
    start_task → validate_environment → run_spark_job → validate_output → end_task

Learning Objectives:
- Creating and configuring DAGs
- Using different operators
- Setting up task dependencies
- Implementing error handling
- Configuring retries and timeouts
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# ============================================================================
# Configuration
# ============================================================================

# Get project root directory
PROJECT_ROOT = os.getenv("PROJECT_ROOT", str(Path(__file__).parent.parent.absolute()))

# Default arguments for the DAG
default_args = {
    'owner': 'data-engineering-team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Retry failed tasks twice
    'retry_delay': timedelta(minutes=1),  # Wait 1 minute between retries
    'execution_timeout': timedelta(minutes=30),  # Maximum execution time
}

# ============================================================================
# Helper Functions (Python Callables)
# ============================================================================

def start_pipeline(**context):
    """
    Initialize the pipeline and log start time.
    
    This function demonstrates:
    - Using context variables in Airflow
    - Logging in Airflow tasks
    - Accessing execution date and run ID
    """
    print("=" * 60)
    print("Starting Spark-Airflow Hello World Pipeline")
    print("=" * 60)
    print(f"Execution Date: {context['execution_date']}")
    print(f"DAG Run ID: {context['dag_run'].run_id}")
    print(f"Task Instance: {context['task_instance']}")
    print(f"Project Root: {PROJECT_ROOT}")
    print("=" * 60)
    return "Pipeline started successfully"

def validate_environment(**context):
    """
    Validate that required files and directories exist.
    
    This function checks:
    - Input data file exists
    - Output directory is writable
    - Spark job script exists
    
    Raises:
        FileNotFoundError: If required files/directories are missing
    """
    print("Validating environment setup...")
    
    # Check for input data
    input_file = os.path.join(PROJECT_ROOT, "data", "input", "sample_sales_data.csv")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input data file not found: {input_file}")
    print(f"✓ Input data file found: {input_file}")
    
    # Check for Spark job script
    spark_job = os.path.join(PROJECT_ROOT, "spark_jobs", "hello_world_spark.py")
    if not os.path.exists(spark_job):
        raise FileNotFoundError(f"Spark job script not found: {spark_job}")
    print(f"✓ Spark job script found: {spark_job}")
    
    # Check output directory
    output_dir = os.path.join(PROJECT_ROOT, "data", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Created output directory: {output_dir}")
    else:
        print(f"✓ Output directory exists: {output_dir}")
    
    # Check if output directory is writable
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Output directory is not writable: {output_dir}")
    print(f"✓ Output directory is writable")
    
    print("Environment validation completed successfully!")
    return "Environment validated"

def validate_output(**context):
    """
    Validate that the Spark job produced expected output files.
    
    This function:
    - Checks if output files were created
    - Verifies output files are not empty
    - Logs output file details
    """
    print("Validating Spark job output...")
    
    output_dir = os.path.join(PROJECT_ROOT, "data", "output")
    
    # List all files in output directory
    output_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.csv') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                output_files.append({
                    'path': file_path,
                    'size': file_size
                })
    
    if not output_files:
        raise ValueError("No output files found! Spark job may have failed.")
    
    print(f"Found {len(output_files)} output file(s):")
    for file_info in output_files:
        print(f"  - {file_info['path']} ({file_info['size']} bytes)")
    
    # Verify files are not empty
    empty_files = [f for f in output_files if f['size'] == 0]
    if empty_files:
        raise ValueError(f"Found {len(empty_files)} empty output file(s)")
    
    print("Output validation completed successfully!")
    return f"Validated {len(output_files)} output files"

def end_pipeline(**context):
    """
    Finalize the pipeline and log completion.
    """
    print("=" * 60)
    print("Pipeline Completed Successfully!")
    print("=" * 60)
    
    # Calculate execution duration
    task_instance = context['task_instance']
    dag_run = context['dag_run']
    
    print(f"DAG Run ID: {dag_run.run_id}")
    print(f"Execution Date: {context['execution_date']}")
    print(f"All tasks completed successfully!")
    print("=" * 60)
    
    return "Pipeline completed"

# ============================================================================
# DAG Definition
# ============================================================================

# Create the DAG
dag = DAG(
    dag_id='hello_world_spark_airflow',
    default_args=default_args,
    description='A Hello World DAG demonstrating Spark integration with Airflow',
    schedule_interval=None,  # Manual trigger only (use @daily, @hourly, etc. for scheduling)
    start_date=days_ago(1),  # Start date (1 day ago)
    catchup=False,  # Don't run for past dates
    tags=['spark', 'hello-world', 'learning', 'etl'],  # Tags for filtering in UI
)

# ============================================================================
# Task Definitions
# ============================================================================

# Task 1: Start the pipeline
task_start = PythonOperator(
    task_id='start_pipeline',
    python_callable=start_pipeline,
    dag=dag,
)

# Task 2: Validate environment
task_validate_env = PythonOperator(
    task_id='validate_environment',
    python_callable=validate_environment,
    dag=dag,
)

# Task 3: Run the Spark job
# This uses BashOperator to execute the Spark job as a subprocess

# Use virtual environment's Python to ensure PySpark is available
task_run_spark = BashOperator(
    task_id='run_spark_job',
    bash_command=f'cd {PROJECT_ROOT} && {PROJECT_ROOT}/.venv/bin/python spark_jobs/hello_world_spark.py',
    env={
        'PROJECT_ROOT': PROJECT_ROOT,
        'PYTHONPATH': PROJECT_ROOT,
    },
    dag=dag,
)

# Task 4: Validate output
task_validate_output = PythonOperator(
    task_id='validate_output',
    python_callable=validate_output,
    dag=dag,
)

# Task 5: End the pipeline
task_end = PythonOperator(
    task_id='end_pipeline',
    python_callable=end_pipeline,
    dag=dag,
)

# ============================================================================
# Task Dependencies
# ============================================================================

# Define the execution order using >> operator (or use set_downstream())
# Flow: start → validate_env → run_spark → validate_output → end

task_start >> task_validate_env >> task_run_spark >> task_validate_output >> task_end

# Alternative syntax (equivalent):
# task_start.set_downstream(task_validate_env)
# task_validate_env.set_downstream(task_run_spark)
# task_run_spark.set_downstream(task_validate_output)
# task_validate_output.set_downstream(task_end)

# ============================================================================
# Additional Information
# ============================================================================

"""
How to use this DAG:

1. Ensure your Airflow environment is set up:
   - AIRFLOW_HOME is set
   - Database is initialized (airflow db init)
   - Scheduler is running (airflow scheduler)
   - Webserver is running (airflow webserver)

2. This DAG will appear in the Airflow UI at http://localhost:8080

3. To manually trigger:
   - Via UI: Click the play button on the DAG
   - Via CLI: airflow dags trigger hello_world_spark_airflow

4. To test individual tasks:
   airflow tasks test hello_world_spark_airflow start_pipeline 2024-01-01

5. Monitor execution:
   - Check the Graph View in Airflow UI
   - View logs for each task
   - Monitor Spark job progress

Common Issues:
- If Spark job fails, check that Java is installed and JAVA_HOME is set
- If Python dependencies are missing, ensure virtual environment is activated
- Check file permissions if validation tasks fail
"""
