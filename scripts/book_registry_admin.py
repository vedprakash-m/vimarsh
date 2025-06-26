#!/usr/bin/env python3
"""
Scripture Registry Admin Dashboard for Vimarsh
Web-based interface for managing spiritual scriptures registry
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Web framework imports
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_cors import CORS
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScriptureRegistryManager:
    """Manages the spiritual scriptures registry with admin functionality."""
    
    def __init__(self, base_dir: str):
        """Initialize the registry manager."""
        self.base_dir = Path(base_dir)
        self.sources_dir = self.base_dir / "data" / "sources"
        self.registry_file = self.sources_dir / "scriptures_registry.json"
        
    def load_registry(self) -> Dict[str, Any]:
        """Load the scriptures registry."""
        if not self.registry_file.exists():
            return self._create_empty_registry()
        
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            return self._create_empty_registry()
    
    def _create_empty_registry(self) -> Dict[str, Any]:
        """Create an empty registry structure."""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "scriptures": {},
            "planned_scriptures": [],
            "metadata_sources": {}
        }
    
    def save_registry(self, registry: Dict[str, Any]):
        """Save the scriptures registry."""
        registry["last_updated"] = datetime.now().isoformat()
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the registry."""
        registry = self.load_registry()
        scriptures = registry.get("scriptures", {})
        
        # Calculate statistics
        total_scriptures = len(scriptures)
        processed_scriptures = len([s for s in scriptures.values() if s.get("status") == "success"])
        vectorized_scriptures = len([s for s in scriptures.values() if s.get("embeddings_uploaded")])
        
        total_chapters = sum(s.get("chapters_processed", 0) for s in scriptures.values())
        total_verses = sum(s.get("verses_processed", 0) for s in scriptures.values())
        total_chunks = sum(s.get("chunks_created", 0) for s in scriptures.values())
        total_vectors = sum(s.get("vectors_count", 0) for s in scriptures.values())
        
        # Scripture status distribution
        status_counts = {}
        for scripture in scriptures.values():
            status = scripture.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Content type distribution
        content_types = {}
        for scripture in scriptures.values():
            scripture_type = scripture.get("type", "unknown")
            content_types[scripture_type] = content_types.get(scripture_type, 0) + 1
        
        return {
            "registry_info": {
                "version": registry.get("version"),
                "last_updated": registry.get("last_updated"),
                "registry_path": str(self.registry_file)
            },
            "statistics": {
                "total_scriptures": total_scriptures,
                "processed_scriptures": processed_scriptures,
                "vectorized_scriptures": vectorized_scriptures,
                "planned_scriptures": len(registry.get("planned_scriptures", [])),
                "total_chapters": total_chapters,
                "total_verses": total_verses,
                "total_chunks": total_chunks,
                "total_vectors": total_vectors
            },
            "distributions": {
                "status": status_counts,
                "content_types": content_types
            },
            "books": list(books.values()),
            "planned_books": registry.get("planned_books", [])
        }
    
    def add_planned_book(self, book_info: Dict[str, Any]) -> bool:
        """Add a new planned book to the registry."""
        try:
            registry = self.load_registry()
            
            # Validate required fields
            required_fields = ["title", "author", "book_id", "type"]
            for field in required_fields:
                if not book_info.get(field):
                    raise ValueError(f"Missing required field: {field}")
            
            # Check for duplicates
            if book_info["book_id"] in registry.get("books", {}):
                raise ValueError(f"Book {book_info['book_id']} already exists")
            
            planned_books = registry.get("planned_books", [])
            if any(b.get("book_id") == book_info["book_id"] for b in planned_books):
                raise ValueError(f"Book {book_info['book_id']} already planned")
            
            # Add metadata
            book_info.update({
                "added_date": datetime.now().isoformat(),
                "status": "planned",
                "priority": book_info.get("priority", "medium")
            })
            
            planned_books.append(book_info)
            registry["planned_books"] = planned_books
            
            self.save_registry(registry)
            logger.info(f"Added planned book: {book_info['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add planned book: {e}")
            raise
    
    def update_book_metadata(self, book_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for an existing book."""
        try:
            registry = self.load_registry()
            
            if book_id not in registry.get("books", {}):
                raise ValueError(f"Book {book_id} not found")
            
            # Update allowed metadata fields
            updatable_fields = [
                "description", "tags", "difficulty_level", "recommended_for",
                "web_sources", "metadata_enriched", "notes"
            ]
            
            for field in updatable_fields:
                if field in metadata:
                    registry["books"][book_id][field] = metadata[field]
            
            registry["books"][book_id]["metadata_updated"] = datetime.now().isoformat()
            
            self.save_registry(registry)
            logger.info(f"Updated metadata for book: {book_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update book metadata: {e}")
            raise
    
    def enrich_metadata_from_web(self, book_id: str, web_sources: List[str]) -> Dict[str, Any]:
        """
        Enrich book metadata from web sources.
        This is a placeholder for future web scraping functionality.
        """
        try:
            registry = self.load_registry()
            
            if book_id not in registry.get("books", {}):
                raise ValueError(f"Book {book_id} not found")
            
            enriched_data = {
                "web_sources": web_sources,
                "metadata_enriched": True,
                "enrichment_date": datetime.now().isoformat(),
                "enriched_fields": []
            }
            
            # Placeholder for actual web scraping
            # In a real implementation, this would:
            # 1. Scrape provided URLs
            # 2. Extract relevant metadata (descriptions, reviews, etc.)
            # 3. Clean and structure the data
            # 4. Update the book entry
            
            for url in web_sources:
                try:
                    # Validate URL
                    parsed = urlparse(url)
                    if not parsed.scheme or not parsed.netloc:
                        continue
                    
                    logger.info(f"Would scrape: {url}")
                    # TODO: Implement actual scraping
                    
                except Exception as e:
                    logger.warning(f"Invalid URL {url}: {e}")
            
            # Update registry
            registry["books"][book_id].update(enriched_data)
            self.save_registry(registry)
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Failed to enrich metadata for {book_id}: {e}")
            raise

# Flask application
app = Flask(__name__)
app.secret_key = "vimarsh_admin_secret_key"  # Change in production
CORS(app)

# Initialize registry manager
base_dir = os.getenv("VIMARSH_BASE_DIR", "/Users/vedprakashmishra/vimarsh")
registry_manager = BookRegistryManager(base_dir)

@app.route('/')
def dashboard():
    """Main dashboard view."""
    try:
        summary = registry_manager.get_registry_summary()
        return render_template('dashboard.html', summary=summary)
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "error")
        return render_template('error.html', error=str(e))

@app.route('/api/registry/summary')
def api_registry_summary():
    """API endpoint for registry summary."""
    try:
        summary = registry_manager.get_registry_summary()
        return jsonify({"success": True, "data": summary})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/books', methods=['GET'])
def api_get_books():
    """Get all books with optional filtering."""
    try:
        summary = registry_manager.get_registry_summary()
        
        # Optional filtering
        status_filter = request.args.get('status')
        book_type_filter = request.args.get('type')
        
        books = summary['books']
        
        if status_filter:
            books = [b for b in books if b.get('status') == status_filter]
        
        if book_type_filter:
            books = [b for b in books if b.get('type') == book_type_filter]
        
        return jsonify({"success": True, "data": books})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/books/planned', methods=['GET', 'POST'])
def api_planned_books():
    """Handle planned books."""
    if request.method == 'GET':
        try:
            summary = registry_manager.get_registry_summary()
            return jsonify({"success": True, "data": summary['planned_books']})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == 'POST':
        try:
            book_info = request.json
            if not book_info:
                return jsonify({"success": False, "error": "No data provided"}), 400
            
            registry_manager.add_planned_book(book_info)
            return jsonify({"success": True, "message": "Planned book added successfully"})
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/books/<book_id>/metadata', methods=['PUT'])
def api_update_book_metadata(book_id):
    """Update book metadata."""
    try:
        metadata = request.json
        if not metadata:
            return jsonify({"success": False, "error": "No metadata provided"}), 400
        
        registry_manager.update_book_metadata(book_id, metadata)
        return jsonify({"success": True, "message": "Metadata updated successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/books/<book_id>/enrich', methods=['POST'])
def api_enrich_metadata(book_id):
    """Enrich book metadata from web sources."""
    try:
        data = request.json
        web_sources = data.get('web_sources', [])
        
        if not web_sources:
            return jsonify({"success": False, "error": "No web sources provided"}), 400
        
        enriched_data = registry_manager.enrich_metadata_from_web(book_id, web_sources)
        return jsonify({"success": True, "data": enriched_data})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/books')
def books_view():
    """Books management view."""
    try:
        summary = registry_manager.get_registry_summary()
        return render_template('books.html', 
                             books=summary['books'], 
                             planned_books=summary['planned_books'])
    except Exception as e:
        flash(f"Error loading books: {e}", "error")
        return render_template('error.html', error=str(e))

@app.route('/books/<book_id>')
def book_detail(book_id):
    """Individual book detail view."""
    try:
        summary = registry_manager.get_registry_summary()
        book = None
        
        # Find book in processed books
        for b in summary['books']:
            if b.get('book_id') == book_id:
                book = b
                break
        
        # If not found, check planned books
        if not book:
            for b in summary['planned_books']:
                if b.get('book_id') == book_id:
                    book = b
                    break
        
        if not book:
            flash(f"Book {book_id} not found", "error")
            return redirect(url_for('books_view'))
        
        return render_template('book_detail.html', book=book)
        
    except Exception as e:
        flash(f"Error loading book details: {e}", "error")
        return render_template('error.html', error=str(e))

@app.route('/add-book')
def add_book_form():
    """Form to add a new planned book."""
    return render_template('add_book.html')

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "registry_path": str(registry_manager.registry_file),
        "registry_exists": registry_manager.registry_file.exists()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Book Registry Admin Dashboard on port {port}")
    logger.info(f"Registry file: {registry_manager.registry_file}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
