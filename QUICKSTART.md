# Quick Reference Guide

## 🚀 First Time Setup

### Prerequisites
- UV Package Manager (installs Python 3.11 automatically)
- Java 8 or 11: `java -version`
- Git: `git --version`

### Initial Setup (One Time)

```bash
# 1. Clone and navigate
git clone <repository-url>
cd SPARK_AIRFLOW_GENAI

# 2. Make scripts executable
chmod +x scripts/*.sh

# 3. Run setup
./scripts/setup.sh

# 4. Activate environment
source .venv/bin/activate

# 5. Verify installation
airflow version
python3 -c "import pyspark; print(pyspark.__version__)"

# 7. Test Spark job
./scripts/run_spark_job.sh

# 8. Start Airflow
./scripts/start_airflow.sh

# 9. Access UI: http://localhost:8080 (admin/admin)
```

### Find Required Paths

```bash
# JAVA_HOME
/usr/libexec/java_home -v 11  # macOS
dirname $(dirname $(readlink -f $(which java)))  # Linux

# Verify PySpark (included with project)
python3 -c "import pyspark; print(pyspark.__version__)"
```

## Common Commands

### Setup and Installation

```bash
# Initial setup
./scripts/setup.sh

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
uv pip install -e .
```

### Running the Project

```bash
# Start Airflow
./scripts/start_airflow.sh

# Stop Airflow
./scripts/stop_airflow.sh

# Run Spark job directly (without Airflow)
./scripts/run_spark_job.sh
```

### Airflow Commands

```bash
# Initialize database
airflow db init

# Create admin user
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com

# List DAGs
airflow dags list

# Trigger DAG
airflow dags trigger hello_world_spark_airflow

# Test specific task
airflow tasks test hello_world_spark_airflow start_pipeline 2024-01-01

# View task logs
airflow tasks logs hello_world_spark_airflow run_spark_job 2024-01-01
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_spark_job.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest --cov=spark_jobs --cov=dags tests/

# Test DAG syntax
python3 dags/hello_world_dag.py
```

### Monitoring

```bash
# View Airflow logs
tail -f logs/webserver.log
tail -f logs/scheduler.log

# View output files
ls -lh data/output/

# View sample output
head data/output/transformed_data_*/part-*.csv
```

## File Locations

| Item | Path |
|------|------|
| DAGs | `dags/` |
| Spark Jobs | `spark_jobs/` |
| Input Data | `data/input/` |
| Output Data | `data/output/` |
| Configuration | `config/` |
| Scripts | `scripts/` |
| Tests | `tests/` |
| Logs | `logs/` |
| Virtual Env | `.venv/` |

## Environment Variables

Key variables in `.env`:

```bash
PROJECT_ROOT=/path/to/project
AIRFLOW_HOME=${PROJECT_ROOT}
JAVA_HOME=/path/to/java
# Note: SPARK_HOME not needed - PySpark includes Spark
```

## URLs

- **Airflow UI**: http://localhost:8080
- **Spark UI**: http://localhost:4040 (when job is running)

Default credentials:
- Username: `admin`
- Password: `admin`

## Troubleshooting Quick Fixes

### Airflow won't start
```bash
# Kill existing processes
pkill -f "airflow"

# Re-initialize database
export AIRFLOW_HOME=$(pwd)
airflow db reset
airflow db init

# Recreate admin user
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

### Port already in use
```bash
# Find process
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Java not found
```bash
# Find Java
/usr/libexec/java_home -v 11  # macOS
which java                     # Linux

# Update .env
export JAVA_HOME=/path/to/java
```

### Module not found
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
uv pip install -e .
```

## PySpark Cheat Sheet

### Read Data
```python
df = spark.read.csv("path/to/file.csv", header=True, inferSchema=True)
```

### Transformations
```python
# Add column
df = df.withColumn("new_col", col("old_col") * 2)

# Filter
df = df.filter(col("amount") > 100)

# Select
df = df.select("col1", "col2")
```

### Aggregations
```python
# Group by
result = df.groupBy("category").agg(
    sum("amount").alias("total"),
    count("*").alias("count")
)
```

### SQL
```python
df.createOrReplaceTempView("my_table")
result = spark.sql("SELECT * FROM my_table WHERE amount > 100")
```

### Write Data
```python
df.write.mode("overwrite").csv("output/path")
```

## Airflow DAG Cheat Sheet

### Basic DAG
```python
dag = DAG(
    'my_dag',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=days_ago(1),
)
```

### Python Operator
```python
task = PythonOperator(
    task_id='my_task',
    python_callable=my_function,
    dag=dag,
)
```

### Bash Operator
```python
task = BashOperator(
    task_id='my_task',
    bash_command='echo "Hello"',
    dag=dag,
)
```

### Task Dependencies
```python
task1 >> task2 >> task3  # Linear
task1 >> [task2, task3] >> task4  # Parallel
```

## Performance Tips

### Spark
- Adjust `spark.sql.shuffle.partitions` based on data size
- Use appropriate memory settings (`spark.driver.memory`)
- Cache DataFrames if reusing: `df.cache()`
- Use `coalesce()` to reduce partitions before writing

### Airflow
- Use SequentialExecutor for simple sequential execution (compatible with SQLite)
- Set appropriate `dag_concurrency`
- Monitor task execution times
- Use task groups for complex DAGs

## Getting Help

1. Check [README.md](README.md) for detailed documentation
2. Review [TROUBLESHOOTING.md](README.md#troubleshooting) section
3. Run tests to verify setup: `pytest tests/`
4. Check logs in `logs/` directory
5. Open an issue on GitHub

---

**Quick Links:**
- [Full Documentation](README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
