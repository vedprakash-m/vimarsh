"""
Onboarding Service for Vimarsh
Manages user onboarding state, quiz processing, and personality matching.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from azure.cosmos import CosmosClient, PartitionKey, exceptions

from .quiz_service import get_quiz_service

logger = logging.getLogger(__name__)


class OnboardingService:
    """Service for managing user onboarding flow"""
    
    CONTAINER_NAME = "onboarding_state"
    
    # Onboarding steps
    STEPS = ["welcome", "quiz", "result", "first_chat", "discovery", "complete"]
    
    # Status values
    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_SKIPPED = "skipped"
    
    def __init__(self):
        """Initialize onboarding service with Cosmos DB connection"""
        self.quiz_service = get_quiz_service()
        self.container = None
        self._init_cosmos_db()
    
    def _init_cosmos_db(self):
        """Initialize Cosmos DB connection"""
        try:
            cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT") or os.environ.get("COSMOS_DB_ENDPOINT")
            cosmos_key = os.environ.get("COSMOS_KEY") or os.environ.get("COSMOS_DB_KEY")
            cosmos_database = os.environ.get("AZURE_COSMOS_DATABASE_NAME", "vimarsh-multi-personality")
            
            if not cosmos_endpoint or not cosmos_key:
                logger.warning("⚠️ Cosmos DB credentials not found, onboarding will use in-memory storage")
                self.container = None
                self._memory_store: Dict[str, Dict] = {}
                return
            
            client = CosmosClient(cosmos_endpoint, cosmos_key)
            database = client.get_database_client(cosmos_database)
            
            # Create container if it doesn't exist
            try:
                self.container = database.create_container_if_not_exists(
                    id=self.CONTAINER_NAME,
                    partition_key=PartitionKey(path="/user_id"),
                    offer_throughput=400
                )
                logger.info(f"✅ Onboarding container '{self.CONTAINER_NAME}' ready")
            except exceptions.CosmosResourceExistsError:
                self.container = database.get_container_client(self.CONTAINER_NAME)
                logger.info(f"✅ Connected to existing onboarding container")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cosmos DB for onboarding: {e}")
            self.container = None
            self._memory_store = {}
    
    def _generate_id(self, user_id: str) -> str:
        """Generate document ID from user_id"""
        return f"onboarding_{user_id}"
    
    async def get_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current onboarding state for a user"""
        try:
            doc_id = self._generate_id(user_id)
            
            if self.container:
                try:
                    item = self.container.read_item(item=doc_id, partition_key=user_id)
                    return item
                except exceptions.CosmosResourceNotFoundError:
                    return None
            else:
                # In-memory fallback
                return self._memory_store.get(doc_id)
                
        except Exception as e:
            logger.error(f"❌ Error getting onboarding state: {e}")
            return None
    
    async def start_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Initialize onboarding for a new user"""
        try:
            # Check if already exists
            existing = await self.get_state(user_id)
            if existing:
                logger.info(f"📋 Returning existing onboarding state for {user_id}")
                return existing
            
            # Create new onboarding state
            doc_id = self._generate_id(user_id)
            now = datetime.now(timezone.utc).isoformat()
            
            state = {
                "id": doc_id,
                "user_id": user_id,
                "status": self.STATUS_IN_PROGRESS,
                "current_step": "welcome",
                "quiz_responses": [],
                "personality_match": None,
                "progress": {
                    "welcome_completed": False,
                    "quiz_completed": False,
                    "first_conversation_completed": False,
                    "feature_discovery_completed": False
                },
                "started_at": now,
                "completed_at": None,
                "time_spent_seconds": 0,
                "skipped": False,
                "skip_reason": None,
                "version": "1.0",
                "created_at": now,
                "updated_at": now
            }
            
            # Save to database
            if self.container:
                self.container.create_item(body=state)
            else:
                self._memory_store[doc_id] = state
            
            logger.info(f"🚀 Started onboarding for user {user_id}")
            return state
            
        except Exception as e:
            logger.error(f"❌ Error starting onboarding: {e}")
            raise
    
    async def submit_quiz_response(
        self, 
        user_id: str, 
        question_id: str, 
        selected_option: str
    ) -> Dict[str, Any]:
        """Submit a single quiz response"""
        try:
            state = await self.get_state(user_id)
            if not state:
                state = await self.start_onboarding(user_id)
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Find and update or add response
            quiz_responses = state.get("quiz_responses", [])
            found = False
            for resp in quiz_responses:
                if resp.get("question_id") == question_id:
                    resp["selected_option"] = selected_option
                    resp["answered_at"] = now
                    found = True
                    break
            
            if not found:
                # Get domain scores for this option
                question = self.quiz_service.get_question(question_id)
                option = self.quiz_service.get_option(question, selected_option) if question else None
                domain_scores = option.get("weights", {}) if option else {}
                
                quiz_responses.append({
                    "question_id": question_id,
                    "selected_option": selected_option,
                    "domain_scores": domain_scores,
                    "answered_at": now
                })
            
            # Update state
            state["quiz_responses"] = quiz_responses
            state["current_step"] = "quiz"
            state["updated_at"] = now
            
            # Check if quiz is complete
            total_questions = len(self.quiz_service.get_questions())
            if len(quiz_responses) >= total_questions:
                state["progress"]["quiz_completed"] = True
            
            # Save
            await self._save_state(state)
            
            return {
                "success": True,
                "responses_count": len(quiz_responses),
                "total_questions": total_questions,
                "quiz_complete": state["progress"]["quiz_completed"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error submitting quiz response: {e}")
            raise
    
    async def complete_quiz(self, user_id: str) -> Dict[str, Any]:
        """Complete quiz and calculate personality match"""
        try:
            state = await self.get_state(user_id)
            if not state:
                raise ValueError("No onboarding state found")
            
            quiz_responses = state.get("quiz_responses", [])
            
            # Validate responses
            is_valid, error = self.quiz_service.validate_responses(quiz_responses)
            if not is_valid:
                # Allow partial completion for better UX
                logger.warning(f"⚠️ Quiz validation: {error}")
            
            # Calculate personality match
            match_result = self.quiz_service.calculate_personality_match(quiz_responses)
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Update state
            state["personality_match"] = match_result
            state["current_step"] = "result"
            state["progress"]["quiz_completed"] = True
            state["progress"]["welcome_completed"] = True
            state["updated_at"] = now
            
            # Save
            await self._save_state(state)
            
            logger.info(f"🎯 Quiz completed for {user_id}: matched with {match_result['primary']}")
            
            return {
                "success": True,
                "match": match_result
            }
            
        except Exception as e:
            logger.error(f"❌ Error completing quiz: {e}")
            raise
    
    async def skip_onboarding(self, user_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Skip onboarding entirely"""
        try:
            state = await self.get_state(user_id)
            if not state:
                state = await self.start_onboarding(user_id)
            
            now = datetime.now(timezone.utc).isoformat()
            
            state["status"] = self.STATUS_SKIPPED
            state["skipped"] = True
            state["skip_reason"] = reason
            state["completed_at"] = now
            state["updated_at"] = now
            
            # Calculate time spent
            started = datetime.fromisoformat(state["started_at"].replace('Z', '+00:00'))
            ended = datetime.fromisoformat(now.replace('Z', '+00:00'))
            state["time_spent_seconds"] = int((ended - started).total_seconds())
            
            await self._save_state(state)
            
            logger.info(f"⏭️ Onboarding skipped for {user_id}: {reason}")
            
            return {"success": True, "status": "skipped"}
            
        except Exception as e:
            logger.error(f"❌ Error skipping onboarding: {e}")
            raise
    
    async def complete_step(self, user_id: str, step: str) -> Dict[str, Any]:
        """Mark a specific step as completed"""
        try:
            state = await self.get_state(user_id)
            if not state:
                raise ValueError("No onboarding state found")
            
            now = datetime.now(timezone.utc).isoformat()
            
            # Update progress based on step
            if step == "welcome":
                state["progress"]["welcome_completed"] = True
                state["current_step"] = "quiz"
            elif step == "quiz":
                state["progress"]["quiz_completed"] = True
                state["current_step"] = "result"
            elif step == "result":
                state["current_step"] = "first_chat"
            elif step == "first_chat":
                state["progress"]["first_conversation_completed"] = True
                state["current_step"] = "discovery"
            elif step == "discovery":
                state["progress"]["feature_discovery_completed"] = True
                state["current_step"] = "complete"
            
            state["updated_at"] = now
            await self._save_state(state)
            
            return {
                "success": True,
                "current_step": state["current_step"],
                "progress": state["progress"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error completing step: {e}")
            raise
    
    async def complete_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Mark onboarding as fully complete"""
        try:
            state = await self.get_state(user_id)
            if not state:
                raise ValueError("No onboarding state found")
            
            now = datetime.now(timezone.utc).isoformat()
            
            state["status"] = self.STATUS_COMPLETED
            state["current_step"] = "complete"
            state["completed_at"] = now
            state["updated_at"] = now
            
            # Mark all progress complete
            state["progress"]["welcome_completed"] = True
            state["progress"]["quiz_completed"] = True
            state["progress"]["first_conversation_completed"] = True
            state["progress"]["feature_discovery_completed"] = True
            
            # Calculate time spent
            started = datetime.fromisoformat(state["started_at"].replace('Z', '+00:00'))
            ended = datetime.fromisoformat(now.replace('Z', '+00:00'))
            state["time_spent_seconds"] = int((ended - started).total_seconds())
            
            await self._save_state(state)
            
            logger.info(f"✅ Onboarding completed for {user_id} in {state['time_spent_seconds']}s")
            
            return {
                "success": True,
                "status": "completed",
                "time_spent_seconds": state["time_spent_seconds"],
                "personality_match": state.get("personality_match")
            }
            
        except Exception as e:
            logger.error(f"❌ Error completing onboarding: {e}")
            raise
    
    async def _save_state(self, state: Dict[str, Any]) -> None:
        """Save state to database"""
        try:
            if self.container:
                self.container.upsert_item(body=state)
            else:
                self._memory_store[state["id"]] = state
        except Exception as e:
            logger.error(f"❌ Error saving onboarding state: {e}")
            raise
    
    def get_quiz_questions(self) -> List[Dict[str, Any]]:
        """Get all quiz questions"""
        return self.quiz_service.get_questions()


# Singleton instance
_onboarding_service = None

def get_onboarding_service() -> OnboardingService:
    """Get singleton onboarding service instance"""
    global _onboarding_service
    if _onboarding_service is None:
        _onboarding_service = OnboardingService()
    return _onboarding_service
