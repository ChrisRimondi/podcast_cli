# Podcast CLI

A powerful command-line interface for managing and summarizing podcasts from the macOS Podcast app using AI. Browse your downloaded episodes, generate intelligent summaries, and explore your podcast library with ease.

## Features

- 📻 **Browse Podcast Subscriptions**: View all your podcast subscriptions from the macOS Podcast app
- 📝 **Episode Management**: View latest episodes with transcripts (limited to 10 most recent)
- 🤖 **AI-Powered Summaries**: Generate comprehensive 5-paragraph summaries from episode transcripts
- 💾 **Smart Caching**: Fast navigation with intelligent caching of data and summaries
- 🎯 **Intuitive Interface**: Simple numbered menu system with clear navigation
- 🚪 **Easy Exit**: Exit commands available at every menu level (`exit`, `quit`, `q`)
- 📅 **Accurate Dates**: Correct 2025 date display for all episodes
- 🔍 **Transcript Filtering**: Only shows episodes with available transcripts for summarization
- ⚡ **Performance Optimized**: Efficient database queries and transcript processing
- 💾 **Save Summaries**: Save generated summaries as PDF files for later reference
- 📡 **RSS Feed Generation**: Create RSS feeds and web pages for podcast summaries

## Installation

### Prerequisites

- macOS with Podcast app installed
- Python 3.8 or higher
- OpenAI API key

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd podcast_cli
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your OpenAI API key:**
   
   The application will create a configuration file at `~/.config/podcast-cli/config.yaml` on first run. Add your OpenAI API key:

   ```yaml
   openai:
     api_key: "sk-your-openai-api-key-here"
     model: "gpt-4"
     max_tokens: 1000
   ```

   Alternatively, you can set the environment variable:
   ```bash
   export OPENAI_API_KEY="sk-your-openai-api-key-here"
   ```

## Usage

### Basic Usage

1. **Run the application:**
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. **Navigate through the interface:**
   - Select a podcast from your subscriptions
   - Choose an episode from the latest 10 episodes with transcripts
   - Generate an AI summary or view episode details
   - Use `exit`, `quit`, or `q` to exit at any time

### User Interface

The application provides a clean, numbered menu system:

```
Your Podcast Subscriptions:
==================================================

1. Dev Interrupted
   By: LinearB

2. Duolingo Spanish Podcast
   By: Duolingo

3. Heidelcast
   By: R. Scott Clark

Type 'exit' to quit the application, 'help' for help, or enter a number to select a podcast.
```

### Episode Display

```
Latest Episodes from "Dev Interrupted":
============================================================

1. Should you join an AI Startup?
   Date: 2025-07-19 | Duration: 45.0m | Transcript: 📝

2. Is Cursor having their Docker moment?
   Date: 2025-07-15 | Duration: 38.0m | Transcript: 📝

Type 'exit' to quit, 'back' to return to podcasts, or enter a number to select an episode.
```

### Episode Actions Menu

When you select an episode, you'll see these options:

```
Episode Actions:
==================================================

1. Generate Summary
2. Show Details
3. Save Summary as PDF
4. Save Summary as RSS
5. Back to Episodes
6. Back to Podcasts
7. Exit

Type 'exit' to quit, 'back' to return to episodes, or enter a number to select an action.
```

### Navigation Commands

- **Numbers**: Select options from menus
- **`exit`/`quit`/`q`**: Exit the application from any menu
- **`back`/`b`**: Return to previous menu
- **`help`/`h`**: Show help information
- **Ctrl+C**: Emergency exit at any time

## Key Features

### Smart Episode Filtering
- Only shows episodes with available transcripts
- Displays the 10 most recent episodes per podcast
- Automatically filters out episodes without summarization capability

### Intelligent Transcript Processing
- Supports both entitled and free transcript snippets
- Attempts to read full TTML transcript files when available
- Falls back to transcript snippets for shorter content
- Minimum 50-character requirement for summarization

### Accurate Date Display
- Correctly displays 2025 publication dates
- Handles timestamp conversion from macOS Podcast app database
- Proper date formatting for all episodes

### Comprehensive Exit System
- Exit commands available at every menu level
- Clear prompts for navigation options
- Graceful handling of user exits

### Summary Saving
- Save generated summaries as PDF files
- Configurable save directory (default: `~/Documents/podcast-summaries`)
- Automatic filename generation with timestamps
- Professional PDF formatting with episode metadata
- Can be enabled/disabled in configuration

### RSS Feed Generation
- Generate RSS feeds with embedded summary text
- Create individual HTML pages for each summary
- Automatic website generation for GitHub Pages
- RSS feed compatible with all podcast readers
- Professional web design with responsive layout

## GitHub Pages Setup

To publish your RSS feed and summaries online:

1. **Push your repository to GitHub** (if not already done)
2. **Enable GitHub Pages**:
   - Go to your repository settings
   - Scroll to "Pages" section
   - Select "Deploy from a branch"
   - Choose "main" branch and "/docs" folder
   - Click "Save"
3. **Update the site URL** in your config:
   ```yaml
   rss:
     site_url: "https://ChrisRimondi.github.io/podcast_cli/"
   ```
4. **Generate summaries** using the CLI - they'll automatically appear on your site

Your summaries will be available at:
- **Website**: `https://ChrisRimondi.github.io/podcast_cli/`
- **RSS Feed**: `https://ChrisRimondi.github.io/podcast_cli/feed.xml`

## Configuration

The configuration file is located at `~/.config/podcast-cli/config.yaml`:

```yaml
openai:
  api_key: "sk-your-api-key"
  model: "gpt-4"  # or "gpt-3.5-turbo"
  max_tokens: 1000

cache:
  enabled: true
  directory: "~/.cache/podcast-cli"
  max_age_hours: 24

podcast_app:
  database_path: "~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Documents/MTLibrary.sqlite"

save:
  enabled: true
  directory: "~/Documents/podcast-summaries"

rss:
  enabled: true
  directory: "docs"
  site_url: "https://ChrisRimondi.github.io/podcast_cli/"
```

## How It Works

1. **Database Access**: Reads from the macOS Podcast app's SQLite database (`MTLibrary.sqlite`)
2. **Episode Filtering**: Only shows episodes with available transcripts
3. **Transcript Processing**: Extracts text from transcript snippets or TTML files
4. **AI Summarization**: Uses OpenAI's GPT models to generate 5-paragraph summaries
5. **Caching**: Caches episode data and summaries for faster access
6. **Date Conversion**: Correctly converts timestamps to 2025 dates

## Requirements

- **macOS**: This application is designed for macOS and reads from the native Podcast app database
- **Python 3.8+**: Required for all Python dependencies
- **OpenAI API Key**: Required for AI summary generation
- **Local Episodes**: Podcast episodes must be downloaded locally in the macOS Podcast app
- **Transcripts**: Episodes must have available transcripts for summarization
- **PDF Generation**: Uses ReportLab library for creating professional PDF summaries

## Troubleshooting

### Common Issues

1. **"No podcast subscriptions found"**
   - Make sure you have subscribed to podcasts in the macOS Podcast app
   - Ensure the Podcast app has been used at least once
   - Check that you have episodes with transcripts downloaded

2. **"OpenAI API key not found"**
   - Add your API key to the configuration file
   - Or set the `OPENAI_API_KEY` environment variable

3. **"No transcript available"**
   - Not all episodes have transcripts
   - Transcripts must be available in the Podcast app
   - Only episodes with transcripts are shown in the interface

4. **"Transcript too short or empty for summarization"**
   - Episode transcript is less than 50 characters
   - Try selecting a different episode with longer transcript content

5. **Database access errors**
   - Ensure the Podcast app is not currently running
   - Check file permissions for the database
   - Verify the database path in configuration

6. **Dates showing as 1994**
   - This issue has been fixed in the current version
   - All dates should now display correctly as 2025

### Logs

Logs are stored at `~/.cache/podcast-cli/app.log` for debugging.

## Development

### Project Structure

```
podcast_cli/
├── main.py                 # Entry point
├── config/                 # Configuration management
│   └── settings.py
├── data/                   # Database and episode management
│   ├── podcast_db.py       # Database interface
│   └── episode_manager.py  # Episode data management
├── ai/                     # AI summarization
│   └── summarizer.py       # OpenAI integration
├── ui/                     # User interface
│   ├── display.py          # Display formatting
│   └── menu.py             # Menu system
├── utils/                  # Utilities and caching
│   ├── cache.py            # Caching system
│   └── helpers.py          # Helper functions
└── requirements.txt        # Dependencies
```

### Recent Improvements

- ✅ **Fixed database table names** - Corrected `ZPODCAST` → `ZMTPODCAST` and `ZEPISODE` → `ZMTEPISODE`
- ✅ **Added episode filtering** - Only shows podcasts with downloaded episodes
- ✅ **Implemented transcript filtering** - Only displays episodes with available transcripts
- ✅ **Enhanced transcript processing** - Full TTML file reading with JSON snippet fallback
- ✅ **Fixed date display** - Corrected 1994 → 2025 date conversion with proper timestamp handling
- ✅ **Added comprehensive exit system** - Exit commands available at every menu level
- ✅ **Improved user interface** - Removed episode count display, better formatting
- ✅ **Added PDF summary saving** - Professional PDF output with episode metadata
- ✅ **Added RSS feed generation** - RSS feeds and web pages for podcast summaries

### Adding Features

The modular design makes it easy to extend:

- **New AI models**: Modify `ai/summarizer.py`
- **Additional data sources**: Extend `data/podcast_db.py`
- **UI improvements**: Update `ui/` components
- **Caching strategies**: Enhance `utils/cache.py`

## Future Enhancements

- 📦 **Distributable Binary**: PyInstaller-based standalone app
- 🎨 **Enhanced UI**: Rich terminal interface with colors and formatting
- 📊 **Analytics**: Podcast listening statistics and insights
- 🔗 **Export**: Export summaries to various formats
- ⚙️ **Advanced Configuration**: More customization options

## License

This project is open source. Please check the license file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests. 