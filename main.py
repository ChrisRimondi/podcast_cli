#!/usr/bin/env python3
"""
Podcast CLI - A simple CLI application for podcast management and summarization
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.menu import PodcastMenu
from config.settings import load_config
from utils.helpers import setup_logging


def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        
        # Load configuration
        config = load_config()
        
        # Initialize and run the main menu
        menu = PodcastMenu(config)
        menu.run()
        
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 