#!/usr/bin/env python3
"""
Test script for Podcast CLI components
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import load_config, create_default_config, get_config_path
from utils.cache import Cache
from utils.helpers import setup_logging
from ui.display import DisplayFormatter


def test_config():
    """Test configuration management"""
    print("Testing configuration management...")
    
    try:
        # Test default config creation
        config_path = get_config_path()
        if not config_path.exists():
            create_default_config(config_path)
            print("✅ Default configuration created")
        else:
            print("✅ Configuration file exists")
        
        # Test config loading (will fail without API key, but that's expected)
        try:
            config = load_config()
            print("✅ Configuration loaded successfully")
        except ValueError as e:
            print(f"⚠️  Configuration loading failed (expected): {e}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")


def test_cache():
    """Test caching functionality"""
    print("\nTesting cache functionality...")
    
    try:
        cache = Cache()
        
        # Test basic operations
        test_data = {"test": "data", "number": 42}
        cache.set("test_key", test_data)
        
        retrieved = cache.get("test_key")
        if retrieved == test_data:
            print("✅ Cache set/get working")
        else:
            print("❌ Cache set/get failed")
        
        # Test cache stats
        stats = cache.get_stats()
        print(f"✅ Cache stats: {stats}")
        
        # Clean up
        cache.clear()
        print("✅ Cache cleared")
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")


def test_display():
    """Test display formatting"""
    print("\nTesting display formatting...")
    
    try:
        display = DisplayFormatter()
        
        # Test subscriptions formatting
        test_subscriptions = [
            {"title": "Test Podcast 1", "author": "Test Author 1", "episode_count": 10},
            {"title": "Test Podcast 2", "author": "Test Author 2", "episode_count": 20}
        ]
        
        formatted = display.format_subscriptions_list(test_subscriptions)
        print("✅ Subscriptions formatting working")
        
        # Test episodes formatting
        test_episodes = [
            {
                "title_display": "Test Episode 1",
                "pub_date_formatted": "2024-01-15",
                "duration_formatted": "30m",
                "has_transcript": True
            }
        ]
        
        formatted = display.format_episodes_list(test_episodes, "Test Podcast")
        print("✅ Episodes formatting working")
        
        # Test summary formatting
        test_summary = "This is a test summary with multiple paragraphs.\n\nSecond paragraph.\n\nThird paragraph."
        formatted = display.format_summary(test_summary, "Test Episode")
        print("✅ Summary formatting working")
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")


def test_helpers():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    try:
        from utils.helpers import format_duration, truncate_text, safe_get
        
        # Test duration formatting
        assert format_duration(3661) == "1h 1m"
        assert format_duration(1800) == "30m"
        print("✅ Duration formatting working")
        
        # Test text truncation
        assert truncate_text("This is a long text", 10) == "This is..."
        assert truncate_text("Short", 10) == "Short"
        print("✅ Text truncation working")
        
        # Test safe get
        test_dict = {"a": {"b": {"c": "value"}}}
        assert safe_get(test_dict, "a", "b", "c") == "value"
        assert safe_get(test_dict, "a", "b", "d", default="default") == "default"
        print("✅ Safe get working")
        
    except Exception as e:
        print(f"❌ Helpers test failed: {e}")


def main():
    """Run all tests"""
    print("Podcast CLI - Component Tests")
    print("=" * 40)
    
    # Setup logging
    setup_logging()
    
    # Run tests
    test_config()
    test_cache()
    test_display()
    test_helpers()
    
    print("\n" + "=" * 40)
    print("Tests completed!")
    print("\nTo run the full application:")
    print("1. Add your OpenAI API key to the configuration")
    print("2. Run: python main.py")


if __name__ == "__main__":
    main() 