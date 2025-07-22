"""
Utility functions for Podcast CLI
"""

import logging
from pathlib import Path
from typing import Optional
import re
from typing import Optional
from pathlib import Path
from datetime import datetime


def setup_logging(level: int = logging.INFO) -> None:
    """Setup logging configuration"""
    # Create cache directory if it doesn't exist
    cache_dir = Path.home() / '.cache' / 'podcast-cli'
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(cache_dir / 'app.log')
        ]
    )


def expand_path(path_str: str) -> Path:
    """Expand a path string with user home directory"""
    return Path(path_str).expanduser()


def safe_get(dictionary: dict, *keys, default=None):
    """Safely get nested dictionary values"""
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def format_duration(seconds: Optional[float]) -> str:
    """Format duration in seconds to human-readable format"""
    if not seconds:
        return "Unknown"
    
    try:
        seconds = float(seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if hours > 0:
            return f"{hours}.{minutes:02d}h"
        else:
            return f"{minutes}.{int(seconds % 60):02d}m"
    except (ValueError, TypeError):
        return "Unknown"


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def save_summary_as_pdf(summary: str, episode_title: str, podcast_title: str, 
                       episode_date: str, duration: str, save_directory: str) -> Optional[str]:
    """Save a summary as a PDF file"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Expand the save directory path
        save_dir = Path(save_directory).expanduser()
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a sanitized filename
        sanitized_title = sanitize_filename(episode_title)
        sanitized_podcast = sanitize_filename(podcast_title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{timestamp}_{sanitized_podcast}_{sanitized_title}.pdf"
        filepath = save_dir / filename
        
        # Create the PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=1  # Center alignment
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        normal_style = styles['Normal']
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        )
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,  # Center alignment
            textColor=colors.grey
        )
        
        # Add title
        story.append(Paragraph(episode_title, title_style))
        story.append(Spacer(1, 20))
        
        # Add metadata
        story.append(Paragraph(f"<b>Podcast:</b> {podcast_title}", metadata_style))
        story.append(Paragraph(f"<b>Date:</b> {episode_date}", metadata_style))
        story.append(Paragraph(f"<b>Duration:</b> {duration}", metadata_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", metadata_style))
        
        story.append(Spacer(1, 30))
        
        # Add summary heading
        story.append(Paragraph("Summary", heading_style))
        story.append(Spacer(1, 12))
        
        # Split summary into paragraphs and add them
        paragraphs = summary.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), normal_style))
                story.append(Spacer(1, 12))
        
        # Add footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("This summary was generated by Podcast CLI using OpenAI's GPT model.", footer_style))
        
        # Build the PDF
        doc.build(story)
        
        return str(filepath)
        
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return None 


def save_summary_as_rss(summary: str, episode_title: str, podcast_title: str, 
                       episode_date: str, duration: str, save_directory: str) -> Optional[str]:
    """Save a summary as an RSS feed item"""
    try:
        from utils.rss_generator import RSSGenerator
        
        # Initialize RSS generator
        rss_gen = RSSGenerator()
        
        # Add the summary to the RSS feed
        saved_path = rss_gen.add_summary(
            episode_title=episode_title,
            podcast_title=podcast_title,
            episode_date=episode_date,
            duration=duration,
            summary=summary
        )
        
        if saved_path:
            print(f"RSS feed updated: {rss_gen.get_feed_url()}")
            print(f"Website updated: {rss_gen.get_site_url()}")
            return saved_path
        else:
            return None
        
    except Exception as e:
        print(f"Error saving RSS feed item: {e}")
        return None 