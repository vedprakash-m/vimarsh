#!/usr/bin/env python3
"""
Priority Status Check - Verify current implementation without breaking anything
"""

import sys
import os

def check_priority1_newton_fix():
    """Verify Priority 1: Newton Personality Fix is complete"""
    print("🚀 Priority 1: Newton Personality Fix")
    print("-" * 40)
    
    try:
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from services.enhanced_simple_llm_service import EnhancedSimpleLLMService
        
        # Create service (without API key - just check structure)
        service = EnhancedSimpleLLMService(api_key="dummy")  # Won't work but will initialize personalities
        
        if hasattr(service, 'personalities') and 'newton' in service.personalities:
            newton = service.personalities['newton']
            
            # Check all Priority 1 requirements
            checks = [
                ("Reduced timeout (20s)", newton.timeout_seconds == 20),
                ("Increased retries (3)", newton.max_retries == 3), 
                ("Optimized char limit (450)", newton.max_chars == 450),
                ("Concise prompt template", "BE CONCISE AND DIRECT" in newton.prompt_template),
                ("Async timeout handling", hasattr(service, '_generate_gemini_response')),
            ]
            
            all_passed = True
            for desc, passed in checks:
                status = "✅" if passed else "❌"
                print(f"  {status} {desc}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("🎉 Priority 1: COMPLETE - Newton timeout fix implemented!")
                return True
            else:
                print("⚠️  Priority 1: Incomplete")
                return False
        else:
            print("❌ Newton personality not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Priority 1: {e}")
        return False

def check_priority2_citations():
    """Verify Priority 2: Citation Enhancement status"""
    print("\n📚 Priority 2: Citation Enhancement")
    print("-" * 40)
    
    try:
        from services.enhanced_simple_llm_service import EnhancedSimpleLLMService
        
        service = EnhancedSimpleLLMService(api_key="dummy")
        
        if hasattr(service, 'personalities'):
            # Check citation configuration
            krishna = service.personalities.get('krishna')
            jesus = service.personalities.get('jesus')
            lincoln = service.personalities.get('lincoln')
            
            citation_checks = [
                ("Krishna requires citations", krishna and krishna.requires_citations),
                ("Krishna has BG reference", krishna and "BG 2.47" in krishna.prompt_template),
                ("Jesus requires citations", jesus and jesus.requires_citations),
                ("Jesus has biblical ref", jesus and "Matthew 22:39" in jesus.prompt_template),
                ("Lincoln requires citations", lincoln and lincoln.requires_citations),
            ]
            
            all_passed = True
            for desc, passed in citation_checks:
                status = "✅" if passed else "❌"
                print(f"  {status} {desc}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("✅ Priority 2: Basic citation structure exists")
                return True
            else:
                print("⚠️  Priority 2: Needs enhancement")
                return False
        else:
            print("❌ Personalities not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Priority 2: {e}")
        return False

def check_priority3_conversation_memory():
    """Check Priority 3: Context Memory status"""
    print("\n🧠 Priority 3: Context Memory (Conversation History)")
    print("-" * 40)
    
    # Check if conversation memory services exist
    memory_files = [
        "services/conversation_memory_service.py",
        "models/conversation_models.py"
    ]
    
    exists_count = 0
    for file_path in memory_files:
        full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
        if os.path.exists(full_path):
            exists_count += 1
            print(f"  ✅ {file_path} exists")
        else:
            print(f"  ❌ {file_path} missing")
    
    if exists_count == 0:
        print("📋 Priority 3: NOT STARTED - Need to implement conversation memory")
        return False
    elif exists_count < len(memory_files):
        print("⚠️  Priority 3: PARTIAL - Some components missing")
        return False
    else:
        print("✅ Priority 3: Files exist - need to verify functionality")
        return True

def main():
    """Check all priority statuses"""
    print("🎯 Vimarsh Enhancement Implementation Status")
    print("=" * 50)
    
    p1_status = check_priority1_newton_fix()
    p2_status = check_priority2_citations()
    p3_status = check_priority3_conversation_memory()
    
    print("\n📊 Summary")
    print("=" * 50)
    print(f"✅ Priority 1 (Newton Fix): {'COMPLETE' if p1_status else 'INCOMPLETE'}")
    print(f"📚 Priority 2 (Citations): {'READY' if p2_status else 'NEEDS WORK'}")
    print(f"🧠 Priority 3 (Memory): {'STARTED' if p3_status else 'NOT STARTED'}")
    
    if p1_status:
        print("\n🎉 Ready to proceed with Priority 2 and 3!")
        print("Next actions:")
        if not p3_status:
            print("1. Implement conversation memory service")
            print("2. Add database schema for conversation history")
            print("3. Integrate memory with LLM service")
    else:
        print("\n⚠️  Need to complete Priority 1 first")
    
    return p1_status and p2_status

if __name__ == "__main__":
    main()
