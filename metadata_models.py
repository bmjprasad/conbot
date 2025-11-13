"""
Metadata Models for Spark Framework
Defines the schema for sources, transformations, data quality rules, and targets
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json


class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    DECIMAL = "decimal"
    ARRAY = "array"
    STRUCT = "struct"


class RuleType(Enum):
    NULL_CHECK = "null_check"
    RANGE_CHECK = "range_check"
    REGEX_CHECK = "regex_check"
    UNIQUE_CHECK = "unique_check"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    CUSTOM_SQL = "custom_sql"


class TransformationType(Enum):
    FILTER = "filter"
    MAP = "map"
    AGGREGATE = "aggregate"
    JOIN = "join"
    UNION = "union"
    WINDOW = "window"
    CUSTOM_SQL = "custom_sql"


@dataclass
class ColumnMetadata:
    """Metadata for a single column"""
    name: str
    data_type: str
    nullable: bool = True
    description: str = ""
    default_value: Optional[Any] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SourceMetadata:
    """Metadata for data source"""
    source_id: str
    name: str
    location: str  # File path, table name, or connection string
    format: str  # parquet, csv, json, jdbc, delta, etc.
    columns: List[ColumnMetadata] = field(default_factory=list)
    partition_columns: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)  # Additional read options
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'name': self.name,
            'location': self.location,
            'format': self.format,
            'columns': [col.to_dict() for col in self.columns],
            'partition_columns': self.partition_columns,
            'options': self.options,
            'description': self.description,
            'created_at': self.created_at
        }


@dataclass
class DataQualityRule:
    """Data quality rule definition"""
    rule_id: str
    name: str
    rule_type: str
    target_columns: List[str]
    condition: str  # SQL condition or validation logic
    severity: str = "error"  # error, warning, info
    description: str = ""
    enabled: bool = True
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TransformationMetadata:
    """Metadata for data transformation"""
    transformation_id: str
    name: str
    transformation_type: str
    source_refs: List[str]  # References to source_id
    logic: str  # SQL query or transformation logic
    output_columns: List[ColumnMetadata] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'transformation_id': self.transformation_id,
            'name': self.name,
            'transformation_type': self.transformation_type,
            'source_refs': self.source_refs,
            'logic': self.logic,
            'output_columns': [col.to_dict() for col in self.output_columns],
            'parameters': self.parameters,
            'description': self.description
        }


@dataclass
class TargetMetadata:
    """Metadata for data target/sink"""
    target_id: str
    name: str
    location: str
    format: str  # parquet, delta, jdbc, etc.
    write_mode: str = "overwrite"  # append, overwrite, merge
    partition_columns: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    source_transformation_ref: str = ""  # Reference to transformation_id
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PipelineMetadata:
    """Complete pipeline metadata"""
    pipeline_id: str
    name: str
    description: str
    sources: List[SourceMetadata] = field(default_factory=list)
    transformations: List[TransformationMetadata] = field(default_factory=list)
    data_quality_rules: List[DataQualityRule] = field(default_factory=list)
    targets: List[TargetMetadata] = field(default_factory=list)
    schedule: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'pipeline_id': self.pipeline_id,
            'name': self.name,
            'description': self.description,
            'sources': [src.to_dict() for src in self.sources],
            'transformations': [t.to_dict() for t in self.transformations],
            'data_quality_rules': [r.to_dict() for r in self.data_quality_rules],
            'targets': [tgt.to_dict() for tgt in self.targets],
            'schedule': self.schedule,
            'tags': self.tags,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
