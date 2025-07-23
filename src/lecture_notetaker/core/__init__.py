"""Core package for the Lecture Notetaker."""

from .transcript_extractor import TranscriptExtractor, VideoInfo, TranscriptSegment
from .ai_processor import AIProcessor, ProcessedContent, KeyConcept, Chapter
from .notion_client import NotionClient
from .lecture_notetaker import LectureNotetaker

__all__ = [
    "TranscriptExtractor",
    "VideoInfo", 
    "TranscriptSegment",
    "AIProcessor",
    "ProcessedContent",
    "KeyConcept",
    "Chapter",
    "NotionClient",
    "LectureNotetaker"
]
