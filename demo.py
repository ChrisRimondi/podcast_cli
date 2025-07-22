#!/usr/bin/env python3
"""
Demo script for Podcast CLI - Shows the interface with mock data
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.display import DisplayFormatter
import time


def demo_interface():
    """Demonstrate the podcast CLI interface with mock data"""
    
    display = DisplayFormatter()
    
    print("🎧 Podcast CLI Demo")
    print("=" * 50)
    print("This demo shows how the application interface works.")
    print("In the real app, this would read from your Podcast app database.\n")
    
    # Mock subscriptions
    mock_subscriptions = [
        {
            "title": "The Daily",
            "author": "The New York Times",
            "episode_count": 1500
        },
        {
            "title": "This American Life",
            "author": "This American Life",
            "episode_count": 800
        },
        {
            "title": "Radiolab",
            "author": "WNYC Studios",
            "episode_count": 600
        },
        {
            "title": "Serial",
            "author": "Serial Productions",
            "episode_count": 50
        },
        {
            "title": "Reply All",
            "author": "Gimlet",
            "episode_count": 200
        }
    ]
    
    print(display.format_subscriptions_list(mock_subscriptions))
    
    # Simulate user selection
    print("Demo: User selects 'The Daily' (option 1)")
    time.sleep(1)
    
    # Mock episodes
    mock_episodes = [
        {
            "title_display": "Breaking News: Major Development in Tech Industry",
            "pub_date_formatted": "2024-01-15",
            "duration_formatted": "25m",
            "has_transcript": True
        },
        {
            "title_display": "Analysis: Economic Trends and Market Predictions",
            "pub_date_formatted": "2024-01-14",
            "duration_formatted": "22m",
            "has_transcript": True
        },
        {
            "title_display": "Interview: Expert Insights on Climate Change",
            "pub_date_formatted": "2024-01-13",
            "duration_formatted": "28m",
            "has_transcript": False
        },
        {
            "title_display": "Weekly Roundup: Top Stories of the Week",
            "pub_date_formatted": "2024-01-12",
            "duration_formatted": "30m",
            "has_transcript": True
        },
        {
            "title_display": "Deep Dive: The Future of Artificial Intelligence",
            "pub_date_formatted": "2024-01-11",
            "duration_formatted": "35m",
            "has_transcript": True
        }
    ]
    
    print(display.format_episodes_list(mock_episodes, "The Daily"))
    
    # Simulate user selection
    print("Demo: User selects first episode (option 1)")
    time.sleep(1)
    
    # Show episode actions
    options = ["Generate Summary", "Show Details", "Back to Episodes", "Back to Podcasts"]
    print(display.format_menu_prompt(options, "Episode Actions"))
    
    print("Demo: User selects 'Generate Summary' (option 1)")
    time.sleep(1)
    
    # Mock summary
    mock_summary = """This episode of The Daily explores the recent major developments in the technology industry, focusing on the latest innovations and their potential impact on society. The hosts discuss how these changes are reshaping the way we work, communicate, and interact with technology in our daily lives.

The episode features interviews with industry experts who provide insights into the current state of the tech sector and predictions for future trends. Key topics include artificial intelligence advancements, the rise of new social media platforms, and the ongoing debate about technology regulation and privacy concerns.

Throughout the discussion, the experts emphasize the importance of understanding both the benefits and potential risks associated with rapid technological change. They highlight how these developments are creating new opportunities while also raising important questions about ethics, security, and the digital divide.

The conversation also touches on the role of government and regulatory bodies in overseeing technological innovation, with different perspectives on how to balance innovation with consumer protection and public safety. The experts agree that thoughtful regulation is necessary but must be carefully crafted to avoid stifling progress.

In conclusion, the episode underscores the transformative nature of current technological developments and the need for informed public discourse about their implications. The hosts encourage listeners to stay engaged with these issues and consider how they might personally be affected by these changes in the coming years."""
    
    print(display.format_summary(mock_summary, "Breaking News: Major Development in Tech Industry"))
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nTo use the real application:")
    print("1. Add your OpenAI API key to ~/.config/podcast-cli/config.yaml")
    print("2. Make sure you have podcasts subscribed in the macOS Podcast app")
    print("3. Run: ./run.sh or python main.py")


if __name__ == "__main__":
    demo_interface() 