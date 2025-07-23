This is a project for the "LLMS and Beyond: Modern topics in reasoning and agentic systems" from the SS2025 @ University of Tübingen.  

# 🎓 Automated Lecture Notetaker

An intelligent agent that automatically processes YouTube lectures and creates structured, summarized notes in your Notion workspace.

## 🌟 Features

- **YouTube Integration**: Fetch video transcripts and metadata using YouTube API
- **AI-Powered Processing**: Leverage Google's Gemini API for intelligent content analysis
- **Smart Summarization**: Generate concise summaries of lecture content
- **Key Concept Extraction**: Identify and highlight important concepts and terms
- **Chapter Generation**: Automatically create logical chapters and sections
- **Notion Integration**: Seamlessly upload structured notes to your Notion workspace
- **Review Questions**: Generate study questions based on content

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/raulgrau/llm-agent.git
   cd llm-agent
   
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On Linux/Mac
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   copy .env.example .env  # On Windows
   # cp .env.example .env  # On Linux/Mac
   # Edit .env with your API keys (see Configuration section)
   ```

3. **Verify Setup**
   ```bash
   python quick_start.py
   ```

4. **Process a Lecture**
   ```bash
   python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
   ```

## 📋 Prerequisites

- Python 3.8+
- YouTube Data API v3 key
- Google AI Studio API key (for Gemini)
- Notion API integration token (optional)
- Notion database ID (optional - for storing notes)

## 🔧 Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/raulgrau/llm-agent.git
cd llm-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env  # On Windows
# cp .env.example .env  # On Linux/Mac
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here

# Google AI (Gemini)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Notion API
NOTION_TOKEN=your_notion_integration_token_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Optional: Custom settings
DEFAULT_MODEL=gemini-pro
CHUNK_SIZE=4000
MAX_RETRIES=3
```

### Getting API Keys

#### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)

#### Google AI Studio (Gemini)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

#### Notion API
1. Go to [Notion Developers](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the Internal Integration Token
4. Share your database with the integration

## 📚 Usage

### Command Line Interface

```bash
# Basic usage
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Skip Notion integration (output to console only)
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --no-notion

# With custom options
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" \
               --chapters 5 \
               --summary-length 200

# Use different language transcript
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --language es

# Test API connections
python main.py --test-connections
```

### Python API

```python
from lecture_notetaker import LectureNotetaker

# Initialize the notetaker
notetaker = LectureNotetaker()

# Process a single video
result = notetaker.process_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID"
)

# Access the structured content
print(f"Summary: {result.summary}")
print(f"Key Concepts: {len(result.key_concepts)}")
print(f"Chapters: {len(result.chapters)}")
print(f"Review Questions: {len(result.review_questions)}")
```

### Available Transcript Languages

The tool automatically detects available transcript languages for each video:

- **Manually Created**: Human-created transcripts (highest quality)
- **Auto-Generated**: YouTube's automatic transcripts
- **Translations**: Machine-translated versions in 16+ languages

You can specify a language using the `--language` flag (e.g., `--language es` for Spanish).

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   YouTube API   │────│  Transcript     │────│   AI Processor  │
│                 │    │   Extractor     │    │   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   Notion API    │────│  Note Generator │←────────────┘
│   (Optional)    │    │                 │
└─────────────────┘    └─────────────────┘
```

### Core Components

- **`transcript_extractor.py`**: Handles YouTube video transcript extraction with multiple language support
- **`ai_processor.py`**: Processes transcripts using Google's Gemini API for intelligent analysis
- **`notion_client.py`**: Manages Notion API interactions for note storage
- **`lecture_notetaker.py`**: Main orchestrator that coordinates the entire workflow
- **`main.py`**: CLI interface and entry point

## 📖 API Reference

### LectureNotetaker Class

```python
class LectureNotetaker:
    def __init__(self, config: Optional[Config] = None)
    
    def process_video(self, url: str, **kwargs) -> ProcessedContent
    def get_video_info(self, url: str) -> VideoInfo
    def test_connections(self) -> Dict[str, bool]
```

### Configuration Options

```python
@dataclass
class Config:
    youtube_api_key: str
    google_ai_api_key: str
    notion_token: str = None  # Optional
    notion_database_id: str = None  # Optional
    model_name: str = "gemini-2.5-flash-lite"
    summary_length: int = 300
    default_chapters: int = 5
    key_concepts_limit: int = 10
```

### Output Structure

```python
@dataclass
class ProcessedContent:
    summary: str
    key_concepts: List[KeyConcept]
    chapters: List[Chapter]
    main_topics: List[str]
    learning_objectives: List[str]
    review_questions: List[str]
```

## 🛠️ Project Structure

```
llm-agent/
├── src/
│   └── lecture_notetaker/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── transcript_extractor.py    # YouTube transcript extraction
│       │   ├── ai_processor.py           # AI content processing
│       │   ├── notion_client.py          # Notion API integration
│       │   └── lecture_notetaker.py      # Main orchestrator
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── config.py                 # Configuration management
│       │   ├── logger.py                 # Logging utilities
│       │   └── exceptions.py             # Custom exceptions
│       └── cli/
│           ├── __init__.py
│           └── main.py                   # CLI argument parsing
├── main.py                               # Main entry point
├── quick_start.py                        # Setup verification script
├── requirements.txt                      # Python dependencies
├── setup.py                             # Package installation
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
├── LICENSE                              # MIT License
└── README.md                            # This documentation
```

---