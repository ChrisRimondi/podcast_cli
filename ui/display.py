"""
Display utilities for Podcast CLI
"""

from typing import List, Dict, Any
from utils.helpers import truncate_text


class DisplayFormatter:
    """Handles formatting and display of podcast data"""
    
    @staticmethod
    def format_subscriptions_list(subscriptions: List[Dict[str, Any]]) -> str:
        """Format subscriptions for display"""
        if not subscriptions:
            return "No podcast subscriptions found."
        
        output = "Your Podcast Subscriptions:\n"
        output += "=" * 50 + "\n\n"
        
        for i, subscription in enumerate(subscriptions, 1):
            title = subscription.get('title', 'Unknown')
            author = subscription.get('author', 'Unknown')
            
            output += f"{i}. {title}\n"
            output += f"   By: {author}\n"
            output += "\n"
        
        return output
    
    @staticmethod
    def format_episodes_list(episodes: List[Dict[str, Any]], podcast_title: str = "") -> str:
        """Format episodes for display"""
        if not episodes:
            return "No episodes found."
        
        output = f"Latest Episodes from \"{podcast_title}\":\n"
        output += "=" * 60 + "\n\n"
        
        for i, episode in enumerate(episodes, 1):
            title = episode.get('title_display', 'Untitled')
            pub_date = episode.get('pub_date_formatted', 'Unknown')
            duration = episode.get('duration_formatted', 'Unknown')
            has_transcript = episode.get('has_transcript', False)
            
            transcript_indicator = "📝" if has_transcript else "❌"
            
            output += f"{i}. {title}\n"
            output += f"   Date: {pub_date} | Duration: {duration} | Transcript: {transcript_indicator}\n"
            output += "\n"
        
        return output
    
    @staticmethod
    def format_summary(summary: str, episode_title: str = "") -> str:
        """Format the AI-generated summary"""
        if not summary:
            return "No summary available."
        
        output = f"Summary for \"{episode_title}\"\n"
        output += "=" * 60 + "\n\n"
        output += summary
        output += "\n\n" + "=" * 60 + "\n"
        
        return output
    
    @staticmethod
    def format_error(message: str) -> str:
        """Format error messages"""
        return f"❌ Error: {message}"
    
    @staticmethod
    def format_success(message: str) -> str:
        """Format success messages"""
        return f"✅ {message}"
    
    @staticmethod
    def format_loading(message: str) -> str:
        """Format loading messages"""
        return f"⏳ {message}..."
    
    @staticmethod
    def format_menu_prompt(options: List[str], title: str = "Select an option") -> str:
        """Format a menu prompt"""
        output = f"{title}:\n"
        output += "-" * 30 + "\n"
        
        for i, option in enumerate(options, 1):
            output += f"{i}. {option}\n"
        
        output += f"\nEnter your choice (1-{len(options)}): "
        return output
    
    @staticmethod
    def format_episode_details(episode: Dict[str, Any]) -> str:
        """Format detailed episode information"""
        output = "Episode Details:\n"
        output += "=" * 40 + "\n"
        
        output += f"Title: {episode.get('title', 'Unknown')}\n"
        output += f"Date: {episode.get('pub_date_formatted', 'Unknown')}\n"
        output += f"Duration: {episode.get('duration_formatted', 'Unknown')}\n"
        output += f"Transcript Available: {'Yes' if episode.get('has_transcript') else 'No'}\n"
        
        if episode.get('description'):
            output += f"\nDescription:\n{episode.get('description')}\n"
        
        return output
    
    @staticmethod
    def format_cache_stats(stats: Dict[str, Any]) -> str:
        """Format cache statistics"""
        output = "Cache Statistics:\n"
        output += "=" * 20 + "\n"
        output += f"Files: {stats.get('files', 0)}\n"
        output += f"Size: {stats.get('size_mb', 0):.2f} MB\n"
        return output 