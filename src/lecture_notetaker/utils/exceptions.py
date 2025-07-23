"""Custom exceptions for the Lecture Notetaker."""


class LectureNotetakerError(Exception):
    """Base exception for all Lecture Notetaker errors."""
    pass


class TranscriptExtractionError(LectureNotetakerError):
    """Raised when transcript extraction fails."""
    pass


class AIProcessingError(LectureNotetakerError):
    """Raised when AI processing fails."""
    pass


class NotionAPIError(LectureNotetakerError):
    """Raised when Notion API operations fail."""
    pass


class ConfigurationError(LectureNotetakerError):
    """Raised when configuration is invalid."""
    pass


class VideoNotFoundError(TranscriptExtractionError):
    """Raised when the specified video cannot be found."""
    pass


class TranscriptNotAvailableError(TranscriptExtractionError):
    """Raised when transcript is not available for the video."""
    pass
