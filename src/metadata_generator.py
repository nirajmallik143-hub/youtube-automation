"""Metadata Generator Module

Uses AI to generate titles, descriptions, and tags for videos
"""

import json
import logging
import random
from typing import Dict, List

logger = logging.getLogger(__name__)

class MetadataGenerator:
    """Generate AI-powered metadata for videos"""
    
    def __init__(self, config_file='config/config.json'):
        """Initialize metadata generator
        
        Args:
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.template_library = self._load_templates()
        
    def _load_config(self):
        """Load configuration"""
        with open('config/config.json') as f:
            return json.load(f)
            
    def _load_templates(self):
        """Load metadata templates"""
        try:
            with open('templates/metadata_templates.json') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Template file not found, using defaults")
            return self._get_default_templates()
            
    def generate_title(self, topic: str, video_type: str = 'educational') -> str:
        """Generate engaging video title
        
        Args:
            topic: Video topic/subject
            video_type: Type of video content
            
        Returns:
            Generated title
        """
        templates = self.template_library.get('title_templates', [])
        if templates:
            template = random.choice(templates)
            title = template.format(topic=topic)
        else:
            title = f"Learn About {topic} - Educational Animation"
            
        # Ensure within YouTube limit
        title = title[:100]
        logger.info(f"Generated title: {title}")
        return title
        
    def generate_description(self, topic: str, duration_minutes: int = 5) -> str:
        """Generate video description
        
        Args:
            topic: Video topic
            duration_minutes: Video duration
            
        Returns:
            Generated description
        """
        description = f"""Learn about {topic} in this educational animation!

⏱️ Duration: {duration_minutes} minutes
🎓 Subject: Educational
👥 Target Audience: Kids (8-14 years)

In this video, you'll discover:
- Key concepts about {topic}
- Interesting facts and examples
- Visual explanations

📚 Subscribe for more educational content!

#Education #Learning #Cartoon
        """
        
        return description[:5000]
        
    def generate_tags(self, topic: str, num_tags: int = 15) -> List[str]:
        """Generate relevant tags
        
        Args:
            topic: Video topic
            num_tags: Number of tags to generate
            
        Returns:
            List of tags
        """
        base_tags = [
            'educational',
            'cartoon',
            'learning',
            'animation',
            'kids',
            'education',
            'animated video',
            'explainer',
            'tutorial',
            'learn'
        ]
        
        topic_tags = [
            topic.lower(),
            f"how {topic.lower()} works",
            f"explain {topic.lower()}",
            f"{topic.lower()} for kids"
        ]
        
        all_tags = base_tags + topic_tags
        selected_tags = list(set(all_tags))[:num_tags]
        
        logger.info(f"Generated {len(selected_tags)} tags")
        return selected_tags
        
    def generate_full_metadata(self, topic: str, video_path: str = None) -> Dict:
        """Generate complete metadata for a video
        
        Args:
            topic: Video topic
            video_path: Optional path to video file
            
        Returns:
            Dictionary with title, description, tags
        """
        metadata = {
            'title': self.generate_title(topic),
            'description': self.generate_description(topic),
            'tags': self.generate_tags(topic),
            'category_id': '27',
            'topic': topic,
            'status': 'generated'
        }
        
        logger.info(f"Full metadata generated for topic: {topic}")
        return metadata
        
    def _get_default_templates(self):
        """Get default templates"""
        return {
            'title_templates': [
                'Learn About {topic} - Educational Animation',
                '{topic} Explained - Animated Guide',
                'How Does {topic} Work? - Educational Video',
                '{topic} for Kids - Learn in 5 Minutes',
                'Understanding {topic} - Cartoon Explanation'
            ]
        }


if __name__ == "__main__":
    generator = MetadataGenerator()
    
    # Example usage
    metadata = generator.generate_full_metadata("Black Holes")
    print(json.dumps(metadata, indent=2))
