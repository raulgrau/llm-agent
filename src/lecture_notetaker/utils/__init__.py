"""Utilities package for the Lecture Notetaker."""

from .config import Config
from .exceptions import (
    LectureNotetakerError,
    TranscriptExtractionError,
    AIProcessingError,
    NotionAPIError,
    ConfigurationError,
    VideoNotFoundError,
    TranscriptNotAvailableError
)
from .logger import setup_logger, logger

__all__ = [
    "Config",
    "LectureNotetakerError",
    "TranscriptExtractionError",
    "AIProcessingError", 
    "NotionAPIError",
    "ConfigurationError",
    "VideoNotFoundError",
    "TranscriptNotAvailableError",
    "setup_logger",
    "logger"
]
