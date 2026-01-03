"""
Unit Tests for Spark Job
=========================
Tests for the hello_world_spark.py Spark job.

Run with: pytest tests/test_spark_job.py
"""

import os
import sys
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# Add parent directory to path to import spark job
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def spark():
    """
    Create a SparkSession for testing.
    Uses local mode with minimal resources.
    """
    spark = SparkSession.builder \
        .appName("SparkJobTesting") \
        .master("local[2]") \
        .config("spark.driver.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    yield spark
    
    spark.stop()

@pytest.fixture
def sample_data(spark):
    """
    Create sample data for testing.
    """
    schema = StructType([
        StructField("transaction_id", IntegerType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product_name", StringType(), True),
        StructField("category", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("transaction_date", StringType(), True),
        StructField("region", StringType(), True),
    ])
    
    data = [
        (1001, "C001", "Laptop", "Electronics", 1, 1200.00, "2024-01-15", "North"),
        (1002, "C002", "Mouse", "Electronics", 2, 25.00, "2024-01-15", "South"),
        (1003, "C003", "Desk Chair", "Furniture", 1, 350.00, "2024-01-16", "East"),
        (1004, "C001", "Monitor", "Electronics", 2, 300.00, "2024-01-16", "North"),
        (1005, "C004", "Keyboard", "Electronics", 1, 75.00, "2024-01-17", "West"),
    ]
    
    return spark.createDataFrame(data, schema)

def test_spark_session_creation(spark):
    """Test that SparkSession is created successfully."""
    assert spark is not None
    assert spark.sparkContext.master == "local[2]"

def test_read_csv_data(spark):
    """Test reading CSV data."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(project_root, "data", "input", "sample_sales_data.csv")
    
    if not os.path.exists(input_path):
        pytest.skip("Input CSV file not found")
    
    df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(input_path)
    
    assert df is not None
    assert df.count() > 0
    assert "transaction_id" in df.columns
    assert "customer_id" in df.columns
    assert "product_name" in df.columns

def test_add_total_amount_column(sample_data):
    """Test adding calculated column."""
    from pyspark.sql.functions import col, round as _round
    
    df_with_total = sample_data.withColumn(
        "total_amount",
        _round(col("quantity") * col("unit_price"), 2)
    )
    
    assert "total_amount" in df_with_total.columns
    
    # Verify calculation for first row (1 * 1200 = 1200)
    first_row = df_with_total.first()
    assert first_row.total_amount == 1200.00

def test_filter_by_amount(sample_data):
    """Test filtering data by amount."""
    from pyspark.sql.functions import col, round as _round
    
    df_with_total = sample_data.withColumn(
        "total_amount",
        _round(col("quantity") * col("unit_price"), 2)
    )
    
    df_filtered = df_with_total.filter(col("total_amount") > 100)
    
    # Should have 3 records (Laptop=1200, Chair=350, Monitor=600)
    assert df_filtered.count() == 3

def test_group_by_category(sample_data):
    """Test grouping and aggregation by category."""
    from pyspark.sql.functions import col, sum as _sum, count, round as _round
    
    df_with_total = sample_data.withColumn(
        "total_amount",
        _round(col("quantity") * col("unit_price"), 2)
    )
    
    sales_by_category = df_with_total.groupBy("category") \
        .agg(
            _sum("total_amount").alias("total_sales"),
            count("transaction_id").alias("transaction_count")
        )
    
    # Should have 2 categories (Electronics, Furniture)
    assert sales_by_category.count() == 2
    
    # Verify Electronics has 4 transactions
    electronics = sales_by_category.filter(col("category") == "Electronics").first()
    assert electronics.transaction_count == 4

def test_spark_sql_query(spark, sample_data):
    """Test Spark SQL functionality."""
    from pyspark.sql.functions import col, round as _round
    
    df_with_total = sample_data.withColumn(
        "total_amount",
        _round(col("quantity") * col("unit_price"), 2)
    )
    
    df_with_total.createOrReplaceTempView("sales")
    
    result = spark.sql("""
        SELECT 
            category,
            COUNT(*) as transaction_count,
            SUM(total_amount) as total_sales
        FROM sales
        GROUP BY category
        ORDER BY total_sales DESC
    """)
    
    assert result is not None
    assert result.count() == 2
    
    # First row should be Electronics (highest sales)
    first_row = result.first()
    assert first_row.category == "Electronics"

def test_output_schema(sample_data):
    """Test that output DataFrame has expected schema."""
    from pyspark.sql.functions import col, round as _round
    
    df_transformed = sample_data.withColumn(
        "total_amount",
        _round(col("quantity") * col("unit_price"), 2)
    ).filter(col("total_amount") > 100)
    
    expected_columns = [
        "transaction_id", "customer_id", "product_name", "category",
        "quantity", "unit_price", "total_amount", "transaction_date", "region"
    ]
    
    for col_name in expected_columns:
        assert col_name in df_transformed.columns

def test_no_null_values(sample_data):
    """Test that there are no null values in required columns."""
    null_counts = sample_data.select(
        [col(c).isNull().cast("int").alias(c) for c in sample_data.columns]
    ).groupBy().sum()
    
    # All null counts should be 0
    for col_name in sample_data.columns:
        assert null_counts.first()[f"sum({col_name})"] == 0

def test_data_type_validation(sample_data):
    """Test that columns have expected data types."""
    schema = sample_data.schema
    
    type_map = {field.name: field.dataType for field in schema.fields}
    
    assert isinstance(type_map["transaction_id"], IntegerType)
    assert isinstance(type_map["customer_id"], StringType)
    assert isinstance(type_map["quantity"], IntegerType)
    assert isinstance(type_map["unit_price"], DoubleType)

def test_aggregation_accuracy(sample_data):
    """Test that aggregations produce correct results."""
    from pyspark.sql.functions import sum as _sum, col, round as _round
    
    df_with_total = sample_data.withColumn(
        "total_amount",
        _round(col("quantity") * col("unit_price"), 2)
    )
    
    # Calculate total sales manually
    # Laptop: 1*1200 = 1200
    # Mouse: 2*25 = 50
    # Chair: 1*350 = 350
    # Monitor: 2*300 = 600
    # Keyboard: 1*75 = 75
    # Total = 2275
    
    total = df_with_total.agg(_sum("total_amount").alias("total")).first().total
    assert total == 2275.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
