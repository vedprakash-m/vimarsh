# Critical Interface Gaps Analysis - CI/CD Failure 2

## Missing Methods by Class (From CI/CD Errors)

### 1. SpeechProcessor Class
**File**: `backend/voice/speech_processor.py`

**Missing Methods**:
- `preprocess_audio()` - Audio preprocessing for speech recognition
- `_recognize_speech` - Speech recognition implementation  

**Missing Module Access**:
- `voice.speech_processor.speech` - Speech recognition module
- `voice.speech_processor.nr` - Noise reduction module

### 2. AudioProcessor Class  
**File**: `backend/voice/audio_utils.py`

**Missing Methods**:
- `convert_format(audio_data, target_format)` - Audio format conversion

**Method Signature Issues**:
- `segment_long_audio()` - Returns wrong count (6 vs 5 expected)

### 3. SanskritRecognitionOptimizer Class
**File**: `backend/voice/sanskrit_optimizer.py`

**Missing Required Parameters**:
- `correct_in_context(text, context)` - Missing context parameter
- `calculate_recognition_confidence(text, context)` - Missing context parameter

**Logic Issues**:
- `detect_sanskrit_terms()` - Returns wrong structure
- `correct_pronunciation()` - Returns 'darma' instead of 'dharma'
- `generate_phonetic_map()` - Assertion fails on phonetic mappings

### 4. SpiritualTTSOptimizer Class
**File**: `backend/voice/tts_optimizer.py`

**Method Signature Issues**:
- `select_optimal_voice()` - Doesn't accept `context` keyword argument
- `adjust_emotional_tone()` - Doesn't accept `target_emotion` keyword argument

**Return Type Issues**:
- `preprocess_for_tts()` - Returns string instead of object with attributes
- Methods return wrong object types (dict vs objects with attributes)

### 5. Import Issues
**Files**: Various test files

**Missing Imports**:
- `TTSOptimizer` not defined in test scope
- Async/await type mismatches with Mock objects

## Priority Implementation Order

### CRITICAL (Blocks many tests)
1. **SpeechProcessor.preprocess_audio()**
2. **AudioProcessor.convert_format()**  
3. **Fix method signatures in SanskritRecognitionOptimizer**

### HIGH (Affects comprehensive tests)
4. **SpiritualTTSOptimizer method signatures**
5. **Fix return types to match test expectations**
6. **Add missing module access for speech/nr**

### MEDIUM (Import and type issues)
7. **Fix TTSOptimizer import**
8. **Fix async/await mock issues**
9. **Correct audio segmentation logic**

## Systematic Fix Strategy

Rather than fixing individual methods, implement:

1. **Interface Contract System** - Validate test expectations match implementations
2. **Mock Type Safety** - Ensure mocks match real object interfaces  
3. **Method Signature Validation** - Check parameter requirements
4. **Return Type Validation** - Ensure return types match test expectations

This addresses the root cause rather than symptoms.
