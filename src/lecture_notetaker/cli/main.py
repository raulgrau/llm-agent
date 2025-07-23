"""Command-line interface for the Lecture Notetaker."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..core.lecture_notetaker import LectureNotetaker
from ..utils.config import Config
from ..utils.logger import setup_logger, logger
from ..utils.exceptions import LectureNotetakerError


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Automated Lecture Notetaker - Convert YouTube lectures to structured Notion notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s --url "https://youtu.be/dQw4w9WgXcQ" --title "Custom Title"
  %(prog)s --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --chapters 8 --no-notion
  %(prog)s --test-connections
        """
    )
    
    # Main arguments
    parser.add_argument(
        "--url",
        type=str,
        help="YouTube video URL to process"
    )
    
    parser.add_argument(
        "--playlist",
        type=str,
        help="YouTube playlist URL to process (processes all videos)"
    )
    
    parser.add_argument(
        "--title",
        type=str,
        help="Custom title for the notes (overrides video title)"
    )
    
    # Processing options
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Preferred transcript language (default: en)"
    )
    
    parser.add_argument(
        "--summary-length",
        type=int,
        default=300,
        help="Target summary length in words (default: 300)"
    )
    
    parser.add_argument(
        "--chapters",
        type=int,
        default=5,
        help="Number of chapters to generate (default: 5)"
    )
    
    parser.add_argument(
        "--key-concepts",
        type=int,
        default=10,
        help="Maximum number of key concepts to extract (default: 10)"
    )
    
    # Notion options
    parser.add_argument(
        "--no-notion",
        action="store_true",
        help="Skip creating Notion page (only process and display results)"
    )
    
    # Utility commands
    parser.add_argument(
        "--test-connections",
        action="store_true",
        help="Test all API connections and exit"
    )
    
    parser.add_argument(
        "--info",
        type=str,
        help="Get video information without processing"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (default: console only)"
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(level=args.log_level, log_file=args.log_file)
    
    try:
        # Load configuration
        if args.config:
            logger.info(f"Loading configuration from {args.config}")
            # In a full implementation, you would load from file
            config = Config.from_env()
        else:
            config = Config.from_env()
        
        # Test connections if requested
        if args.test_connections:
            return test_connections(config)
        
        # Get video info if requested
        if args.info:
            return get_video_info(config, args.info)
        
        # Process video or playlist
        if args.url:
            return process_video(config, args)
        elif args.playlist:
            return process_playlist(config, args)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except LectureNotetakerError as e:
        logger.error(f"Application error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def test_connections(config: Config) -> int:
    """Test all API connections."""
    logger.info("Testing API connections...")
    
    try:
        notetaker = LectureNotetaker(config)
        results = notetaker.test_connections()
        
        print("\n🔍 Connection Test Results:")
        print("=" * 30)
        
        all_good = True
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            service_name = service.replace('_', ' ').title()
            print(f"{status_icon} {service_name}: {'Connected' if status else 'Failed'}")
            if not status:
                all_good = False
        
        if all_good:
            print("\n🎉 All connections successful! You're ready to go.")
            return 0
        else:
            print("\n⚠️  Some connections failed. Please check your API keys and configuration.")
            return 1
            
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return 1


def get_video_info(config: Config, url: str) -> int:
    """Get and display video information."""
    try:
        notetaker = LectureNotetaker(config)
        video_info = notetaker.get_video_info(url)
        
        print("\n📺 Video Information:")
        print("=" * 50)
        print(f"Title: {video_info.title}")
        print(f"Channel: {video_info.channel_title}")
        print(f"Duration: {video_info.duration // 60}:{video_info.duration % 60:02d}")
        print(f"Published: {video_info.published_at.split('T')[0]}")
        print(f"Views: {video_info.view_count:,}")
        if video_info.like_count:
            print(f"Likes: {video_info.like_count:,}")
        print(f"URL: https://www.youtube.com/watch?v={video_info.id}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        return 1


def process_video(config: Config, args: argparse.Namespace) -> int:
    """Process a single video."""
    try:
        logger.info(f"Processing video: {args.url}")
        
        notetaker = LectureNotetaker(config)
        result = notetaker.process_video(
            url=args.url,
            title=args.title,
            language=args.language,
            summary_length=args.summary_length,
            chapters=args.chapters,
            key_concepts_limit=args.key_concepts,
            create_notion_page=not args.no_notion
        )
        
        if not result.success:
            logger.error(f"Processing failed: {result.error_message}")
            return 1
        
        # Display results
        print("\n🎓 Processing Complete!")
        print("=" * 50)
        print(f"📺 Video: {result.video_info.title}")
        print(f"📝 Summary: {len(result.processed_content.summary.split())} words")
        print(f"🔑 Key Concepts: {len(result.processed_content.key_concepts)}")
        print(f"📖 Chapters: {len(result.processed_content.chapters)}")
        print(f"❓ Review Questions: {len(result.processed_content.questions)}")
        
        if result.notion_url:
            print(f"🔗 Notion Page: {result.notion_url}")
        
        # Display summary if not creating Notion page
        if args.no_notion:
            print(f"\n📋 Summary:")
            print("-" * 20)
            print(result.processed_content.summary)
            
            if result.processed_content.key_concepts:
                print(f"\n🔑 Key Concepts:")
                print("-" * 20)
                for i, concept in enumerate(result.processed_content.key_concepts[:5], 1):
                    print(f"{i}. **{concept.term}**: {concept.definition}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        return 1


def process_playlist(config: Config, args: argparse.Namespace) -> int:
    """Process a playlist."""
    logger.info(f"Processing playlist: {args.playlist}")
    
    try:
        notetaker = LectureNotetaker(config)
        results = notetaker.process_playlist(args.playlist)
        
        print(f"\n🎵 Processed {len(results)} videos from playlist")
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        print(f"✅ Successful: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Playlist processing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
