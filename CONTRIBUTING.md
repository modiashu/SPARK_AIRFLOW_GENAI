# Contributing to Spark-Airflow Hello World

Thank you for your interest in contributing to this learning project! This document provides guidelines for contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in the GitHub Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment details (OS, Python version, etc.)

### Submitting Changes

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/SPARK_AIRFLOW_GENAI.git
   cd SPARK_AIRFLOW_GENAI
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test Your Changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Test Spark job
   ./scripts/run_spark_job.sh
   
   # Test DAG
   python3 dags/hello_world_dag.py
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Describe your changes clearly
   - Reference any related issues

## Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused
- Maximum line length: 100 characters

Example:
```python
def process_data(df, threshold=100):
    """
    Process DataFrame and filter by threshold.
    
    Args:
        df: Input DataFrame
        threshold: Minimum value for filtering
        
    Returns:
        Filtered DataFrame
    """
    return df.filter(col("amount") > threshold)
```

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Update README.md for significant changes
- Add inline comments for complex logic

## Development Setup

1. **Install Development Dependencies**
   ```bash
   uv pip install -e ".[dev]"
   ```

2. **Run Pre-commit Checks**
   ```bash
   # Format code
   black spark_jobs/ dags/ tests/
   
   # Check style
   flake8 spark_jobs/ dags/ tests/
   ```

## Areas for Contribution

We welcome contributions in these areas:

### Beginner-Friendly

- Fix typos in documentation
- Improve error messages
- Add more test cases
- Enhance code comments

### Intermediate

- Add new data transformations
- Implement additional aggregations
- Create new example datasets
- Improve logging

### Advanced

- Add Spark Streaming example
- Implement MLlib integration
- Add advanced Airflow features
- Performance optimization

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions
- Reach out to maintainers

Thank you for contributing! 🎉
