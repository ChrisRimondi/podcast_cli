"""
Podcast database interface for reading from macOS Podcast app
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.helpers import expand_path, safe_get


class PodcastDatabase:
    """Interface to the macOS Podcast app database"""
    
    def __init__(self, database_path: str):
        self.database_path = expand_path(database_path)
        self.logger = logging.getLogger(__name__)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a connection to the podcast database"""
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Podcast database not found at {self.database_path}. "
                "Make sure the Podcast app is installed and has been used."
            )
        
        return sqlite3.connect(str(self.database_path))
    
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all podcast subscriptions that have episodes with transcripts"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Query to get podcast subscriptions that have episodes with transcripts
                # Only include podcasts that actually have episodes with transcript snippets in the database
                query = """
                SELECT 
                    ZMTPODCAST.Z_PK as podcast_id,
                    ZMTPODCAST.ZTITLE as title,
                    ZMTPODCAST.ZAUTHOR as author,
                    ZMTPODCAST.ZITEMDESCRIPTION as description,
                    ZMTPODCAST.ZFEEDURL as feed_url,
                    ZMTPODCAST.ZIMAGEURL as artwork_url,
                    COUNT(ZMTEPISODE.Z_PK) as episode_count
                FROM ZMTPODCAST 
                INNER JOIN ZMTEPISODE ON ZMTPODCAST.Z_PK = ZMTEPISODE.ZPODCAST
                WHERE ZMTPODCAST.ZTITLE IS NOT NULL
                AND (ZMTEPISODE.ZENTITLEDTRANSCRIPTSNIPPET IS NOT NULL 
                     OR ZMTEPISODE.ZFREETRANSCRIPTSNIPPET IS NOT NULL)
                GROUP BY ZMTPODCAST.Z_PK, ZMTPODCAST.ZTITLE, ZMTPODCAST.ZAUTHOR, 
                         ZMTPODCAST.ZITEMDESCRIPTION, ZMTPODCAST.ZFEEDURL, ZMTPODCAST.ZIMAGEURL
                HAVING COUNT(ZMTEPISODE.Z_PK) > 0
                ORDER BY ZMTPODCAST.ZTITLE
                """
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                subscriptions = []
                for row in rows:
                    subscription = {
                        'id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'description': row[3],
                        'feed_url': row[4],
                        'artwork_url': row[5],
                        'episode_count': row[6]
                    }
                    subscriptions.append(subscription)
                
                return subscriptions
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading subscriptions: {e}")
            raise
    
    def _convert_timestamp_to_date(self, timestamp: int) -> str:
        """Convert podcast timestamp to correct date string"""
        try:
            import datetime
            # The timestamps need an offset to convert to correct 2025 dates
            # Based on analysis, adding 978,244,620 seconds converts 1994 dates to 2025
            offset = 978244620
            corrected_timestamp = timestamp + offset
            date_obj = datetime.datetime.fromtimestamp(corrected_timestamp)
            return date_obj.strftime('%Y-%m-%d')
        except Exception as e:
            self.logger.error(f"Error converting timestamp {timestamp}: {e}")
            return str(timestamp)  # Fallback to raw timestamp if conversion fails
    
    def get_episodes(self, podcast_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get episodes for a specific podcast (most recent 10 with transcripts by default)"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Query to get episodes for a podcast that have transcript snippets
                # Order by publication date descending to get most recent first
                query = """
                SELECT 
                    ZMTEPISODE.Z_PK as episode_id,
                    ZMTEPISODE.ZTITLE as title,
                    ZMTEPISODE.ZITEMDESCRIPTION as description,
                    ZMTEPISODE.ZPUBDATE as pub_date,
                    ZMTEPISODE.ZDURATION as duration,
                    ZMTEPISODE.ZASSETURL as asset_url,
                    ZMTEPISODE.ZENTITLEDTRANSCRIPTSNIPPET as entitled_transcript,
                    ZMTEPISODE.ZFREETRANSCRIPTSNIPPET as free_transcript,
                    ZMTEPISODE.ZPLAYHEAD as playback_position,
                    ZMTEPISODE.ZPLAYSTATE as playback_state
                FROM ZMTEPISODE 
                WHERE ZMTEPISODE.ZPODCAST = ?
                AND (ZMTEPISODE.ZENTITLEDTRANSCRIPTSNIPPET IS NOT NULL 
                     OR ZMTEPISODE.ZFREETRANSCRIPTSNIPPET IS NOT NULL)
                ORDER BY ZMTEPISODE.ZPUBDATE DESC
                LIMIT ?
                """
                
                cursor.execute(query, (podcast_id, limit))
                rows = cursor.fetchall()
                
                episodes = []
                for row in rows:
                    episode = {
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'pub_date': self._convert_timestamp_to_date(row[3]) if row[3] else None,
                        'duration': row[4],
                        'asset_url': row[5],
                        'entitled_transcript': row[6],
                        'free_transcript': row[7],
                        'playback_position': row[8],
                        'playback_state': row[9]
                    }
                    episodes.append(episode)
                
                return episodes
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading episodes: {e}")
            raise
    
    def get_episode_transcript(self, episode_id: int) -> Optional[str]:
        """Get transcript for a specific episode"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # First try to get the transcript identifier (file path)
                query = """
                SELECT ZTRANSCRIPTIDENTIFIER, ZENTITLEDTRANSCRIPTSNIPPET, ZFREETRANSCRIPTSNIPPET
                FROM ZMTEPISODE 
                WHERE Z_PK = ?
                """
                
                cursor.execute(query, (episode_id,))
                row = cursor.fetchone()
                
                if row:
                    transcript_identifier = row[0]
                    entitled_snippet = row[1]
                    free_snippet = row[2]
                    
                    # Try to read the full transcript file first
                    if transcript_identifier:
                        full_transcript = self._read_transcript_file(transcript_identifier)
                        if full_transcript and len(full_transcript.strip()) > 50:
                            return full_transcript
                    
                    # Fall back to snippets if file reading fails
                    transcript_json = entitled_snippet or free_snippet
                    if transcript_json:
                        snippet_transcript = self._extract_transcript_text(transcript_json)
                        if snippet_transcript and len(snippet_transcript.strip()) > 50:
                            return snippet_transcript
                return None
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error reading transcript: {e}")
            return None
    
    def _read_transcript_file(self, transcript_identifier: str) -> Optional[str]:
        """Read and parse transcript from TTML file"""
        try:
            import re
            from pathlib import Path
            
            # Construct the path to the transcript file
            base_path = Path("~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML")
            base_path = base_path.expanduser()
            
            # The identifier format is like: "PodcastContent221/v4/06/d0/0d/06d00dc6-f417-0085-1989-b64671af104f/transcript_1000552192762.ttml"
            # We need to find the actual file which might have additional suffixes
            identifier_parts = transcript_identifier.split('/')
            if len(identifier_parts) < 2:
                return None
            
            # Try to find the file with various possible suffixes
            possible_paths = [
                base_path / transcript_identifier,
                base_path / f"{transcript_identifier}-{identifier_parts[-1]}",
                base_path / f"{transcript_identifier}-{identifier_parts[-1].replace('.ttml', '')}.ttml"
            ]
            
            transcript_file = None
            for path in possible_paths:
                if path.exists():
                    transcript_file = path
                    break
            
            if not transcript_file:
                # Try to find the file by searching for the filename
                filename = identifier_parts[-1]
                for file_path in base_path.rglob(f"*{filename}*"):
                    if file_path.is_file():
                        transcript_file = file_path
                        break
            
            if not transcript_file:
                return None
            
            # Read the TTML file
            with open(transcript_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text from TTML format
            return self._extract_text_from_ttml(content)
            
        except Exception as e:
            self.logger.error(f"Error reading transcript file: {e}")
            return None
    
    def _extract_text_from_ttml(self, ttml_content: str) -> str:
        """Extract plain text from TTML content"""
        try:
            import re
            
            # Remove XML tags and extract text content
            # This is a simple approach - in production you might want to use an XML parser
            
            # Remove XML declarations and metadata
            text = re.sub(r'<\?xml[^>]*\?>', '', ttml_content)
            text = re.sub(r'<!DOCTYPE[^>]*>', '', text)
            
            # Remove all XML tags but keep their content
            text = re.sub(r'<[^>]*>', ' ', text)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error parsing TTML: {e}")
            return ttml_content
    
    def _extract_transcript_text(self, transcript_json: str) -> str:
        """Extract plain text from JSON transcript format"""
        try:
            import json
            transcript_data = json.loads(transcript_json)
            
            if isinstance(transcript_data, list):
                # Extract content from each transcript segment
                text_parts = []
                for segment in transcript_data:
                    if isinstance(segment, dict) and 'content' in segment:
                        text_parts.append(segment['content'])
                return ' '.join(text_parts)
            else:
                return str(transcript_data)
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.error(f"Error parsing transcript JSON: {e}")
            return transcript_json  # Return raw JSON if parsing fails
    
    def search_podcasts(self, search_term: str) -> List[Dict[str, Any]]:
        """Search podcasts by title or author"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    ZMTPODCAST.Z_PK as podcast_id,
                    ZMTPODCAST.ZTITLE as title,
                    ZMTPODCAST.ZAUTHOR as author,
                    ZMTPODCAST.ZITEMDESCRIPTION as description
                FROM ZMTPODCAST 
                WHERE ZMTPODCAST.ZTITLE LIKE ? OR ZMTPODCAST.ZAUTHOR LIKE ?
                ORDER BY ZMTPODCAST.ZTITLE
                """
                
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern))
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = {
                        'id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'description': row[3]
                    }
                    results.append(result)
                
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error searching podcasts: {e}")
            raise 