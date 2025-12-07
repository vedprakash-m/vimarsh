#!/usr/bin/env python3
"""Quick check: Do these personalities have zero embeddings or not?"""

import asyncio
from services.enhanced_rag_service_v6 import EnhancedRAGService
import statistics

async def check_embeddings():
    service = EnhancedRAGService()
    
    personalities = [
        "archimedes", "leonardo_da_vinci", "rabindranath_tagore", 
        "william_shakespeare", "sigmund_freud"
    ]
    
    for personality in personalities:
        query = f"SELECT TOP 1 c.embedding FROM c WHERE c.personality_id = '{personality}' AND IS_DEFINED(c.embedding)"
        results = list(service.container.query_items(query=query, enable_cross_partition_query=True))
        
        if results:
            emb = results[0].get('embedding', [])
            non_zero = sum(1 for v in emb if v != 0)
            avg_mag = statistics.mean([abs(v) for v in emb]) if non_zero > 0 else 0
            print(f"\n{personality}:")
            print(f"  Dimension: {len(emb)}")
            print(f"  Non-zero: {non_zero}/{len(emb)}")
            print(f"  Avg magnitude: {avg_mag:.6f}")
            print(f"  First 5 values: {emb[:5]}")
        else:
            print(f"\n{personality}: NO EMBEDDINGS FOUND")

asyncio.run(check_embeddings())
