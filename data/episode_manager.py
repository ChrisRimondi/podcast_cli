"""
Episode management for Podcast CLI
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.cache import Cache
from utils.helpers import format_duration, truncate_text
from data.podcast_db import PodcastDatabase


class EpisodeManager:
    """Manages episode data and operations"""
    
    def __init__(self, podcast_db: PodcastDatabase, cache: Cache):
        self.podcast_db = podcast_db
        self.cache = cache
        self.logger = logging.getLogger(__name__)
    
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all podcast subscriptions with caching"""
        cache_key = "subscriptions"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            subscriptions = self.podcast_db.get_subscriptions()
            self.cache.set(cache_key, subscriptions)
            return subscriptions
        except Exception as e:
            self.logger.error(f"Error getting subscriptions: {e}")
            raise
    
    def get_episodes(self, podcast_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get episodes for a podcast with caching (limited to 10 most recent by default)"""
        cache_key = f"episodes_{podcast_id}_{limit}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            # Always limit to 10 episodes for CLI display
            episodes = self.podcast_db.get_episodes(podcast_id, limit=10)
            
            # Process and format episode data
            formatted_episodes = []
            for episode in episodes:
                formatted_episode = self._format_episode(episode)
                formatted_episodes.append(formatted_episode)
            
            self.cache.set(cache_key, formatted_episodes)
            return formatted_episodes
        except Exception as e:
            self.logger.error(f"Error getting episodes: {e}")
            raise
    
    def get_episode_transcript(self, episode_id: int) -> Optional[str]:
        """Get transcript for an episode with caching"""
        cache_key = f"transcript_{episode_id}"
        cached_transcript = self.cache.get(cache_key)
        
        if cached_transcript:
            return cached_transcript
        
        try:
            transcript = self.podcast_db.get_episode_transcript(episode_id)
            if transcript:
                self.cache.set(cache_key, transcript)
            return transcript
        except Exception as e:
            self.logger.error(f"Error getting transcript: {e}")
            return None
    
    def _format_episode(self, episode: Dict[str, Any]) -> Dict[str, Any]:
        """Format episode data for display"""
        formatted = episode.copy()
        
        # Format duration
        if episode.get('duration'):
            formatted['duration_formatted'] = format_duration(episode['duration'])
        else:
            formatted['duration_formatted'] = "Unknown"
        
        # Format publication date
        if episode.get('pub_date'):
            try:
                # The pub_date is now already a formatted string from the database
                # Just use it directly instead of trying to convert from timestamp
                formatted['pub_date_formatted'] = episode['pub_date']
            except (ValueError, TypeError):
                formatted['pub_date_formatted'] = "Unknown"
        else:
            formatted['pub_date_formatted'] = "Unknown"
        
        # Truncate title and description for display
        if episode.get('title'):
            formatted['title_display'] = truncate_text(episode['title'], 60)
        else:
            formatted['title_display'] = "Untitled"
        
        if episode.get('description'):
            formatted['description_display'] = truncate_text(episode['description'], 100)
        else:
            formatted['description_display'] = "No description available"
        
        # Check if transcript is available (using new transcript fields)
        has_transcript = bool(episode.get('entitled_transcript') or episode.get('free_transcript'))
        formatted['has_transcript'] = has_transcript
        
        return formatted
    
    def search_podcasts(self, search_term: str) -> List[Dict[str, Any]]:
        """Search podcasts by title or author"""
        try:
            results = self.podcast_db.search_podcasts(search_term)
            
            # Format search results
            formatted_results = []
            for result in results:
                formatted_result = result.copy()
                if result.get('title'):
                    formatted_result['title_display'] = truncate_text(result['title'], 50)
                if result.get('author'):
                    formatted_result['author_display'] = truncate_text(result['author'], 30)
                formatted_results.append(formatted_result)
            
            return formatted_results
        except Exception as e:
            self.logger.error(f"Error searching podcasts: {e}")
            raise
    
    def get_episode_by_id(self, episode_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific episode by ID"""
        # This would require a new method in PodcastDatabase
        # For now, we'll implement a simple search through cached episodes
        # In a full implementation, we'd add a get_episode_by_id method to PodcastDatabase
        
        # This is a placeholder - in practice, we'd want to implement this properly
        self.logger.warning("get_episode_by_id not fully implemented")
        return None
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats() 