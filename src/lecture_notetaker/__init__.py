"""
Automated Lecture Notetaker

An intelligent agent that processes YouTube lectures and creates structured notes in Notion.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.lecture_notetaker import LectureNotetaker
from .utils.config import Config
from .utils.exceptions import (
    LectureNotetakerError,
    TranscriptExtractionError,
    AIProcessingError,
    NotionAPIError
)

__all__ = [
    "LectureNotetaker",
    "Config",
    "LectureNotetakerError",
    "TranscriptExtractionError", 
    "AIProcessingError",
    "NotionAPIError"
]
