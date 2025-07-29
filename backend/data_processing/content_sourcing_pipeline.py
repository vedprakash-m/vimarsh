"""
Enhanced Content Sourcing Pipeline for Vimarsh Multi-Personality Platform
Based on Gemini's deep research report for authentic foundational texts.
Integrates with metadata management and existing data processing pipeline.
Enhanced with better error handling, retry logic, and quality validation.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib
import PyPDF2
from bs4 import BeautifulSoup
import json

# Import existing components with fallback
try:
    from metadata_manager import MetadataManager, EnhancedContentProcessor
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False

try:
    from sacred_text_loader import SacredTextEntry
    SACRED_TEXT_AVAILABLE = True
except ImportError:
    SACRED_TEXT_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ContentSource:
    """Represents a content source from the research report."""
    personality: str
    domain: str  # spiritual, scientific, historical, philosophical
    work_title: str
    edition_translation: str
    repository: str
    download_url: str
    format_type: str  # pdf, html, text
    authenticity_notes: str
    public_domain: bool = True
    priority: int = 1  # 1=highest, 3=lowest
    content_quality: str = "high"  # high, medium, low
    file_size_mb: Optional[float] = None
    estimated_chunks: Optional[int] = None
    
    @property
    def source_id(self) -> str:
        """Generate unique source identifier."""
        content = f"{self.personality}_{self.work_title}_{self.edition_translation}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    @property
    def filename(self) -> str:
        """Generate safe filename for downloaded content."""
        safe_name = "".join(c for c in f"{self.personality}_{self.work_title}" 
                           if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return f"{safe_name.replace(' ', '_')}.{self.format_type}"

class EnhancedContentSourcingPipeline:
    """Enhanced pipeline for downloading and processing content from research report sources."""
    
    def __init__(self, base_path: Path, max_retries: int = 3, delay_between_requests: float = 1.0):
        self.base_path = base_path
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.downloaded_content = {}
        self.processing_stats = {
            'downloaded': 0,
            'processed': 0,
            'failed': 0,
            'skipped': 0
        }
        self.session_timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
    
    def get_priority_sources(self) -> List[ContentSource]:
        """Returns priority content sources based on Gemini's research report.
        Note: Krishna content excluded as it's already loaded in the system."""
        return [
            # Spiritual Domain - High Priority (Krishna excluded - already loaded)
            ContentSource(
                personality="Buddha",
                domain="spiritual",
                work_title="Anguttara Nikaya Part I",
                edition_translation="Nyanaponika Thera & Bhikkhu Bodhi",
                repository="urbandharma.org",
                download_url="http://www.urbandharma.org/pdf1/wh155AnguttaraNikaya1.pdf",
                format_type="pdf",
                authenticity_notes="Free PDF download from Urban Dharma.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=800
            ),
            ContentSource(
                personality="Buddha",
                domain="spiritual",
                work_title="Anguttara Nikaya Part II",
                edition_translation="Nyanaponika Thera & Bhikkhu Bodhi",
                repository="urbandharma.org",
                download_url="http://www.urbandharma.org/pdf1/wh208AnguttaraNikaya2.pdf",
                format_type="pdf",
                authenticity_notes="Free PDF download from Urban Dharma.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=1000
            ),
            ContentSource(
                personality="Buddha",
                domain="spiritual",
                work_title="Anguttara Nikaya Part III",
                edition_translation="Nyanaponika Thera & Bhikkhu Bodhi",
                repository="urbandharma.org",
                download_url="http://www.urbandharma.org/pdf1/wh238AnguttaraNikaya3.pdf",
                format_type="pdf",
                authenticity_notes="Free PDF download from Urban Dharma.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=1200
            ),
            ContentSource(
                personality="Jesus Christ",
                domain="spiritual",
                work_title="King James Bible (Old Testament)",
                edition_translation="King James Version 1611",
                repository="christistheway.com",
                download_url="http://www.christistheway.com/pdfs/KJVold.pdf",
                format_type="pdf",
                authenticity_notes="Public domain. Direct PDF of Old Testament.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=2000
            ),
            ContentSource(
                personality="Rumi",
                domain="spiritual",
                work_title="Masnavi I Ma'navi",
                edition_translation="E. H. Whinfield (abridged translation, 1898)",
                repository="Internet Archive",
                download_url="https://archive.org/download/MaAarifEMathnawi/Ma-aarif-E-Mathnawi.pdf",
                format_type="pdf",
                authenticity_notes="Public domain. Complete translation by H.M. Akhta Ra.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=1500
            ),
            
            # Scientific Domain - High Priority
            ContentSource(
                personality="Einstein",
                domain="scientific",
                work_title="On the Electrodynamics of Moving Bodies",
                edition_translation="Original 1905 Paper (English)",
                repository="astro.puc.cl",
                download_url="https://www.astro.puc.cl/~rparra/tools/PAPERS/specrel.pdf",
                format_type="pdf",
                authenticity_notes="Direct PDF of the seminal special relativity paper.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=150
            ),
            ContentSource(
                personality="Einstein",
                domain="scientific",
                work_title="Relativity: The Special and General Theory",
                edition_translation="Translation by Robert W. Lawson",
                repository="Internet Archive",
                download_url="https://archive.org/download/bub_gb_3H46AAAAMAAJ/bub_gb_3H46AAAAMAAJ.pdf",
                format_type="pdf",
                authenticity_notes="Public domain. Complete popular exposition.",
                public_domain=True,
                priority=2,
                content_quality="high",
                estimated_chunks=400
            ),
            ContentSource(
                personality="Newton",
                domain="scientific",
                work_title="Principia Mathematica",
                edition_translation="Original Latin Edition",
                repository="Project Gutenberg",
                download_url="https://www.gutenberg.org/files/28233/28233-pdf.pdf",
                format_type="pdf",
                authenticity_notes="Public domain. Original Latin text.",
                public_domain=True,
                priority=2,
                content_quality="high",
                estimated_chunks=2000
            ),
            ContentSource(
                personality="Newton",
                domain="scientific",
                work_title="Opticks",
                edition_translation="Original English Edition",
                repository="Internet Archive",
                download_url="https://archive.org/download/optickstreatise00newta/optickstreatise00newta.pdf",
                format_type="pdf",
                authenticity_notes="Public domain. Original English work on optics.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=800
            ),
            ContentSource(
                personality="Tesla",
                domain="scientific",
                work_title="Tesla Papers and Lectures",
                edition_translation="Collected Works",
                repository="Smithsonian Libraries",
                download_url="https://library.si.edu/digital-library/book/nikolateslapape00tesl",
                format_type="pdf",
                authenticity_notes="Public domain (CC0 1.0). Comprehensive collection.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=600
            ),
            
            # Historical Domain
            ContentSource(
                personality="Lincoln",
                domain="historical",
                work_title="Complete Works of Abraham Lincoln",
                edition_translation="Edited by John G. Nicolay and John Hay",
                repository="Project Gutenberg",
                download_url="https://www.gutenberg.org/ebooks/3253",
                format_type="html",
                authenticity_notes="Public domain. Comprehensive collection of writings.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=1500
            ),
            ContentSource(
                personality="Chanakya",
                domain="historical",
                work_title="Arthashastra",
                edition_translation="R. Shamasastry (English translation)",
                repository="Sanskrit eBooks",
                download_url="https://ia802703.us.archive.org/13/items/Arthasastra_English_Translation/Arthashastra_of_Chanakya_-_English.pdf",
                format_type="pdf",
                authenticity_notes="Public domain. Complete English translation.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=1000
            ),
            ContentSource(
                personality="Confucius",
                domain="historical",
                work_title="The Analects",
                edition_translation="James Legge (translation)",
                repository="Project Gutenberg",
                download_url="http://www.gutenberg.org/ebooks/3330",
                format_type="html",
                authenticity_notes="Public domain. Classic translation with Chinese text.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=400
            ),
            
            # Philosophical Domain
            ContentSource(
                personality="Marcus Aurelius",
                domain="philosophical",
                work_title="Meditations",
                edition_translation="George W. Chrystal (translation)",
                repository="Project Gutenberg",
                download_url="http://www.gutenberg.org/ebooks/55317",
                format_type="html",
                authenticity_notes="Public domain. Multiple machine-readable formats available.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=300
            ),
            ContentSource(
                personality="Lao Tzu",
                domain="philosophical",
                work_title="Tao Te Ching",
                edition_translation="James Legge (translation)",
                repository="Project Gutenberg",
                download_url="http://www.gutenberg.org/ebooks/216",
                format_type="html",
                authenticity_notes="Public domain. Classic translation.",
                public_domain=True,
                priority=1,
                content_quality="high",
                estimated_chunks=200
            ),
            ContentSource(
                personality="Lao Tzu",
                domain="philosophical",
                work_title="Tao Te Ching (Alternative Translation)",
                edition_translation="J.H. McDonald (1996)",
                repository="Minnesota State University Faculty",
                download_url="https://faculty.mnsu.edu/scottgr/wp-content/uploads/sites/34/2014/08/TaoTeChing.pdf",
                format_type="pdf",
                authenticity_notes="Modern public domain translation.",
                public_domain=True,
                priority=2,
                content_quality="medium",
                estimated_chunks=180
            ),
        ]
    
    async def download_content_with_retry(self, source: ContentSource) -> Optional[str]:
        """Download content from a source with retry logic."""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🕉️ Downloading {source.personality}: {source.work_title} (attempt {attempt + 1})")
                
                if source.format_type == "pdf":
                    content = await self._download_pdf(source)
                elif source.format_type == "html":
                    content = await self._download_html(source)
                else:
                    content = await self._download_text(source)
                
                if content:
                    return content
                    
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed for {source.personality}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.delay_between_requests * (attempt + 1))
                    
        self.processing_stats['failed'] += 1
        return None

    async def _download_pdf(self, source: ContentSource) -> Optional[str]:
        """Download and extract text from PDF with enhanced error handling."""
        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            try:
                async with session.get(source.download_url) as response:
                    if response.status == 200:
                        pdf_content = await response.read()
                        
                        # Save PDF locally
                        pdf_path = self.base_path / source.filename
                        with open(pdf_path, 'wb') as f:
                            f.write(pdf_content)
                        
                        # Extract text with better error handling
                        try:
                            with open(pdf_path, 'rb') as f:
                                reader = PyPDF2.PdfReader(f)
                                text = ""
                                for page_num, page in enumerate(reader.pages):
                                    try:
                                        page_text = page.extract_text()
                                        if page_text.strip():  # Only add non-empty pages
                                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                                    except Exception as e:
                                        logger.warning(f"⚠️ Failed to extract text from page {page_num + 1}: {str(e)}")
                                        continue
                            
                            if text.strip():
                                self.processing_stats['downloaded'] += 1
                                logger.info(f"✅ Successfully extracted {len(text)} characters from {source.work_title}")
                                return text
                            else:
                                logger.error(f"❌ No text extracted from PDF: {source.work_title}")
                                return None
                                
                        except Exception as e:
                            logger.error(f"❌ PDF processing failed for {source.personality}: {str(e)}")
                            return None
                    else:
                        logger.error(f"❌ HTTP {response.status} for {source.download_url}")
                        return None
            except asyncio.TimeoutError:
                logger.error(f"❌ Timeout downloading {source.download_url}")
                return None
            except Exception as e:
                logger.error(f"❌ Network error downloading {source.download_url}: {str(e)}")
                return None

    async def _download_html(self, source: ContentSource) -> Optional[str]:
        """Download and extract text from HTML with enhanced processing."""
        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            try:
                async with session.get(source.download_url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Parse HTML and extract text
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Remove unwanted elements
                        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                            script.decompose()
                        
                        # Try to find main content area
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content'})
                        if main_content:
                            text = main_content.get_text()
                        else:
                            text = soup.get_text()
                        
                        # Clean up text
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Basic quality check
                        if len(text) > 1000:  # Minimum length check
                            self.processing_stats['downloaded'] += 1
                            logger.info(f"✅ Successfully extracted {len(text)} characters from {source.work_title}")
                            return text
                        else:
                            logger.warning(f"⚠️ Extracted text too short for {source.work_title}: {len(text)} chars")
                            return None
                    else:
                        logger.error(f"❌ HTTP {response.status} for {source.download_url}")
                        return None
            except Exception as e:
                logger.error(f"❌ Error downloading HTML {source.download_url}: {str(e)}")
                return None

    async def _download_text(self, source: ContentSource) -> Optional[str]:
        """Download plain text content."""
        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            try:
                async with session.get(source.download_url) as response:
                    if response.status == 200:
                        text = await response.text()
                        self.processing_stats['downloaded'] += 1
                        logger.info(f"✅ Successfully downloaded {len(text)} characters from {source.work_title}")
                        return text
                    else:
                        logger.error(f"❌ HTTP {response.status} for {source.download_url}")
                        return None
            except Exception as e:
                logger.error(f"❌ Error downloading text {source.download_url}: {str(e)}")
                return None

    def convert_to_sacred_text_entries(self, processed_content: Dict[str, Dict]) -> List[Dict]:
        """Convert processed content to SacredTextEntry format for integration."""
        entries = []
        
        for source_id, content_data in processed_content.items():
            # Split content into manageable chunks
            text = content_data['content']
            chunks = self._chunk_text(text, max_chunk_size=2000)
            
            for i, chunk in enumerate(chunks):
                if SACRED_TEXT_AVAILABLE:
                    # Use actual SacredTextEntry if available
                    from sacred_text_loader import SacredTextEntry
                    entry = SacredTextEntry(
                        id=f"sourced_{source_id}_{i}",
                        text=chunk,
                        source=content_data['work_title'],
                        spiritual_theme=content_data['domain'],
                        keywords=[content_data['personality'].lower()],
                        language="English"
                    )
                    entries.append(entry.to_dict())
                else:
                    # Create dict directly if SacredTextEntry not available
                    entry = {
                        "id": f"sourced_{source_id}_{i}",
                        "text": chunk,
                        "content": chunk,
                        "source": content_data['work_title'],
                        "spiritual_theme": content_data['domain'],
                        "keywords": [content_data['personality'].lower()],
                        "language": "English",
                        "personality": content_data['personality'],
                        "domain": content_data['domain'],
                        "source_metadata": content_data.get('source_metadata', {})
                    }
                    entries.append(entry)
        
        return entries

    def _chunk_text(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        """Split text into chunks for processing."""
        # Simple sentence-based chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 100]  # Filter very short chunks

    async def process_priority_sources(self, max_sources: Optional[int] = None) -> Dict[str, Dict]:
        """Process high-priority sources first."""
        sources = self.get_priority_sources()
        
        # Sort by priority
        sources.sort(key=lambda x: x.priority)
        
        if max_sources:
            sources = sources[:max_sources]
        
        logger.info(f"🚀 Processing {len(sources)} priority content sources")
        
        # Process in batches to avoid overwhelming servers
        batch_size = 3
        processed_content = {}
        
        for i in range(0, len(sources), batch_size):
            batch = sources[i:i + batch_size]
            logger.info(f"📦 Processing batch {i//batch_size + 1}: {[s.personality for s in batch]}")
            
            # Add delay between batches
            if i > 0:
                await asyncio.sleep(self.delay_between_requests * 2)
            
            tasks = [self.download_content_with_retry(source) for source in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source, result in zip(batch, results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Exception processing {source.personality}: {str(result)}")
                    continue
                    
                if result and len(result.strip()) > 500:  # Quality check
                    processed_content[source.source_id] = {
                        'personality': source.personality,
                        'domain': source.domain,
                        'work_title': source.work_title,
                        'content': result,
                        'source_metadata': {
                            'edition_translation': source.edition_translation,
                            'repository': source.repository,
                            'authenticity_notes': source.authenticity_notes,
                            'public_domain': source.public_domain,
                            'priority': source.priority,
                            'content_quality': source.content_quality,
                            'estimated_chunks': source.estimated_chunks
                        }
                    }
                    self.processing_stats['processed'] += 1
                    logger.info(f"✅ Successfully processed {source.personality}: {source.work_title}")
                else:
                    self.processing_stats['skipped'] += 1
                    logger.warning(f"⚠️ Skipped {source.personality}: {source.work_title} - insufficient content")
        
        logger.info(f"🎉 Content sourcing complete: {self.processing_stats}")
        return processed_content

# Usage example
async def main():
    """Example usage of the enhanced content sourcing pipeline."""
    pipeline = EnhancedContentSourcingPipeline(Path("./downloaded_content"))
    pipeline.base_path.mkdir(exist_ok=True)
    
    # Process priority sources with limit for testing
    content = await pipeline.process_priority_sources(max_sources=5)
    
    # Convert to format compatible with existing pipeline
    sacred_entries = pipeline.convert_to_sacred_text_entries(content)
    
    # Save processed content
    with open("sourced_content.json", "w", encoding="utf-8") as f:
        json.dump({
            "processed_content": content,
            "sacred_entries": sacred_entries,
            "processing_stats": pipeline.processing_stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 Downloaded and processed {len(content)} sources")
    print(f"📊 Statistics: {pipeline.processing_stats}")
    print(f"📚 Generated {len(sacred_entries)} text entries for database")

async def process_specific_personalities(personalities: List[str]):
    """Process content for specific personalities only."""
    pipeline = EnhancedContentSourcingPipeline(Path("./personality_content"))
    pipeline.base_path.mkdir(exist_ok=True)
    
    all_sources = pipeline.get_priority_sources()
    filtered_sources = [s for s in all_sources if s.personality in personalities]
    
    logger.info(f"🎯 Processing {len(filtered_sources)} sources for personalities: {personalities}")
    
    processed_content = {}
    for source in filtered_sources:
        content = await pipeline.download_content_with_retry(source)
        if content:
            processed_content[source.source_id] = {
                'personality': source.personality,
                'domain': source.domain,
                'work_title': source.work_title,
                'content': content,
                'source_metadata': {
                    'edition_translation': source.edition_translation,
                    'repository': source.repository,
                    'authenticity_notes': source.authenticity_notes,
                    'public_domain': source.public_domain
                }
            }
    
    return processed_content

def get_content_statistics():
    """Get statistics about available content sources."""
    pipeline = EnhancedContentSourcingPipeline(Path("./temp"))
    sources = pipeline.get_priority_sources()
    
    stats = {
        'total_sources': len(sources),
        'by_domain': {},
        'by_personality': {},
        'by_priority': {},
        'estimated_total_chunks': 0
    }
    
    for source in sources:
        # By domain
        stats['by_domain'][source.domain] = stats['by_domain'].get(source.domain, 0) + 1
        
        # By personality
        stats['by_personality'][source.personality] = stats['by_personality'].get(source.personality, 0) + 1
        
        # By priority
        stats['by_priority'][f"Priority {source.priority}"] = stats['by_priority'].get(f"Priority {source.priority}", 0) + 1
        
        # Estimated chunks
        if source.estimated_chunks:
            stats['estimated_total_chunks'] += source.estimated_chunks
    
    return stats

if __name__ == "__main__":
    # Run main processing
    asyncio.run(main())
    
    # Print statistics
    print("\n📈 Content Source Statistics:")
    stats = get_content_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
