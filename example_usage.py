#!/usr/bin/env python3
"""
Example Usage of Spark Metadata Conversational Bot
Demonstrates programmatic usage and various features
"""

from metadata_models import (
    PipelineMetadata, SourceMetadata, TransformationMetadata,
    DataQualityRule, TargetMetadata, ColumnMetadata
)
from metadata_storage import MetadataStore
from conversation_bot import MetadataBot
from spark_integration import SparkMetadataExecutor, MetadataValidator


def example1_conversational_bot():
    """Example 1: Using the conversational bot programmatically"""
    print("=" * 70)
    print("Example 1: Conversational Bot Usage")
    print("=" * 70)
    
    bot = MetadataBot(storage_path="./example_metadata")
    
    # Simulate conversation
    messages = [
        "create pipeline name: sales_etl, description: Sales data ETL pipeline",
        "add source name: sales, location: /data/sales.csv, format: csv",
        "add column name: order_id, type: integer, nullable: false",
        "add column name: customer_id, type: integer",
        "add column name: amount, type: double",
        "add column name: order_date, type: date",
        "add transformation name: filter_valid, logic: SELECT * FROM sales WHERE amount > 0",
        "add rule name: positive_amounts, condition: amount > 0, columns: amount, severity: error",
        "add rule name: no_null_ids, condition: order_id IS NOT NULL, columns: order_id, severity: error",
        "add target name: clean_sales, location: /output/sales.parquet, format: parquet, mode: overwrite",
        "save"
    ]
    
    for msg in messages:
        print(f"\nUser: {msg}")
        response = bot.process_message(msg)
        print(f"Bot: {response}")
    
    print("\n" + "=" * 70 + "\n")


def example2_programmatic_creation():
    """Example 2: Creating metadata programmatically"""
    print("=" * 70)
    print("Example 2: Programmatic Metadata Creation")
    print("=" * 70)
    
    # Create pipeline
    pipeline = PipelineMetadata(
        pipeline_id="customer_360",
        name="Customer 360 Pipeline",
        description="Comprehensive customer data integration"
    )
    
    # Add customer source
    customer_source = SourceMetadata(
        source_id="customers",
        name="Customer Master Data",
        location="/data/customers.parquet",
        format="parquet",
        columns=[
            ColumnMetadata(name="customer_id", data_type="integer", nullable=False),
            ColumnMetadata(name="name", data_type="string"),
            ColumnMetadata(name="email", data_type="string"),
            ColumnMetadata(name="signup_date", data_type="date"),
        ]
    )
    pipeline.sources.append(customer_source)
    
    # Add orders source
    orders_source = SourceMetadata(
        source_id="orders",
        name="Order Transactions",
        location="/data/orders.parquet",
        format="parquet",
        columns=[
            ColumnMetadata(name="order_id", data_type="integer", nullable=False),
            ColumnMetadata(name="customer_id", data_type="integer", nullable=False),
            ColumnMetadata(name="amount", data_type="double"),
            ColumnMetadata(name="order_date", data_type="date"),
        ]
    )
    pipeline.sources.append(orders_source)
    
    # Add transformation to join data
    join_transform = TransformationMetadata(
        transformation_id="customer_orders",
        name="Customer Order History",
        transformation_type="join",
        source_refs=["customers", "orders"],
        logic="""
            SELECT 
                c.customer_id,
                c.name,
                c.email,
                COUNT(o.order_id) as total_orders,
                SUM(o.amount) as total_spent,
                MAX(o.order_date) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name, c.email
        """
    )
    pipeline.transformations.append(join_transform)
    
    # Add data quality rules
    pipeline.data_quality_rules.extend([
        DataQualityRule(
            rule_id="unique_customers",
            name="Unique Customer IDs",
            rule_type="unique_check",
            target_columns=["customer_id"],
            condition="customer_id IS NOT NULL",
            severity="error"
        ),
        DataQualityRule(
            rule_id="valid_emails",
            name="Valid Email Format",
            rule_type="regex_check",
            target_columns=["email"],
            condition="email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            severity="warning"
        ),
        DataQualityRule(
            rule_id="positive_amounts",
            name="Positive Order Amounts",
            rule_type="range_check",
            target_columns=["total_spent"],
            condition="total_spent >= 0",
            severity="error"
        )
    ])
    
    # Add target
    target = TargetMetadata(
        target_id="customer_360_view",
        name="Customer 360 View",
        location="/output/customer_360.delta",
        format="delta",
        write_mode="overwrite",
        partition_columns=["last_order_date"],
        source_transformation_ref="customer_orders"
    )
    pipeline.targets.append(target)
    
    # Save pipeline
    store = MetadataStore("./example_metadata")
    store.save_pipeline(pipeline)
    
    print(f"\n✓ Created pipeline: {pipeline.name}")
    print(f"  - Sources: {len(pipeline.sources)}")
    print(f"  - Transformations: {len(pipeline.transformations)}")
    print(f"  - DQ Rules: {len(pipeline.data_quality_rules)}")
    print(f"  - Targets: {len(pipeline.targets)}")
    print(f"\n✓ Saved to: ./example_metadata/pipelines/{pipeline.pipeline_id}.json")
    
    print("\n" + "=" * 70 + "\n")
    
    return pipeline


def example3_code_generation(pipeline):
    """Example 3: Generate PySpark code from metadata"""
    print("=" * 70)
    print("Example 3: PySpark Code Generation")
    print("=" * 70)
    
    executor = SparkMetadataExecutor(spark_session=None)
    code = executor.generate_spark_code(pipeline)
    
    print("\nGenerated PySpark Code:\n")
    print(code)
    
    # Save to file
    output_file = f"./generated_{pipeline.pipeline_id}.py"
    with open(output_file, 'w') as f:
        f.write(code)
    
    print(f"\n✓ Code saved to: {output_file}")
    print("\n" + "=" * 70 + "\n")


def example4_validation():
    """Example 4: Validate pipeline metadata"""
    print("=" * 70)
    print("Example 4: Pipeline Validation")
    print("=" * 70)
    
    store = MetadataStore("./example_metadata")
    
    # Create a pipeline with issues for demonstration
    bad_pipeline = PipelineMetadata(
        pipeline_id="invalid_pipeline",
        name="Invalid Pipeline",
        description="This pipeline has validation issues"
    )
    
    # No sources or targets - should fail validation
    
    validator = MetadataValidator()
    issues = validator.validate_pipeline(bad_pipeline)
    
    if issues:
        print("\n⚠️  Validation Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Pipeline validation passed!")
    
    print("\n" + "=" * 70 + "\n")


def example5_excel_export():
    """Example 5: Export pipeline to Excel"""
    print("=" * 70)
    print("Example 5: Excel Export")
    print("=" * 70)
    
    store = MetadataStore("./example_metadata")
    pipelines = store.list_pipelines()
    
    if pipelines:
        pipeline_id = pipelines[0]
        output_file = f"./{pipeline_id}_export.xlsx"
        
        print(f"\nExporting pipeline '{pipeline_id}' to Excel...")
        
        success = store.export_to_excel(pipeline_id, output_file)
        
        if success:
            print(f"✓ Successfully exported to: {output_file}")
            print("\nThe Excel file contains sheets for:")
            print("  - Sources (with columns)")
            print("  - Transformations")
            print("  - Data Quality Rules")
            print("  - Targets")
        else:
            print("✗ Export failed. Make sure pandas and openpyxl are installed:")
            print("  pip install pandas openpyxl")
    else:
        print("\nNo pipelines available for export")
    
    print("\n" + "=" * 70 + "\n")


def example6_spark_execution():
    """Example 6: Execute pipeline with Spark (requires PySpark)"""
    print("=" * 70)
    print("Example 6: Spark Pipeline Execution (Simulated)")
    print("=" * 70)
    
    print("""
This example shows how to execute a pipeline with actual Spark.
Note: Requires PySpark and actual data files.

Code example:
    """)
    
    code = """
from pyspark.sql import SparkSession
from metadata_storage import MetadataStore
from spark_integration import SparkMetadataExecutor
from metadata_models import PipelineMetadata

# Initialize Spark
spark = SparkSession.builder \\
    .appName("MetadataExecution") \\
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \\
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \\
    .getOrCreate()

# Load pipeline metadata
store = MetadataStore("./example_metadata")
pipeline_data = store.load_pipeline("customer_360")

# Create pipeline object (you'd need proper deserialization)
# pipeline = reconstruct_pipeline_from_dict(pipeline_data)

# Execute pipeline
executor = SparkMetadataExecutor(spark)
results = executor.execute_pipeline(pipeline, validate_dq=True)

# Check results
print("Execution Results:")
print(f"  Sources loaded: {results['sources_loaded']}")
print(f"  Transformations applied: {results['transformations_applied']}")
print(f"  Targets written: {results['targets_written']}")

# Check DQ validation results
if results['dq_validations']:
    print("\\nData Quality Validations:")
    for validation in results['dq_validations']:
        status = "✓ PASSED" if validation['passed'] else "✗ FAILED"
        print(f"  {status}: {validation['rule_name']}")
        if not validation['passed']:
            print(f"    Violations: {validation['violation_count']}")

# Check for errors
if results['errors']:
    print("\\n⚠️  Errors:")
    for error in results['errors']:
        print(f"  - {error}")

spark.stop()
    """
    
    print(code)
    print("\n" + "=" * 70 + "\n")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Spark Metadata Bot - Usage Examples" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")
    
    # Example 1: Conversational bot
    example1_conversational_bot()
    
    # Example 2: Programmatic creation
    pipeline = example2_programmatic_creation()
    
    # Example 3: Code generation
    example3_code_generation(pipeline)
    
    # Example 4: Validation
    example4_validation()
    
    # Example 5: Excel export
    example5_excel_export()
    
    # Example 6: Spark execution
    example6_spark_execution()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Try the interactive bot: python cli.py interactive")
    print("  2. Check generated files in ./example_metadata/")
    print("  3. Review generated PySpark code")
    print("  4. Explore the CLI: python cli.py --help")
    print("\n")


if __name__ == "__main__":
    main()
