"""AI processing module using Google's Gemini API."""

import re
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from .transcript_extractor import TranscriptSegment, VideoInfo
from ..utils.exceptions import AIProcessingError
from ..utils.logger import logger


@dataclass
class KeyConcept:
    """A key concept extracted from the lecture."""
    term: str
    definition: str
    importance: str
    timestamp: Optional[float] = None


@dataclass
class Chapter:
    """A chapter/section of the lecture."""
    title: str
    start_time: float
    end_time: float
    summary: str
    key_points: List[str]


@dataclass
class ProcessedContent:
    """Result of AI processing."""
    summary: str
    key_concepts: List[KeyConcept]
    chapters: List[Chapter]
    main_topics: List[str]
    learning_objectives: List[str]
    questions: List[str]


class AIProcessor:
    """Processes lecture transcripts using Google's Gemini API."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """Initialize the AI processor.
        
        Args:
            api_key: Google AI API key
            model_name: Name of the Gemini model to use
        """
        if not genai:
            raise AIProcessingError(
                "Google Generative AI not installed. Please run: pip install google-generativeai"
            )
            
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        self._init_model()
    
    def _init_model(self) -> None:
        """Initialize the Gemini model."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized {self.model_name} model")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise AIProcessingError(f"Model initialization failed: {e}")
    
    def process_transcript(
        self,
        video_info: VideoInfo,
        transcript_segments: List[TranscriptSegment],
        summary_length: int = 300,
        num_chapters: int = 5,
        key_concepts_limit: int = 10
    ) -> ProcessedContent:
        """Process the transcript and extract structured information.
        
        Args:
            video_info: Video metadata
            transcript_segments: List of transcript segments
            summary_length: Target length for summary (words)
            num_chapters: Number of chapters to create
            key_concepts_limit: Maximum number of key concepts to extract
            
        Returns:
            ProcessedContent with structured information
        """
        # Combine transcript text
        full_transcript = self._combine_transcript(transcript_segments)
        
        logger.info("Starting AI processing of transcript...")
        
        # Process different aspects in parallel if possible, or sequentially
        try:
            # Generate summary
            summary = self._generate_summary(video_info, full_transcript, summary_length)
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(
                video_info, full_transcript, key_concepts_limit
            )
            
            # Generate chapters
            chapters = self._generate_chapters(
                video_info, transcript_segments, num_chapters
            )
            
            # Extract main topics
            main_topics = self._extract_main_topics(video_info, full_transcript)
            
            # Generate learning objectives
            learning_objectives = self._generate_learning_objectives(
                video_info, full_transcript
            )
            
            # Generate review questions
            questions = self._generate_questions(video_info, full_transcript)
            
            return ProcessedContent(
                summary=summary,
                key_concepts=key_concepts,
                chapters=chapters,
                main_topics=main_topics,
                learning_objectives=learning_objectives,
                questions=questions
            )
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            raise AIProcessingError(f"Processing failed: {e}")
    
    def _combine_transcript(self, segments: List[TranscriptSegment]) -> str:
        """Combine transcript segments into a single text."""
        return '\n'.join(segment.text for segment in segments)
    
    def _generate_summary(self, video_info: VideoInfo, transcript: str, target_length: int) -> str:
        """Generate a concise summary of the lecture."""
        prompt = f"""
        Please create a comprehensive summary of this lecture transcript.
        
        Video Title: {video_info.title}
        Channel: {video_info.channel_title}
        Duration: {video_info.duration // 60} minutes
        
        Target length: Approximately {target_length} words
        
        Focus on:
        - Main topics and themes
        - Key learning points
        - Important concepts and definitions
        - Practical applications or examples
        
        Transcript:
        {transcript[:8000]}  # Limit to avoid token limits
        
        Summary:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary generation failed. Please try again."
    
    def _extract_key_concepts(
        self, video_info: VideoInfo, transcript: str, limit: int
    ) -> List[KeyConcept]:
        """Extract key concepts and definitions from the lecture."""
        prompt = f"""
        Analyze this lecture transcript and extract the most important key concepts.
        
        Video Title: {video_info.title}
        
        For each concept, provide:
        1. Term/Concept name
        2. Clear definition or explanation
        3. Why it's important in the context of this lecture
        
        Extract the top {limit} most important concepts.
        
        Format your response as:
        CONCEPT: [Term]
        DEFINITION: [Clear definition]
        IMPORTANCE: [Why it matters]
        ---
        
        Transcript:
        {transcript[:8000]}
        
        Key Concepts:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_key_concepts(response.text)
        except Exception as e:
            logger.error(f"Key concept extraction failed: {e}")
            return []
    
    def _parse_key_concepts(self, text: str) -> List[KeyConcept]:
        """Parse key concepts from AI response."""
        concepts = []
        concept_blocks = text.split('---')
        
        for block in concept_blocks:
            block = block.strip()
            if not block:
                continue
                
            lines = block.split('\n')
            concept_data = {}
            
            for line in lines:
                if line.startswith('CONCEPT:'):
                    concept_data['term'] = line.replace('CONCEPT:', '').strip()
                elif line.startswith('DEFINITION:'):
                    concept_data['definition'] = line.replace('DEFINITION:', '').strip()
                elif line.startswith('IMPORTANCE:'):
                    concept_data['importance'] = line.replace('IMPORTANCE:', '').strip()
            
            if all(key in concept_data for key in ['term', 'definition', 'importance']):
                concepts.append(KeyConcept(**concept_data))
        
        return concepts
    
    def _generate_chapters(
        self, video_info: VideoInfo, segments: List[TranscriptSegment], num_chapters: int
    ) -> List[Chapter]:
        """Generate logical chapters for the lecture."""
        # Calculate chapter duration
        total_duration = video_info.duration
        chapter_duration = total_duration / num_chapters
        
        chapters = []
        full_transcript = self._combine_transcript(segments)
        
        for i in range(num_chapters):
            start_time = i * chapter_duration
            end_time = min((i + 1) * chapter_duration, total_duration)
            
            # Get transcript segment for this chapter
            chapter_segments = [
                seg for seg in segments 
                if seg.start >= start_time and seg.start < end_time
            ]
            chapter_text = '\n'.join(seg.text for seg in chapter_segments)
            
            if not chapter_text.strip():
                continue
            
            prompt = f"""
            Create a chapter summary for this section of the lecture.
            
            Video: {video_info.title}
            Chapter {i+1} of {num_chapters}
            Time: {int(start_time//60)}:{int(start_time%60):02d} - {int(end_time//60)}:{int(end_time%60):02d}
            
            Provide:
            1. A descriptive chapter title
            2. A brief summary (2-3 sentences)
            3. 3-5 key points covered in this section
            
            Format:
            TITLE: [Chapter Title]
            SUMMARY: [Brief summary]
            KEY_POINTS:
            - [Point 1]
            - [Point 2]
            - [Point 3]
            
            Chapter Content:
            {chapter_text[:2000]}
            """
            
            try:
                response = self.model.generate_content(prompt)
                chapter = self._parse_chapter(response.text, start_time, end_time)
                if chapter:
                    chapters.append(chapter)
                    
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Chapter {i+1} generation failed: {e}")
                # Create a fallback chapter
                chapters.append(Chapter(
                    title=f"Chapter {i+1}",
                    start_time=start_time,
                    end_time=end_time,
                    summary="Content summary not available.",
                    key_points=["Key points not available."]
                ))
        
        return chapters
    
    def _parse_chapter(self, text: str, start_time: float, end_time: float) -> Optional[Chapter]:
        """Parse chapter information from AI response."""
        lines = text.split('\n')
        chapter_data = {
            'start_time': start_time,
            'end_time': end_time,
            'key_points': []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                chapter_data['title'] = line.replace('TITLE:', '').strip()
            elif line.startswith('SUMMARY:'):
                chapter_data['summary'] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('KEY_POINTS:'):
                current_section = 'key_points'
            elif line.startswith('- ') and current_section == 'key_points':
                chapter_data['key_points'].append(line.replace('- ', '').strip())
        
        if 'title' in chapter_data and 'summary' in chapter_data:
            return Chapter(**chapter_data)
        
        return None
    
    def _extract_main_topics(self, video_info: VideoInfo, transcript: str) -> List[str]:
        """Extract main topics from the lecture."""
        prompt = f"""
        Identify the main topics covered in this lecture.
        
        Video: {video_info.title}
        
        List the 5-8 most important topics in order of importance.
        Be concise - each topic should be 2-5 words.
        
        Transcript:
        {transcript[:6000]}
        
        Main Topics:
        """
        
        try:
            response = self.model.generate_content(prompt)
            topics = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove numbering if present
                    topic = re.sub(r'^\d+\.?\s*', '', line)
                    if topic:
                        topics.append(topic)
            return topics[:8]  # Limit to 8 topics
        except Exception as e:
            logger.error(f"Main topics extraction failed: {e}")
            return []
    
    def _generate_learning_objectives(self, video_info: VideoInfo, transcript: str) -> List[str]:
        """Generate learning objectives for the lecture."""
        prompt = f"""
        Based on this lecture content, create clear learning objectives.
        
        Video: {video_info.title}
        
        Generate 4-6 learning objectives that students should achieve after watching this lecture.
        Start each objective with an action verb (understand, explain, analyze, apply, etc.).
        
        Format: "Students will be able to..."
        
        Transcript:
        {transcript[:6000]}
        
        Learning Objectives:
        """
        
        try:
            response = self.model.generate_content(prompt)
            objectives = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and (line.startswith('Students will') or line.startswith('-')):
                    objective = line.replace('- ', '').strip()
                    objectives.append(objective)
            return objectives[:6]  # Limit to 6 objectives
        except Exception as e:
            logger.error(f"Learning objectives generation failed: {e}")
            return []
    
    def _generate_questions(self, video_info: VideoInfo, transcript: str) -> List[str]:
        """Generate review questions for the lecture."""
        prompt = f"""
        Create thoughtful review questions for this lecture.
        
        Video: {video_info.title}
        
        Generate 5-8 questions that test understanding of the key concepts.
        Mix different types: factual, conceptual, and application questions.
        
        Transcript:
        {transcript[:6000]}
        
        Review Questions:
        """
        
        try:
            response = self.model.generate_content(prompt)
            questions = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and ('?' in line):
                    # Remove numbering if present
                    question = re.sub(r'^\d+\.?\s*', '', line)
                    if question:
                        questions.append(question)
            return questions[:8]  # Limit to 8 questions
        except Exception as e:
            logger.error(f"Questions generation failed: {e}")
            return []
