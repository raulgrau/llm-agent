"""YouTube transcript extraction module."""

import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import googleapiclient.discovery
except ImportError:
    googleapiclient = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    from pytube import YouTube
except ImportError:
    YouTube = None

from ..utils.exceptions import (
    TranscriptExtractionError,
    VideoNotFoundError,
    TranscriptNotAvailableError
)
from ..utils.logger import logger


@dataclass
class VideoInfo:
    """Information about a YouTube video."""
    id: str
    title: str
    description: str
    duration: int  # in seconds
    channel_title: str
    published_at: str
    view_count: int
    like_count: Optional[int] = None
    thumbnail_url: Optional[str] = None


@dataclass
class TranscriptSegment:
    """A segment of video transcript."""
    text: str
    start: float
    duration: float
    
    @property
    def end(self) -> float:
        """End time of the segment."""
        return self.start + self.duration


class TranscriptExtractor:
    """Extracts transcripts and metadata from YouTube videos."""
    
    def __init__(self, youtube_api_key: str):
        """Initialize the transcript extractor.
        
        Args:
            youtube_api_key: YouTube Data API v3 key
        """
        self.youtube_api_key = youtube_api_key
        self.youtube_service = None
        
        # Check for required dependencies
        if not googleapiclient:
            raise TranscriptExtractionError(
                "Google API client not installed. Please run: pip install google-api-python-client"
            )
        
        if not YouTubeTranscriptApi:
            raise TranscriptExtractionError(
                "YouTube Transcript API not installed. Please run: pip install youtube-transcript-api"
            )
        
        self._init_youtube_service()
    
    def _init_youtube_service(self) -> None:
        """Initialize YouTube API service."""
        try:
            self.youtube_service = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=self.youtube_api_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize YouTube service: {e}")
            raise TranscriptExtractionError(f"YouTube API initialization failed: {e}")
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID
            
        Raises:
            TranscriptExtractionError: If video ID cannot be extracted
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise TranscriptExtractionError(f"Could not extract video ID from URL: {url}")
    
    def get_video_info(self, video_id: str) -> VideoInfo:
        """Get video information from YouTube API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            VideoInfo object with video metadata
            
        Raises:
            VideoNotFoundError: If video is not found
            TranscriptExtractionError: If API call fails
        """
        try:
            request = self.youtube_service.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                raise VideoNotFoundError(f"Video not found: {video_id}")
            
            video_data = response['items'][0]
            snippet = video_data['snippet']
            statistics = video_data['statistics']
            content_details = video_data['contentDetails']
            
            # Parse duration (ISO 8601 format)
            duration = self._parse_duration(content_details['duration'])
            
            return VideoInfo(
                id=video_id,
                title=snippet['title'],
                description=snippet['description'],
                duration=duration,
                channel_title=snippet['channelTitle'],
                published_at=snippet['publishedAt'],
                view_count=int(statistics.get('viewCount', 0)),
                like_count=int(statistics.get('likeCount', 0)) if 'likeCount' in statistics else None,
                thumbnail_url=snippet['thumbnails'].get('maxres', {}).get('url')
            )
            
        except VideoNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get video info for {video_id}: {e}")
            raise TranscriptExtractionError(f"Failed to get video info: {e}")
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration string to seconds.
        
        Args:
            duration_str: ISO 8601 duration string (e.g., 'PT1H2M30S')
            
        Returns:
            Duration in seconds
        """
        # Remove 'PT' prefix
        duration_str = duration_str.replace('PT', '')
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        if 'H' in duration_str:
            hours_match = re.search(r'(\d+)H', duration_str)
            if hours_match:
                hours = int(hours_match.group(1))
        
        # Extract minutes
        if 'M' in duration_str:
            minutes_match = re.search(r'(\d+)M', duration_str)
            if minutes_match:
                minutes = int(minutes_match.group(1))
        
        # Extract seconds
        if 'S' in duration_str:
            seconds_match = re.search(r'(\d+)S', duration_str)
            if seconds_match:
                seconds = int(seconds_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    def get_transcript(self, video_id: str, language: str = 'en') -> List[TranscriptSegment]:
        """Get transcript for a YouTube video.
        
        Args:
            video_id: YouTube video ID
            language: Preferred language code (default: 'en')
            
        Returns:
            List of transcript segments
            
        Raises:
            TranscriptNotAvailableError: If transcript is not available
            TranscriptExtractionError: If extraction fails
        """
        try:
            # Based on the debug output, we need to instantiate YouTubeTranscriptApi
            api_instance = YouTubeTranscriptApi()
            
            # First, try to list available transcripts
            try:
                available_info = api_instance.list(video_id)
                logger.info(f"Available transcripts info: {available_info}")
            except Exception as e:
                logger.warning(f"Could not list available transcripts: {e}")
            
            # Try to fetch the transcript
            try:
                transcript_data = api_instance.fetch(video_id)
                logger.info(f"Fetched transcript data type: {type(transcript_data)}")
                
                # If we got data, try to parse it
                if transcript_data:
                    logger.info(f"First few characters of transcript: {str(transcript_data)[:200]}...")
            except Exception as e:
                logger.error(f"Failed to fetch transcript: {e}")
                raise TranscriptNotAvailableError(
                    f"No transcript available for video: {video_id}. Error: {e}"
                )
            
            # The transcript_data might be a string or some other format
            # Let's try to parse it into segments
            segments = []
            
            # Check if it's a FetchedTranscript object with snippets
            if hasattr(transcript_data, 'snippets'):
                logger.info(f"Processing FetchedTranscript with {len(transcript_data.snippets)} snippets")
                for snippet in transcript_data.snippets:
                    if hasattr(snippet, 'text') and hasattr(snippet, 'start') and hasattr(snippet, 'duration'):
                        segments.append(TranscriptSegment(
                            text=snippet.text.strip(),
                            start=float(snippet.start),
                            duration=float(snippet.duration)
                        ))
                    else:
                        # Fallback for dict-like snippet
                        segments.append(TranscriptSegment(
                            text=str(getattr(snippet, 'text', snippet)).strip(),
                            start=float(getattr(snippet, 'start', 0)),
                            duration=float(getattr(snippet, 'duration', 5.0))
                        ))
            elif isinstance(transcript_data, str):
                # If it's a string, we need to split it into segments
                # This is a simple approach - split by lines or sentences
                lines = transcript_data.split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line:
                        segments.append(TranscriptSegment(
                            text=line,
                            start=float(i * 5),  # Estimate 5 seconds per line
                            duration=5.0
                        ))
            elif isinstance(transcript_data, list):
                # If it's already a list, try to parse each entry
                for i, entry in enumerate(transcript_data):
                    if isinstance(entry, dict):
                        segments.append(TranscriptSegment(
                            text=entry.get('text', '').strip(),
                            start=float(entry.get('start', i * 5)),
                            duration=float(entry.get('duration', 5.0))
                        ))
                    else:
                        text = str(entry).strip()
                        if text:
                            segments.append(TranscriptSegment(
                                text=text,
                                start=float(i * 5),
                                duration=5.0
                            ))
            else:
                # Unknown format, convert to string
                text = str(transcript_data).strip()
                if text:
                    segments.append(TranscriptSegment(
                        text=text,
                        start=0.0,
                        duration=60.0  # Default duration
                    ))
            
            if not segments:
                raise TranscriptNotAvailableError(
                    f"No usable transcript data found for video: {video_id}"
                )
            
            logger.info(f"Successfully extracted transcript with {len(segments)} segments")
            return segments
            
        except TranscriptNotAvailableError:
            raise
        except Exception as e:
            logger.error(f"Failed to get transcript for {video_id}: {e}")
            raise TranscriptExtractionError(f"Transcript extraction failed: {e}")
    
    def get_transcript_text(self, video_id: str, language: str = 'en') -> str:
        """Get transcript as a single text string.
        
        Args:
            video_id: YouTube video ID
            language: Preferred language code (default: 'en')
            
        Returns:
            Full transcript text
        """
        segments = self.get_transcript(video_id, language)
        return '\n'.join(segment.text for segment in segments)
    
    def extract_from_url(self, url: str, language: str = 'en') -> Tuple[VideoInfo, List[TranscriptSegment]]:
        """Extract video info and transcript from YouTube URL.
        
        Args:
            url: YouTube video URL
            language: Preferred language code (default: 'en')
            
        Returns:
            Tuple of (VideoInfo, List[TranscriptSegment])
        """
        video_id = self.extract_video_id(url)
        video_info = self.get_video_info(video_id)
        transcript = self.get_transcript(video_id, language)
        
        return video_info, transcript
