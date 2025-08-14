# Script and Content Consolidation Plan

## Current Mess Assessment

### Temporary Test Scripts (TO BE CONSOLIDATED/DELETED)
- test_all_personality_ids.py
- test_all_personality_ids_simple.py
- test_citation_grounding.py
- test_content_acquisition.py
- test_enhanced_rag_fixed.py
- test_enhanced_rag_integration.py
- test_gap_remediation.py
- test_gap_remediation_updated.py
- test_guidance_integration.py
- test_hybrid_search.py
- test_hybrid_search_simple.py
- test_memory_integration.py
- test_personality_content.py
- test_personality_simple.py
- test_phase6_integration.py
- test_phase7_1_validation.py
- test_phase7_2_content_enhancement.py
- test_phase7_3_content_acquisition.py
- test_phase7_3_corrected_analysis.py
- test_phase7_rag_extension.py
- test_phase8_deployment.py
- test_simple_rag_fix.py

### Temporary Processing Scripts (TO BE CONSOLIDATED)
- alternative_source_acquisition.py
- comprehensive_content_acquisition.py
- content_inventory_manager.py
- enhanced_pdf_processor.py
- process_personality_content.py
- process_uploaded_pdfs.py
- targeted_content_acquisition.py
- upload_chunks_to_cosmos.py
- generate_embeddings.py

### Temporary JSON Reports (TO BE ARCHIVED)
- comprehensive_acquisition_20250812_*.json
- comprehensive_content_report_20250812_*.json
- content_inventory_20250812_*.json
- enhanced_pdf_processing_20250812_*.json
- phase7_3_*.json
- targeted_content_acquisition_20250812_*.json
- processing_plan_20250812_*.json

## Consolidation Strategy

### 1. Create scripts/ directory with clean tools:
- scripts/content_manager.py (consolidated content operations)
- scripts/test_suite.py (consolidated testing)
- scripts/diagnostics.py (consolidated analysis)

### 2. Archive temporary files:
- Move all temp files to backup/temp_scripts/
- Keep only production scripts in backend/

### 3. Content consolidation:
- All source texts in data/sources/
- All processed chunks in Cosmos DB only
- Clear local processing artifacts
