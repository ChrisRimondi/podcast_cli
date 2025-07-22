"""
AI-powered transcript summarization using OpenAI
"""

import logging
from typing import Optional, Dict, Any
from utils.cache import Cache
from utils.helpers import safe_get


class TranscriptSummarizer:
    """Handles transcript summarization using OpenAI API"""
    
    def __init__(self, config: Dict[str, Any], cache: Cache):
        self.config = config
        self.cache = cache
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=safe_get(config, 'openai', 'api_key'),
                max_retries=3
            )
        except ImportError:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {e}")
    
    def summarize_transcript(self, transcript: str, episode_title: str = "") -> Optional[str]:
        """Generate a 5-paragraph summary from transcript"""
        if not transcript or len(transcript.strip()) < 50:
            self.logger.warning("Transcript too short or empty for summarization")
            return None
        
        # Create cache key based on transcript content
        import hashlib
        transcript_hash = hashlib.md5(transcript.encode()).hexdigest()
        cache_key = f"summary_{transcript_hash}"
        
        # Check cache first
        cached_summary = self.cache.get(cache_key)
        if cached_summary:
            self.logger.info("Using cached summary")
            return cached_summary
        
        try:
            # Prepare the prompt for 5-paragraph summary
            prompt = self._create_summary_prompt(transcript, episode_title)
            
            # Get model configuration
            model = safe_get(self.config, 'openai', 'model', default='gpt-4')
            max_tokens = safe_get(self.config, 'openai', 'max_tokens', default=1000)
            
            # Generate summary
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional podcast summarizer. Create clear, engaging 5-paragraph summaries that capture the key points and insights from podcast episodes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Cache the summary
            self.cache.set(cache_key, summary)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None
    
    def _create_summary_prompt(self, transcript: str, episode_title: str) -> str:
        """Create the prompt for summary generation"""
        title_context = f"Episode: {episode_title}\n\n" if episode_title else ""
        
        prompt = f"""
{title_context}Please create a comprehensive 5-paragraph summary of the following podcast transcript. 

The summary should:
1. Start with an engaging introduction that captures the main topic
2. Provide key insights and main points discussed
3. Include important quotes or statements from speakers
4. Cover the conclusions or takeaways
5. End with a thoughtful reflection on the episode's significance

Transcript:
{transcript[:8000]}  # Limit transcript length to avoid token limits

Please format the summary as 5 distinct paragraphs with clear transitions between them.
"""
        return prompt
    
    def test_connection(self) -> bool:
        """Test the OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            self.logger.error(f"OpenAI API test failed: {e}")
            return False
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get API usage information (if available)"""
        try:
            # This would require additional API calls to get usage data
            # For now, return basic info
            return {
                "model": safe_get(self.config, 'openai', 'model', default='gpt-4'),
                "max_tokens": safe_get(self.config, 'openai', 'max_tokens', default=1000)
            }
        except Exception as e:
            self.logger.error(f"Error getting usage info: {e}")
            return {} 