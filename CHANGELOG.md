# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-29

### Added
- Initial project setup with UV package manager
- Basic PySpark job with transformations and aggregations
- Airflow DAG with task dependencies and error handling
- Sample sales data CSV file
- Configuration files for Spark and Airflow
- Setup, start, and stop scripts
- Comprehensive README with setup instructions
- Unit tests for Spark job
- Integration tests for Airflow DAG
- Contributing guidelines
- MIT License

### Features
- Read CSV data with Spark
- DataFrame transformations (withColumn, filter)
- Aggregations using DataFrame API and Spark SQL
- Airflow task orchestration with 5 tasks
- SequentialExecutor with SQLite backend (simple setup for learning)
- Comprehensive logging and error handling
- Output validation

### Documentation
- Architecture overview
- Technology stack details
- Step-by-step setup guide
- Troubleshooting section
- Learning resources

## [Unreleased]

### Planned
- Spark Streaming example
- Advanced error handling patterns
- Performance optimization guide
- Docker/Podman containerization
- CI/CD pipeline setup
- Additional sample datasets
- Machine Learning integration example
