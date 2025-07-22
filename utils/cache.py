"""
Caching utilities for Podcast CLI
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict
import hashlib


class Cache:
    """Simple file-based cache implementation"""
    
    def __init__(self, cache_dir: str = "~/.cache/podcast-cli"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a given key"""
        # Create a hash of the key to use as filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Get a value from cache if it exists and is not expired"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if cache is expired
            cached_time = cached_data.get('timestamp')
            if cached_time:
                age = datetime.now() - cached_time
                if age > timedelta(hours=max_age_hours):
                    cache_path.unlink()  # Remove expired cache
                    return None
            
            return cached_data.get('data')
            
        except (pickle.PickleError, EOFError, KeyError):
            # Remove corrupted cache file
            if cache_path.exists():
                cache_path.unlink()
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Store a value in cache with current timestamp"""
        cache_path = self._get_cache_path(key)
        
        cached_data = {
            'data': value,
            'timestamp': datetime.now()
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
        except Exception as e:
            # Log error but don't fail the application
            print(f"Warning: Failed to cache data: {e}")
    
    def clear(self) -> None:
        """Clear all cached data"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'files': len(cache_files),
            'size_bytes': total_size,
            'size_mb': total_size / (1024 * 1024)
        } 