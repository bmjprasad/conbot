# Quick Start Guide

## 5-Minute Getting Started

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the Bot

```bash
python cli.py interactive
```

### Step 3: Create Your First Pipeline

Copy and paste these commands one at a time:

```
create pipeline name: my_first_pipeline

add source name: input_data, location: /data/input.csv, format: csv

add column name: id, type: integer, nullable: false

add column name: value, type: double

add transformation name: filter_positive, logic: SELECT * FROM input_data WHERE value > 0

add rule name: check_positive, condition: value > 0, columns: value

add target name: output_data, location: /output/result.parquet, format: parquet

save
```

### Step 4: View Your Pipeline

```bash
python cli.py list
python cli.py show my_first_pipeline
```

### Step 5: Generate Spark Code

```bash
python cli.py generate my_first_pipeline -o my_pipeline.py
cat my_pipeline.py
```

## That's It! 🎉

You've just created a complete Spark pipeline metadata definition using natural language!

## What's Next?

### Export to Excel
```bash
python cli.py export my_first_pipeline -o pipeline.xlsx
```

### Run Examples
```bash
python example_usage.py
```

### Customize Your Pipeline

Try these commands in the bot:

```
# Add more complex transformations
add transformation name: aggregate, logic: SELECT id, AVG(value) as avg_value FROM input_data GROUP BY id

# Add different data quality rules
add rule name: unique_ids, condition: COUNT(DISTINCT id) = COUNT(*), columns: id, severity: error

# Configure write mode
add target name: incremental, location: /output/delta, format: delta, mode: append
```

### Learn More

- Read the full [README.md](README.md) for detailed documentation
- Run `python example_usage.py` to see more examples
- Type `help` in the bot to see all available commands

## Common Use Cases

### ETL Pipeline
```
create pipeline name: etl_pipeline
add source name: raw_data, location: s3://bucket/raw/, format: parquet
add transformation name: clean, logic: SELECT * FROM raw_data WHERE valid=true
add target name: curated, location: s3://bucket/curated/, format: delta
```

### Data Quality Check
```
add rule name: completeness, condition: column_name IS NOT NULL, columns: column_name
add rule name: uniqueness, condition: COUNT(DISTINCT id) = COUNT(id), columns: id
add rule name: range, condition: value BETWEEN 0 AND 100, columns: value
```

### Multi-Source Join
```
add source name: customers, location: /data/customers.parquet, format: parquet
add source name: orders, location: /data/orders.parquet, format: parquet
add transformation name: customer_orders, logic: SELECT c.*, o.order_id FROM customers c JOIN orders o ON c.id = o.customer_id
```

## Tips

1. **Be specific**: Include name, location, and format when adding sources/targets
2. **Use SQL**: Transformation logic should be valid Spark SQL
3. **Save often**: Use `save` command to persist your work
4. **Check validation**: Use `python cli.py validate <pipeline_id>` before execution
5. **Start simple**: Create basic pipelines first, then add complexity

## Need Help?

- Type `help` in the bot for available commands
- Check [README.md](README.md) for detailed documentation
- Review examples in `example_usage.py`

Happy metadata building! 🚀
