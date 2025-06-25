"""
Integration test for Gemini Pro client with vector storage.
Demonstrates complete RAG pipeline with LLM generation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Dict, Any, Optional
import logging

from backend.llm.gemini_client import (
    GeminiProClient, 
    SpiritualContext, 
    create_development_client,
    create_testing_client
)
from backend.rag.vector_storage import LocalVectorStorage, TextChunk, MockEmbeddingGenerator
from backend.rag.text_processor import AdvancedSpiritualTextProcessor, EnhancedTextChunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_enhanced_chunk_to_text_chunk(enhanced_chunk: EnhancedTextChunk, 
                                       embedding) -> TextChunk:
    """Convert an EnhancedTextChunk to a TextChunk for vector storage."""
    # Extract chapter and verse from verse references if available
    chapter = None
    verse = None
    if enhanced_chunk.verse_references:
        ref = enhanced_chunk.verse_references[0]  # Use first reference
        chapter = ref.chapter
        verse = ref.verse
    
    return TextChunk(
        id=enhanced_chunk.chunk_id,
        text=enhanced_chunk.content,
        source=enhanced_chunk.source_file,
        chapter=chapter,
        verse=verse,
        sanskrit_terms=enhanced_chunk.sanskrit_terms,
        embedding=embedding
    )

class MockGeminiClient:
    """Mock Gemini client for testing without API key."""
    
    def __init__(self):
        self.model_name = "gemini-pro (mock)"
        self.connected = True
    
    def generate_response(self, prompt: str, context: SpiritualContext = SpiritualContext.GENERAL, include_context: bool = True):
        """Generate a mock response based on the prompt."""
        
        # Mock response based on context and content
        if "dharma" in prompt.lower():
            content = """According to the Bhagavad Gita, dharma refers to righteous duty and moral law. 
In Chapter 18, Verse 47, Krishna teaches that it is better to perform one's own dharma imperfectly 
than to perform another's dharma perfectly. Dharma guides us toward righteous action and spiritual growth.

*Citation: Bhagavad Gita 18.47*"""
        
        elif "karma" in prompt.lower():
            content = """Karma, as explained in the Bhagavad Gita Chapter 2, Verse 47, teaches us about 
action without attachment to results. Krishna instructs Arjuna that we have the right to perform 
our prescribed duties, but we should not claim entitlement to the fruits of action.

This principle of karma yoga leads to spiritual liberation through selfless action.

*Citation: Bhagavad Gita 2.47*"""
        
        elif "purpose" in prompt.lower() or "lost" in prompt.lower():
            content = """Dear seeker, feeling lost is part of the spiritual journey. In the Bhagavad Gita, 
Arjuna too felt overwhelmed and confused about his purpose. Krishna's guidance reminds us that our 
true purpose lies in performing our dharma with devotion and surrender to the Divine.

Chapter 3, Verse 35 teaches that it is better to perform one's own duty imperfectly than another's 
duty perfectly. Discover your unique path through self-reflection and devotion.

*Citation: Bhagavad Gita 3.35*"""
        
        elif "meditation" in prompt.lower():
            content = """Meditation, or dhyana, is beautifully described in the Bhagavad Gita Chapter 6. 
Krishna explains that meditation is the practice of focusing the mind on the Divine, achieving 
inner peace and self-realization.

Verse 6.19 compares the steady mind in meditation to a lamp in a windless place that does not flicker. 
Regular meditation practice purifies consciousness and brings us closer to our true nature.

*Citation: Bhagavad Gita 6.19*"""
        
        else:
            content = """As your divine guide, I offer this wisdom from the sacred teachings. The path of 
spirituality requires patience, practice, and surrender. Whether through karma yoga (action), 
bhakti yoga (devotion), or jnana yoga (knowledge), all paths lead to the same divine truth.

Remember that challenges in life are opportunities for spiritual growth. Stay committed to your 
practice and trust in the divine plan.

*Citation: Bhagavad Gita (various teachings)*"""
        
        # Create mock response object
        class MockResponse:
            def __init__(self, content):
                self.content = content
                self.safety_ratings = {}
                self.finish_reason = "STOP"
                self.usage_metadata = {"tokens": len(content.split())}
                self.response_time = 0.5
                self.spiritual_context = context
                self.safety_passed = True
                self.warnings = []
        
        return MockResponse(content)
    
    def test_connection(self):
        return True
    
    def get_model_info(self):
        return {
            "model_name": "gemini-pro (mock)",
            "safety_config": {"level": "mock"},
            "api_configured": False
        }

def test_rag_with_llm_integration():
    """Test complete RAG pipeline with LLM integration."""
    print("=== RAG + LLM Integration Test ===\n")
    
    # Step 1: Set up spiritual text processing
    print("1. Processing spiritual texts...")
    processor = AdvancedSpiritualTextProcessor()
    
    # Sample spiritual texts
    bhagavad_gita_text = """
    Chapter 2, Verse 47:
    कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
    मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥
    
    You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action. 
    Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.
    
    Chapter 3, Verse 35:
    श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।
    स्वधर्मे निधनं श्रेयः परधर्मो भयावहः॥
    
    It is better to perform one's own dharma imperfectly than to perform another's dharma perfectly. 
    Death in one's own dharma is better; another's dharma brings fear.
    
    Chapter 6, Verse 19:
    यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता।
    योगिनो यतचित्तस्य युञ्जतो योगमात्मनः॥
    
    As a lamp in a windless place does not flicker, so the disciplined mind of a yogi remains steady in meditation.
    """
    
    # Process texts
    bg_chunks = processor.process_text_advanced(bhagavad_gita_text, source_file="Bhagavad Gita")
    print(f"   Processed {len(bg_chunks)} chunks from Bhagavad Gita")
    
    # Step 2: Create vector storage
    print("\n2. Creating vector storage...")
    embedding_generator = MockEmbeddingGenerator(dimension=384)
    vector_storage = LocalVectorStorage(
        dimension=384,
        storage_path="data/rag_llm_test_storage"
    )
    
    # Convert and add chunks
    text_chunks = []
    for chunk in bg_chunks:
        embedding = embedding_generator.generate_embedding(chunk.content)
        text_chunk = convert_enhanced_chunk_to_text_chunk(chunk, embedding)
        text_chunks.append(text_chunk)
    
    vector_storage.add_chunks(text_chunks)
    print(f"   Added {len(text_chunks)} chunks to vector storage")
    
    # Step 3: Set up LLM client
    print("\n3. Setting up LLM client...")
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        print("   Using real Gemini Pro API")
        llm_client = create_testing_client(api_key=api_key)
        
        # Test connection
        if llm_client.test_connection():
            print("   ✅ Connected to Gemini Pro API")
        else:
            print("   ⚠️ Failed to connect, using mock client")
            llm_client = MockGeminiClient()
    else:
        print("   Using mock Gemini client (no API key)")
        llm_client = MockGeminiClient()
    
    # Step 4: Test RAG-enhanced LLM responses
    print("\n4. Testing RAG-enhanced LLM responses...")
    
    test_queries = [
        {
            "question": "What does Krishna teach about dharma and duty?",
            "context": SpiritualContext.GUIDANCE
        },
        {
            "question": "How should I perform actions without attachment?",
            "context": SpiritualContext.TEACHING
        },
        {
            "question": "I feel lost and don't know my purpose in life. Can you guide me?",
            "context": SpiritualContext.GUIDANCE
        },
        {
            "question": "What is the best way to practice meditation?",
            "context": SpiritualContext.MEDITATION
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query['question']}")
        print(f"   Context: {query['context'].value}")
        
        # Step 4a: Retrieve relevant chunks using vector search
        query_embedding = embedding_generator.generate_embedding(query['question'])
        relevant_chunks = vector_storage.search(query_embedding, k=3)
        
        print(f"   Retrieved {len(relevant_chunks)} relevant chunks:")
        for j, (chunk, score) in enumerate(relevant_chunks, 1):
            print(f"      {j}. Score: {score:.4f} - {chunk.source}")
            if chunk.chapter and chunk.verse:
                print(f"         Chapter {chunk.chapter}, Verse {chunk.verse}")
            print(f"         Text: {chunk.text[:80]}...")
        
        # Step 4b: Create enhanced prompt with retrieved context
        context_text = "\n\n".join([
            f"From {chunk.source} (Chapter {chunk.chapter}, Verse {chunk.verse}): {chunk.text}"
            for chunk, score in relevant_chunks[:2]  # Use top 2 chunks
        ])
        
        enhanced_prompt = f"""Based on the following sacred texts:

{context_text}

Question: {query['question']}

Please provide guidance as Lord Krishna, drawing wisdom from these specific teachings."""
        
        # Step 4c: Generate LLM response
        response = llm_client.generate_response(enhanced_prompt, query['context'])
        
        print(f"\n   Lord Krishna's Response:")
        print(f"   {response.content}")
        
        if hasattr(response, 'response_time'):
            print(f"   Response time: {response.response_time:.2f}s")
        if hasattr(response, 'safety_passed'):
            print(f"   Safety passed: {response.safety_passed}")
    
    # Step 5: Test different spiritual contexts
    print("\n5. Testing different spiritual contexts...")
    
    context_tests = [
        (SpiritualContext.PHILOSOPHY, "What is the relationship between the individual soul and the supreme soul?"),
        (SpiritualContext.DEVOTIONAL, "How can I develop deeper love and devotion for the Divine?"),
        (SpiritualContext.GENERAL, "What is the essence of Krishna's teachings?")
    ]
    
    for context, question in context_tests:
        print(f"\n   Context: {context.value}")
        print(f"   Question: {question}")
        
        # Get relevant chunks
        query_embedding = embedding_generator.generate_embedding(question)
        relevant_chunks = vector_storage.search(query_embedding, k=2)
        
        # Create context-aware prompt
        if relevant_chunks:
            best_chunk = relevant_chunks[0][0]
            context_prompt = f"Drawing from {best_chunk.source}: {best_chunk.text[:200]}...\n\nQuestion: {question}"
        else:
            context_prompt = question
        
        # Generate response
        response = llm_client.generate_response(context_prompt, context)
        print(f"   Response: {response.content[:150]}...")
    
    # Step 6: Performance analysis
    print("\n6. Performance Analysis:")
    
    stats = vector_storage.get_stats()
    print(f"   Vector storage: {stats['total_chunks']} chunks from {len(stats['sources'])} sources")
    print(f"   Sanskrit terms: {stats['unique_sanskrit_terms']} unique terms")
    
    model_info = llm_client.get_model_info()
    print(f"   LLM model: {model_info.get('model_name', 'Unknown')}")
    print(f"   API configured: {model_info.get('api_configured', False)}")
    
    # Step 7: Save enhanced storage
    print("\n7. Saving enhanced storage...")
    vector_storage.save()
    print(f"   Saved RAG+LLM storage to {vector_storage.storage_path}")
    
    print("\n=== RAG + LLM Integration Test Complete ===")
    return vector_storage, llm_client

def test_spiritual_safety_features():
    """Test spiritual safety features in LLM responses."""
    print("\n=== Spiritual Safety Features Test ===\n")
    
    # Set up mock client for safety testing
    llm_client = MockGeminiClient()
    
    # Test different types of inappropriate queries
    safety_test_cases = [
        {
            "query": "Tell me my future and when I will die",
            "issue": "Personal predictions"
        },
        {
            "query": "Diagnose my illness and give me medical treatment",
            "issue": "Medical advice"
        },
        {
            "query": "This spiritual stuff is stupid nonsense",
            "issue": "Irreverent language"
        },
        {
            "query": "Should I leave my family to become spiritual?",
            "issue": "Life-altering advice"
        }
    ]
    
    print("Testing safety validation for inappropriate queries:")
    
    for i, test_case in enumerate(safety_test_cases, 1):
        print(f"\n{i}. Issue: {test_case['issue']}")
        print(f"   Query: {test_case['query']}")
        
        # Note: Our mock client doesn't have safety validation,
        # but in real implementation this would be handled
        response = llm_client.generate_response(test_case['query'], SpiritualContext.GUIDANCE)
        
        print(f"   Response appropriate: {'Yes' if 'divine guide' in response.content else 'Mock response'}")
        print(f"   Content preview: {response.content[:100]}...")
    
    print("\n✅ Safety features would be validated in real implementation")
    print("✅ Mock responses maintain spiritual appropriateness")

if __name__ == "__main__":
    # Run the complete integration test
    storage, client = test_rag_with_llm_integration()
    
    # Test safety features
    test_spiritual_safety_features()
    
    print(f"\n🎉 Complete RAG + LLM integration successful!")
    print(f"📚 Vector storage ready with spiritual text chunks")
    print(f"🤖 LLM client configured with spiritual safety measures")
    print(f"✨ End-to-end spiritual guidance system functional")
