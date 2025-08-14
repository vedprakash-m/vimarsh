"""
Content Acquisition Service for New Personality Content
Handles research, acquisition, and processing of source materials for 14 new personalities
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import requests
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

@dataclass
class ContentSource:
    """Represents a content source for a personality"""
    source_id: str
    personality_id: str
    title: str
    author: str
    source_type: str  # book, speech, letter, paper, collection
    domain: str
    url: str = ""
    file_path: str = ""
    file_size_mb: float = 0.0
    copyright_status: str = "public_domain"  # public_domain, fair_use, licensed
    authenticity_score: float = 95.0  # 0-100
    authority_level: str = "primary"  # primary, secondary, reference
    publication_info: Dict[str, Any] = None
    acquisition_notes: str = ""
    processing_status: str = "pending"  # pending, acquired, processed, failed
    created_at: str = ""
    processed_at: str = ""

    def __post_init__(self):
        if self.publication_info is None:
            self.publication_info = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

@dataclass
class ContentPlan:
    """Content acquisition plan for a personality"""
    personality_id: str
    domain: str
    sources: List[ContentSource]
    priority: int = 1
    estimated_tokens: int = 100000

@dataclass 
class ContentMetrics:
    """Content processing metrics"""
    total_sources: int = 0
    acquired_sources: int = 0
    processed_sources: int = 0
    total_chunks: int = 0
    total_size_mb: float = 0.0
    average_quality_score: float = 0.0
    processing_time_minutes: float = 0.0

class ContentAcquisitionService:
    """Service for acquiring and processing personality content"""
    
    def __init__(self, data_dir: str = "/Users/ved/Apps/vimarsh/data"):
        self.data_dir = Path(data_dir)
        self.sources_dir = self.data_dir / "sources"
        self.personality_sources_dir = self.sources_dir / "personalities"
        self.registry_file = self.sources_dir / "personality_content_registry.json"
        
        # Create directories if they don't exist
        self.personality_sources_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize content registry
        self.content_registry = self._load_registry()
        
        # Define new personality content plans
        self.personality_content_plans = self._initialize_content_plans()

    def _load_registry(self) -> Dict[str, Any]:
        """Load existing content registry or create new one"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load registry: {e}")
        
        return {
            "version": "2.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "personalities": {},
            "metrics": {
                "total_personalities": 0,
                "total_sources": 0,
                "total_chunks": 0,
                "total_size_mb": 0.0
            }
        }

    def _save_registry(self):
        """Save content registry to file"""
        try:
            self.content_registry["last_updated"] = datetime.now().isoformat()
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.content_registry, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Content registry saved to {self.registry_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save registry: {e}")

    def _initialize_content_plans(self) -> Dict[str, List[ContentSource]]:
        """Initialize content acquisition plans for 14 new personalities"""
        
        plans = {
            # LITERARY DOMAIN (2 personalities)
            "william_shakespeare": [
                ContentSource(
                    source_id="shakespeare_complete_works_pg",
                    personality_id="william_shakespeare",
                    title="The Complete Works of William Shakespeare",
                    author="William Shakespeare",
                    source_type="collection",
                    domain="literary",
                    url="https://www.gutenberg.org/files/100/100-h/100-h.htm",
                    authenticity_score=98.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "Project Gutenberg",
                        "edition": "Modern spelling edition - Single file",
                        "original_period": "1564-1616",
                        "works_included": "~39 plays, 154 sonnets, narrative poems",
                        "persona_strategy": "playwright_voice"
                    },
                    acquisition_notes="Complete works - preferred for unified corpus. Strategy: 'The Playwright' persona rather than character voices"
                ),
                ContentSource(
                    source_id="shakespeare_mit_collection",
                    personality_id="william_shakespeare",
                    title="Complete Works of William Shakespeare",
                    author="William Shakespeare", 
                    source_type="collection",
                    domain="literary",
                    url="http://shakespeare.mit.edu/",
                    authenticity_score=98.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "MIT",
                        "edition": "MIT Digital Shakespeare - Searchable",
                        "format": "Individual works with search capability"
                    },
                    acquisition_notes="MIT's comprehensive Shakespeare - supplementary source for cross-reference"
                ),
                ContentSource(
                    source_id="shakespeare_first_folio_1623",
                    personality_id="william_shakespeare",
                    title="First Folio (1623)",
                    author="William Shakespeare",
                    source_type="historical_collection",
                    domain="literary", 
                    url="https://archive.org/details/shk00001",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "Internet Archive",
                        "edition": "Facsimile of 1623 First Folio",
                        "historical_significance": "First collected edition",
                        "year": "1623"
                    },
                    acquisition_notes="Historical reference - original source facsimile for authenticity verification"
                )
            ],
            
            "rabindranath_tagore": [
                ContentSource(
                    source_id="tagore_gitanjali",
                    personality_id="rabindranath_tagore",
                    title="Gitanjali (Song Offerings)",
                    author="Rabindranath Tagore",
                    source_type="book",
                    domain="literary",
                    url="https://www.gutenberg.org/cache/epub/7164/pg7164-images.html",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "Project Gutenberg",
                        "original_year": "1912",
                        "nobel_prize": "Literature 1913",
                        "translation": "Author's own English translation",
                        "authenticity_note": "Self-translation means intentional international voice"
                    },
                    acquisition_notes="Nobel Prize-winning poetry - self-translated for global authenticity"
                ),
                ContentSource(
                    source_id="tagore_gardener_stray_birds",
                    personality_id="rabindranath_tagore",
                    title="The Gardener and Stray Birds Collections",
                    author="Rabindranath Tagore",
                    source_type="collection",
                    domain="literary",
                    url="https://onlinebooks.library.upenn.edu/webbin/book/lookupname?key=Tagore%2C%20Rabindranath%2C%201861%2D1941",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "University of Pennsylvania Digital Library",
                        "note": "Multiple collections by Tagore",
                        "translation": "Author's own English translations"
                    },
                    acquisition_notes="Additional poetry and philosophical works - author's international voice"
                ),
                ContentSource(
                    source_id="tagore_bichitra_archive",
                    personality_id="rabindranath_tagore",
                    title="Bichitra Digital Archive - Tagore Collection",
                    author="Rabindranath Tagore",
                    source_type="digital_archive",
                    domain="literary",
                    url="https://bichitra.jdvu.ac.in/",
                    authenticity_score=98.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "Jadavpur University",
                        "note": "Comprehensive digital archive of Tagore's works",
                        "languages": "Bengali and English"
                    },
                    acquisition_notes="Comprehensive archive - supplementary source for breadth"
                )
            ],
            
            # PHILOSOPHICAL DOMAIN (4 personalities)
            "socrates": [
                ContentSource(
                    source_id="plato_early_dialogues_jowett",
                    personality_id="socrates",
                    title="Plato's Early Dialogues (Complete - Jowett Translation)",
                    author="Plato",
                    source_type="dialogue_collection",
                    domain="philosophical",
                    url="https://www.gutenberg.org/files/29441/29441-h/29441-h.htm",
                    authenticity_score=95.0,
                    authority_level="primary",
                    publication_info={
                        "recorder": "Plato",
                        "translator": "Benjamin Jowett",
                        "period": "Early dialogues - most Socratic",
                        "context": "Socratic method and philosophy",
                        "dialogues_included": "Apology, Crito, Euthyphro, Meno, etc."
                    },
                    acquisition_notes="Primary source for Socratic philosophy - Jowett translation recommended for consistency"
                ),
                ContentSource(
                    source_id="xenophon_memorabilia_dakyns",
                    personality_id="socrates",
                    title="Xenophon's Memorabilia (Socratic Works)",
                    author="Xenophon",
                    source_type="biographical_work",
                    domain="philosophical",
                    url="https://www.gutenberg.org/ebooks/1177",
                    authenticity_score=90.0,
                    authority_level="primary",
                    publication_info={
                        "recorder": "Xenophon",
                        "translator": "H.G. Dakyns",
                        "context": "Practical, moral teacher view of Socrates",
                        "supplemental_works": "Apology, Oeconomicus"
                    },
                    acquisition_notes="Supplementary view - Xenophontic Socrates as practical moral teacher"
                ),
                ContentSource(
                    source_id="xenophon_apology_symposium",
                    personality_id="socrates", 
                    title="Xenophon's Apology and Symposium",
                    author="Xenophon",
                    source_type="dialogue",
                    domain="philosophical",
                    url="https://www.gutenberg.org/ebooks/1171",
                    authenticity_score=90.0,
                    authority_level="primary",
                    publication_info={
                        "recorder": "Xenophon",
                        "translator": "H.G. Dakyns",
                        "note": "Alternative account of Socrates' defense and social interactions"
                    },
                    acquisition_notes="Cross-reference with Plato's accounts for balanced persona"
                )
            ],
            
            "plato": [
                ContentSource(
                    source_id="plato_dialogues_complete_jowett",
                    personality_id="plato",
                    title="The Dialogues of Plato (Complete - Jowett Translation)",
                    author="Plato",
                    source_type="dialogue_collection",
                    domain="philosophical",
                    url="https://www.gutenberg.org/files/29441/29441-h/29441-h.htm",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "translator": "Benjamin Jowett",
                        "period_coverage": "Early, Middle, and Late dialogues",
                        "dialogues_included": "Republic, Phaedo, Symposium, Laws, Timaeus, etc.",
                        "philosophical_evolution": "Covers Plato's development over decades"
                    },
                    acquisition_notes="Complete dialogues - Jowett translation for consistency. Tag as early/middle/late for contextual responses"
                ),
                ContentSource(
                    source_id="plato_republic_archive",
                    personality_id="plato",
                    title="The Republic (Archive Edition)",
                    author="Plato",
                    source_type="dialogue",
                    domain="philosophical",
                    url="https://archive.org/details/a604578400platuoft",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "translator": "Jowett translation",
                        "period": "Middle dialogues - Plato's mature philosophy",
                        "subject": "Justice, ideal state, philosophy of forms"
                    },
                    acquisition_notes="The Republic - central work for understanding Plato's political and metaphysical philosophy"
                )
            ],
            
            "aristotle": [
                ContentSource(
                    source_id="aristotle_works_ross_oxford",
                    personality_id="aristotle",
                    title="The Works of Aristotle (W. D. Ross Oxford Edition)",
                    author="Aristotle",
                    source_type="complete_works",
                    domain="philosophical",
                    url="https://archive.org/details/worksofaristotle512aris",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "translator": "W. D. Ross and J. A. Smith",
                        "publisher": "Oxford - Revised Oxford Translation",
                        "coverage": "Complete works including logic, metaphysics, ethics, politics",
                        "note": "Recommended translation for terminological coherence"
                    },
                    acquisition_notes="Complete works - Ross translation maintains consistency across corpus"
                ),
                ContentSource(
                    source_id="aristotle_mit_classics",
                    personality_id="aristotle",
                    title="Aristotle Works Collection (MIT Classics)",
                    author="Aristotle",
                    source_type="digital_collection",
                    domain="philosophical",
                    url="https://classics.mit.edu/Browse/browse-Aristotle.html",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "MIT Classics",
                        "format": "Individual searchable works",
                        "works_included": "Nicomachean Ethics, Politics, Metaphysics, Poetics, Organon"
                    },
                    acquisition_notes="MIT digital collection - supplementary for individual work access"
                ),
                ContentSource(
                    source_id="aristotle_nicomachean_ethics_mit",
                    personality_id="aristotle",
                    title="Nicomachean Ethics",
                    author="Aristotle",
                    source_type="treatise",
                    domain="philosophical",
                    url="https://classics.mit.edu/Aristotle/nicomachaen.html",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "period": "4th century BCE",
                        "subject": "Ethics, virtue, happiness, moral philosophy",
                        "note": "Central work for understanding Aristotelian ethics"
                    },
                    acquisition_notes="Core ethical treatise - foundational for understanding Aristotle's moral philosophy"
                )
            ],
            
            # SCIENTIFIC DOMAIN (3 personalities)
            # SCIENTIFIC DOMAIN (3 personalities)
            "leonardo_da_vinci": [
                ContentSource(
                    source_id="leonardo_notebooks_richter_1888",
                    personality_id="leonardo_da_vinci",
                    title="The Notebooks of Leonardo Da Vinci — Complete",
                    author="Leonardo da Vinci",
                    source_type="personal_notebooks",
                    domain="scientific",
                    url="http://www.gutenberg.org/ebooks/5000",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "compiler": "Jean Paul Richter",
                        "compilation_year": "1888",
                        "content": "Multi-disciplinary notes covering anatomy, engineering, botany, geology, art, philosophy",
                        "writing_style": "Famous mirror writing (right-to-left)",
                        "organization": "Thematically organized by Richter"
                    },
                    acquisition_notes="Primary source - complete notebooks. Challenge: non-linear, multi-topic chunks require metadata tagging"
                ),
                ContentSource(
                    source_id="leonardo_codex_forster_vam",
                    personality_id="leonardo_da_vinci",
                    title="The Forster Codices (V&A Museum High-Resolution)",
                    author="Leonardo da Vinci",
                    source_type="manuscript_collection",
                    domain="scientific",
                    url="https://www.vam.ac.uk/articles/explore-leonardo-da-vinci-codex-forster-i#?c=0&m=0&s=0&cv=0&xywh=-888%2C-111%2C3250%2C2211",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "collection": "Victoria & Albert Museum",
                        "codices": "Forster I, II, III",
                        "format": "High-resolution digitized facsimiles",
                        "content": "Original manuscript pages"
                    },
                    acquisition_notes="Facsimile manuscripts - visual authenticity verification. Includes Codex I, II, III links"
                ),
                ContentSource(
                    source_id="leonardo_treatise_painting_pg",
                    personality_id="leonardo_da_vinci",
                    title="A Treatise on Painting",
                    author="Leonardo da Vinci",
                    source_type="treatise",
                    domain="scientific",
                    url="http://www.gutenberg.org/ebooks/46915",
                    authenticity_score=95.0,
                    authority_level="primary",
                    publication_info={
                        "subject": "Art theory and painting techniques",
                        "compilation": "Compiled from notebook entries"
                    },
                    acquisition_notes="Artistic and scientific methodology - shows Leonardo's systematic approach"
                )
            ],
            
            "archimedes": [
                ContentSource(
                    source_id="archimedes_works_heath_1897",
                    personality_id="archimedes",
                    title="The Works of Archimedes (T. L. Heath Translation)",
                    author="Archimedes",
                    source_type="mathematical_treatises",
                    domain="scientific",
                    url="https://en.wikisource.org/wiki/Author:Archimedes",
                    authenticity_score=95.0,
                    authority_level="primary",
                    publication_info={
                        "translator": "T. L. Heath",
                        "translation_year": "1897",
                        "period": "c. 287–c. 212 BCE",
                        "treatises_included": "On the Sphere and Cylinder, Measurement of a Circle, On Floating Bodies, On the Equilibrium of Planes",
                        "content_note": "Dense mathematical proofs, not narrative dialogue"
                    },
                    acquisition_notes="Primary mathematical works - AI should act as educator, using proofs for simplified explanations"
                ),
                ContentSource(
                    source_id="archimedes_pg_collection",
                    personality_id="archimedes",
                    title="The Works of Archimedes (Project Gutenberg)",
                    author="Archimedes",
                    source_type="biography_and_works",
                    domain="scientific",
                    url="https://www.gutenberg.org/ebooks/35550",
                    authenticity_score=95.0,
                    authority_level="primary",
                    publication_info={
                        "editor": "T. L. Heath",
                        "content": "Heath's biography and mathematical works",
                        "format": "Biographical context plus treatises"
                    },
                    acquisition_notes="Heath's comprehensive treatment - biography provides context for mathematical personality"
                ),
                ContentSource(
                    source_id="archimedes_palimpsest_digital",
                    personality_id="archimedes",
                    title="The Archimedes Palimpsest (Digital Project)",
                    author="Archimedes",
                    source_type="historical_manuscript",
                    domain="scientific",
                    url="http://www.digitalarchimedes.org/",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "discovery": "Rediscovered 'The Method of Mechanical Theorems'",
                        "historical_significance": "Lost work recovered through palimpsest analysis",
                        "content": "Mathematical methodology and mechanical insights"
                    },
                    acquisition_notes="Unique historical source - shows Archimedes' mathematical thinking process"
                )
            ],
            
            "sigmund_freud": [
                ContentSource(
                    source_id="freud_interpretation_of_dreams_brill",
                    personality_id="sigmund_freud",
                    title="The Interpretation of Dreams",
                    author="Sigmund Freud",
                    source_type="scientific_treatise",
                    domain="scientific",
                    url="http://www.gutenberg.org/ebooks/author/391",
                    authenticity_score=95.0,
                    authority_level="primary",
                    publication_info={
                        "translator": "A. A. Brill",
                        "original_year": "1900",
                        "field": "Psychoanalysis",
                        "translation_note": "Brill era - introduced Freud to Anglophone world"
                    },
                    acquisition_notes="Public domain Brill translation - reflects historical terminology that introduced Freud to English speakers"
                ),
                ContentSource(
                    source_id="freud_collection_project_gutenberg",
                    personality_id="sigmund_freud",
                    title="Freud Collection - Project Gutenberg",
                    author="Sigmund Freud",
                    source_type="collection",
                    domain="scientific",
                    url="http://www.gutenberg.org/ebooks/author/391",
                    authenticity_score=95.0,
                    authority_level="primary",
                    publication_info={
                        "translator": "A. A. Brill",
                        "collection_includes": "Psychopathology of Everyday Life, Three Essays on Sexuality, etc.",
                        "era": "Pre-Strachey translations"
                    },
                    acquisition_notes="Complete Freud collection in Brill translations - authentic historical introduction to psychoanalysis"
                ),
                ContentSource(
                    source_id="freud_papers_loc",
                    personality_id="sigmund_freud",
                    title="Sigmund Freud Papers - Library of Congress",
                    author="Sigmund Freud",
                    source_type="archival_collection",
                    domain="scientific",
                    url="https://www.loc.gov/collections/sigmund-freud-papers/",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "publisher": "Library of Congress",
                        "content": "Personal papers, correspondence, manuscripts",
                        "access": "Digital archive"
                    },
                    acquisition_notes="Official archival collection - supplements published works with personal insights"
                )
            ],
            
            # HISTORICAL DOMAIN (6 personalities)
            "benjamin_franklin": [
                ContentSource(
                    source_id="franklin_autobiography",
                    personality_id="benjamin_franklin",
                    title="The Autobiography of Benjamin Franklin",
                    author="Benjamin Franklin",
                    source_type="autobiography",
                    domain="historical",
                    url="https://www.gutenberg.org/files/20203/20203-0.txt",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "period": "1706-1790",
                        "context": "American founding father, scientist, diplomat"
                    }
                )
            ],
            
            "martin_luther_king_jr": [
                ContentSource(
                    source_id="mlk_stanford_papers",
                    personality_id="martin_luther_king_jr",
                    title="MLK Papers Project - Letters and Sermons",
                    author="Martin Luther King Jr.",
                    source_type="archival_collection",
                    domain="historical",
                    url="https://kinginstitute.stanford.edu/",
                    authenticity_score=95.0,
                    authority_level="primary",
                    copyright_status="fair_use",
                    publication_info={
                        "publisher": "Stanford Martin Luther King, Jr. Research and Education Institute",
                        "content": "Letters, sermons, drafts, and lesser-known speeches",
                        "copyright_note": "Famous works copyrighted until 2058 - using archival materials"
                    },
                    acquisition_notes="Copyright-conscious strategy: build on archival voice from lesser-known works"
                ),
                ContentSource(
                    source_id="mlk_king_center_archive",
                    personality_id="martin_luther_king_jr",
                    title="The King Center Digital Archive",
                    author="Martin Luther King Jr.",
                    source_type="digital_archive",
                    domain="historical",
                    url="https://thekingcenter.org/archive",
                    authenticity_score=95.0,
                    authority_level="primary",
                    copyright_status="fair_use",
                    publication_info={
                        "publisher": "The King Center",
                        "content": "Letters, speeches, official records",
                        "usage": "Fair use - short attributed excerpts"
                    },
                    acquisition_notes="Official archive - use sparingly under fair use doctrine"
                )
            ],
            
            "nelson_mandela": [
                ContentSource(
                    source_id="mandela_long_walk",
                    personality_id="nelson_mandela",
                    title="Long Walk to Freedom (Excerpts)",
                    author="Nelson Mandela",
                    source_type="autobiography",
                    domain="historical",
                    url="", # Note: Full book under copyright, will use speeches instead
                    authenticity_score=100.0,
                    authority_level="primary",
                    acquisition_notes="Use public domain speeches and statements"
                )
            ],
            
            "george_washington": [
                ContentSource(
                    source_id="washington_farewell_address",
                    personality_id="george_washington",
                    title="Washington's Farewell Address",
                    author="George Washington",
                    source_type="speech",
                    domain="historical",
                    url="https://www.gutenberg.org/files/41/41-0.txt",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "date": "September 19, 1796",
                        "context": "Presidential farewell address"
                    }
                )
            ],
            
            "gandhi": [
                ContentSource(
                    source_id="gandhi_autobiography",
                    personality_id="gandhi",
                    title="The Story of My Experiments with Truth",
                    author="Mahatma Gandhi", 
                    source_type="autobiography",
                    domain="historical",
                    url="https://www.gutenberg.org/files/4347/4347-0.txt",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "original_year": "1927",
                        "subject": "Non-violence, truth, independence movement"
                    }
                )
            ],
            
            "swami_vivekananda": [
                ContentSource(
                    source_id="vivekananda_complete_works",
                    personality_id="swami_vivekananda",
                    title="The Complete Works of Swami Vivekananda",
                    author="Swami Vivekananda",
                    source_type="collection",
                    domain="historical",
                    url="https://www.gutenberg.org/files/1571/1571-0.txt",
                    authenticity_score=100.0,
                    authority_level="primary",
                    publication_info={
                        "period": "1863-1902",
                        "subject": "Vedanta, yoga, spirituality, East-West dialogue"
                    }
                )
            ]
        }
        
        return plans

    async def acquire_content_for_personality(self, personality_id: str) -> Tuple[bool, str, ContentMetrics]:
        """Acquire all content sources for a specific personality"""
        if personality_id not in self.personality_content_plans:
            return False, f"No content plan found for {personality_id}", ContentMetrics()
        
        logger.info(f"🔍 Starting content acquisition for {personality_id}")
        start_time = time.time()
        
        sources = self.personality_content_plans[personality_id]
        personality_dir = self.personality_sources_dir / personality_id
        personality_dir.mkdir(exist_ok=True)
        
        metrics = ContentMetrics(total_sources=len(sources))
        acquired_sources = []
        errors = []
        
        for source in sources:
            try:
                success, message = await self._acquire_single_source(source, personality_dir)
                if success:
                    acquired_sources.append(source)
                    metrics.acquired_sources += 1
                    logger.info(f"✅ Acquired: {source.title}")
                else:
                    errors.append(f"{source.title}: {message}")
                    logger.warning(f"⚠️ Failed to acquire {source.title}: {message}")
                    
            except Exception as e:
                error_msg = f"{source.title}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"❌ Error acquiring {source.title}: {e}")
        
        # Update registry
        if personality_id not in self.content_registry["personalities"]:
            self.content_registry["personalities"][personality_id] = {
                "name": personality_id.replace("_", " ").title(),
                "domain": sources[0].domain if sources else "unknown",
                "sources": [],
                "metrics": {
                    "total_sources": 0,
                    "acquired_sources": 0,
                    "total_chunks": 0,
                    "total_size_mb": 0.0
                },
                "last_updated": datetime.now().isoformat()
            }
        
        # Update with acquired sources
        for source in acquired_sources:
            self.content_registry["personalities"][personality_id]["sources"].append(asdict(source))
        
        self.content_registry["personalities"][personality_id]["metrics"] = asdict(metrics)
        self._save_registry()
        
        # Calculate processing time
        processing_time = (time.time() - start_time) / 60
        metrics.processing_time_minutes = processing_time
        
        if errors:
            error_summary = "; ".join(errors[:3])  # Show first 3 errors
            if len(errors) > 3:
                error_summary += f" ... and {len(errors) - 3} more"
            return False, f"Partial success. Errors: {error_summary}", metrics
        
        return True, f"Successfully acquired {metrics.acquired_sources} sources", metrics

    async def _acquire_single_source(self, source: ContentSource, personality_dir: Path) -> Tuple[bool, str]:
        """Acquire a single content source"""
        if not source.url:
            # For sources without URLs, create placeholder files
            return self._create_placeholder_source(source, personality_dir)
        
        try:
            # Download content
            response = requests.get(source.url, timeout=30)
            response.raise_for_status()
            
            # Generate filename
            filename = f"{source.source_id}.txt"
            file_path = personality_dir / filename
            
            # Save content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Update source metadata
            source.file_path = str(file_path)
            source.file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            source.processing_status = "acquired"
            source.processed_at = datetime.now().isoformat()
            
            return True, "Successfully downloaded"
            
        except requests.RequestException as e:
            return False, f"Download failed: {str(e)}"
        except Exception as e:
            return False, f"Processing failed: {str(e)}"

    def _create_placeholder_source(self, source: ContentSource, personality_dir: Path) -> Tuple[bool, str]:
        """Create placeholder file for sources without direct URLs"""
        filename = f"{source.source_id}_placeholder.txt"
        file_path = personality_dir / filename
        
        placeholder_content = f"""# {source.title}
Author: {source.author}
Type: {source.source_type}
Domain: {source.domain}

[PLACEHOLDER CONTENT]

This is a placeholder for content that needs to be manually acquired.

Source Information:
- Authority Level: {source.authority_level}
- Authenticity Score: {source.authenticity_score}
- Copyright Status: {source.copyright_status}

Acquisition Notes:
{source.acquisition_notes}

Publication Info:
{json.dumps(source.publication_info, indent=2)}

TODO: 
1. Manually acquire content from authorized sources
2. Verify copyright compliance
3. Process and chunk content
4. Generate embeddings
"""
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            source.file_path = str(file_path)
            source.file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            source.processing_status = "placeholder_created"
            source.processed_at = datetime.now().isoformat()
            
            return True, "Placeholder created - manual acquisition required"
            
        except Exception as e:
            return False, f"Failed to create placeholder: {str(e)}"

    async def acquire_all_personality_content(self) -> Dict[str, Any]:
        """Acquire content for all 14 new personalities"""
        logger.info("🚀 Starting bulk content acquisition for all 14 new personalities")
        
        results = {}
        overall_metrics = ContentMetrics()
        
        for personality_id in self.personality_content_plans.keys():
            success, message, metrics = await self.acquire_content_for_personality(personality_id)
            
            results[personality_id] = {
                "success": success,
                "message": message,
                "metrics": asdict(metrics)
            }
            
            # Aggregate metrics
            overall_metrics.total_sources += metrics.total_sources
            overall_metrics.acquired_sources += metrics.acquired_sources
            overall_metrics.total_size_mb += metrics.total_size_mb
            overall_metrics.processing_time_minutes += metrics.processing_time_minutes
        
        # Update overall registry metrics
        self.content_registry["metrics"]["total_personalities"] = len(self.personality_content_plans)
        self.content_registry["metrics"]["total_sources"] = overall_metrics.total_sources
        self.content_registry["metrics"]["total_size_mb"] = overall_metrics.total_size_mb
        self._save_registry()
        
        summary = {
            "overall_success": overall_metrics.acquired_sources > 0,
            "personalities_processed": len(results),
            "overall_metrics": asdict(overall_metrics),
            "individual_results": results,
            "registry_file": str(self.registry_file)
        }
        
        logger.info(f"✅ Bulk acquisition complete: {overall_metrics.acquired_sources}/{overall_metrics.total_sources} sources acquired")
        return summary

    def get_personality_content_plan(self, personality_id: str) -> Optional[ContentPlan]:
        """Get content plan for a specific personality"""
        if personality_id not in self.personality_content_plans:
            return None
        
        sources = self.personality_content_plans[personality_id]
        if not sources:
            return None
        
        # Determine domain from personality ID
        domain_mapping = {
            "william_shakespeare": "Literary",
            "rabindranath_tagore": "Literary", 
            "socrates": "Philosophical",
            "plato": "Philosophical",
            "aristotle": "Philosophical",
            "leonardo_da_vinci": "Scientific",
            "archimedes": "Scientific",
            "sigmund_freud": "Scientific",
            "benjamin_franklin": "Historical",
            "martin_luther_king_jr": "Historical",
            "nelson_mandela": "Historical",
            "george_washington": "Historical",
            "gandhi": "Spiritual",
            "swami_vivekananda": "Spiritual"
        }
        
        domain = domain_mapping.get(personality_id, "Literary")
        
        return ContentPlan(
            personality_id=personality_id,
            domain=domain,
            sources=sources,
            priority=1,
            estimated_tokens=100000
        )

    async def get_overall_content_status(self) -> Dict[str, Any]:
        """Get overall content status for all personalities"""
        return {
            "status": "operational",
            "summary": {
                "total_personalities": len(self.personality_content_plans),
                "domains_covered": ["literary", "philosophical", "scientific", "historical", "spiritual"],
                "total_sources": sum(len(sources) for sources in self.personality_content_plans.values()),
                "authenticity_average": sum(
                    sum(source.authenticity_score for source in sources) / len(sources)
                    for sources in self.personality_content_plans.values()
                ) / len(self.personality_content_plans),
                "last_updated": datetime.now().isoformat()
            },
            "personalities": list(self.personality_content_plans.keys())
        }

    async def get_content_status(self, personality_id: str) -> Dict[str, Any]:
        """Get content status for a specific personality"""
        if personality_id not in self.personality_content_plans:
            return {
                "status": "not_found",
                "personality_id": personality_id,
                "message": "Personality not found in content plans"
            }
        
        sources = self.personality_content_plans[personality_id]
        
        status_info = {
            "status": "available",
            "personality_id": personality_id,
            "total_sources": len(sources),
            "sources_by_type": {},
            "processing_status": {
                "pending": 0,
                "acquired": 0,
                "processed": 0,
                "failed": 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
        # Count sources by type and status
        for source in sources:
            source_type = source.source_type
            if source_type not in status_info["sources_by_type"]:
                status_info["sources_by_type"][source_type] = 0
            status_info["sources_by_type"][source_type] += 1
            
            processing_status = source.processing_status
            if processing_status in status_info["processing_status"]:
                status_info["processing_status"][processing_status] += 1
        
        return status_info

    def get_acquisition_status(self) -> Dict[str, Any]:
        """Get current status of content acquisition"""
        return {
            "registry_info": {
                "version": self.content_registry.get("version", "unknown"),
                "last_updated": self.content_registry.get("last_updated", "never"),
                "personalities_count": len(self.content_registry.get("personalities", {}))
            },
            "overall_metrics": self.content_registry.get("metrics", {}),
            "personalities": {
                pid: {
                    "name": pdata.get("name", pid),
                    "domain": pdata.get("domain", "unknown"),
                    "sources_count": len(pdata.get("sources", [])),
                    "metrics": pdata.get("metrics", {}),
                    "last_updated": pdata.get("last_updated", "never")
                }
                for pid, pdata in self.content_registry.get("personalities", {}).items()
            }
        }
