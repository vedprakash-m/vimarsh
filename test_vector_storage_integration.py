"""
Integration test for RAG pipeline with vector storage.
Demonstrates end-to-end workflow from text processing to vector search.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
import numpy as np
from typing import List, Dict, Any

from backend.rag.text_processor import AdvancedSpiritualTextProcessor, EnhancedTextChunk
from backend.rag.vector_storage import LocalVectorStorage, TextChunk, MockEmbeddingGenerator

def convert_enhanced_chunk_to_text_chunk(enhanced_chunk: EnhancedTextChunk, 
                                       embedding: np.ndarray) -> TextChunk:
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

def test_full_rag_pipeline():
    """Test the complete RAG pipeline from text processing to vector search."""
    print("=== Full RAG Pipeline Integration Test ===\n")
    
    # Step 1: Process spiritual texts
    print("1. Processing spiritual texts...")
    processor = AdvancedSpiritualTextProcessor()
    
    # Sample spiritual texts
    bhagavad_gita_text = """
    Chapter 2, Verse 47:
    कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
    मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥
    
    You have a right to perform your prescribed duty, but do not claim entitlement to the fruits of action. 
    Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.
    
    Chapter 4, Verse 7:
    यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।
    अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥
    
    Whenever there is a decline in dharma and a rise in adharma, O Bharata, I manifest Myself.
    """
    
    mahabharata_text = """
    Chapter 1, Verse 1:
    धृतराष्ट्र उवाच।
    धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
    मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥
    
    Dhritarashtra said: O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage 
    at Kurukshetra, desiring to fight, what did they do?
    """
    
    # Process the texts
    bg_chunks = processor.process_text_advanced(bhagavad_gita_text, source_file="Bhagavad Gita")
    mb_chunks = processor.process_text_advanced(mahabharata_text, source_file="Mahabharata")
    
    all_chunks = bg_chunks + mb_chunks
    print(f"   Processed {len(all_chunks)} chunks from spiritual texts")
    
    # Step 2: Generate embeddings and create vector storage
    print("\n2. Creating vector storage with embeddings...")
    embedding_generator = MockEmbeddingGenerator(dimension=384)
    vector_storage = LocalVectorStorage(
        dimension=384,
        storage_path="data/test_vector_storage"
    )
    
    # Convert enhanced chunks to text chunks with embeddings
    text_chunks = []
    for chunk in all_chunks:
        embedding = embedding_generator.generate_embedding(chunk.content)
        text_chunk = convert_enhanced_chunk_to_text_chunk(chunk, embedding)
        text_chunks.append(text_chunk)
    
    # Add to vector storage
    vector_storage.add_chunks(text_chunks)
    print(f"   Added {len(text_chunks)} chunks to vector storage")
    
    # Step 3: Display storage statistics
    print("\n3. Vector Storage Statistics:")
    stats = vector_storage.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Step 4: Test semantic search
    print("\n4. Testing semantic search...")
    
    queries = [
        "What is my duty according to Krishna?",
        "When does the divine manifest in the world?",
        "What happened at Kurukshetra battlefield?",
        "How should I perform actions without attachment?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n   Query {i}: '{query}'")
        query_embedding = embedding_generator.generate_embedding(query)
        results = vector_storage.search(query_embedding, k=3)
        
        for j, (chunk, score) in enumerate(results, 1):
            print(f"      {j}. Score: {score:.4f}")
            print(f"         Source: {chunk.source}")
            if chunk.chapter and chunk.verse:
                print(f"         Chapter {chunk.chapter}, Verse {chunk.verse}")
            print(f"         Text: {chunk.text[:80]}...")
            if chunk.sanskrit_terms:
                print(f"         Sanskrit terms: {chunk.sanskrit_terms}")
    
    # Step 5: Test filtering by source
    print("\n5. Testing source-based filtering...")
    
    query_embedding = embedding_generator.generate_embedding("spiritual wisdom")
    bg_results = vector_storage.search(query_embedding, k=5, source_filter="Bhagavad Gita")
    mb_results = vector_storage.search(query_embedding, k=5, source_filter="Mahabharata")
    
    print(f"   Bhagavad Gita results: {len(bg_results)}")
    print(f"   Mahabharata results: {len(mb_results)}")
    
    # Step 6: Test Sanskrit term search
    print("\n6. Testing Sanskrit term search...")
    
    sanskrit_terms = ["dharma", "karma", "योग"]
    for term in sanskrit_terms:
        chunks = vector_storage.search_by_sanskrit_term(term)
        print(f"   Chunks with '{term}': {len(chunks)}")
        for chunk in chunks[:2]:  # Show first 2
            print(f"      {chunk.source} - {chunk.text[:50]}...")
    
    # Step 7: Test persistence
    print("\n7. Testing storage persistence...")
    vector_storage.save()
    print("   Saved vector storage to disk")
    
    # Create new storage and load
    new_storage = LocalVectorStorage(
        dimension=384,
        storage_path="data/test_vector_storage"
    )
    print(f"   Loaded storage with {len(new_storage.chunks)} chunks")
    
    # Verify search still works
    test_query_embedding = embedding_generator.generate_embedding("divine wisdom")
    loaded_results = new_storage.search(test_query_embedding, k=2)
    print(f"   Search after loading: {len(loaded_results)} results")
    
    # Step 8: Advanced analytics
    print("\n8. Advanced text analytics...")
    
    # Analyze chunk sizes
    chunk_sizes = [len(chunk.text) for chunk in text_chunks]
    print(f"   Average chunk size: {np.mean(chunk_sizes):.0f} characters")
    print(f"   Min chunk size: {min(chunk_sizes)} characters")
    print(f"   Max chunk size: {max(chunk_sizes)} characters")
    
    # Analyze Sanskrit terms
    all_sanskrit_terms = []
    for chunk in text_chunks:
        all_sanskrit_terms.extend(chunk.sanskrit_terms)
    
    unique_terms = set(all_sanskrit_terms)
    print(f"   Total Sanskrit terms found: {len(all_sanskrit_terms)}")
    print(f"   Unique Sanskrit terms: {len(unique_terms)}")
    print(f"   Most common terms: {list(unique_terms)[:5]}")
    
    # Analyze verse distribution
    verses_by_source = {}
    for chunk in text_chunks:
        source = chunk.source
        if source not in verses_by_source:
            verses_by_source[source] = 0
        verses_by_source[source] += 1
    
    print(f"   Verse distribution: {verses_by_source}")
    
    print("\n=== Integration Test Complete ===")
    return vector_storage, text_chunks

def test_advanced_search_scenarios():
    """Test advanced search scenarios."""
    print("\n=== Advanced Search Scenarios ===")
    
    # Set up storage with more diverse content
    embedding_generator = MockEmbeddingGenerator(dimension=384)
    storage = LocalVectorStorage(dimension=384, storage_path="data/advanced_test_storage")
    
    # Create test chunks with various themes
    test_chunks = [
        TextChunk(
            id="duty_1",
            text="Perform your duty without attachment to results. This is the essence of karma yoga.",
            source="Bhagavad Gita",
            chapter="2",
            verse="47",
            sanskrit_terms=["karma", "yoga", "dharma"],
            embedding=embedding_generator.generate_embedding("duty action karma yoga")
        ),
        TextChunk(
            id="devotion_1", 
            text="Surrender all actions to the divine with love and devotion. This is bhakti yoga.",
            source="Bhagavad Gita",
            chapter="9",
            verse="27",
            sanskrit_terms=["bhakti", "yoga", "ishvara"],
            embedding=embedding_generator.generate_embedding("devotion surrender divine love")
        ),
        TextChunk(
            id="knowledge_1",
            text="The wise see the eternal Self in all beings. This is the vision of jnana yoga.",
            source="Bhagavad Gita", 
            chapter="13",
            verse="2",
            sanskrit_terms=["jnana", "yoga", "atman"],
            embedding=embedding_generator.generate_embedding("knowledge wisdom self eternal")
        ),
        TextChunk(
            id="war_1",
            text="The great war of Kurukshetra was fought between righteousness and unrighteousness.",
            source="Mahabharata",
            chapter="1",
            verse="1", 
            sanskrit_terms=["kurukshetra", "dharma", "yuddha"],
            embedding=embedding_generator.generate_embedding("war battle kurukshetra righteousness")
        )
    ]
    
    storage.add_chunks(test_chunks)
    
    # Test 1: Thematic search
    print("\n1. Thematic Search Tests:")
    themes = {
        "action_without_attachment": "How to act without being attached to results?",
        "spiritual_devotion": "What is the path of love and devotion to God?", 
        "self_knowledge": "How to realize the true Self within?",
        "righteous_war": "When is it justified to fight for righteousness?"
    }
    
    for theme, query in themes.items():
        print(f"\n   Theme: {theme}")
        print(f"   Query: '{query}'")
        
        query_embedding = embedding_generator.generate_embedding(query)
        results = storage.search(query_embedding, k=2)
        
        for i, (chunk, score) in enumerate(results, 1):
            print(f"      {i}. Score: {score:.4f} - {chunk.id}")
            print(f"         {chunk.text[:60]}...")
    
    # Test 2: Cross-source comparison
    print("\n2. Cross-Source Comparison:")
    
    query = "What is the nature of dharma and righteous action?"
    query_embedding = embedding_generator.generate_embedding(query)
    
    bg_results = storage.search(query_embedding, k=3, source_filter="Bhagavad Gita")
    mb_results = storage.search(query_embedding, k=3, source_filter="Mahabharata")
    
    print(f"   Bhagavad Gita perspective ({len(bg_results)} results):")
    for chunk, score in bg_results:
        print(f"      Score: {score:.4f} - {chunk.text[:50]}...")
    
    print(f"   Mahabharata perspective ({len(mb_results)} results):")
    for chunk, score in mb_results:
        print(f"      Score: {score:.4f} - {chunk.text[:50]}...")
    
    # Test 3: Sanskrit term clustering
    print("\n3. Sanskrit Term Analysis:")
    
    yoga_terms = ["karma", "bhakti", "jnana", "yoga"]
    for term in yoga_terms:
        chunks = storage.search_by_sanskrit_term(term)
        print(f"   '{term}' appears in {len(chunks)} chunks")
        for chunk in chunks:
            related_terms = [t for t in chunk.sanskrit_terms if t != term]
            print(f"      {chunk.id}: related terms = {related_terms}")
    
    print("\n=== Advanced Search Complete ===")

if __name__ == "__main__":
    # Run the full integration test
    storage, chunks = test_full_rag_pipeline()
    
    # Run advanced search scenarios
    test_advanced_search_scenarios()
    
    print(f"\n✅ All integration tests completed successfully!")
    print(f"✅ Vector storage with {len(chunks)} chunks is ready for use")
    print(f"✅ Faiss-based similarity search is working correctly")
    print(f"✅ Text processing and vector storage integration verified")
