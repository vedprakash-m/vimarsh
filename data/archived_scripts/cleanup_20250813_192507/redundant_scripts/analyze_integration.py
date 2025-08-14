#!/usr/bin/env python3
"""
Quick script to analyze content integration results.
"""
import json
import sys

def analyze_integration_results():
    try:
        with open('content_integration_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get sacred text entries
        entries = data.get('sacred_text_entries', [])
        print(f"Total sacred text entries: {len(entries)}")
        
        # Count by personality
        personalities = {}
        for entry in entries:
            personality = entry.get('personality', 'Unknown')
            personalities[personality] = personalities.get(personality, 0) + 1
        
        print("\nEntries by personality:")
        for personality in sorted(personalities.keys()):
            print(f"  {personality}: {personalities[personality]} entries")
        
        # Check sourced content
        sourced = data.get('sourced_content', {})
        print(f"\nSourced content items: {len(sourced)}")
        
        # Analyze sourced content by personality
        sourced_personalities = {}
        for item_id, item_data in sourced.items():
            personality = item_data.get('personality', 'Unknown')
            sourced_personalities[personality] = sourced_personalities.get(personality, 0) + 1
        
        print("\nSourced content by personality:")
        for personality in sorted(sourced_personalities.keys()):
            print(f"  {personality}: {sourced_personalities[personality]} sources")
        
        # Check processing statistics
        stats = data.get('processing_statistics', {})
        if stats:
            print(f"\nProcessing Statistics:")
            print(f"  Success rate: {stats.get('success_rate', 'N/A')}")
            print(f"  Total characters: {stats.get('total_characters', 'N/A'):,}")
            print(f"  Processing time: {stats.get('processing_time_seconds', 'N/A')} seconds")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing results: {str(e)}")
        return False

if __name__ == "__main__":
    analyze_integration_results()
