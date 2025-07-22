"""
Configuration management for Podcast CLI
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def get_config_path() -> Path:
    """Get the configuration file path"""
    config_dir = Path.home() / ".config" / "podcast-cli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.yaml"


def create_default_config(config_path: Path) -> None:
    """Create a default configuration file"""
    default_config = {
        "openai": {
            "api_key": "",
            "model": "gpt-4",
            "max_tokens": 1000
        },
        "cache": {
            "enabled": True,
            "directory": "~/.cache/podcast-cli",
            "max_age_hours": 24
        },
        "podcast_app": {
            "database_path": "~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Documents/MTLibrary.sqlite"
        },
        "save": {
            "directory": "~/Documents/podcast-summaries",
            "enabled": True
        },
        "rss": {
            "enabled": True,
            "directory": "docs",
            "site_url": "https://yourusername.github.io/podcast_cli/"
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)


def load_config() -> Dict[str, Any]:
    """Load configuration from file and environment variables"""
    config_path = get_config_path()
    
    # Create default config if it doesn't exist
    if not config_path.exists():
        create_default_config(config_path)
        print(f"Created default configuration at {config_path}")
        print("Please add your OpenAI API key to the configuration file.")
        return {}
    
    # Load config from file
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Override with environment variables
    if os.getenv('OPENAI_API_KEY'):
        if 'openai' not in config:
            config['openai'] = {}
        config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
    
    # Validate required configuration
    if not config.get('openai', {}).get('api_key'):
        raise ValueError(
            "OpenAI API key not found. Please add it to the configuration file "
            f"({config_path}) or set the OPENAI_API_KEY environment variable."
        )
    
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False) 