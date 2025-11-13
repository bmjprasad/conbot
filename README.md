# Spark Metadata Conversational Bot

A conversational AI bot that helps you build and manage metadata for Spark-based data pipelines through natural language interaction. Say goodbye to manually filling Excel templates!

## 🎯 Overview

This bot replaces traditional Excel-based metadata management with an intuitive conversational interface. Simply chat with the bot to define:

- **Data Sources**: Column definitions, file locations, formats
- **Transformations**: SQL logic, data processing steps  
- **Data Quality Rules**: Validation conditions, severity levels
- **Target Sinks**: Output locations, write modes, formats

The bot automatically:
- ✅ Stores metadata in structured JSON format
- ✅ Validates pipeline configurations
- ✅ Generates executable PySpark code
- ✅ Exports to Excel for compatibility
- ✅ Integrates with Spark for execution

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Interactive Mode

```bash
python cli.py interactive
```

Or run the bot directly:

```bash
python conversation_bot.py
```

## 💬 Usage Examples

### Example 1: Create a Simple ETL Pipeline

```
You: create pipeline name: customer_etl, description: ETL for customer data

Bot: ✓ Created pipeline 'customer_etl' (ID: customer_etl)
     What would you like to add?

You: add source name: customers, location: /data/customers.parquet, format: parquet

Bot: ✓ Added source 'customers'
     Would you like to add columns to this source?

You: add column name: customer_id, type: integer, nullable: false

Bot: ✓ Added column 'customer_id' (integer) to source 'customers'

You: add column name: name, type: string

Bot: ✓ Added column 'name' (string) to source 'customers'

You: add transformation name: filter_active, logic: SELECT * FROM customers WHERE status='active'

Bot: ✓ Added transformation 'filter_active'

You: add rule name: check_nulls, condition: customer_id IS NOT NULL, columns: customer_id

Bot: ✓ Added data quality rule 'check_nulls'

You: add target name: active_customers, location: /output/active.parquet, format: delta, mode: overwrite

Bot: ✓ Added target 'active_customers'

You: save

Bot: ✓ Pipeline 'customer_etl' saved successfully!
     Summary:
       - Sources: 1
       - Transformations: 1
       - Data Quality Rules: 1
       - Targets: 1
```

### Example 2: Define Complex Transformations

```
You: add transformation name: aggregate_sales, type: aggregate

Bot: What is the transformation logic/SQL for 'aggregate_sales'?

You: SELECT customer_id, SUM(amount) as total_sales, COUNT(*) as order_count 
     FROM orders GROUP BY customer_id

Bot: ✓ Transformation 'aggregate_sales' added
```

### Example 3: Add Data Quality Rules

```
You: add rule name: range_check, type: range_check, condition: amount > 0 AND amount < 1000000, 
     columns: amount, severity: error

Bot: ✓ Added data quality rule 'range_check'
     Type: range_check
     Condition: amount > 0 AND amount < 1000000
     Severity: error
```

## 🛠️ CLI Commands

### Interactive Mode
```bash
python cli.py interactive
```

### List All Pipelines
```bash
python cli.py list
```

### Show Pipeline Details
```bash
python cli.py show customer_etl
```

### Export to Excel
```bash
python cli.py export customer_etl -o output.xlsx
```

### Generate PySpark Code
```bash
python cli.py generate customer_etl -o pipeline.py
```

### Validate Pipeline
```bash
python cli.py validate customer_etl
```

## 📋 Bot Commands Reference

### Pipeline Management
- `create pipeline name: <name>, description: <desc>` - Create new pipeline
- `save` - Save current pipeline
- `list` - List all saved pipelines
- `load pipeline <id>` - Load existing pipeline

### Data Sources
- `add source name: <name>, location: <path>, format: <format>` - Add data source
- `add column name: <name>, type: <type>, nullable: true/false` - Add column to source

**Supported formats**: parquet, csv, json, jdbc, delta, avro, orc

**Supported types**: string, integer, double, boolean, date, timestamp, decimal, array, struct

### Transformations
- `add transformation name: <name>, type: <type>, logic: <sql>` - Add transformation

**Transformation types**: filter, map, aggregate, join, union, window, custom_sql

### Data Quality Rules
- `add rule name: <name>, type: <type>, condition: <condition>, columns: <cols>, severity: <level>` - Add DQ rule

**Rule types**: null_check, range_check, regex_check, unique_check, referential_integrity, custom_sql

**Severity levels**: error, warning, info

### Targets
- `add target name: <name>, location: <path>, format: <format>, mode: <mode>` - Add target sink

**Write modes**: append, overwrite, merge

### Other Commands
- `help` - Show available commands
- `export to excel` - Export current pipeline to Excel
- `exit` / `quit` - Exit the bot

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Conversational Interface (CLI/Chat)   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        Conversation Bot Engine          │
│  - Intent Recognition                   │
│  - Context Management                   │
│  - Natural Language Processing          │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Metadata Models Layer           │
│  - Pipeline Metadata                    │
│  - Source/Target Definitions            │
│  - Transformation Logic                 │
│  - Data Quality Rules                   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Storage Backend (JSON)          │
│  - Persistence                          │
│  - CRUD Operations                      │
│  - Excel Export                         │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Spark Integration Module           │
│  - Code Generation                      │
│  - Pipeline Execution                   │
│  - DQ Validation                        │
└─────────────────────────────────────────┘
```

## 📦 Project Structure

```
.
├── metadata_models.py      # Data models for pipeline metadata
├── metadata_storage.py     # Storage backend (JSON + Excel export)
├── conversation_bot.py     # Conversational bot engine
├── spark_integration.py    # Spark integration & code generation
├── cli.py                  # Command-line interface
├── requirements.txt        # Python dependencies
└── README.md              # This file

Generated:
└── metadata_store/        # Storage directory
    └── pipelines/         # Saved pipeline JSON files
```

## 🔌 Integration with Spark

### Execute Pipeline Directly

```python
from metadata_storage import MetadataStore
from spark_integration import SparkMetadataExecutor
from pyspark.sql import SparkSession

# Initialize Spark
spark = SparkSession.builder.appName("MyApp").getOrCreate()

# Load pipeline
store = MetadataStore()
pipeline_data = store.load_pipeline("customer_etl")

# Execute
executor = SparkMetadataExecutor(spark)
results = executor.execute_pipeline(pipeline, validate_dq=True)

print(f"Sources loaded: {results['sources_loaded']}")
print(f"Transformations applied: {results['transformations_applied']}")
print(f"DQ validations: {results['dq_validations']}")
print(f"Targets written: {results['targets_written']}")
```

### Generate Standalone Code

```bash
python cli.py generate customer_etl -o generated_pipeline.py
python generated_pipeline.py  # Run generated code
```

## 🎨 Features

### ✨ Conversational Interface
- Natural language understanding
- Context-aware responses
- Multi-step workflows
- Error handling and guidance

### 📊 Metadata Management
- Structured schema definitions
- Source/target configurations
- Transformation logic
- Data quality rules
- Version control ready (JSON format)

### 🔍 Data Quality
- Multiple rule types
- Severity levels (error/warning/info)
- Automated validation during execution
- Detailed violation reporting

### 🚀 Spark Integration
- Automatic code generation
- Direct pipeline execution
- DQ validation
- Support for multiple formats

### 📈 Excel Compatibility
- Export to Excel templates
- Multiple sheets (sources, transformations, DQ, targets)
- Compatible with existing workflows
- Easy sharing and documentation

## 🔧 Advanced Usage

### Custom Storage Location

```bash
python cli.py --storage-path /custom/path interactive
```

### Programmatic Usage

```python
from conversation_bot import MetadataBot

bot = MetadataBot(storage_path="./my_metadata")

# Process messages
response = bot.process_message("create pipeline name: my_pipeline")
print(response)

response = bot.process_message("add source name: data, location: /path/to/data")
print(response)

response = bot.process_message("save")
print(response)
```

### Extend with Advanced NLP

The bot uses simple keyword matching by default. For production use, integrate with:

- **Rasa**: Open-source conversational AI framework
- **spaCy**: Industrial-strength NLP
- **Transformers**: Pre-trained language models (BERT, GPT)

```python
# Example: Add to conversation_bot.py
from transformers import pipeline

class MetadataBot:
    def __init__(self, use_transformers=True):
        if use_transformers:
            self.classifier = pipeline("zero-shot-classification")
    
    def detect_intent(self, user_input):
        # Use transformer model for intent detection
        candidate_labels = list(self.intents.keys())
        result = self.classifier(user_input, candidate_labels)
        return result['labels'][0], result['scores'][0]
```

## 📝 Metadata Schema

### Pipeline Metadata Structure

```json
{
  "pipeline_id": "customer_etl",
  "name": "Customer ETL Pipeline",
  "description": "Extract, transform, and load customer data",
  "sources": [
    {
      "source_id": "customers",
      "name": "Customers Source",
      "location": "/data/customers.parquet",
      "format": "parquet",
      "columns": [
        {
          "name": "customer_id",
          "data_type": "integer",
          "nullable": false,
          "description": "Unique customer identifier"
        }
      ]
    }
  ],
  "transformations": [
    {
      "transformation_id": "filter_active",
      "name": "Filter Active Customers",
      "transformation_type": "filter",
      "source_refs": ["customers"],
      "logic": "SELECT * FROM customers WHERE status='active'"
    }
  ],
  "data_quality_rules": [
    {
      "rule_id": "check_nulls",
      "name": "Null Check",
      "rule_type": "null_check",
      "target_columns": ["customer_id"],
      "condition": "customer_id IS NOT NULL",
      "severity": "error"
    }
  ],
  "targets": [
    {
      "target_id": "active_customers",
      "name": "Active Customers",
      "location": "/output/active.parquet",
      "format": "parquet",
      "write_mode": "overwrite"
    }
  ]
}
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. **Advanced NLP**: Integrate Rasa or transformers for better intent recognition
2. **Web Interface**: Build a web UI for the bot
3. **More Formats**: Add support for Kafka, MongoDB, etc.
4. **Lineage Tracking**: Add data lineage visualization
5. **Scheduling**: Integration with Airflow/Databricks Jobs
6. **Version Control**: Git integration for metadata versioning

## 📄 License

MIT License - feel free to use in your projects!

## 🐛 Troubleshooting

### Bot doesn't understand my command
- Try rephrasing with keywords from the help command
- Use explicit format: `add source name: X, location: Y, format: Z`
- Check examples in this README

### Excel export fails
```bash
pip install pandas openpyxl
```

### Spark execution fails
```bash
pip install pyspark
# Or use your existing Spark installation
```

### Storage path issues
```bash
# Ensure directory exists and is writable
mkdir -p ./metadata_store/pipelines
chmod 755 ./metadata_store
```

## 📧 Support

For issues or questions:
1. Check the examples in this README
2. Use the `help` command in the bot
3. Review error messages carefully
4. Check that all dependencies are installed

---

**Built to make Spark metadata management conversational and intuitive!** 🚀
