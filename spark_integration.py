"""
Spark Integration Module
Converts metadata definitions into executable Spark code and validates data quality
"""
from typing import Dict, List, Optional, Any
from metadata_models import (
    PipelineMetadata, SourceMetadata, TransformationMetadata,
    DataQualityRule, TargetMetadata
)
from metadata_storage import MetadataStore


class SparkMetadataExecutor:
    """Execute pipeline metadata using PySpark"""
    
    def __init__(self, spark_session=None):
        """
        Initialize with existing Spark session or create a new one
        
        Args:
            spark_session: Existing SparkSession (optional)
        """
        self.spark = spark_session
        if self.spark is None:
            try:
                from pyspark.sql import SparkSession
                self.spark = SparkSession.builder \
                    .appName("MetadataExecutor") \
                    .getOrCreate()
            except ImportError:
                print("Warning: PySpark not available. Install with: pip install pyspark")
    
    def load_source(self, source: SourceMetadata):
        """Load data source as Spark DataFrame"""
        if self.spark is None:
            raise RuntimeError("Spark session not available")
        
        options = source.options.copy()
        
        # Handle different formats
        if source.format.lower() == 'csv':
            options.setdefault('header', 'true')
            options.setdefault('inferSchema', 'true')
        
        df = self.spark.read \
            .format(source.format) \
            .options(**options) \
            .load(source.location)
        
        # Register as temp view for SQL access
        df.createOrReplaceTempView(source.source_id)
        
        return df
    
    def apply_transformation(self, transformation: TransformationMetadata, 
                           source_dfs: Dict[str, Any]):
        """Apply transformation logic"""
        if self.spark is None:
            raise RuntimeError("Spark session not available")
        
        # Register all source DataFrames as temp views if not already done
        for source_id, df in source_dfs.items():
            if not hasattr(df, 'createOrReplaceTempView'):
                continue
            df.createOrReplaceTempView(source_id)
        
        # Execute transformation logic (assumes SQL)
        result_df = self.spark.sql(transformation.logic)
        
        # Register result as temp view
        result_df.createOrReplaceTempView(transformation.transformation_id)
        
        return result_df
    
    def validate_data_quality(self, rule: DataQualityRule, df):
        """Validate data quality rule"""
        if self.spark is None:
            raise RuntimeError("Spark session not available")
        
        # Create temp view for validation
        df.createOrReplaceTempView("_dq_check_table")
        
        # Execute validation
        validation_sql = f"SELECT COUNT(*) as violation_count FROM _dq_check_table WHERE NOT ({rule.condition})"
        result = self.spark.sql(validation_sql).collect()
        
        violation_count = result[0]['violation_count']
        
        validation_result = {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'passed': violation_count == 0,
            'violation_count': violation_count,
            'severity': rule.severity
        }
        
        return validation_result
    
    def write_target(self, target: TargetMetadata, df):
        """Write DataFrame to target"""
        if self.spark is None:
            raise RuntimeError("Spark session not available")
        
        writer = df.write.format(target.format).mode(target.write_mode)
        
        if target.partition_columns:
            writer = writer.partitionBy(*target.partition_columns)
        
        if target.options:
            writer = writer.options(**target.options)
        
        writer.save(target.location)
        
        return True
    
    def execute_pipeline(self, pipeline: PipelineMetadata, 
                        validate_dq: bool = True) -> Dict[str, Any]:
        """Execute complete pipeline"""
        results = {
            'pipeline_id': pipeline.pipeline_id,
            'sources_loaded': [],
            'transformations_applied': [],
            'dq_validations': [],
            'targets_written': [],
            'errors': []
        }
        
        # Load sources
        source_dfs = {}
        for source in pipeline.sources:
            try:
                df = self.load_source(source)
                source_dfs[source.source_id] = df
                results['sources_loaded'].append(source.source_id)
            except Exception as e:
                results['errors'].append(f"Error loading source {source.source_id}: {str(e)}")
        
        # Apply transformations
        transformation_dfs = {}
        for transformation in pipeline.transformations:
            try:
                df = self.apply_transformation(transformation, source_dfs)
                transformation_dfs[transformation.transformation_id] = df
                results['transformations_applied'].append(transformation.transformation_id)
            except Exception as e:
                results['errors'].append(f"Error in transformation {transformation.transformation_id}: {str(e)}")
        
        # Validate data quality
        if validate_dq and pipeline.data_quality_rules:
            # Run DQ checks on transformed data
            for rule in pipeline.data_quality_rules:
                try:
                    # Apply to last transformation or first source
                    if transformation_dfs:
                        check_df = list(transformation_dfs.values())[-1]
                    elif source_dfs:
                        check_df = list(source_dfs.values())[-1]
                    else:
                        continue
                    
                    validation_result = self.validate_data_quality(rule, check_df)
                    results['dq_validations'].append(validation_result)
                    
                    # Stop on critical errors
                    if not validation_result['passed'] and rule.severity == 'error':
                        results['errors'].append(f"Data quality check failed: {rule.name}")
                        return results
                except Exception as e:
                    results['errors'].append(f"Error validating rule {rule.rule_id}: {str(e)}")
        
        # Write to targets
        for target in pipeline.targets:
            try:
                # Get source DataFrame
                if target.source_transformation_ref and target.source_transformation_ref in transformation_dfs:
                    output_df = transformation_dfs[target.source_transformation_ref]
                elif transformation_dfs:
                    output_df = list(transformation_dfs.values())[-1]
                elif source_dfs:
                    output_df = list(source_dfs.values())[-1]
                else:
                    results['errors'].append(f"No data available for target {target.target_id}")
                    continue
                
                self.write_target(target, output_df)
                results['targets_written'].append(target.target_id)
            except Exception as e:
                results['errors'].append(f"Error writing to target {target.target_id}: {str(e)}")
        
        return results
    
    def generate_spark_code(self, pipeline: PipelineMetadata) -> str:
        """Generate executable PySpark code from metadata"""
        code_lines = [
            "# Generated PySpark code from metadata",
            "from pyspark.sql import SparkSession",
            "",
            "# Initialize Spark",
            "spark = SparkSession.builder.appName('{}').getOrCreate()".format(pipeline.name),
            "",
            "# Load Sources"
        ]
        
        # Generate source loading code
        for source in pipeline.sources:
            code_lines.append(f"\n# Source: {source.name}")
            options_str = ", ".join([f"{k}='{v}'" for k, v in source.options.items()])
            if options_str:
                code_lines.append(
                    f"{source.source_id} = spark.read.format('{source.format}').options({options_str}).load('{source.location}')"
                )
            else:
                code_lines.append(
                    f"{source.source_id} = spark.read.format('{source.format}').load('{source.location}')"
                )
            code_lines.append(f"{source.source_id}.createOrReplaceTempView('{source.source_id}')")
        
        # Generate transformation code
        if pipeline.transformations:
            code_lines.append("\n# Transformations")
            for trans in pipeline.transformations:
                code_lines.append(f"\n# Transformation: {trans.name}")
                code_lines.append(f"{trans.transformation_id} = spark.sql('''")
                code_lines.append(f"{trans.logic}")
                code_lines.append(f"''')")
                code_lines.append(f"{trans.transformation_id}.createOrReplaceTempView('{trans.transformation_id}')")
        
        # Generate DQ validation code
        if pipeline.data_quality_rules:
            code_lines.append("\n# Data Quality Validations")
            code_lines.append("dq_results = []")
            for rule in pipeline.data_quality_rules:
                code_lines.append(f"\n# Rule: {rule.name}")
                code_lines.append(f"violations = spark.sql('''")
                code_lines.append(f"SELECT COUNT(*) as count FROM {pipeline.transformations[-1].transformation_id if pipeline.transformations else pipeline.sources[-1].source_id}")
                code_lines.append(f"WHERE NOT ({rule.condition})")
                code_lines.append(f"''').collect()[0]['count']")
                code_lines.append(f"dq_results.append({{'rule': '{rule.name}', 'violations': violations, 'passed': violations == 0}})")
                if rule.severity == 'error':
                    code_lines.append(f"if violations > 0:")
                    code_lines.append(f"    raise Exception('Data quality check failed: {rule.name}')")
        
        # Generate target writing code
        if pipeline.targets:
            code_lines.append("\n# Write to Targets")
            for target in pipeline.targets:
                code_lines.append(f"\n# Target: {target.name}")
                source_ref = target.source_transformation_ref or \
                           (pipeline.transformations[-1].transformation_id if pipeline.transformations else pipeline.sources[-1].source_id)
                
                if target.partition_columns:
                    partitions = ", ".join([f"'{col}'" for col in target.partition_columns])
                    code_lines.append(
                        f"{source_ref}.write.format('{target.format}').mode('{target.write_mode}').partitionBy({partitions}).save('{target.location}')"
                    )
                else:
                    code_lines.append(
                        f"{source_ref}.write.format('{target.format}').mode('{target.write_mode}').save('{target.location}')"
                    )
        
        code_lines.append("\nprint('Pipeline executed successfully!')")
        
        return "\n".join(code_lines)


class MetadataValidator:
    """Validate metadata definitions"""
    
    @staticmethod
    def validate_pipeline(pipeline: PipelineMetadata) -> List[str]:
        """Validate pipeline metadata and return list of issues"""
        issues = []
        
        # Check if pipeline has sources
        if not pipeline.sources:
            issues.append("Pipeline has no data sources defined")
        
        # Check if pipeline has targets
        if not pipeline.targets:
            issues.append("Pipeline has no targets defined")
        
        # Validate source references in transformations
        source_ids = {src.source_id for src in pipeline.sources}
        transformation_ids = {trans.transformation_id for trans in pipeline.transformations}
        
        for trans in pipeline.transformations:
            for ref in trans.source_refs:
                if ref not in source_ids and ref not in transformation_ids:
                    issues.append(f"Transformation '{trans.name}' references unknown source '{ref}'")
        
        # Validate target references
        for target in pipeline.targets:
            if target.source_transformation_ref:
                if target.source_transformation_ref not in transformation_ids and \
                   target.source_transformation_ref not in source_ids:
                    issues.append(f"Target '{target.name}' references unknown transformation '{target.source_transformation_ref}'")
        
        # Validate DQ rules
        for rule in pipeline.data_quality_rules:
            if not rule.condition:
                issues.append(f"Data quality rule '{rule.name}' has no condition defined")
        
        return issues


def main():
    """Example usage"""
    from metadata_storage import MetadataStore
    
    store = MetadataStore()
    pipelines = store.list_pipelines()
    
    if not pipelines:
        print("No pipelines found. Create one using the conversation bot first.")
        return
    
    # Load first pipeline
    pipeline_data = store.load_pipeline(pipelines[0])
    print(f"Loaded pipeline: {pipeline_data['name']}")
    
    # Validate
    validator = MetadataValidator()
    # Would need to reconstruct PipelineMetadata object for validation
    
    print("\nTo execute the pipeline with Spark, use:")
    print("  executor = SparkMetadataExecutor()")
    print("  results = executor.execute_pipeline(pipeline)")


if __name__ == "__main__":
    main()
