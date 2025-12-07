#!/usr/bin/env python3
"""Test if Azure OpenAI is generating valid embeddings"""

import asyncio
import sys
sys.path.insert(0, '/Users/ved/Apps/vimarsh/data')
from services.azure_openai_embedding_service import AzureOpenAIEmbeddingService
import statistics

async def test():
    service = AzureOpenAIEmbeddingService()
    emb = await service.generate_embedding('Archimedes discovered the principle of buoyancy.')
    print(f'Generated embedding: {len(emb)} dimensions')
    non_zero = sum(1 for v in emb if v != 0)
    avg = statistics.mean([abs(v) for v in emb])
    print(f'Non-zero: {non_zero}/{len(emb)}')
    print(f'Avg magnitude: {avg:.6f}')
    print(f'First 5 values: {emb[:5]}')
    
    if non_zero == 0:
        print("\n❌ PROBLEM: Generated embedding is all zeros!")
    else:
        print("\n✅ Embedding generation works correctly")

asyncio.run(test())
