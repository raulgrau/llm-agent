#!/usr/bin/env python3
"""Main entry point for the Automated Lecture Notetaker."""

import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from lecture_notetaker.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
