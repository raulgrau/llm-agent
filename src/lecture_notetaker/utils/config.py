"""Configuration management for the Lecture Notetaker."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Configuration class for the Lecture Notetaker."""
    
    # API Keys
    youtube_api_key: str
    google_ai_api_key: str
    notion_token: str
    notion_database_id: str
    
    # AI Model Settings
    model_name: str = "gemini-pro"
    chunk_size: int = 4000
    max_retries: int = 3
    
    # Processing Settings
    summary_length: int = 300
    default_chapters: int = 5
    key_concepts_limit: int = 10
    
    # Notion Settings
    notion_page_title_template: str = "📚 {title} - Lecture Notes"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", ""),
            notion_token=os.getenv("NOTION_TOKEN", ""),
            notion_database_id=os.getenv("NOTION_DATABASE_ID", ""),
            model_name=os.getenv("DEFAULT_MODEL", "gemini-pro"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "4000")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            summary_length=int(os.getenv("SUMMARY_LENGTH", "300")),
            default_chapters=int(os.getenv("DEFAULT_CHAPTERS", "5")),
            key_concepts_limit=int(os.getenv("KEY_CONCEPTS_LIMIT", "10")),
            notion_page_title_template=os.getenv(
                "NOTION_PAGE_TITLE_TEMPLATE", 
                "📚 {title} - Lecture Notes"
            )
        )
    
    def validate(self) -> None:
        """Validate that all required configuration is present."""
        missing_keys = []
        
        if not self.youtube_api_key:
            missing_keys.append("YOUTUBE_API_KEY")
        if not self.google_ai_api_key:
            missing_keys.append("GOOGLE_AI_API_KEY")
        if not self.notion_token:
            missing_keys.append("NOTION_TOKEN")
        if not self.notion_database_id:
            missing_keys.append("NOTION_DATABASE_ID")
            
        if missing_keys:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_keys)}"
            )
