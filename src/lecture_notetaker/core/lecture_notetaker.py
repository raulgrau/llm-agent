"""Main LectureNotetaker class that orchestrates the entire process."""

from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass

from .transcript_extractor import TranscriptExtractor, VideoInfo, TranscriptSegment
from .ai_processor import AIProcessor, ProcessedContent
from .notion_client import NotionClient
from ..utils.config import Config
from ..utils.exceptions import LectureNotetakerError, ConfigurationError
from ..utils.logger import logger


@dataclass
class NoteResult:
    """Result of processing a lecture video."""
    video_info: VideoInfo
    processed_content: ProcessedContent
    notion_url: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class LectureNotetaker:
    """Main class for automated lecture note-taking."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the lecture notetaker.
        
        Args:
            config: Configuration object. If None, will load from environment
        """
        self.config = config or Config.from_env()
        self.config.validate()
        
        # Initialize components
        self.transcript_extractor = TranscriptExtractor(self.config.youtube_api_key)
        self.ai_processor = AIProcessor(
            self.config.google_ai_api_key, 
            self.config.model_name
        )
        self.notion_client = NotionClient(
            self.config.notion_token, 
            self.config.notion_database_id
        )
        
        logger.info("LectureNotetaker initialized successfully")
    
    def process_video(
        self,
        url: str,
        title: Optional[str] = None,
        language: str = 'en',
        summary_length: Optional[int] = None,
        chapters: Optional[int] = None,
        key_concepts_limit: Optional[int] = None,
        create_notion_page: bool = True
    ) -> NoteResult:
        """Process a single YouTube video and create lecture notes.
        
        Args:
            url: YouTube video URL
            title: Custom title for the notes (optional)
            language: Preferred transcript language
            summary_length: Target summary length in words
            chapters: Number of chapters to create
            key_concepts_limit: Maximum number of key concepts
            create_notion_page: Whether to create a Notion page
            
        Returns:
            NoteResult with processing results
        """
        try:
            logger.info(f"Starting to process video: {url}")
            
            # Extract video info and transcript
            video_info, transcript_segments = self.transcript_extractor.extract_from_url(
                url, language
            )
            
            # Override title if provided
            if title:
                video_info.title = title
            
            logger.info(f"Extracted transcript with {len(transcript_segments)} segments")
            
            # Process with AI
            processed_content = self.ai_processor.process_transcript(
                video_info=video_info,
                transcript_segments=transcript_segments,
                summary_length=summary_length or self.config.summary_length,
                num_chapters=chapters or self.config.default_chapters,
                key_concepts_limit=key_concepts_limit or self.config.key_concepts_limit
            )
            
            logger.info("AI processing completed")
            
            notion_url = None
            if create_notion_page:
                # Create Notion page
                notion_url = self.notion_client.create_lecture_notes(
                    video_info=video_info,
                    processed_content=processed_content,
                    page_title_template=self.config.notion_page_title_template
                )
                logger.info(f"Created Notion page: {notion_url}")
            
            return NoteResult(
                video_info=video_info,
                processed_content=processed_content,
                notion_url=notion_url,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Failed to process video {url}: {e}")
            return NoteResult(
                video_info=VideoInfo(
                    id="", title="Error", description="", duration=0,
                    channel_title="", published_at="", view_count=0
                ),
                processed_content=ProcessedContent(
                    summary="", key_concepts=[], chapters=[],
                    main_topics=[], learning_objectives=[], questions=[]
                ),
                success=False,
                error_message=str(e)
            )
    
    def process_playlist(
        self,
        playlist_url: str,
        max_videos: Optional[int] = None,
        **kwargs
    ) -> List[NoteResult]:
        """Process multiple videos from a YouTube playlist.
        
        Args:
            playlist_url: YouTube playlist URL
            max_videos: Maximum number of videos to process
            **kwargs: Additional arguments passed to process_video
            
        Returns:
            List of NoteResult objects
        """
        # This is a simplified implementation
        # In a full implementation, you would extract video URLs from the playlist
        logger.warning("Playlist processing not fully implemented yet")
        return []
    
    def get_video_info(self, url: str) -> VideoInfo:
        """Get video information without processing transcript.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoInfo object
        """
        video_id = self.transcript_extractor.extract_video_id(url)
        return self.transcript_extractor.get_video_info(video_id)
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all API connections.
        
        Returns:
            Dictionary with connection test results
        """
        results = {}
        
        # Test YouTube API
        try:
            self.transcript_extractor._init_youtube_service()
            results['youtube'] = True
            logger.info("YouTube API connection: OK")
        except Exception as e:
            results['youtube'] = False
            logger.error(f"YouTube API connection failed: {e}")
        
        # Test Google AI API
        try:
            self.ai_processor._init_model()
            results['google_ai'] = True
            logger.info("Google AI API connection: OK")
        except Exception as e:
            results['google_ai'] = False
            logger.error(f"Google AI API connection failed: {e}")
        
        # Test Notion API
        try:
            results['notion'] = self.notion_client.test_connection()
            if results['notion']:
                logger.info("Notion API connection: OK")
            else:
                logger.error("Notion API connection failed")
        except Exception as e:
            results['notion'] = False
            logger.error(f"Notion API connection failed: {e}")
        
        return results
