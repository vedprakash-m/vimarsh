#!/usr/bin/env python3
"""
Process Uploaded PDFs from intake/new folder
Extract text, chunk content, and save to database with proper personality mapping
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PDF libraries not installed. Installing...")

# Import our chunking and database services
from data_processing.chunk_generator import ChunkGenerator
from services.cosmos_client import CosmosClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, intake_dir: str = "/Users/ved/Apps/vimarsh/intake/new"):
        self.intake_dir = Path(intake_dir)
        self.output_dir = Path("/Users/ved/Apps/vimarsh/data/sources/personalities")
        
        # Map PDF filenames to personalities and source info
        self.pdf_mapping = {
            "Gandhi-2015.170524.Hind-Swaraj-Or-Indian-Home-Rule_text.pdf": {
                "personality": "gandhi",
                "source_name": "Hind Swaraj - Indian Home Rule",
                "filename": "gandhi_hind_swaraj_home_rule.txt",
                "source": "Internet Archive - Alternative PDF"
            },
            "Mahatma-Gandhi-An-Autobiography.pdf": {
                "personality": "gandhi", 
                "source_name": "Story of My Experiments with Truth",
                "filename": "gandhi_autobiography_experiments_truth.txt",
                "source": "mkgandhi.org - Manual Download"
            },
            "TaoTeChing.pdf": {
                "personality": "lao_tzu",
                "source_name": "J.H. McDonald Translation (1996)",
                "filename": "lao_tzu_tao_te_ching_mcdonald_1996.txt",
                "source": "Minnesota State University - Manual Download"
            },
            "Tesla - My Inventions and Other Works Jan.-Oct. 1919, Nikola Tesla.pdf": {
                "personality": "tesla",
                "source_name": "Tesla - My Inventions Extended Collection",
                "filename": "tesla_my_inventions_extended_collection.txt",
                "source": "Extended Tesla Collection"
            },
            "Tesla -Electrical Experimenter Magazine 1919 Tesla & More.pdf": {
                "personality": "tesla",
                "source_name": "Tesla - Electrical Experimenter Magazine Extended",
                "filename": "tesla_electrical_experimenter_extended.txt",
                "source": "Electrical Experimenter Magazine Collection"
            },
            "Tesla Articles Electrical Experimenter.pdf": {
                "personality": "tesla",
                "source_name": "Tesla Articles - Electrical Experimenter",
                "filename": "tesla_electrical_experimenter_articles.txt",
                "source": "Internet Archive - Alternative PDF"
            },
            "nikola-tesla-papers.pdf": {
                "personality": "tesla",
                "source_name": "Tesla Papers - Smithsonian",
                "filename": "tesla_papers_smithsonian.txt",
                "source": "Internet Archive - Alternative PDF"
            },
            "teslainventions_1812.pdf": {
                "personality": "tesla",
                "source_name": "Tesla Inventions Historical Collection",
                "filename": "tesla_inventions_historical_1812.txt",
                "source": "Historical Tesla Collection"
            }
        }
        
        self.chunk_generator = ChunkGenerator()
        self.cosmos_client = None
    
    def install_pdf_libraries(self):
        """Install required PDF processing libraries"""
        import subprocess
        import sys
        
        try:
            logger.info("📦 Installing PDF processing libraries...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2", "pdfplumber"])
            logger.info("✅ PDF libraries installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install PDF libraries: {e}")
            return False
    
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
    
    def save_extracted_text(self, text: str, personality: str, filename: str) -> bool:
        """Save extracted text to personality directory"""
        try:
            personality_dir = self.output_dir / personality
            personality_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = personality_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            file_size = len(text) / 1024
            logger.info(f"💾 Saved {filename} ({file_size:.1f} KB) to {personality}/ directory")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving {filename}: {e}")
            return False
    
    async def process_single_pdf(self, pdf_path: Path) -> Dict:
        """Process a single PDF file"""
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
        
        # Save extracted text
        success = self.save_extracted_text(
            text, 
            mapping['personality'], 
            mapping['filename']
        )
        
        if not success:
            return {"success": False, "reason": "Text saving failed"}
        
        return {
            "success": True,
            "pdf_name": pdf_name,
            "personality": mapping['personality'],
            "filename": mapping['filename'],
            "source_name": mapping['source_name'],
            "text_length": len(text),
            "text_file": str(self.output_dir / mapping['personality'] / mapping['filename'])
        }
    
    async def chunk_and_upload_text(self, text_file_path: str, personality: str, source_name: str) -> Dict:
        """Chunk text and upload to Cosmos DB"""
        try:
            logger.info(f"🔄 Chunking and uploading {Path(text_file_path).name}...")
            
            # Initialize Cosmos client if not already done
            if not self.cosmos_client:
                self.cosmos_client = CosmosClient()
            
            # Generate chunks
            chunks = await self.chunk_generator.generate_chunks_from_file(
                text_file_path, 
                personality,
                source_name
            )
            
            if not chunks:
                return {"success": False, "reason": "No chunks generated"}
            
            # Upload chunks to database
            uploaded_count = 0
            for chunk in chunks:
                try:
                    await self.cosmos_client.store_chunk(chunk)
                    uploaded_count += 1
                except Exception as e:
                    logger.warning(f"⚠️ Failed to upload chunk: {e}")
                    continue
            
            logger.info(f"✅ Uploaded {uploaded_count}/{len(chunks)} chunks for {personality}")
            
            return {
                "success": True,
                "total_chunks": len(chunks),
                "uploaded_chunks": uploaded_count,
                "personality": personality,
                "source_name": source_name
            }
            
        except Exception as e:
            logger.error(f"❌ Error chunking/uploading {text_file_path}: {e}")
            return {"success": False, "reason": str(e)}
    
    async def process_all_pdfs(self) -> Dict:
        """Process all PDFs in the intake directory"""
        logger.info("🚀 PROCESSING UPLOADED PDFs")
        logger.info("=" * 60)
        
        # Check if PDF libraries are available
        if not PDF_AVAILABLE:
            if not self.install_pdf_libraries():
                return {"success": False, "reason": "Could not install PDF libraries"}
            
            # Try importing again
            try:
                import PyPDF2
                import pdfplumber
                global PDF_AVAILABLE
                PDF_AVAILABLE = True
            except ImportError:
                return {"success": False, "reason": "PDF libraries still not available"}
        
        # Find all PDF files
        pdf_files = list(self.intake_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning("⚠️ No PDF files found in intake/new directory")
            return {"success": False, "reason": "No PDF files found"}
        
        logger.info(f"📄 Found {len(pdf_files)} PDF files to process")
        
        results = []
        chunking_results = []
        
        # Process each PDF
        for pdf_path in pdf_files:
            result = await self.process_single_pdf(pdf_path)
            results.append(result)
            
            if result["success"]:
                # Chunk and upload the extracted text
                chunk_result = await self.chunk_and_upload_text(
                    result["text_file"],
                    result["personality"],
                    result["source_name"]
                )
                chunking_results.append(chunk_result)
        
        # Summary
        successful_extractions = sum(1 for r in results if r["success"])
        successful_uploads = sum(1 for r in chunking_results if r["success"])
        total_chunks = sum(r.get("uploaded_chunks", 0) for r in chunking_results if r["success"])
        
        logger.info(f"\n📊 PDF PROCESSING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"📄 PDFs processed: {len(pdf_files)}")
        logger.info(f"✅ Successful extractions: {successful_extractions}")
        logger.info(f"📤 Successful uploads: {successful_uploads}")
        logger.info(f"🧩 Total chunks uploaded: {total_chunks:,}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"pdf_processing_results_{timestamp}.json"
        
        summary_data = {
            'timestamp': timestamp,
            'total_pdfs': len(pdf_files),
            'successful_extractions': successful_extractions,
            'successful_uploads': successful_uploads,
            'total_chunks_uploaded': total_chunks,
            'extraction_results': results,
            'chunking_results': chunking_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        logger.info(f"📁 Detailed results saved to: {results_file}")
        
        return summary_data

async def main():
    """Main execution"""
    try:
        processor = PDFProcessor()
        results = await processor.process_all_pdfs()
        
        if results.get("success", True):  # True if no explicit success field
            logger.info(f"\n🎉 PDF processing complete!")
            logger.info(f"📈 Uploaded {results.get('total_chunks_uploaded', 0):,} chunks to database")
        else:
            logger.error(f"❌ PDF processing failed: {results.get('reason', 'Unknown error')}")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Processing interrupted by user")
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
