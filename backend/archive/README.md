# Archive Directory

This directory contains legacy code, development iterations, and deprecated files that are no longer needed for production but kept for reference.

## Contents

### Function App Variants (`function_app_variants/`)
- `function_app_minimal.py` - Simple test version (24 lines)
- `function_app_full.py` - Older full version (1943 lines) 
- `function_app_enhanced_safety.py` - Development iteration with safety features
- `function_app_multi.py` - Development iteration with multi-personality system

### Development & Debug Files
- `debug_personalities.py` - Debug utilities for personality system
- `demo_security_validator.py` - Security validation demo
- `demo_transaction_manager.py` - Transaction management demo
- `generate_admin_token.py` - Admin token generation utility
- `generate_dev_token.py` - Development token generation utility
- `performance_report_20250711_110152.json` - Old performance report

## Current Production File
- **`function_app.py`** (in backend root) - Active production version with multi-personality system

## Archive Date
July 26, 2025

## Notes
- These files were moved to reduce confusion and keep the backend directory clean
- The `.funcignore` file ensures archived files are not deployed to Azure
- Test files were moved to the `tests/` directory
