"""
RSS Generator for Podcast Summaries
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom


class RSSGenerator:
    """Generate RSS feeds and HTML pages for podcast summaries"""
    
    def __init__(self, docs_directory: str = "docs"):
        self.docs_dir = Path(docs_directory)
        self.summaries_dir = self.docs_dir / "summaries"
        self.assets_dir = self.docs_dir / "assets"
        
        # Ensure directories exist
        self.docs_dir.mkdir(exist_ok=True)
        self.summaries_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
        # RSS feed configuration
        self.feed_title = "Podcast Summaries"
        self.feed_description = "AI-generated summaries of podcast episodes"
        self.feed_link = "https://yourusername.github.io/podcast_cli/"  # Update this
        self.feed_language = "en"
        
        # Track all summaries for RSS feed
        self.summaries: List[Dict] = []
        self._load_existing_summaries()
    
    def _load_existing_summaries(self):
        """Load existing summaries from the summaries directory"""
        if not self.summaries_dir.exists():
            return
            
        for html_file in self.summaries_dir.glob("*.html"):
            # Extract summary data from filename
            filename = html_file.stem
            parts = filename.split("_", 2)
            if len(parts) >= 3:
                date_str, podcast_name, episode_title = parts[0], parts[1], parts[2]
                try:
                    # Parse the date
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                    
                    # Read the HTML file to get the summary content
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract summary text (simplified - could be more robust)
                    summary_match = re.search(r'<div class="summary-content">(.*?)</div>', content, re.DOTALL)
                    summary_text = summary_match.group(1) if summary_match else ""
                    
                    self.summaries.append({
                        'title': episode_title.replace('-', ' ').title(),
                        'podcast': podcast_name.replace('-', ' ').title(),
                        'date': date_obj,
                        'summary': summary_text,
                        'filename': filename,
                        'url': f"{self.feed_link}summaries/{filename}.html"
                    })
                except Exception as e:
                    print(f"Error loading summary {filename}: {e}")
    
    def _sanitize_filename(self, text: str) -> str:
        """Create a safe filename from text"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '-', text)
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        # Replace spaces with hyphens
        filename = re.sub(r'\s+', '-', filename)
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        return filename.lower()
    
    def add_summary(self, episode_title: str, podcast_title: str, 
                   episode_date: str, duration: str, summary: str) -> str:
        """Add a new summary and generate HTML page"""
        try:
            # Parse the date
            date_obj = datetime.strptime(episode_date, "%Y-%m-%d")
            date_str = date_obj.strftime("%Y%m%d")
            
            # Create filename
            sanitized_podcast = self._sanitize_filename(podcast_title)
            sanitized_title = self._sanitize_filename(episode_title)
            filename = f"{date_str}_{sanitized_podcast}_{sanitized_title}"
            
            # Create HTML page
            html_content = self._generate_summary_html(
                episode_title, podcast_title, episode_date, duration, summary, filename
            )
            
            html_file = self.summaries_dir / f"{filename}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Add to summaries list
            summary_data = {
                'title': episode_title,
                'podcast': podcast_title,
                'date': date_obj,
                'summary': summary,
                'filename': filename,
                'url': f"{self.feed_link}summaries/{filename}.html"
            }
            
            # Insert at beginning (most recent first)
            self.summaries.insert(0, summary_data)
            
            # Update RSS feed
            self._update_rss_feed()
            
            # Update index page
            self._update_index_page()
            
            return str(html_file)
            
        except Exception as e:
            print(f"Error adding summary: {e}")
            return ""
    
    def _generate_summary_html(self, episode_title: str, podcast_title: str,
                             episode_date: str, duration: str, summary: str, filename: str) -> str:
        """Generate HTML content for a single summary page"""
        
        # Convert summary paragraphs to HTML
        summary_paragraphs = summary.split('\n\n')
        summary_html = ""
        for paragraph in summary_paragraphs:
            if paragraph.strip():
                summary_html += f'<p>{paragraph.strip()}</p>\n'
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{episode_title} - Podcast Summary</title>
    <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← Back to All Summaries</a>
        
        <div class="summary-detail">
            <h1>{episode_title}</h1>
            
            <div class="metadata">
                <span><strong>Podcast:</strong> {podcast_title}</span>
                <span><strong>Date:</strong> {episode_date}</span>
                <span><strong>Duration:</strong> {duration}</span>
            </div>
            
            <div class="summary-content">
                {summary_html}
            </div>
            
            <div class="date">
                Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    </div>
    
    <footer>
        <p>This summary was generated by Podcast CLI using OpenAI's GPT model.</p>
    </footer>
</body>
</html>"""
        
        return html_content
    
    def _update_rss_feed(self):
        """Update the RSS feed file"""
        try:
            # Create RSS feed
            rss = ET.Element('rss', version='2.0')
            channel = ET.SubElement(rss, 'channel')
            
            # Channel metadata
            ET.SubElement(channel, 'title').text = self.feed_title
            ET.SubElement(channel, 'description').text = self.feed_description
            ET.SubElement(channel, 'link').text = self.feed_link
            ET.SubElement(channel, 'language').text = self.feed_language
            ET.SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Add items (summaries)
            for summary in self.summaries[:20]:  # Limit to 20 most recent
                item = ET.SubElement(channel, 'item')
                ET.SubElement(item, 'title').text = summary['title']
                
                # Create description with HTML content
                description = ET.SubElement(item, 'description')
                description.text = f"""<![CDATA[
                <h3>Podcast: {summary['podcast']}</h3>
                <p><strong>Date:</strong> {summary['date'].strftime('%Y-%m-%d')}</p>
                
                <h4>Summary:</h4>
                {summary['summary']}
                ]]>
                """
                
                ET.SubElement(item, 'link').text = summary['url']
                ET.SubElement(item, 'guid').text = summary['url']
                ET.SubElement(item, 'pubDate').text = summary['date'].strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # Write RSS file
            rss_file = self.docs_dir / "feed.xml"
            with open(rss_file, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")[23:])
                
        except Exception as e:
            print(f"Error updating RSS feed: {e}")
    
    def _update_index_page(self):
        """Update the main index page"""
        try:
            # Generate summary items HTML
            summary_items = ""
            for summary in self.summaries[:20]:  # Limit to 20 most recent
                # Truncate summary for preview
                preview = summary['summary'][:200] + "..." if len(summary['summary']) > 200 else summary['summary']
                
                summary_items += f"""
                <div class="summary-item">
                    <h2><a href="summaries/{summary['filename']}.html">{summary['title']}</a></h2>
                    <div class="metadata">
                        <span><strong>Podcast:</strong> {summary['podcast']}</span>
                        <span><strong>Date:</strong> {summary['date'].strftime('%Y-%m-%d')}</span>
                    </div>
                    <div class="summary-content">
                        <p>{preview}</p>
                    </div>
                    <div class="date">
                        <a href="summaries/{summary['filename']}.html">Read full summary →</a>
                    </div>
                </div>
                """
            
            index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Podcast Summaries</title>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Podcast Summaries</h1>
            <p class="subtitle">AI-generated summaries of podcast episodes</p>
            <a href="feed.xml" class="rss-link">📡 RSS Feed</a>
        </header>
        
        {summary_items}
    </div>
    
    <footer>
        <p>Generated by Podcast CLI using OpenAI's GPT model</p>
    </footer>
</body>
</html>"""
            
            # Write index file
            index_file = self.docs_dir / "index.html"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
                
        except Exception as e:
            print(f"Error updating index page: {e}")
    
    def get_feed_url(self) -> str:
        """Get the RSS feed URL"""
        return f"{self.feed_link}feed.xml"
    
    def get_site_url(self) -> str:
        """Get the main site URL"""
        return self.feed_link 