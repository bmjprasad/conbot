#!/usr/bin/env python3
"""
Basic tests to verify the bot is working correctly
"""

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import metadata_models
        print("  ✓ metadata_models")
    except ImportError as e:
        print(f"  ✗ metadata_models: {e}")
        return False
    
    try:
        import metadata_storage
        print("  ✓ metadata_storage")
    except ImportError as e:
        print(f"  ✗ metadata_storage: {e}")
        return False
    
    try:
        import conversation_bot
        print("  ✓ conversation_bot")
    except ImportError as e:
        print(f"  ✗ conversation_bot: {e}")
        return False
    
    try:
        import spark_integration
        print("  ✓ spark_integration")
    except ImportError as e:
        print(f"  ✗ spark_integration: {e}")
        return False
    
    try:
        import cli
        print("  ✓ cli")
    except ImportError as e:
        print(f"  ✗ cli: {e}")
        return False
    
    return True


def test_metadata_models():
    """Test metadata models"""
    print("\nTesting metadata models...")
    from metadata_models import PipelineMetadata, SourceMetadata, ColumnMetadata
    
    try:
        pipeline = PipelineMetadata(
            pipeline_id="test",
            name="Test Pipeline",
            description="Test"
        )
        print("  ✓ PipelineMetadata creation")
        
        source = SourceMetadata(
            source_id="test_source",
            name="Test Source",
            location="/data/test",
            format="parquet"
        )
        pipeline.sources.append(source)
        print("  ✓ SourceMetadata creation")
        
        column = ColumnMetadata(
            name="test_col",
            data_type="string"
        )
        source.columns.append(column)
        print("  ✓ ColumnMetadata creation")
        
        json_str = pipeline.to_json()
        print("  ✓ JSON serialization")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_storage():
    """Test storage backend"""
    print("\nTesting storage backend...")
    from metadata_storage import MetadataStore
    from metadata_models import PipelineMetadata
    
    try:
        store = MetadataStore("./test_metadata")
        print("  ✓ MetadataStore initialization")
        
        pipeline = PipelineMetadata(
            pipeline_id="test_pipeline",
            name="Test Pipeline",
            description="Test"
        )
        
        success = store.save_pipeline(pipeline)
        if success:
            print("  ✓ Pipeline save")
        else:
            print("  ✗ Pipeline save failed")
            return False
        
        loaded = store.load_pipeline("test_pipeline")
        if loaded:
            print("  ✓ Pipeline load")
        else:
            print("  ✗ Pipeline load failed")
            return False
        
        pipelines = store.list_pipelines()
        if "test_pipeline" in pipelines:
            print("  ✓ Pipeline list")
        else:
            print("  ✗ Pipeline not in list")
            return False
        
        # Cleanup
        store.delete_pipeline("test_pipeline")
        import shutil
        shutil.rmtree("./test_metadata", ignore_errors=True)
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_bot():
    """Test conversation bot"""
    print("\nTesting conversation bot...")
    from conversation_bot import MetadataBot
    
    try:
        bot = MetadataBot("./test_bot_metadata")
        print("  ✓ Bot initialization")
        
        response = bot.process_message("help")
        if response and "help" in response.lower():
            print("  ✓ Help command")
        else:
            print("  ✗ Help command failed")
            return False
        
        response = bot.process_message("create pipeline name: test")
        if "created" in response.lower():
            print("  ✓ Create pipeline")
        else:
            print("  ✗ Create pipeline failed")
            return False
        
        # Cleanup
        import shutil
        shutil.rmtree("./test_bot_metadata", ignore_errors=True)
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Running Basic Tests for Spark Metadata Bot")
    print("=" * 70)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Metadata Models", test_metadata_models()))
    results.append(("Storage Backend", test_storage()))
    results.append(("Conversation Bot", test_bot()))
    
    print("\n" + "=" * 70)
    print("Test Results:")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python cli.py interactive")
        print("  2. Try: python example_usage.py")
        print("  3. Read: QUICKSTART.md")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
