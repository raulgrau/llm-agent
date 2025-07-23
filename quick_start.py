"""
Quick start script - processes a sample video to test the setup
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from lecture_notetaker import LectureNotetaker
from lecture_notetaker.utils.config import Config

def quick_start():
    """Quick start function to test the setup."""
    print("🚀 Automated Lecture Notetaker - Quick Start")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and fill in your API keys.")
        print(f"   Expected location: {env_file}")
        return False
    
    try:
        # Load configuration
        config = Config.from_env()
        config.validate()
        print("✅ Configuration loaded successfully")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("📝 Please check your .env file and ensure all required keys are set.")
        return False
    
    try:
        # Initialize notetaker
        notetaker = LectureNotetaker(config)
        print("✅ Notetaker initialized")
        
        # Test connections
        print("\n🔍 Testing API connections...")
        connections = notetaker.test_connections()
        
        all_connected = True
        for service, status in connections.items():
            status_icon = "✅" if status else "❌"
            service_name = service.replace('_', ' ').title()
            print(f"{status_icon} {service_name}")
            if not status:
                all_connected = False
        
        if not all_connected:
            print("\n❌ Some API connections failed.")
            print("📝 Please check your API keys in the .env file.")
            return False
        
        print("\n🎉 All connections successful!")
        print("\n📚 Ready to process lectures!")
        print("\nTo process a video, run:")
        print('python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"')
        
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False

if __name__ == "__main__":
    success = quick_start()
    sys.exit(0 if success else 1)
