"""Notion API client for creating and managing lecture notes."""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from notion_client import Client
except ImportError:
    Client = None

from .ai_processor import ProcessedContent, KeyConcept, Chapter
from .transcript_extractor import VideoInfo
from ..utils.exceptions import NotionAPIError
from ..utils.logger import logger


class NotionClient:
    """Client for interacting with Notion API."""
    
    def __init__(self, token: str, database_id: str):
        """Initialize the Notion client.
        
        Args:
            token: Notion integration token
            database_id: ID of the database to store notes
        """
        if not Client:
            raise NotionAPIError(
                "Notion client not installed. Please run: pip install notion-client"
            )
            
        self.token = token
        self.database_id = database_id
        self.client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the Notion client."""
        try:
            self.client = Client(auth=self.token)
            logger.info("Notion client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Notion client: {e}")
            raise NotionAPIError(f"Notion client initialization failed: {e}")
    
    def create_lecture_notes(
        self,
        video_info: VideoInfo,
        processed_content: ProcessedContent,
        page_title_template: str = "📚 {title} - Lecture Notes"
    ) -> str:
        """Create a comprehensive lecture notes page in Notion.
        
        Args:
            video_info: Video metadata
            processed_content: AI-processed content
            page_title_template: Template for page title
            
        Returns:
            URL of the created Notion page
            
        Raises:
            NotionAPIError: If page creation fails
        """
        try:
            # Generate page title
            page_title = page_title_template.format(title=video_info.title)
            
            # Create the page
            page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=self._create_page_properties(video_info, page_title),
                children=self._create_page_content(video_info, processed_content)
            )
            
            page_url = page.get("url", "")
            logger.info(f"Created Notion page: {page_url}")
            return page_url
            
        except Exception as e:
            logger.error(f"Failed to create Notion page: {e}")
            raise NotionAPIError(f"Page creation failed: {e}")
    
    def _create_page_properties(self, video_info: VideoInfo, title: str) -> Dict[str, Any]:
        """Create page properties for the database.
        
        Args:
            video_info: Video metadata
            title: Page title
            
        Returns:
            Dictionary of page properties
        """
        # Use only the most basic property that every Notion database has
        properties = {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        }
        
        # Don't add any other properties since they might not exist in the user's database
        # The video URL and other info will be included in the page content instead
        
        return properties
    
    def _create_page_content(
        self, video_info: VideoInfo, processed_content: ProcessedContent
    ) -> List[Dict[str, Any]]:
        """Create the content blocks for the Notion page.
        
        Args:
            video_info: Video metadata
            processed_content: AI-processed content
            
        Returns:
            List of Notion blocks
        """
        blocks = []
        
        # Header with video information
        blocks.extend(self._create_header_section(video_info))
        
        # Summary section
        blocks.extend(self._create_summary_section(processed_content.summary))
        
        # Learning objectives
        if processed_content.learning_objectives:
            blocks.extend(self._create_learning_objectives_section(
                processed_content.learning_objectives
            ))
        
        # Main topics
        if processed_content.main_topics:
            blocks.extend(self._create_main_topics_section(processed_content.main_topics))
        
        # Key concepts
        if processed_content.key_concepts:
            blocks.extend(self._create_key_concepts_section(processed_content.key_concepts))
        
        # Chapters
        if processed_content.chapters:
            blocks.extend(self._create_chapters_section(processed_content.chapters))
        
        # Review questions
        if processed_content.questions:
            blocks.extend(self._create_questions_section(processed_content.questions))
        
        # Footer
        blocks.extend(self._create_footer_section())
        
        return blocks
    
    def _create_header_section(self, video_info: VideoInfo) -> List[Dict[str, Any]]:
        """Create header section with video info."""
        blocks = []
        
        # Video title as heading
        blocks.append({
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": video_info.title
                        }
                    }
                ]
            }
        })
        
        # Video metadata
        duration_str = f"{video_info.duration // 60}:{video_info.duration % 60:02d}"
        metadata_text = (
            f"📺 **Channel:** {video_info.channel_title}\n"
            f"⏱️ **Duration:** {duration_str}\n"
            f"📅 **Published:** {video_info.published_at.split('T')[0]}\n"
            f"👀 **Views:** {video_info.view_count:,}\n"
            f"🔗 **URL:** https://www.youtube.com/watch?v={video_info.id}"
        )
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": metadata_text
                        }
                    }
                ]
            }
        })
        
        # Divider
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        return blocks
    
    def _create_summary_section(self, summary: str) -> List[Dict[str, Any]]:
        """Create summary section."""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📋 Summary"
                        }
                    }
                ]
            }
        })
        
        # Split summary into paragraphs if it's long
        paragraphs = summary.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": paragraph.strip()
                                }
                            }
                        ]
                    }
                })
        
        return blocks
    
    def _create_learning_objectives_section(self, objectives: List[str]) -> List[Dict[str, Any]]:
        """Create learning objectives section."""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "🎯 Learning Objectives"
                        }
                    }
                ]
            }
        })
        
        # Create bulleted list
        for objective in objectives:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": objective
                            }
                        }
                    ]
                }
            })
        
        return blocks
    
    def _create_main_topics_section(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Create main topics section."""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📚 Main Topics"
                        }
                    }
                ]
            }
        })
        
        # Create numbered list
        for i, topic in enumerate(topics, 1):
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": topic
                            }
                        }
                    ]
                }
            })
        
        return blocks
    
    def _create_key_concepts_section(self, concepts: List[KeyConcept]) -> List[Dict[str, Any]]:
        """Create key concepts section."""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "🔑 Key Concepts"
                        }
                    }
                ]
            }
        })
        
        for concept in concepts:
            # Concept term as heading
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": concept.term
                            },
                            "annotations": {
                                "bold": True
                            }
                        }
                    ]
                }
            })
            
            # Definition
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"**Definition:** {concept.definition}"
                            }
                        }
                    ]
                }
            })
            
            # Importance
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"**Why it matters:** {concept.importance}"
                            }
                        }
                    ]
                }
            })
        
        return blocks
    
    def _create_chapters_section(self, chapters: List[Chapter]) -> List[Dict[str, Any]]:
        """Create chapters section."""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "📖 Chapters"
                        }
                    }
                ]
            }
        })
        
        for i, chapter in enumerate(chapters, 1):
            # Chapter title with timestamp
            start_min = int(chapter.start_time // 60)
            start_sec = int(chapter.start_time % 60)
            end_min = int(chapter.end_time // 60)
            end_sec = int(chapter.end_time % 60)
            
            chapter_title = f"{i}. {chapter.title} ({start_min}:{start_sec:02d} - {end_min}:{end_sec:02d})"
            
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": chapter_title
                            }
                        }
                    ]
                }
            })
            
            # Chapter summary
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": chapter.summary
                            }
                        }
                    ]
                }
            })
            
            # Key points
            if chapter.key_points:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "**Key Points:**"
                                },
                                "annotations": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                })
                
                for point in chapter.key_points:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": point
                                    }
                                }
                            ]
                        }
                    })
        
        return blocks
    
    def _create_questions_section(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Create review questions section."""
        blocks = []
        
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "❓ Review Questions"
                        }
                    }
                ]
            }
        })
        
        for i, question in enumerate(questions, 1):
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": question
                            }
                        }
                    ]
                }
            })
        
        return blocks
    
    def _create_footer_section(self) -> List[Dict[str, Any]]:
        """Create footer section."""
        blocks = []
        
        # Divider
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        
        # Footer text
        footer_text = (
            f"📝 *Notes generated automatically by Automated Lecture Notetaker*\n"
            f"⏰ Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')}"
        )
        
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": footer_text
                        },
                        "annotations": {
                            "italic": True
                        }
                    }
                ]
            }
        })
        
        return blocks
    
    def test_connection(self) -> bool:
        """Test the Notion API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to retrieve database info
            self.client.databases.retrieve(database_id=self.database_id)
            logger.info("Notion connection test successful")
            return True
        except Exception as e:
            logger.error(f"Notion connection test failed: {e}")
            return False
