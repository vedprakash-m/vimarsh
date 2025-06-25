"""
Data Ingestion Pipeline for Spiritual Texts

This module processes source spiritual texts and prepares them for the RAG pipeline,
maintaining proper verse boundaries, citations, and semantic coherence.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from dataclasses import dataclass
import json

# Import our text processor
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from rag.text_processor import AdvancedSpiritualTextProcessor, TextType, EnhancedTextChunk

logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocument:
    """Represents a processed spiritual document with metadata"""
    source_file: str
    text_type: TextType
    total_chunks: int
    chunks: List[EnhancedTextChunk]
    metadata: Dict[str, Any]
    processing_timestamp: str


class DataIngestionPipeline:
    """
    Main pipeline for ingesting and processing spiritual texts.
    
    Handles the complete flow from raw text files to processed chunks
    ready for vector embedding and storage.
    """
    
    def __init__(self, source_dir: str, output_dir: str):
        """
        Initialize the data ingestion pipeline.
        
        Args:
            source_dir: Directory containing source text files
            output_dir: Directory for processed output
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.processor = AdvancedSpiritualTextProcessor()
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DataIngestionPipeline initialized: {source_dir} -> {output_dir}")
    
    def determine_text_type(self, filename: str) -> TextType:
        """
        Determine the type of spiritual text from filename.
        
        Args:
            filename: Name of the source file
            
        Returns:
            Appropriate TextType enum value
        """
        filename_lower = filename.lower()
        
        if 'bhagavad' in filename_lower or 'gita' in filename_lower:
            return TextType.BHAGAVAD_GITA
        elif 'mahabharata' in filename_lower:
            return TextType.MAHABHARATA
        elif 'bhagavatam' in filename_lower or 'srimad' in filename_lower:
            return TextType.SRIMAD_BHAGAVATAM
        elif 'upanishad' in filename_lower:
            return TextType.UPANISHADS
        elif 'veda' in filename_lower:
            return TextType.VEDAS
        elif 'purana' in filename_lower:
            return TextType.PURANAS
        else:
            return TextType.UNKNOWN
    
    def clean_text(self, raw_text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            raw_text: Raw text from source file
            
        Returns:
            Cleaned and normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', raw_text)
        
        # Remove or standardize special characters
        text = text.replace('\r', '\n')
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Preserve verse numbers and chapter markers
        text = re.sub(r'(\d+\.\d+)', r'\n\1', text)  # Ensure verse numbers start new lines
        
        return text.strip()
    
    def process_file(self, file_path: Path) -> Optional[ProcessedDocument]:
        """
        Process a single source text file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ProcessedDocument with chunks and metadata, or None if processing fails
        """
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Read the source file
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # Determine text type
            text_type = self.determine_text_type(file_path.name)
            
            # Clean the text
            cleaned_text = self.clean_text(raw_text)
            
            # Process into chunks
            chunks = self.processor.process_text_advanced(cleaned_text, str(file_path))
            
            # Create processed document
            processed_doc = ProcessedDocument(
                source_file=str(file_path),
                text_type=text_type,
                total_chunks=len(chunks),
                chunks=chunks,
                metadata={
                    "file_size": len(raw_text),
                    "cleaned_size": len(cleaned_text),
                    "text_hash": hashlib.md5(cleaned_text.encode()).hexdigest(),
                    "processing_version": "1.0.0"
                },
                processing_timestamp=str(Path(file_path).stat().st_mtime)
            )
            
            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks created")
            return processed_doc
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {str(e)}")
            return None
    
    def save_processed_document(self, doc: ProcessedDocument) -> str:
        """
        Save processed document to output directory.
        
        Args:
            doc: ProcessedDocument to save
            
        Returns:
            Path to the saved file
        """
        # Create output filename
        source_name = Path(doc.source_file).stem
        output_file = self.output_dir / f"{source_name}_processed.json"
        
        # Convert to serializable format
        doc_dict = {
            "source_file": doc.source_file,
            "text_type": doc.text_type.value,
            "total_chunks": doc.total_chunks,
            "chunks": [chunk.to_dict() for chunk in doc.chunks],
            "metadata": doc.metadata,
            "processing_timestamp": doc.processing_timestamp
        }
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved processed document: {output_file}")
        return str(output_file)
    
    def process_all_sources(self) -> Dict[str, Any]:
        """
        Process all source files in the source directory.
        
        Returns:
            Summary of processing results
        """
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
        
        # Find all text files
        text_files = list(self.source_dir.glob("*.txt"))
        if not text_files:
            logger.warning(f"No .txt files found in {self.source_dir}")
            return {"processed": 0, "failed": 0, "files": []}
        
        processed_files = []
        failed_files = []
        
        # Process each file
        for file_path in text_files:
            processed_doc = self.process_file(file_path)
            
            if processed_doc:
                output_path = self.save_processed_document(processed_doc)
                processed_files.append({
                    "source": str(file_path),
                    "output": output_path,
                    "chunks": processed_doc.total_chunks,
                    "text_type": processed_doc.text_type.value
                })
            else:
                failed_files.append(str(file_path))
        
        # Create summary
        summary = {
            "processed": len(processed_files),
            "failed": len(failed_files),
            "total_chunks": sum(f["chunks"] for f in processed_files),
            "files": processed_files,
            "failed_files": failed_files,
            "output_directory": str(self.output_dir)
        }
        
        # Save summary
        summary_file = self.output_dir / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Processing complete: {summary['processed']} files, {summary['total_chunks']} chunks")
        return summary


def main():
    """Main function for running the data ingestion pipeline."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Define paths
    script_dir = Path(__file__).parent
    source_dir = script_dir.parent.parent / "data" / "sources"  # Go up to project root
    output_dir = script_dir.parent / "data" / "processed"
    
    # Create and run pipeline
    pipeline = DataIngestionPipeline(str(source_dir), str(output_dir))
    results = pipeline.process_all_sources()
    
    print("\n=== Data Ingestion Complete ===")
    print(f"Processed files: {results['processed']}")
    print(f"Failed files: {results['failed']}")
    print(f"Total chunks created: {results['total_chunks']}")
    print(f"Output directory: {results['output_directory']}")
    
    if results['files']:
        print("\nProcessed files:")
        for file_info in results['files']:
            print(f"  - {Path(file_info['source']).name}: {file_info['chunks']} chunks ({file_info['text_type']})")
    
    if results['failed_files']:
        print(f"\nFailed files: {results['failed_files']}")


if __name__ == "__main__":
    main()
