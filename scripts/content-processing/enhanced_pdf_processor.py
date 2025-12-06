#!/usr/bin/env python3
"""
Enhanced PDF Processor for Uploaded Content
Process PDFs from intake/new folder, extract text, create chunks, and upload to Cosmos DB
Uses existing cosmos integration infrastructure
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import sys
import os
import hashlib
import time

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
except ImportError:
    print("⚠️ python-dotenv not available")

# Import PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Import Azure Cosmos DB
try:
    from azure.cosmos import CosmosClient
    from azure.cosmos.exceptions import CosmosResourceExistsError, CosmosHttpResponseError
    COSMOS_AVAILABLE = True
except ImportError:
    COSMOS_AVAILABLE = False

# Import embedding service
try:
    from services.gemini_embedding_service import get_gemini_embedding_service
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPDFProcessor:
    def __init__(self, intake_dir: str = "/Users/ved/Apps/vimarsh/intake/new"):
        self.intake_dir = Path(intake_dir)
        self.output_dir = Path("/Users/ved/Apps/vimarsh/data/sources/personalities")
        
        # Enhanced PDF mapping with personality info
        self.pdf_mapping = {
            "Gandhi-2015.170524.Hind-Swaraj-Or-Indian-Home-Rule_text.pdf": {
                "personality": "gandhi",
                "source_name": "Hind Swaraj - Indian Home Rule",
                "filename": "gandhi_hind_swaraj_home_rule.txt",
                "source": "Internet Archive - Alternative PDF",
                "domain": "political_philosophy",
                "source_type": "authenticated_public_domain"
            },
            "Mahatma-Gandhi-An-Autobiography.pdf": {
                "personality": "gandhi", 
                "source_name": "Story of My Experiments with Truth",
                "filename": "gandhi_autobiography_experiments_truth.txt",
                "source": "mkgandhi.org - Manual Download",
                "domain": "autobiography",
                "source_type": "authenticated_public_domain"
            },
            "TaoTeChing.pdf": {
                "personality": "lao_tzu",
                "source_name": "Tao Te Ching - J.H. McDonald Translation",
                "filename": "lao_tzu_tao_te_ching_mcdonald_1996.txt",
                "source": "Minnesota State University - Manual Download",
                "domain": "spiritual",
                "source_type": "authenticated_public_domain"
            },
            "Tesla - My Inventions and Other Works Jan.-Oct. 1919, Nikola Tesla.pdf": {
                "personality": "tesla",
                "source_name": "Tesla - My Inventions Extended Collection",
                "filename": "tesla_my_inventions_extended_collection.txt",
                "source": "Extended Tesla Collection",
                "domain": "scientific",
                "source_type": "authenticated_public_domain"
            },
            "Tesla -Electrical Experimenter Magazine 1919 Tesla & More.pdf": {
                "personality": "tesla",
                "source_name": "Tesla - Electrical Experimenter Magazine Extended",
                "filename": "tesla_electrical_experimenter_extended.txt",
                "source": "Electrical Experimenter Magazine Collection",
                "domain": "scientific",
                "source_type": "authenticated_public_domain"
            },
            "Tesla Articles Electrical Experimenter.pdf": {
                "personality": "tesla",
                "source_name": "Tesla Articles - Electrical Experimenter",
                "filename": "tesla_electrical_experimenter_articles.txt",
                "source": "Internet Archive - Alternative PDF",
                "domain": "scientific",
                "source_type": "authenticated_public_domain"
            },
            "nikola-tesla-papers.pdf": {
                "personality": "tesla",
                "source_name": "Tesla Papers - Smithsonian Collection",
                "filename": "tesla_papers_smithsonian.txt",
                "source": "Internet Archive - Alternative PDF",
                "domain": "scientific",
                "source_type": "authenticated_public_domain"
            },
            "teslainventions_1812.pdf": {
                "personality": "tesla",
                "source_name": "Tesla Inventions Historical Collection",
                "filename": "tesla_inventions_historical_1812.txt",
                "source": "Historical Tesla Collection",
                "domain": "scientific",
                "source_type": "authenticated_public_domain"
            }
        }
        
        # Initialize services
        self.cosmos_client = None
        self.container = None
        self.embedding_service = None
        
    def install_pdf_libraries(self):
        """Install required PDF processing libraries"""
        import subprocess
        try:
            logger.info("📦 Installing PDF processing libraries...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "pdfplumber"])
            logger.info("✅ PDF libraries installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install PDF libraries: {e}")
            return False
    
    def setup_cosmos_client(self) -> bool:
        """Setup Cosmos DB client and container"""
        if not COSMOS_AVAILABLE:
            logger.error("❌ Azure Cosmos DB SDK not installed!")
            return False
            
        try:
            connection_string = os.getenv('AZURE_COSMOS_CONNECTION_STRING')
            if not connection_string:
                logger.error("❌ AZURE_COSMOS_CONNECTION_STRING not found")
                return False
            
            self.cosmos_client = CosmosClient.from_connection_string(connection_string)
            database = self.cosmos_client.get_database_client('vimarsh-multi-personality')
            self.container = database.get_container_client('personality_vectors')
            
            logger.info("✅ Connected to Cosmos DB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Cosmos DB: {e}")
            return False
    
    def setup_embedding_service(self) -> bool:
        """Setup Gemini embedding service"""
        if not EMBEDDING_AVAILABLE:
            logger.warning("⚠️ Embedding service not available - chunks will not have embeddings")
            return False
            
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("❌ GEMINI_API_KEY not found")
                return False
                
            self.embedding_service = get_gemini_embedding_service()
            logger.info("✅ Gemini embedding service initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup embedding service: {e}")
            return False
    
    def extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (preferred method)"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"⚠️ Error extracting page {page_num + 1}: {e}")
                        continue
            return text
        except Exception as e:
            logger.error(f"❌ pdfplumber extraction failed: {e}")
            return ""
    
    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2 (fallback method)"""
        try:
            import PyPDF2
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        logger.warning(f"⚠️ Error extracting page {page_num + 1}: {e}")
                        continue
            return text
        except Exception as e:
            logger.error(f"❌ PyPDF2 extraction failed: {e}")
            return ""
    
    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using best available method"""
        logger.info(f"📄 Extracting text from {pdf_path.name}...")
        
        # Try pdfplumber first (better quality)
        text = self.extract_text_pdfplumber(pdf_path)
        
        # Fallback to PyPDF2 if pdfplumber fails
        if not text or len(text.strip()) < 100:
            logger.info("🔄 Trying PyPDF2 as fallback...")
            text = self.extract_text_pypdf2(pdf_path)
        
        if text and len(text.strip()) > 100:
            logger.info(f"✅ Extracted {len(text):,} characters from {pdf_path.name}")
            return text
        else:
            logger.error(f"❌ Failed to extract meaningful text from {pdf_path.name}")
            return ""
    
    def chunk_text(self, text: str, max_chunk_size: int = 800) -> List[str]:
        """Simple text chunking by sentences and paragraphs"""
        if not text:
            return []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would make chunk too long, start new chunk
            if len(current_chunk) + len(paragraph) + 2 > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        chunks = [chunk for chunk in chunks if len(chunk) > 50]
        
        return chunks
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using Gemini"""
        if not self.embedding_service:
            return None
            
        try:
            result = self.embedding_service.generate_embedding(
                text, 
                task_type="RETRIEVAL_DOCUMENT"
            )
            
            if result and result.embedding:
                return result.embedding
            else:
                logger.warning(f"⚠️ Embedding generation failed")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Embedding error: {e}")
            return None
    
    def create_chunk_document(self, chunk_text: str, chunk_index: int, mapping: Dict, 
                            total_chunks: int, embedding: Optional[List[float]]) -> Dict:
        """Create a document for Cosmos DB storage"""
        
        # Generate unique ID
        chunk_id = f"{mapping['personality']}_{mapping['source_name'].replace(' ', '_').lower()}_{chunk_index:04d}"
        chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
        final_id = f"{chunk_id}_{chunk_hash}"
        
        document = {
            "id": final_id,
            "personality": mapping["personality"],
            "content": chunk_text,
            "source": mapping["source_name"],
            "domain": mapping["domain"],
            "source_type": mapping["source_type"],
            "source_metadata": {
                "original_filename": mapping["filename"],
                "extraction_method": "pdf_processing",
                "chunk_index": chunk_index,
                "total_chunks": total_chunks
            },
            "integration_date": datetime.now().isoformat(),
            "document_type": "personality_content",
            "content_type": "foundational_text",
            "chunk_metadata": {
                "length": len(chunk_text),
                "word_count": len(chunk_text.split()),
                "processing_timestamp": datetime.now().isoformat()
            }
        }
        
        # Add embedding if available
        if embedding:
            document["embedding"] = embedding
            document["embedding_model"] = "gemini-embedding-001"
            document["embedding_dimensions"] = len(embedding)
            document["has_embedding"] = True
        else:
            document["has_embedding"] = False
        
        return document
    
    async def process_single_pdf(self, pdf_path: Path) -> Dict:
        """Process a single PDF file into chunks and upload to Cosmos DB"""
        pdf_name = pdf_path.name
        
        if pdf_name not in self.pdf_mapping:
            logger.warning(f"⚠️ Unknown PDF: {pdf_name} - skipping")
            return {"success": False, "reason": "Unknown PDF"}
        
        mapping = self.pdf_mapping[pdf_name]
        
        logger.info(f"\n🎯 Processing {pdf_name}")
        logger.info(f"📝 Source: {mapping['source_name']}")
        logger.info(f"👤 Personality: {mapping['personality']}")
        
        # Extract text from PDF
        text = self.extract_pdf_text(pdf_path)
        if not text:
            return {"success": False, "reason": "Text extraction failed"}
        
        # Create chunks
        chunks = self.chunk_text(text)
        if not chunks:
            return {"success": False, "reason": "No chunks created"}
        
        logger.info(f"🧩 Created {len(chunks)} chunks")
        
        # Process chunks and upload to Cosmos DB
        uploaded_count = 0
        failed_count = 0
        
        for i, chunk_text in enumerate(chunks):
            try:
                # Generate embedding
                embedding = await self.generate_embedding(chunk_text)
                
                # Create document
                document = self.create_chunk_document(
                    chunk_text, i, mapping, len(chunks), embedding
                )
                
                # Upload to Cosmos DB
                self.container.upsert_item(document)
                uploaded_count += 1
                
                if uploaded_count % 10 == 0:
                    logger.info(f"   ✅ Uploaded {uploaded_count}/{len(chunks)} chunks...")
                
                # Small delay to avoid overwhelming the service
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to upload chunk {i}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"✅ Completed {pdf_name}: {uploaded_count} uploaded, {failed_count} failed")
        
        return {
            "success": True,
            "pdf_name": pdf_name,
            "personality": mapping['personality'],
            "total_chunks": len(chunks),
            "uploaded_chunks": uploaded_count,
            "failed_chunks": failed_count,
            "text_length": len(text)
        }
    
    async def process_all_pdfs(self) -> Dict:
        """Process all PDFs in the intake directory"""
        logger.info("🚀 ENHANCED PDF PROCESSING WITH COSMOS DB INTEGRATION")
        logger.info("=" * 70)
        
        # Check dependencies
        if not PDF_AVAILABLE:
            if not self.install_pdf_libraries():
                return {"success": False, "reason": "Could not install PDF libraries"}
            
            # Reimport after installation
            try:
                import PyPDF2
                import pdfplumber
                # Successfully imported after installation
                logger.info("✅ PDF libraries now available")
            except ImportError:
                return {"success": False, "reason": "PDF libraries still not available"}
        
        # Setup services
        if not self.setup_cosmos_client():
            return {"success": False, "reason": "Cosmos DB setup failed"}
        
        embedding_available = self.setup_embedding_service()
        if not embedding_available:
            logger.warning("⚠️ Proceeding without embeddings")
        
        # Find PDF files
        pdf_files = list(self.intake_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning("⚠️ No PDF files found in intake/new directory")
            return {"success": False, "reason": "No PDF files found"}
        
        logger.info(f"📄 Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        results = []
        total_chunks = 0
        total_uploaded = 0
        
        for pdf_path in pdf_files:
            result = await self.process_single_pdf(pdf_path)
            results.append(result)
            
            if result["success"]:
                total_chunks += result["total_chunks"]
                total_uploaded += result["uploaded_chunks"]
        
        # Summary
        successful_pdfs = sum(1 for r in results if r["success"])
        
        logger.info(f"\n📊 PROCESSING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"📄 PDFs processed: {len(pdf_files)}")
        logger.info(f"✅ Successful: {successful_pdfs}")
        logger.info(f"🧩 Total chunks created: {total_chunks:,}")
        logger.info(f"📤 Total chunks uploaded: {total_uploaded:,}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"enhanced_pdf_processing_{timestamp}.json"
        
        summary_data = {
            'timestamp': timestamp,
            'total_pdfs': len(pdf_files),
            'successful_pdfs': successful_pdfs,
            'total_chunks_created': total_chunks,
            'total_chunks_uploaded': total_uploaded,
            'embedding_service_available': embedding_available,
            'processing_results': results
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        logger.info(f"📁 Detailed results saved to: {results_file}")
        
        return summary_data

async def main():
    """Main execution"""
    try:
        processor = EnhancedPDFProcessor()
        results = await processor.process_all_pdfs()
        
        if results.get("success", True):  # True if no explicit success field
            logger.info(f"\n🎉 PDF processing complete!")
            logger.info(f"📈 Uploaded {results.get('total_chunks_uploaded', 0):,} chunks to Cosmos DB")
        else:
            logger.error(f"❌ PDF processing failed: {results.get('reason', 'Unknown error')}")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Processing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
