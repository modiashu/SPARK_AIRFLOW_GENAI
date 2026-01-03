"""
Hello World Spark Job
=====================
A simple PySpark job that demonstrates basic DataFrame operations and SQL queries.

This job:
1. Reads sales transaction data from a CSV file
2. Performs data transformations (filtering, aggregations)
3. Executes SQL queries using Spark SQL
4. Writes the results to output files

Learning Objectives:
- Creating a SparkSession
- Reading data with Spark
- DataFrame API operations (select, filter, groupBy, agg)
- Using Spark SQL
- Writing output data
- Basic error handling
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, round as _round, avg
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_spark_session(app_name="HelloWorldSparkJob"):
    """
    Create and configure a SparkSession for local execution.
    
    Configuration highlights:
    - master("local[*]"): Run Spark locally using all available cores
    - spark.driver.memory: Memory allocated to the Spark driver
    - spark.sql.shuffle.partitions: Number of partitions for shuffles (reduced for local mode)
    - spark.eventLog.dir: Directory for Spark event logs (created automatically)
    
    Returns:
        SparkSession: Configured Spark session
    """
    logger.info(f"Creating Spark session: {app_name}")
    
    try:

        # Create spark-events directory for event logging
        project_root = Path(__file__).parent.parent
        spark_events_dir = project_root / "logs" / "spark-events"
        spark_events_dir.mkdir(parents=True, exist_ok=True)
        
        # Create spark-warehouse directory
        spark_warehouse_dir = project_root / "spark-warehouse"
        spark_warehouse_dir.mkdir(parents=True, exist_ok=True)
        
        spark = SparkSession.builder \
            .appName(app_name) \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "4") \
            .config("spark.sql.warehouse.dir", str(spark_warehouse_dir)) \
            .config("spark.eventLog.enabled", "true") \
            .config("spark.eventLog.dir", str(spark_events_dir)) \
            .getOrCreate()
        
        # Set log level to reduce verbosity
        spark.sparkContext.setLogLevel("WARN")
        
        logger.info(f"Spark session created successfully - Version: {spark.version}")
        return spark
    
    except Exception as e:
        logger.error(f"Failed to create Spark session: {str(e)}")
        raise

def read_sales_data(spark, input_path):
    """
    Read sales data from CSV file.
    
    Args:
        spark: SparkSession object
        input_path: Path to the input CSV file
        
    Returns:
        DataFrame: Spark DataFrame containing sales data
    """
    logger.info(f"Reading data from: {input_path}")
    
    try:
        # Read CSV with schema inference and header
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv(input_path)
        
        record_count = df.count()
        logger.info(f"Successfully read {record_count} records")
        logger.info(f"Schema: {df.schema}")
        
        return df
    
    except Exception as e:
        logger.error(f"Failed to read data: {str(e)}")
        raise

def perform_dataframe_transformations(df):
    """
    Perform basic DataFrame transformations.
    
    Operations:
    1. Calculate total amount for each transaction
    2. Filter transactions above a threshold
    3. Select relevant columns
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame: Transformed DataFrame
    """
    logger.info("Performing DataFrame transformations...")
    
    try:
        # Add a calculated column: total_amount = quantity * unit_price
        df_with_total = df.withColumn(
            "total_amount",
            _round(col("quantity") * col("unit_price"), 2)
        )
        
        # Filter transactions with total amount > 100
        df_filtered = df_with_total.filter(col("total_amount") > 100)
        
        # Select relevant columns
        df_transformed = df_filtered.select(
            "transaction_id",
            "customer_id",
            "product_name",
            "category",
            "quantity",
            "unit_price",
            "total_amount",
            "transaction_date",
            "region"
        )
        
        logger.info(f"Transformation complete. Records after filtering: {df_transformed.count()}")
        return df_transformed
    
    except Exception as e:
        logger.error(f"Transformation failed: {str(e)}")
        raise

def perform_aggregations(spark, df):
    """
    Perform aggregations using both DataFrame API and Spark SQL.
    
    Calculations:
    - Total sales by category
    - Average transaction value by region
    - Transaction count by customer
    
    Args:
        spark: SparkSession object
        df: Input DataFrame
        
    Returns:
        dict: Dictionary containing aggregation results
    """
    logger.info("Performing aggregations...")
    
    try:
        # Register DataFrame as a temporary view for SQL queries
        df.createOrReplaceTempView("sales")
        
        # Aggregation 1: Total sales by category (DataFrame API)
        sales_by_category = df.groupBy("category") \
            .agg(
                _sum("total_amount").alias("total_sales"),
                count("transaction_id").alias("transaction_count")
            ) \
            .orderBy(col("total_sales").desc())
        
        logger.info("Sales by Category:")
        sales_by_category.show()
        
        # Aggregation 2: Average transaction value by region (Spark SQL)
        avg_by_region = spark.sql("""
            SELECT 
                region,
                ROUND(AVG(total_amount), 2) as avg_transaction_value,
                COUNT(*) as transaction_count,
                ROUND(SUM(total_amount), 2) as total_sales
            FROM sales
            GROUP BY region
            ORDER BY total_sales DESC
        """)
        
        logger.info("Average Transaction Value by Region:")
        avg_by_region.show()
        
        # Aggregation 3: Top customers by transaction count
        top_customers = spark.sql("""
            SELECT 
                customer_id,
                COUNT(*) as transaction_count,
                ROUND(SUM(total_amount), 2) as total_spent
            FROM sales
            GROUP BY customer_id
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        
        logger.info("Top 5 Customers:")
        top_customers.show()
        
        return {
            "sales_by_category": sales_by_category,
            "avg_by_region": avg_by_region,
            "top_customers": top_customers
        }
    
    except Exception as e:
        logger.error(f"Aggregation failed: {str(e)}")
        raise

def write_output(df, output_path, format="csv"):
    """
    Write DataFrame to output file.
    
    Args:
        df: DataFrame to write
        output_path: Path to write the output
        format: Output format (csv, json, parquet)
    """
    logger.info(f"Writing output to: {output_path}")
    
    try:
        if format == "csv":
            df.coalesce(1) \
                .write \
                .mode("overwrite") \
                .option("header", "true") \
                .csv(output_path)
        elif format == "json":
            df.coalesce(1) \
                .write \
                .mode("overwrite") \
                .json(output_path)
        elif format == "parquet":
            df.write \
                .mode("overwrite") \
                .parquet(output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Successfully wrote output in {format} format")
    
    except Exception as e:
        logger.error(f"Failed to write output: {str(e)}")
        raise

def main():
    """
    Main execution function.
    """
    # Get project root directory
    project_root = os.getenv("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Define input and output paths
    input_path = os.path.join(project_root, "data", "input", "sample_sales_data.csv")
    output_base = os.path.join(project_root, "data", "output")
    
    logger.info("=" * 60)
    logger.info("Starting Hello World Spark Job")
    logger.info("=" * 60)
    logger.info(f"Project Root: {project_root}")
    logger.info(f"Input Path: {input_path}")
    logger.info(f"Output Base: {output_base}")
    
    spark = None
    try:
        # Step 1: Create Spark session
        spark = create_spark_session("HelloWorldSparkJob")
        
        # Step 2: Read data
        df_raw = read_sales_data(spark, input_path)
        
        # Show sample data
        logger.info("Sample data (first 5 rows):")
        df_raw.show(5)
        
        # Step 3: Perform transformations
        df_transformed = perform_dataframe_transformations(df_raw)
        
        # Step 4: Perform aggregations
        aggregations = perform_aggregations(spark, df_transformed)
        
        # Step 5: Write outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Write transformed data
        write_output(
            df_transformed,
            os.path.join(output_base, f"transformed_data_{timestamp}"),
            format="csv"
        )
        
        # Write aggregations
        write_output(
            aggregations["sales_by_category"],
            os.path.join(output_base, f"sales_by_category_{timestamp}"),
            format="csv"
        )
        
        write_output(
            aggregations["avg_by_region"],
            os.path.join(output_base, f"avg_by_region_{timestamp}"),
            format="csv"
        )
        
        write_output(
            aggregations["top_customers"],
            os.path.join(output_base, f"top_customers_{timestamp}"),
            format="csv"
        )
        
        logger.info("=" * 60)
        logger.info("Spark Job Completed Successfully!")
        logger.info("=" * 60)
        
        return 0
    
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Spark Job Failed: {str(e)}")
        logger.error("=" * 60)
        return 1
    
    finally:
        # Clean up: Stop Spark session
        if spark:
            logger.info("Stopping Spark session...")
            spark.stop()

if __name__ == "__main__":
    sys.exit(main())
