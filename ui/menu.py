"""
Main menu system for Podcast CLI
"""

import logging
from typing import List, Dict, Any, Optional
from data.podcast_db import PodcastDatabase
from data.episode_manager import EpisodeManager
from ai.summarizer import TranscriptSummarizer
from ui.display import DisplayFormatter
from utils.cache import Cache
from utils.helpers import safe_get


class PodcastMenu:
    """Main menu system for the podcast CLI"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        database_path = safe_get(config, 'podcast_app', 'database_path')
        self.podcast_db = PodcastDatabase(database_path)
        
        cache_dir = safe_get(config, 'cache', 'directory', default="~/.cache/podcast-cli")
        self.cache = Cache(cache_dir)
        
        self.episode_manager = EpisodeManager(self.podcast_db, self.cache)
        self.summarizer = TranscriptSummarizer(config, self.cache)
        self.display = DisplayFormatter()
        
        # State
        self.current_podcast = None
        self.current_episodes = []
    
    def run(self):
        """Main application loop"""
        print("Welcome to Podcast CLI!")
        print("Loading your subscriptions...\n")
        
        try:
            while True:
                self.show_main_menu()
                # After returning from main menu, ask if user wants to continue
                print("\nType 'exit' to quit or press Enter to continue browsing podcasts.")
                user_input = input().strip().lower()
                if user_input in ['exit', 'quit', 'q']:
                    break
        except KeyboardInterrupt:
            print("\nGoodbye!")
    
    def show_main_menu(self):
        """Display the main menu"""
        try:
            subscriptions = self.episode_manager.get_subscriptions()
            
            if not subscriptions:
                print("No podcast subscriptions found.")
                print("Make sure you have subscribed to podcasts in the macOS Podcast app.")
                print("\nType 'exit' to quit.")
                input("Press Enter to continue...")
                return
            
            print(self.display.format_subscriptions_list(subscriptions))
            print("\nType 'exit' to quit the application, 'help' for help, or enter a number to select a podcast.")
            
            # Get user selection
            choice = self._get_user_choice(len(subscriptions))
            if choice is None:
                return
            
            selected_podcast = subscriptions[choice - 1]
            self.current_podcast = selected_podcast
            
            self.show_episodes_menu(selected_podcast)
            
        except Exception as e:
            print(self.display.format_error(f"Error loading subscriptions: {e}"))
            self.logger.error(f"Error in main menu: {e}")
    
    def show_episodes_menu(self, podcast: Dict[str, Any]):
        """Display episodes for a selected podcast"""
        try:
            print(f"\n{self.display.format_loading('Loading episodes')}")
            
            episodes = self.episode_manager.get_episodes(podcast['id'], limit=10)
            self.current_episodes = episodes
            
            if not episodes:
                print("No episodes found for this podcast.")
                print("\nType 'exit' to quit or 'back' to return to podcasts.")
                user_input = input().strip().lower()
                if user_input in ['exit', 'quit', 'q']:
                    return
                elif user_input in ['back', 'b']:
                    return
                return
            
            print(self.display.format_episodes_list(episodes, podcast['title']))
            print("\nType 'exit' to quit, 'back' to return to podcasts, or enter a number to select an episode.")
            
            # Get user selection
            choice = self._get_user_choice(len(episodes))
            if choice is None:
                return
            
            selected_episode = episodes[choice - 1]
            self.show_episode_actions(selected_episode, podcast['title'])
            
        except Exception as e:
            print(self.display.format_error(f"Error loading episodes: {e}"))
            self.logger.error(f"Error in episodes menu: {e}")
    
    def show_episode_actions(self, episode: Dict[str, Any], podcast_title: str):
        """Show actions available for a selected episode"""
        options = ["Generate Summary", "Show Details", "Save Summary as PDF", "Save Summary as RSS", "Back to Episodes", "Back to Podcasts", "Exit"]
        
        while True:
            print(f"\n{self.display.format_menu_prompt(options, 'Episode Actions')}")
            
            choice = self._get_user_choice(len(options))
            if choice is None:
                return
            
            if choice == 1:  # Generate Summary
                self.generate_summary(episode, podcast_title)
            elif choice == 2:  # Show Details
                print(self.display.format_episode_details(episode))
                input("\nPress Enter to continue...")
            elif choice == 3:  # Save Summary as PDF
                self.save_summary_as_pdf(episode, podcast_title)
            elif choice == 4:  # Save Summary as RSS
                self.save_summary_as_rss(episode, podcast_title)
            elif choice == 5:  # Back to Episodes
                if self.current_podcast:
                    self.show_episodes_menu(self.current_podcast)
                return
            elif choice == 6:  # Back to Podcasts
                return
            elif choice == 7:  # Exit
                return
    
    def generate_summary(self, episode: Dict[str, Any], podcast_title: str):
        """Generate and display a summary for an episode"""
        try:
            if not episode.get('has_transcript'):
                print(self.display.format_error("No transcript available for this episode."))
                return
            
            print(f"\n{self.display.format_loading('Generating summary')}")
            
            # Get transcript
            transcript = self.episode_manager.get_episode_transcript(episode['id'])
            if not transcript:
                print(self.display.format_error("Failed to retrieve transcript."))
                return
            
            # Generate summary
            episode_title_full = episode.get('title', 'Unknown Episode')
            summary = self.summarizer.summarize_transcript(transcript, episode_title_full)
            
            if summary:
                print(self.display.format_summary(summary, episode_title_full))
            else:
                print(self.display.format_error("Failed to generate summary."))
                
        except Exception as e:
            print(self.display.format_error(f"Error generating summary: {e}"))
            self.logger.error(f"Error in summary generation: {e}")
    
    def save_summary_as_pdf(self, episode: Dict[str, Any], podcast_title: str):
        """Save a summary as a PDF file"""
        try:
            # Check if save is enabled in config
            if not self.config.get('save', {}).get('enabled', True):
                print(self.display.format_error("Summary saving is disabled in configuration."))
                return
            
            # Get save directory from config
            save_directory = self.config.get('save', {}).get('directory', '~/Documents/podcast-summaries')
            
            if not episode.get('has_transcript'):
                print(self.display.format_error("No transcript available for this episode."))
                return
            
            print(f"\n{self.display.format_loading('Generating and saving summary')}")
            
            # Get transcript
            transcript = self.episode_manager.get_episode_transcript(episode['id'])
            if not transcript:
                print(self.display.format_error("Failed to retrieve transcript."))
                return
            
            # Generate summary
            episode_title_full = episode.get('title', 'Unknown Episode')
            summary = self.summarizer.summarize_transcript(transcript, episode_title_full)
            
            if not summary:
                print(self.display.format_error("Failed to generate summary."))
                return
            
            # Save as PDF
            from utils.helpers import save_summary_as_pdf
            
            episode_date = episode.get('pub_date_formatted', 'Unknown')
            duration = episode.get('duration_formatted', 'Unknown')
            
            saved_path = save_summary_as_pdf(
                summary=summary,
                episode_title=episode_title_full,
                podcast_title=podcast_title,
                episode_date=episode_date,
                duration=duration,
                save_directory=save_directory
            )
            
            if saved_path:
                print(self.display.format_success(f"Summary saved to: {saved_path}"))
                print(f"\n{self.display.format_summary(summary, episode_title_full)}")
            else:
                print(self.display.format_error("Failed to save summary file."))
                
        except Exception as e:
            print(self.display.format_error(f"Error saving summary: {e}"))
            self.logger.error(f"Error in summary saving: {e}")
    
    def save_summary_as_rss(self, episode: Dict[str, Any], podcast_title: str):
        """Save a summary as an RSS feed item"""
        try:
            # Check if RSS saving is enabled in config
            if not self.config.get('rss', {}).get('enabled', False):
                print(self.display.format_error("RSS saving is disabled in configuration."))
                return

            # Get RSS directory from config
            rss_directory = self.config.get('rss', {}).get('directory', '~/Documents/podcast-summaries')

            if not episode.get('has_transcript'):
                print(self.display.format_error("No transcript available for this episode."))
                return

            print(f"\n{self.display.format_loading('Generating and saving RSS feed item')}")

            # Get transcript
            transcript = self.episode_manager.get_episode_transcript(episode['id'])
            if not transcript:
                print(self.display.format_error("Failed to retrieve transcript."))
                return

            # Generate summary
            episode_title_full = episode.get('title', 'Unknown Episode')
            summary = self.summarizer.summarize_transcript(transcript, episode_title_full)

            if not summary:
                print(self.display.format_error("Failed to generate summary."))
                return

            # Save as RSS feed item
            from utils.helpers import save_summary_as_rss

            episode_date = episode.get('pub_date_formatted', 'Unknown')
            duration = episode.get('duration_formatted', 'Unknown')

            saved_path = save_summary_as_rss(
                summary=summary,
                episode_title=episode_title_full,
                podcast_title=podcast_title,
                episode_date=episode_date,
                duration=duration,
                save_directory=rss_directory
            )

            if saved_path:
                print(self.display.format_success(f"RSS feed item saved to: {saved_path}"))
                print(f"\n{self.display.format_summary(summary, episode_title_full)}")
            else:
                print(self.display.format_error("Failed to save RSS feed item."))

        except Exception as e:
            print(self.display.format_error(f"Error saving RSS feed item: {e}"))
            self.logger.error(f"Error in RSS saving: {e}")
    
    def _get_user_choice(self, max_options: int) -> Optional[int]:
        """Get user input for menu selection"""
        while True:
            try:
                user_input = input().strip()
                
                # Handle exit commands
                if user_input.lower() in ['q', 'quit', 'exit']:
                    return None
                
                # Handle back commands (only valid in certain contexts)
                if user_input.lower() in ['back', 'b']:
                    return None
                
                # Handle help command
                if user_input.lower() in ['help', 'h']:
                    self.show_help()
                    print(f"\nEnter a number between 1 and {max_options} to continue:")
                    continue
                
                # Handle numeric input
                choice = int(user_input)
                if 1 <= choice <= max_options:
                    return choice
                else:
                    print(f"Please enter a number between 1 and {max_options}")
                    
            except ValueError:
                print("Please enter a valid number, 'exit' to quit, 'back' to go back, or 'help' for help")
            except KeyboardInterrupt:
                return None
    
    def show_help(self):
        """Display help information"""
        help_text = """
Podcast CLI Help
================

Navigation:
- Enter numbers to select options
- Type 'q', 'quit', or 'exit' to exit
- Use Ctrl+C to exit at any time

Features:
- Browse your podcast subscriptions
- View latest episodes from each podcast
- Generate AI-powered summaries from transcripts
- View episode details and metadata

Note: Transcripts must be available in the Podcast app for summarization to work.
        """
        print(help_text)
    
    def show_cache_info(self):
        """Display cache information"""
        try:
            stats = self.episode_manager.get_cache_stats()
            print(self.display.format_cache_stats(stats))
        except Exception as e:
            print(self.display.format_error(f"Error getting cache stats: {e}"))
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            self.episode_manager.clear_cache()
            print(self.display.format_success("Cache cleared successfully"))
        except Exception as e:
            print(self.display.format_error(f"Error clearing cache: {e}")) 