"""
Conversational Bot for Spark Metadata Management
Handles natural language interaction for defining metadata
"""
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from metadata_models import (
    PipelineMetadata, SourceMetadata, TransformationMetadata,
    DataQualityRule, TargetMetadata, ColumnMetadata
)
from metadata_storage import MetadataStore


class ConversationState:
    """Tracks the state of an ongoing conversation"""
    
    def __init__(self):
        self.current_pipeline = None
        self.current_context = None  # source, transformation, dq_rule, target
        self.pending_data = {}
        self.conversation_history = []
    
    def reset(self):
        """Reset conversation state"""
        self.__init__()


class MetadataBot:
    """Conversational bot for building Spark metadata"""
    
    def __init__(self, storage_path: str = "./metadata_store"):
        self.store = MetadataStore(storage_path)
        self.state = ConversationState()
        self.intents = {
            'create_pipeline': ['create pipeline', 'new pipeline', 'start pipeline'],
            'add_source': ['add source', 'new source', 'define source', 'create source'],
            'add_column': ['add column', 'define column', 'new column'],
            'add_transformation': ['add transformation', 'new transformation', 'transform', 'create transformation'],
            'add_dq_rule': ['add rule', 'add quality rule', 'data quality', 'add validation', 'define rule'],
            'add_target': ['add target', 'new target', 'define target', 'sink to', 'write to'],
            'save_pipeline': ['save', 'save pipeline', 'finish', 'complete'],
            'list_pipelines': ['list', 'show pipelines', 'list pipelines'],
            'load_pipeline': ['load', 'open pipeline', 'load pipeline'],
            'export_excel': ['export', 'export to excel', 'generate excel'],
            'help': ['help', 'what can you do', 'commands']
        }
    
    def detect_intent(self, user_input: str) -> Tuple[str, float]:
        """Simple intent detection based on keyword matching"""
        user_input_lower = user_input.lower()
        best_intent = 'unknown'
        best_score = 0.0
        
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    score = len(pattern) / len(user_input_lower)
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        return best_intent, best_score
    
    def extract_key_value(self, text: str, key: str) -> Optional[str]:
        """Extract value for a key from text"""
        patterns = [
            f"{key}\\s*[:=]\\s*([^,]+)",
            f"{key}\\s+is\\s+([^,]+)",
            f"{key}\\s+([^,]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def process_message(self, user_input: str) -> str:
        """Process user message and return bot response"""
        self.state.conversation_history.append(('user', user_input))
        
        intent, confidence = self.detect_intent(user_input)
        
        response = ""
        
        if intent == 'create_pipeline':
            response = self._handle_create_pipeline(user_input)
        elif intent == 'add_source':
            response = self._handle_add_source(user_input)
        elif intent == 'add_column':
            response = self._handle_add_column(user_input)
        elif intent == 'add_transformation':
            response = self._handle_add_transformation(user_input)
        elif intent == 'add_dq_rule':
            response = self._handle_add_dq_rule(user_input)
        elif intent == 'add_target':
            response = self._handle_add_target(user_input)
        elif intent == 'save_pipeline':
            response = self._handle_save_pipeline()
        elif intent == 'list_pipelines':
            response = self._handle_list_pipelines()
        elif intent == 'load_pipeline':
            response = self._handle_load_pipeline(user_input)
        elif intent == 'export_excel':
            response = self._handle_export_excel(user_input)
        elif intent == 'help':
            response = self._handle_help()
        else:
            response = self._handle_context_based_input(user_input)
        
        self.state.conversation_history.append(('bot', response))
        return response
    
    def _handle_create_pipeline(self, user_input: str) -> str:
        """Handle pipeline creation"""
        name = self.extract_key_value(user_input, "name")
        if not name:
            name = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        pipeline_id = name.lower().replace(" ", "_")
        description = self.extract_key_value(user_input, "description") or ""
        
        self.state.current_pipeline = PipelineMetadata(
            pipeline_id=pipeline_id,
            name=name,
            description=description
        )
        
        return (f"✓ Created pipeline '{name}' (ID: {pipeline_id})\n"
                f"What would you like to add? You can:\n"
                f"- Add a data source\n"
                f"- Add a transformation\n"
                f"- Add data quality rules\n"
                f"- Add a target")
    
    def _handle_add_source(self, user_input: str) -> str:
        """Handle adding a data source"""
        if not self.state.current_pipeline:
            return "Please create a pipeline first using 'create pipeline'"
        
        # Extract source details
        name = self.extract_key_value(user_input, "name") or f"source_{len(self.state.current_pipeline.sources) + 1}"
        location = self.extract_key_value(user_input, "location") or self.extract_key_value(user_input, "path")
        format_type = self.extract_key_value(user_input, "format") or "parquet"
        
        if not location:
            self.state.current_context = 'source_needs_location'
            self.state.pending_data = {'name': name, 'format': format_type}
            return f"What is the file location/path for source '{name}'?"
        
        source_id = name.lower().replace(" ", "_")
        source = SourceMetadata(
            source_id=source_id,
            name=name,
            location=location,
            format=format_type
        )
        
        self.state.current_pipeline.sources.append(source)
        self.state.current_context = 'source'
        self.state.pending_data = {'source': source}
        
        return (f"✓ Added source '{name}'\n"
                f"  Location: {location}\n"
                f"  Format: {format_type}\n\n"
                f"Would you like to add columns to this source? (e.g., 'add column name: id, type: integer')")
    
    def _handle_add_column(self, user_input: str) -> str:
        """Handle adding a column to current source"""
        if self.state.current_context != 'source':
            return "Please add a source first before defining columns"
        
        source = self.state.pending_data.get('source')
        if not source:
            return "No active source to add columns to"
        
        # Extract column details
        col_name = self.extract_key_value(user_input, "name")
        col_type = self.extract_key_value(user_input, "type") or "string"
        nullable_str = self.extract_key_value(user_input, "nullable")
        nullable = nullable_str.lower() != 'false' if nullable_str else True
        description = self.extract_key_value(user_input, "description") or ""
        
        if not col_name:
            return "Please specify the column name (e.g., 'name: customer_id')"
        
        column = ColumnMetadata(
            name=col_name,
            data_type=col_type,
            nullable=nullable,
            description=description
        )
        
        source.columns.append(column)
        
        return (f"✓ Added column '{col_name}' ({col_type}) to source '{source.name}'\n"
                f"Add more columns or move to next step?")
    
    def _handle_add_transformation(self, user_input: str) -> str:
        """Handle adding a transformation"""
        if not self.state.current_pipeline:
            return "Please create a pipeline first"
        
        if not self.state.current_pipeline.sources:
            return "Please add at least one source before defining transformations"
        
        name = self.extract_key_value(user_input, "name") or f"transform_{len(self.state.current_pipeline.transformations) + 1}"
        trans_type = self.extract_key_value(user_input, "type") or "custom_sql"
        logic = self.extract_key_value(user_input, "logic") or self.extract_key_value(user_input, "sql")
        
        if not logic:
            self.state.current_context = 'transformation_needs_logic'
            self.state.pending_data = {'name': name, 'type': trans_type}
            return f"What is the transformation logic/SQL for '{name}'?"
        
        # Use all sources by default
        source_refs = [src.source_id for src in self.state.current_pipeline.sources]
        
        trans_id = name.lower().replace(" ", "_")
        transformation = TransformationMetadata(
            transformation_id=trans_id,
            name=name,
            transformation_type=trans_type,
            source_refs=source_refs,
            logic=logic
        )
        
        self.state.current_pipeline.transformations.append(transformation)
        
        return (f"✓ Added transformation '{name}'\n"
                f"  Type: {trans_type}\n"
                f"  Logic: {logic[:50]}...\n\n"
                f"Continue with data quality rules or targets?")
    
    def _handle_add_dq_rule(self, user_input: str) -> str:
        """Handle adding a data quality rule"""
        if not self.state.current_pipeline:
            return "Please create a pipeline first"
        
        name = self.extract_key_value(user_input, "name") or f"rule_{len(self.state.current_pipeline.data_quality_rules) + 1}"
        rule_type = self.extract_key_value(user_input, "type") or "custom_sql"
        condition = self.extract_key_value(user_input, "condition") or self.extract_key_value(user_input, "check")
        columns_str = self.extract_key_value(user_input, "columns") or self.extract_key_value(user_input, "column")
        severity = self.extract_key_value(user_input, "severity") or "error"
        
        if not condition:
            self.state.current_context = 'dq_rule_needs_condition'
            self.state.pending_data = {'name': name, 'type': rule_type}
            return f"What is the validation condition for rule '{name}'?"
        
        target_columns = [c.strip() for c in columns_str.split(",")] if columns_str else ["*"]
        
        rule_id = name.lower().replace(" ", "_")
        rule = DataQualityRule(
            rule_id=rule_id,
            name=name,
            rule_type=rule_type,
            target_columns=target_columns,
            condition=condition,
            severity=severity
        )
        
        self.state.current_pipeline.data_quality_rules.append(rule)
        
        return (f"✓ Added data quality rule '{name}'\n"
                f"  Type: {rule_type}\n"
                f"  Condition: {condition}\n"
                f"  Severity: {severity}\n\n"
                f"Add more rules or continue to define targets?")
    
    def _handle_add_target(self, user_input: str) -> str:
        """Handle adding a target/sink"""
        if not self.state.current_pipeline:
            return "Please create a pipeline first"
        
        name = self.extract_key_value(user_input, "name") or f"target_{len(self.state.current_pipeline.targets) + 1}"
        location = self.extract_key_value(user_input, "location") or self.extract_key_value(user_input, "path")
        format_type = self.extract_key_value(user_input, "format") or "parquet"
        write_mode = self.extract_key_value(user_input, "mode") or "overwrite"
        
        if not location:
            self.state.current_context = 'target_needs_location'
            self.state.pending_data = {'name': name, 'format': format_type, 'mode': write_mode}
            return f"What is the target location/path for '{name}'?"
        
        # Reference last transformation if available
        source_ref = ""
        if self.state.current_pipeline.transformations:
            source_ref = self.state.current_pipeline.transformations[-1].transformation_id
        
        target_id = name.lower().replace(" ", "_")
        target = TargetMetadata(
            target_id=target_id,
            name=name,
            location=location,
            format=format_type,
            write_mode=write_mode,
            source_transformation_ref=source_ref
        )
        
        self.state.current_pipeline.targets.append(target)
        
        return (f"✓ Added target '{name}'\n"
                f"  Location: {location}\n"
                f"  Format: {format_type}\n"
                f"  Write Mode: {write_mode}\n\n"
                f"Target added successfully! Use 'save' to save the pipeline.")
    
    def _handle_save_pipeline(self) -> str:
        """Save the current pipeline"""
        if not self.state.current_pipeline:
            return "No pipeline to save. Create a pipeline first."
        
        self.state.current_pipeline.updated_at = datetime.now().isoformat()
        
        if self.store.save_pipeline(self.state.current_pipeline):
            pipeline_name = self.state.current_pipeline.name
            pipeline_id = self.state.current_pipeline.pipeline_id
            
            # Summary
            summary = (
                f"✓ Pipeline '{pipeline_name}' saved successfully!\n\n"
                f"Summary:\n"
                f"  - Sources: {len(self.state.current_pipeline.sources)}\n"
                f"  - Transformations: {len(self.state.current_pipeline.transformations)}\n"
                f"  - Data Quality Rules: {len(self.state.current_pipeline.data_quality_rules)}\n"
                f"  - Targets: {len(self.state.current_pipeline.targets)}\n\n"
                f"Pipeline ID: {pipeline_id}\n"
                f"You can load it later using 'load pipeline {pipeline_id}'"
            )
            
            self.state.reset()
            return summary
        else:
            return "Error saving pipeline. Please try again."
    
    def _handle_list_pipelines(self) -> str:
        """List all saved pipelines"""
        pipelines = self.store.list_pipelines()
        if not pipelines:
            return "No pipelines found. Create one using 'create pipeline'"
        
        response = "Saved Pipelines:\n"
        for pipeline_id in pipelines:
            pipeline = self.store.load_pipeline(pipeline_id)
            if pipeline:
                response += f"  - {pipeline['name']} (ID: {pipeline_id})\n"
        
        return response
    
    def _handle_load_pipeline(self, user_input: str) -> str:
        """Load an existing pipeline"""
        pipeline_id = user_input.replace("load", "").replace("pipeline", "").strip()
        
        if not pipeline_id:
            return "Please specify pipeline ID (e.g., 'load pipeline my_pipeline')"
        
        pipeline_data = self.store.load_pipeline(pipeline_id)
        if not pipeline_data:
            return f"Pipeline '{pipeline_id}' not found"
        
        # Reconstruct pipeline object
        # This is simplified - in production you'd have proper deserialization
        return f"Pipeline '{pipeline_data['name']}' loaded (simplified view)\n{pipeline_data}"
    
    def _handle_export_excel(self, user_input: str) -> str:
        """Export pipeline to Excel"""
        if not self.state.current_pipeline:
            return "No active pipeline. Create or load a pipeline first."
        
        output_path = self.extract_key_value(user_input, "to") or f"{self.state.current_pipeline.pipeline_id}.xlsx"
        
        if self.store.export_to_excel(self.state.current_pipeline.pipeline_id, output_path):
            return f"✓ Pipeline exported to {output_path}"
        else:
            return "Error exporting to Excel. Make sure pandas and openpyxl are installed."
    
    def _handle_help(self) -> str:
        """Provide help information"""
        return """
Spark Metadata Bot - Available Commands:

Pipeline Management:
  - create pipeline name: <name> - Create a new pipeline
  - save - Save the current pipeline
  - list - List all pipelines
  - load pipeline <id> - Load an existing pipeline

Data Sources:
  - add source name: <name>, location: <path>, format: <format>
  - add column name: <name>, type: <type>, nullable: true/false

Transformations:
  - add transformation name: <name>, type: <type>, logic: <sql>

Data Quality:
  - add rule name: <name>, type: <type>, condition: <condition>, columns: <cols>

Targets:
  - add target name: <name>, location: <path>, format: <format>, mode: <mode>

Other:
  - export to excel - Export current pipeline to Excel
  - help - Show this help message

Example:
  "create pipeline name: customer_etl"
  "add source name: customers, location: /data/customers.parquet, format: parquet"
  "add column name: customer_id, type: integer, nullable: false"
  "add transformation name: filter_active, logic: SELECT * FROM customers WHERE status='active'"
  "add rule name: check_nulls, condition: customer_id IS NOT NULL, columns: customer_id"
  "add target name: active_customers, location: /output/active.parquet"
  "save"
"""
    
    def _handle_context_based_input(self, user_input: str) -> str:
        """Handle input based on current context"""
        context = self.state.current_context
        
        if context == 'source_needs_location':
            data = self.state.pending_data
            source_id = data['name'].lower().replace(" ", "_")
            source = SourceMetadata(
                source_id=source_id,
                name=data['name'],
                location=user_input.strip(),
                format=data['format']
            )
            self.state.current_pipeline.sources.append(source)
            self.state.current_context = 'source'
            self.state.pending_data = {'source': source}
            return f"✓ Source '{data['name']}' added with location: {user_input}\nAdd columns to this source?"
        
        elif context == 'transformation_needs_logic':
            data = self.state.pending_data
            trans_id = data['name'].lower().replace(" ", "_")
            source_refs = [src.source_id for src in self.state.current_pipeline.sources]
            transformation = TransformationMetadata(
                transformation_id=trans_id,
                name=data['name'],
                transformation_type=data['type'],
                source_refs=source_refs,
                logic=user_input.strip()
            )
            self.state.current_pipeline.transformations.append(transformation)
            self.state.current_context = None
            self.state.pending_data = {}
            return f"✓ Transformation '{data['name']}' added"
        
        elif context == 'dq_rule_needs_condition':
            data = self.state.pending_data
            rule_id = data['name'].lower().replace(" ", "_")
            rule = DataQualityRule(
                rule_id=rule_id,
                name=data['name'],
                rule_type=data['type'],
                target_columns=["*"],
                condition=user_input.strip()
            )
            self.state.current_pipeline.data_quality_rules.append(rule)
            self.state.current_context = None
            self.state.pending_data = {}
            return f"✓ Data quality rule '{data['name']}' added"
        
        elif context == 'target_needs_location':
            data = self.state.pending_data
            target_id = data['name'].lower().replace(" ", "_")
            source_ref = ""
            if self.state.current_pipeline.transformations:
                source_ref = self.state.current_pipeline.transformations[-1].transformation_id
            target = TargetMetadata(
                target_id=target_id,
                name=data['name'],
                location=user_input.strip(),
                format=data['format'],
                write_mode=data['mode'],
                source_transformation_ref=source_ref
            )
            self.state.current_pipeline.targets.append(target)
            self.state.current_context = None
            self.state.pending_data = {}
            return f"✓ Target '{data['name']}' added with location: {user_input}"
        
        return ("I didn't understand that. Type 'help' to see available commands.")


def main():
    """Interactive CLI for the bot"""
    bot = MetadataBot()
    print("=" * 60)
    print("Spark Metadata Conversational Bot")
    print("=" * 60)
    print(bot._handle_help())
    print("\nType 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            response = bot.process_message(user_input)
            print(f"\nBot: {response}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
