"""
Admin API endpoints for Vector Database Management

Provides comprehensive admin panel functionality for managing the multi-personality
vector database, including migration, statistics, and maintenance operations.
"""

import logging
from azure.functions import HttpRequest, HttpResponse
import json
from datetime import datetime

from ..services.vector_database_service import VectorDatabaseService, PersonalityType, ContentType

logger = logging.getLogger(__name__)


class VectorDatabaseAdminAPI:
    """Admin API for vector database management"""
    
    def __init__(self):
        self.vector_db = VectorDatabaseService()
    
    async def handle_request(self, req: HttpRequest) -> HttpResponse:
        """Main request handler for vector database admin operations"""
        try:
            method = req.method
            route = req.route_params.get('operation', '')
            
            if method == 'GET':
                return await self._handle_get_request(route, req)
            elif method == 'POST':
                return await self._handle_post_request(route, req)
            elif method == 'DELETE':
                return await self._handle_delete_request(route, req)
            else:
                return HttpResponse(
                    json.dumps({"error": f"Method {method} not supported"}),
                    status_code=405,
                    headers={"Content-Type": "application/json"}
                )
                
        except Exception as e:
            logger.error(f"❌ Admin API error: {e}")
            return HttpResponse(
                json.dumps({"error": "Internal server error", "details": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _handle_get_request(self, route: str, req: HttpRequest) -> HttpResponse:
        """Handle GET requests for data retrieval"""
        
        if route == 'stats':
            return await self._get_database_stats()
        
        elif route == 'search':
            return await self._search_vectors(req)
        
        elif route == 'documents':
            return await self._list_documents(req)
        
        elif route == 'personalities':
            return await self._list_personalities()
        
        elif route == 'health':
            return await self._check_database_health()
        
        else:
            return HttpResponse(
                json.dumps({"error": f"Unknown GET route: {route}"}),
                status_code=404,
                headers={"Content-Type": "application/json"}
            )
    
    async def _handle_post_request(self, route: str, req: HttpRequest) -> HttpResponse:
        """Handle POST requests for data modification"""
        
        if route == 'migrate':
            return await self._migrate_database()
        
        elif route == 'generate-embeddings':
            return await self._generate_embeddings(req)
        
        elif route == 'cleanup':
            return await self._cleanup_database()
        
        elif route == 'reindex':
            return await self._reindex_database()
        
        elif route == 'bulk-import':
            return await self._bulk_import_documents(req)
        
        else:
            return HttpResponse(
                json.dumps({"error": f"Unknown POST route: {route}"}),
                status_code=404,
                headers={"Content-Type": "application/json"}
            )
    
    async def _handle_delete_request(self, route: str, req: HttpRequest) -> HttpResponse:
        """Handle DELETE requests for data removal"""
        
        if route == 'document':
            return await self._delete_document(req)
        
        elif route == 'personality':
            return await self._delete_personality_data(req)
        
        elif route == 'duplicates':
            return await self._remove_duplicates()
        
        else:
            return HttpResponse(
                json.dumps({"error": f"Unknown DELETE route: {route}"}),
                status_code=404,
                headers={"Content-Type": "application/json"}
            )
    
    async def _get_database_stats(self) -> HttpResponse:
        """Get comprehensive database statistics"""
        try:
            stats = await self.vector_db.get_database_stats()
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "stats": {
                        "total_documents": stats.total_documents,
                        "documents_by_personality": stats.documents_by_personality,
                        "documents_by_content_type": stats.documents_by_content_type,
                        "documents_by_source": stats.documents_by_source,
                        "avg_embedding_similarity": stats.avg_embedding_similarity,
                        "last_updated": stats.last_updated,
                        "storage_size_mb": stats.storage_size_mb,
                        "total_embeddings_generated": stats.total_embeddings_generated,
                        "failed_embeddings": stats.failed_embeddings,
                        "embedding_coverage": (
                            stats.total_embeddings_generated / stats.total_documents * 100
                            if stats.total_documents > 0 else 0
                        )
                    }
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _search_vectors(self, req: HttpRequest) -> HttpResponse:
        """Perform semantic search with admin-level details"""
        try:
            # Parse query parameters
            query = req.params.get('query', '')
            personality = req.params.get('personality')
            content_type = req.params.get('content_type')
            top_k = int(req.params.get('top_k', 10))
            min_relevance = float(req.params.get('min_relevance', 0.1))
            
            if not query:
                return HttpResponse(
                    json.dumps({"success": False, "error": "Query parameter required"}),
                    status_code=400,
                    headers={"Content-Type": "application/json"}
                )
            
            # Convert string parameters to enums
            personality_enum = PersonalityType(personality) if personality else None
            content_types = [ContentType(content_type)] if content_type else None
            
            # Perform search
            results = await self.vector_db.semantic_search(
                query=query,
                personality=personality_enum,
                content_types=content_types,
                top_k=top_k,
                min_relevance=min_relevance
            )
            
            # Format results for admin view
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.document.id,
                    "content": result.document.content[:200] + "..." if len(result.document.content) > 200 else result.document.content,
                    "full_content": result.document.content,
                    "personality": result.document.personality.value,
                    "content_type": result.document.content_type.value,
                    "source": result.document.source,
                    "title": result.document.title,
                    "citation": result.document.citation,
                    "relevance_score": result.relevance_score,
                    "personality_match": result.personality_match,
                    "content_type_match": result.content_type_match,
                    "created_at": result.document.created_at,
                    "metadata": result.document.metadata
                })
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "query": query,
                    "filters": {
                        "personality": personality,
                        "content_type": content_type,
                        "top_k": top_k,
                        "min_relevance": min_relevance
                    },
                    "results_count": len(formatted_results),
                    "results": formatted_results
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _migrate_database(self) -> HttpResponse:
        """Migrate from old database structure to multi-personality format"""
        try:
            logger.info("🔄 Starting database migration...")
            
            success = await self.vector_db.migrate_existing_data()
            
            if success:
                # Get updated stats
                stats = await self.vector_db.get_database_stats()
                
                return HttpResponse(
                    json.dumps({
                        "success": True,
                        "message": "Database migration completed successfully",
                        "migrated_documents": stats.total_documents,
                        "documents_by_personality": stats.documents_by_personality,
                        "timestamp": datetime.utcnow().isoformat()
                    }),
                    headers={"Content-Type": "application/json"}
                )
            else:
                return HttpResponse(
                    json.dumps({
                        "success": False,
                        "error": "Migration completed with some failures",
                        "message": "Check logs for details"
                    }),
                    status_code=207,  # Multi-status
                    headers={"Content-Type": "application/json"}
                )
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _generate_embeddings(self, req: HttpRequest) -> HttpResponse:
        """Generate embeddings for documents that don't have them"""
        try:
            # Parse request body for batch size
            batch_size = 10
            try:
                if req.get_body():
                    body = req.get_json()
                    batch_size = body.get('batch_size', 10)
            except Exception:
                pass  # Use default batch size
            
            logger.info(f"🤖 Starting embedding generation with batch size {batch_size}...")
            
            successful, failed = await self.vector_db.bulk_generate_embeddings(batch_size)
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Embedding generation completed",
                    "successful_embeddings": successful,
                    "failed_embeddings": failed,
                    "batch_size": batch_size,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _cleanup_database(self) -> HttpResponse:
        """Clean up database by removing duplicates and invalid entries"""
        try:
            logger.info("🧹 Starting database cleanup...")
            
            duplicates_removed = await self.vector_db.cleanup_duplicates()
            
            # Get updated stats
            stats = await self.vector_db.get_database_stats()
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Database cleanup completed",
                    "duplicates_removed": duplicates_removed,
                    "total_documents": stats.total_documents,
                    "storage_size_mb": stats.storage_size_mb,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Database cleanup failed: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _list_personalities(self) -> HttpResponse:
        """List all available personalities with their document counts"""
        try:
            stats = await self.vector_db.get_database_stats()
            
            personalities = []
            for personality_type in PersonalityType:
                count = stats.documents_by_personality.get(personality_type.value, 0)
                personalities.append({
                    "id": personality_type.value,
                    "name": personality_type.value.replace('_', ' ').title(),
                    "document_count": count,
                    "enabled": count > 0
                })
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "personalities": personalities,
                    "total_personalities": len(personalities),
                    "active_personalities": len([p for p in personalities if p["enabled"]])
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to list personalities: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _check_database_health(self) -> HttpResponse:
        """Check database health and connectivity"""
        try:
            # Basic connectivity check
            stats = await self.vector_db.get_database_stats()
            
            # Calculate health metrics
            embedding_coverage = (
                stats.total_embeddings_generated / stats.total_documents * 100
                if stats.total_documents > 0 else 0
            )
            
            health_status = "healthy"
            issues = []
            
            if embedding_coverage < 90:
                issues.append(f"Low embedding coverage: {embedding_coverage:.1f}%")
                health_status = "warning"
            
            if stats.failed_embeddings > stats.total_embeddings_generated * 0.1:
                issues.append(f"High embedding failure rate: {stats.failed_embeddings}")
                health_status = "critical"
            
            if stats.total_documents == 0:
                issues.append("No documents found in database")
                health_status = "critical"
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "health_status": health_status,
                    "database_connected": self.vector_db.container is not None,
                    "embedding_model_loaded": self.vector_db.embedding_model is not None,
                    "total_documents": stats.total_documents,
                    "embedding_coverage": embedding_coverage,
                    "storage_size_mb": stats.storage_size_mb,
                    "issues": issues,
                    "last_updated": stats.last_updated,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return HttpResponse(
                json.dumps({
                    "success": False,
                    "health_status": "critical",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
    
    async def _remove_duplicates(self) -> HttpResponse:
        """Remove duplicate documents from the database"""
        try:
            logger.info("🔄 Starting duplicate removal...")
            
            removed_count = await self.vector_db.cleanup_duplicates()
            
            return HttpResponse(
                json.dumps({
                    "success": True,
                    "message": "Duplicate removal completed",
                    "duplicates_removed": removed_count,
                    "timestamp": datetime.utcnow().isoformat()
                }),
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"❌ Duplicate removal failed: {e}")
            return HttpResponse(
                json.dumps({"success": False, "error": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )


# Global instance for Azure Functions
vector_db_admin = VectorDatabaseAdminAPI()
