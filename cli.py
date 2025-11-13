#!/usr/bin/env python3
"""
CLI Interface for Spark Metadata Conversational Bot
Provides command-line interface for managing metadata
"""
import argparse
import sys
from pathlib import Path
from conversation_bot import MetadataBot
from metadata_storage import MetadataStore
from spark_integration import SparkMetadataExecutor, MetadataValidator


def interactive_mode():
    """Run bot in interactive conversation mode"""
    bot = MetadataBot()
    print("=" * 70)
    print(" " * 15 + "Spark Metadata Conversational Bot")
    print("=" * 70)
    print("\nWelcome! I'll help you build metadata for your Spark pipelines.")
    print("Type 'help' to see available commands or 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nBot: Goodbye! Your metadata has been saved.")
                break
            
            if not user_input:
                continue
            
            response = bot.process_message(user_input)
            print(f"\nBot: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again or type 'help' for assistance.\n")


def list_pipelines(args):
    """List all saved pipelines"""
    store = MetadataStore(args.storage_path)
    pipelines = store.list_pipelines()
    
    if not pipelines:
        print("No pipelines found.")
        return
    
    print(f"\nFound {len(pipelines)} pipeline(s):\n")
    for pipeline_id in pipelines:
        pipeline = store.load_pipeline(pipeline_id)
        if pipeline:
            print(f"  📦 {pipeline['name']}")
            print(f"     ID: {pipeline_id}")
            print(f"     Sources: {len(pipeline['sources'])}")
            print(f"     Transformations: {len(pipeline['transformations'])}")
            print(f"     DQ Rules: {len(pipeline['data_quality_rules'])}")
            print(f"     Targets: {len(pipeline['targets'])}")
            print(f"     Created: {pipeline['created_at']}")
            print()


def show_pipeline(args):
    """Show details of a specific pipeline"""
    store = MetadataStore(args.storage_path)
    pipeline = store.load_pipeline(args.pipeline_id)
    
    if not pipeline:
        print(f"Pipeline '{args.pipeline_id}' not found.")
        return
    
    print(f"\n{'=' * 70}")
    print(f"Pipeline: {pipeline['name']} (ID: {args.pipeline_id})")
    print(f"{'=' * 70}")
    print(f"Description: {pipeline['description']}")
    print(f"Created: {pipeline['created_at']}")
    print(f"Updated: {pipeline['updated_at']}")
    
    # Sources
    if pipeline['sources']:
        print(f"\n{'─' * 70}")
        print("📥 SOURCES:")
        for src in pipeline['sources']:
            print(f"\n  • {src['name']} ({src['source_id']})")
            print(f"    Location: {src['location']}")
            print(f"    Format: {src['format']}")
            if src['columns']:
                print(f"    Columns:")
                for col in src['columns']:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"      - {col['name']}: {col['data_type']} {nullable}")
    
    # Transformations
    if pipeline['transformations']:
        print(f"\n{'─' * 70}")
        print("🔄 TRANSFORMATIONS:")
        for trans in pipeline['transformations']:
            print(f"\n  • {trans['name']} ({trans['transformation_id']})")
            print(f"    Type: {trans['transformation_type']}")
            print(f"    Source Refs: {', '.join(trans['source_refs'])}")
            print(f"    Logic: {trans['logic'][:100]}...")
    
    # Data Quality Rules
    if pipeline['data_quality_rules']:
        print(f"\n{'─' * 70}")
        print("✓ DATA QUALITY RULES:")
        for rule in pipeline['data_quality_rules']:
            enabled = "✓" if rule['enabled'] else "✗"
            print(f"\n  {enabled} {rule['name']} ({rule['rule_id']})")
            print(f"    Type: {rule['rule_type']}")
            print(f"    Columns: {', '.join(rule['target_columns'])}")
            print(f"    Condition: {rule['condition']}")
            print(f"    Severity: {rule['severity']}")
    
    # Targets
    if pipeline['targets']:
        print(f"\n{'─' * 70}")
        print("📤 TARGETS:")
        for tgt in pipeline['targets']:
            print(f"\n  • {tgt['name']} ({tgt['target_id']})")
            print(f"    Location: {tgt['location']}")
            print(f"    Format: {tgt['format']}")
            print(f"    Write Mode: {tgt['write_mode']}")
            print(f"    Source: {tgt['source_transformation_ref']}")
    
    print(f"\n{'=' * 70}\n")


def export_pipeline(args):
    """Export pipeline to Excel"""
    store = MetadataStore(args.storage_path)
    
    if not store.load_pipeline(args.pipeline_id):
        print(f"Pipeline '{args.pipeline_id}' not found.")
        return
    
    output_path = args.output or f"{args.pipeline_id}.xlsx"
    
    print(f"Exporting pipeline '{args.pipeline_id}' to {output_path}...")
    
    if store.export_to_excel(args.pipeline_id, output_path):
        print(f"✓ Successfully exported to {output_path}")
    else:
        print("✗ Export failed. Make sure pandas and openpyxl are installed.")


def generate_code(args):
    """Generate Spark code from pipeline metadata"""
    store = MetadataStore(args.storage_path)
    pipeline_data = store.load_pipeline(args.pipeline_id)
    
    if not pipeline_data:
        print(f"Pipeline '{args.pipeline_id}' not found.")
        return
    
    # Reconstruct pipeline object (simplified)
    from metadata_models import PipelineMetadata, SourceMetadata, TransformationMetadata, TargetMetadata, DataQualityRule
    
    pipeline = PipelineMetadata(
        pipeline_id=pipeline_data['pipeline_id'],
        name=pipeline_data['name'],
        description=pipeline_data['description']
    )
    
    # Reconstruct sources, transformations, etc. (simplified)
    # In production, you'd have proper deserialization
    
    executor = SparkMetadataExecutor(spark_session=None)
    code = executor.generate_spark_code(pipeline)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(code)
        print(f"✓ Generated code saved to {args.output}")
    else:
        print("\n" + "=" * 70)
        print("Generated PySpark Code:")
        print("=" * 70 + "\n")
        print(code)
        print("\n" + "=" * 70 + "\n")


def validate_pipeline(args):
    """Validate pipeline metadata"""
    store = MetadataStore(args.storage_path)
    pipeline_data = store.load_pipeline(args.pipeline_id)
    
    if not pipeline_data:
        print(f"Pipeline '{args.pipeline_id}' not found.")
        return
    
    print(f"Validating pipeline '{args.pipeline_id}'...\n")
    
    # Basic validations
    issues = []
    
    if not pipeline_data['sources']:
        issues.append("❌ No sources defined")
    else:
        print(f"✓ Sources: {len(pipeline_data['sources'])}")
    
    if not pipeline_data['targets']:
        issues.append("❌ No targets defined")
    else:
        print(f"✓ Targets: {len(pipeline_data['targets'])}")
    
    print(f"✓ Transformations: {len(pipeline_data['transformations'])}")
    print(f"✓ Data Quality Rules: {len(pipeline_data['data_quality_rules'])}")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    else:
        print("\n✅ Pipeline validation passed!")
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Spark Metadata Conversational Bot CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s interactive                    # Start interactive mode
  %(prog)s list                           # List all pipelines
  %(prog)s show my_pipeline               # Show pipeline details
  %(prog)s export my_pipeline -o out.xlsx # Export to Excel
  %(prog)s generate my_pipeline           # Generate Spark code
  %(prog)s validate my_pipeline           # Validate pipeline
        """
    )
    
    parser.add_argument(
        '--storage-path',
        default='./metadata_store',
        help='Path to metadata storage directory (default: ./metadata_store)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    subparsers.add_parser(
        'interactive',
        help='Start interactive conversation mode'
    )
    
    # List pipelines
    subparsers.add_parser(
        'list',
        help='List all pipelines'
    )
    
    # Show pipeline
    show_parser = subparsers.add_parser(
        'show',
        help='Show pipeline details'
    )
    show_parser.add_argument('pipeline_id', help='Pipeline ID')
    
    # Export pipeline
    export_parser = subparsers.add_parser(
        'export',
        help='Export pipeline to Excel'
    )
    export_parser.add_argument('pipeline_id', help='Pipeline ID')
    export_parser.add_argument('-o', '--output', help='Output file path')
    
    # Generate code
    generate_parser = subparsers.add_parser(
        'generate',
        help='Generate Spark code from pipeline'
    )
    generate_parser.add_argument('pipeline_id', help='Pipeline ID')
    generate_parser.add_argument('-o', '--output', help='Output file path')
    
    # Validate pipeline
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate pipeline metadata'
    )
    validate_parser.add_argument('pipeline_id', help='Pipeline ID')
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to interactive mode
        interactive_mode()
        return
    
    # Route to appropriate handler
    if args.command == 'interactive':
        interactive_mode()
    elif args.command == 'list':
        list_pipelines(args)
    elif args.command == 'show':
        show_pipeline(args)
    elif args.command == 'export':
        export_pipeline(args)
    elif args.command == 'generate':
        generate_code(args)
    elif args.command == 'validate':
        sys.exit(validate_pipeline(args))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
