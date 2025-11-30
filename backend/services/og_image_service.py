"""
OG Image Service - Dynamic Social Preview Image Generation
Generates beautiful, domain-themed images for social sharing.

Uses SVG-based generation with personality portraits and wisdom quotes
for high-quality, fast-loading social preview images.
"""

import logging
import hashlib
import base64
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Domain(Enum):
    """Personality domain categories with visual themes."""
    SPIRITUAL = "spiritual"
    PHILOSOPHICAL = "philosophical"
    LEADERSHIP = "leadership"
    SCIENTIFIC = "scientific"
    LITERARY = "literary"
    PSYCHOLOGY = "psychology"


@dataclass
class DomainTheme:
    """Visual theme for each domain."""
    primary_color: str
    secondary_color: str
    gradient_start: str
    gradient_end: str
    accent_color: str
    icon: str


# Domain-specific color themes matching frontend Sacred Harmony design
DOMAIN_THEMES: Dict[str, DomainTheme] = {
    "spiritual": DomainTheme(
        primary_color="#FF9933",  # Sacred Saffron
        secondary_color="#1E3A5F",  # Krishna Blue
        gradient_start="#FF9933",
        gradient_end="#CC7A29",
        accent_color="#FFD700",  # Divine Gold
        icon="🙏"
    ),
    "philosophical": DomainTheme(
        primary_color="#4A5568",  # Sage Gray
        secondary_color="#2D3748",
        gradient_start="#4A5568",
        gradient_end="#2D3748",
        accent_color="#68D391",  # Wisdom Green
        icon="🔮"
    ),
    "leadership": DomainTheme(
        primary_color="#805AD5",  # Regal Purple
        secondary_color="#553C9A",
        gradient_start="#805AD5",
        gradient_end="#553C9A",
        accent_color="#F6E05E",  # Crown Gold
        icon="👑"
    ),
    "scientific": DomainTheme(
        primary_color="#3182CE",  # Cosmos Blue
        secondary_color="#2B6CB0",
        gradient_start="#3182CE",
        gradient_end="#2B6CB0",
        accent_color="#63B3ED",  # Star Light
        icon="⚛️"
    ),
    "literary": DomainTheme(
        primary_color="#D69E2E",  # Ink Gold
        secondary_color="#B7791F",
        gradient_start="#D69E2E",
        gradient_end="#B7791F",
        accent_color="#FBD38D",  # Parchment
        icon="📜"
    ),
    "psychology": DomainTheme(
        primary_color="#9F7AEA",  # Mind Purple
        secondary_color="#805AD5",
        gradient_start="#9F7AEA",
        gradient_end="#805AD5",
        accent_color="#E9D8FD",  # Thought Lavender
        icon="🧠"
    ),
}

# Personality display names and domains
PERSONALITY_INFO: Dict[str, Dict[str, str]] = {
    # Spiritual
    "krishna": {"name": "Lord Krishna", "domain": "spiritual", "title": "Divine Guide"},
    "buddha": {"name": "Buddha", "domain": "spiritual", "title": "The Awakened One"},
    "jesus": {"name": "Jesus Christ", "domain": "spiritual", "title": "Prince of Peace"},
    "rumi": {"name": "Rumi", "domain": "spiritual", "title": "Mystical Poet"},
    "vivekananda": {"name": "Swami Vivekananda", "domain": "spiritual", "title": "Spiritual Giant"},
    
    # Philosophical
    "marcus_aurelius": {"name": "Marcus Aurelius", "domain": "philosophical", "title": "Philosopher Emperor"},
    "lao_tzu": {"name": "Lao Tzu", "domain": "philosophical", "title": "Sage of the Tao"},
    "confucius": {"name": "Confucius", "domain": "philosophical", "title": "Master Teacher"},
    "aristotle": {"name": "Aristotle", "domain": "philosophical", "title": "The Philosopher"},
    "plato": {"name": "Plato", "domain": "philosophical", "title": "Father of Philosophy"},
    "socrates": {"name": "Socrates", "domain": "philosophical", "title": "Gadfly of Athens"},
    
    # Leadership
    "chanakya": {"name": "Chanakya", "domain": "leadership", "title": "Master Strategist"},
    "lincoln": {"name": "Abraham Lincoln", "domain": "leadership", "title": "The Great Emancipator"},
    "franklin": {"name": "Benjamin Franklin", "domain": "leadership", "title": "Founding Father"},
    "washington": {"name": "George Washington", "domain": "leadership", "title": "Father of the Nation"},
    "gandhi": {"name": "Mahatma Gandhi", "domain": "leadership", "title": "Father of Non-Violence"},
    "mlk": {"name": "Martin Luther King Jr.", "domain": "leadership", "title": "Dream Weaver"},
    
    # Scientific
    "einstein": {"name": "Albert Einstein", "domain": "scientific", "title": "Father of Relativity"},
    "newton": {"name": "Isaac Newton", "domain": "scientific", "title": "Father of Physics"},
    "tesla": {"name": "Nikola Tesla", "domain": "scientific", "title": "Master of Lightning"},
    "archimedes": {"name": "Archimedes", "domain": "scientific", "title": "The Geometer"},
    "davinci": {"name": "Leonardo da Vinci", "domain": "scientific", "title": "The Renaissance Man"},
    
    # Literary
    "tagore": {"name": "Rabindranath Tagore", "domain": "literary", "title": "Bard of Bengal"},
    "shakespeare": {"name": "William Shakespeare", "domain": "literary", "title": "The Bard"},
    
    # Psychology
    "freud": {"name": "Sigmund Freud", "domain": "psychology", "title": "Father of Psychoanalysis"},
}


class OGImageService:
    """Service for generating dynamic Open Graph images."""
    
    def __init__(self):
        self.width = 1200
        self.height = 630
        self.logger = logging.getLogger(__name__)
    
    def get_personality_info(self, personality: str) -> Dict[str, str]:
        """Get personality display info with fallback."""
        return PERSONALITY_INFO.get(
            personality.lower().replace(" ", "_"),
            {"name": personality.title(), "domain": "spiritual", "title": "Wisdom Guide"}
        )
    
    def get_domain_theme(self, domain: str) -> DomainTheme:
        """Get domain theme with fallback to spiritual."""
        return DOMAIN_THEMES.get(domain.lower(), DOMAIN_THEMES["spiritual"])
    
    def truncate_text(self, text: str, max_chars: int = 180) -> str:
        """Truncate text with ellipsis for display."""
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 3].rsplit(' ', 1)[0] + "..."
    
    def escape_xml(self, text: str) -> str:
        """Escape special characters for XML/SVG."""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))
    
    def wrap_text(self, text: str, max_chars_per_line: int = 45) -> list[str]:
        """Wrap text into multiple lines for SVG display."""
        words = text.split()
        lines: list[str] = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip() if current_line else word
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines[:4]  # Max 4 lines
    
    def generate_cache_key(self, wisdom_text: str, personality: str) -> str:
        """Generate a unique cache key for the image."""
        content = f"{wisdom_text}|{personality}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def generate_svg(
        self,
        wisdom_text: str,
        personality: str,
        citation: Optional[str] = None
    ) -> str:
        """
        Generate an SVG image for social sharing.
        
        Args:
            wisdom_text: The wisdom quote to display
            personality: The personality ID
            citation: Optional citation text
            
        Returns:
            SVG string
        """
        # Get personality and theme info
        info = self.get_personality_info(personality)
        theme = self.get_domain_theme(info["domain"])
        
        # Prepare text content
        escaped_wisdom = self.escape_xml(self.truncate_text(wisdom_text, 200))
        wisdom_lines = self.wrap_text(escaped_wisdom, 50)
        
        escaped_name = self.escape_xml(info["name"])
        escaped_title = self.escape_xml(info["title"])
        escaped_citation = self.escape_xml(citation or "")
        
        # Generate text elements for wisdom
        wisdom_text_elements = ""
        base_y = 280
        line_height = 38
        
        for i, line in enumerate(wisdom_lines):
            y_pos = base_y + (i * line_height)
            wisdom_text_elements += f'''
            <text x="600" y="{y_pos}" text-anchor="middle" 
                  font-family="Georgia, 'Times New Roman', serif" font-size="28"
                  fill="#FFFFFF" opacity="0.95">
                {line}
            </text>'''
        
        # Citation element
        citation_element = ""
        if escaped_citation:
            citation_y = base_y + (len(wisdom_lines) * line_height) + 20
            citation_element = f'''
            <text x="600" y="{citation_y}" text-anchor="middle" 
                  font-family="Georgia, 'Times New Roman', serif" font-size="16"
                  fill="{theme.accent_color}" font-style="italic" opacity="0.8">
                — {escaped_citation}
            </text>'''
        
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" 
     xmlns="http://www.w3.org/2000/svg">
    
    <!-- Background Gradient -->
    <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{theme.gradient_start}"/>
            <stop offset="100%" style="stop-color:{theme.gradient_end}"/>
        </linearGradient>
        <linearGradient id="overlayGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:rgba(0,0,0,0.1)"/>
            <stop offset="100%" style="stop-color:rgba(0,0,0,0.4)"/>
        </linearGradient>
        <!-- Decorative pattern -->
        <pattern id="diagonalHatch" patternUnits="userSpaceOnUse" width="10" height="10">
            <path d="M-1,1 l2,-2 M0,10 l10,-10 M9,11 l2,-2" 
                  stroke="{theme.accent_color}" stroke-width="0.5" opacity="0.1"/>
        </pattern>
    </defs>
    
    <!-- Main Background -->
    <rect width="{self.width}" height="{self.height}" fill="url(#bgGradient)"/>
    <rect width="{self.width}" height="{self.height}" fill="url(#overlayGradient)"/>
    <rect width="{self.width}" height="{self.height}" fill="url(#diagonalHatch)"/>
    
    <!-- Decorative Elements -->
    <circle cx="100" cy="100" r="200" fill="{theme.accent_color}" opacity="0.05"/>
    <circle cx="1100" cy="530" r="180" fill="{theme.accent_color}" opacity="0.05"/>
    
    <!-- Quote Mark -->
    <text x="100" y="200" font-family="Georgia, serif" font-size="200" 
          fill="{theme.accent_color}" opacity="0.15">❝</text>
    
    <!-- Domain Icon -->
    <text x="1100" y="100" font-size="60" opacity="0.5">{theme.icon}</text>
    
    <!-- Wisdom Text -->
    {wisdom_text_elements}
    
    <!-- Citation -->
    {citation_element}
    
    <!-- Personality Info Box -->
    <rect x="40" y="530" width="300" height="70" rx="10" ry="10" 
          fill="rgba(0,0,0,0.3)"/>
    <text x="60" y="565" font-family="'Helvetica Neue', Arial, sans-serif" 
          font-size="22" font-weight="bold" fill="#FFFFFF">
        {escaped_name}
    </text>
    <text x="60" y="588" font-family="'Helvetica Neue', Arial, sans-serif" 
          font-size="14" fill="{theme.accent_color}" opacity="0.9">
        {escaped_title}
    </text>
    
    <!-- Vimarsh Branding -->
    <rect x="860" y="540" width="300" height="50" rx="8" ry="8" 
          fill="rgba(0,0,0,0.4)"/>
    <text x="890" y="573" font-family="'Helvetica Neue', Arial, sans-serif" 
          font-size="20" font-weight="bold" fill="#FFFFFF">
        🙏 Vimarsh
    </text>
    <text x="1000" y="573" font-family="'Helvetica Neue', Arial, sans-serif" 
          font-size="14" fill="rgba(255,255,255,0.7)">
        Timeless Wisdom
    </text>
    
    <!-- Subtle border -->
    <rect x="10" y="10" width="{self.width - 20}" height="{self.height - 20}" 
          rx="15" ry="15" fill="none" stroke="{theme.accent_color}" 
          stroke-width="2" opacity="0.2"/>
</svg>'''
        
        return svg
    
    def generate_data_uri(
        self,
        wisdom_text: str,
        personality: str,
        citation: Optional[str] = None
    ) -> str:
        """
        Generate a data URI for the OG image.
        
        Args:
            wisdom_text: The wisdom quote
            personality: The personality ID
            citation: Optional citation text
            
        Returns:
            Data URI string for embedding in HTML
        """
        svg = self.generate_svg(wisdom_text, personality, citation)
        encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded}"
    
    def generate_og_image_url(
        self,
        share_id: str,
        base_url: str = "https://vimarsh.app"
    ) -> str:
        """
        Generate URL for the OG image endpoint.
        
        Args:
            share_id: The share ID for this wisdom
            base_url: Base URL of the application
            
        Returns:
            URL string for og:image meta tag
        """
        return f"{base_url}/api/og-image/{share_id}"
    
    def get_image_response(
        self,
        wisdom_text: str,
        personality: str,
        citation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate complete OG image response.
        
        Args:
            wisdom_text: The wisdom quote
            personality: The personality ID
            citation: Optional citation text
            
        Returns:
            Dict with SVG content and headers
        """
        try:
            svg = self.generate_svg(wisdom_text, personality, citation)
            cache_key = self.generate_cache_key(wisdom_text, personality)
            
            return {
                "content": svg,
                "content_type": "image/svg+xml",
                "headers": {
                    "Cache-Control": "public, max-age=86400",  # 24 hours
                    "ETag": f'"{cache_key}"',
                    "Content-Type": "image/svg+xml; charset=utf-8"
                },
                "success": True
            }
        except Exception as e:
            self.logger.error(f"❌ OG image generation error: {str(e)}")
            return {
                "content": None,
                "error": str(e),
                "success": False
            }


# Singleton instance
og_image_service = OGImageService()


def generate_og_image(
    wisdom_text: str,
    personality: str,
    citation: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate OG image.
    
    Args:
        wisdom_text: The wisdom quote to display
        personality: The personality ID
        citation: Optional citation text
        
    Returns:
        Dict with SVG content and metadata
    """
    return og_image_service.get_image_response(wisdom_text, personality, citation)
