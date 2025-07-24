/**
 * Voice Testing Interface Component
 * 
 * Allows users to test and compare different personality voices
 * with sample texts and voice characteristic adjustments.
 */

import React, { useState } from 'react';
import PersonalityVoiceSelector from './PersonalityVoiceSelector';

interface Personality {
  id: string;
  name: string;
  domain: 'spiritual' | 'historical' | 'scientific' | 'philosophical';
  voice_settings: {
    language: string;
    voice_name?: string;
    speaking_rate: number;
    pitch: number;
    volume: number;
    voice_characteristics: {
      gender: 'male' | 'female';
      age: 'young' | 'middle' | 'elderly';
      accent?: string;
      tone: 'reverent' | 'authoritative' | 'contemplative' | 'scholarly';
    };
  };
  pronunciation_guide: {
    [term: string]: {
      phonetic: string;
      audio_url?: string;
      language: string;
    };
  };
}

// Sample personalities for testing
const TEST_PERSONALITIES: Personality[] = [
  {
    id: 'krishna',
    name: 'Lord Krishna',
    domain: 'spiritual',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.75,
      pitch: -1.5,
      volume: 0.9,
      voice_characteristics: {
        gender: 'male',
        age: 'middle',
        tone: 'reverent'
      }
    },
    pronunciation_guide: {
      'dharma': { phonetic: 'DHAR-ma', language: 'sanskrit' },
      'karma': { phonetic: 'KAR-ma', language: 'sanskrit' },
      'yoga': { phonetic: 'YO-ga', language: 'sanskrit' },
      'moksha': { phonetic: 'MOHK-sha', language: 'sanskrit' }
    }
  },
  {
    id: 'einstein',
    name: 'Albert Einstein',
    domain: 'scientific',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.85,
      pitch: 0.0,
      volume: 0.9,
      voice_characteristics: {
        gender: 'male',
        age: 'elderly',
        accent: 'slight_german',
        tone: 'scholarly'
      }
    },
    pronunciation_guide: {
      'relativity': { phonetic: 'rel-uh-TIV-i-tee', language: 'english' },
      'spacetime': { phonetic: 'SPACE-time', language: 'english' },
      'quantum': { phonetic: 'KWAN-tum', language: 'english' }
    }
  },
  {
    id: 'lincoln',
    name: 'Abraham Lincoln',
    domain: 'historical',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.8,
      pitch: -0.5,
      volume: 0.95,
      voice_characteristics: {
        gender: 'male',
        age: 'middle',
        accent: 'midwest_american',
        tone: 'authoritative'
      }
    },
    pronunciation_guide: {
      'Gettysburg': { phonetic: 'GET-eez-burg', language: 'english' },
      'emancipation': { phonetic: 'ih-man-si-PAY-shun', language: 'english' }
    }
  },
  {
    id: 'marcus_aurelius',
    name: 'Marcus Aurelius',
    domain: 'philosophical',
    voice_settings: {
      language: 'en-US',
      voice_name: 'Google US English Male',
      speaking_rate: 0.7,
      pitch: -1.0,
      volume: 0.85,
      voice_characteristics: {
        gender: 'male',
        age: 'middle',
        tone: 'contemplative'
      }
    },
    pronunciation_guide: {
      'stoicism': { phonetic: 'STOH-i-sizm', language: 'english' },
      'virtue': { phonetic: 'VUR-choo', language: 'english' },
      'logos': { phonetic: 'LOH-gos', language: 'greek' }
    }
  }
];

const SAMPLE_TEXTS = {
  krishna: "Namaste, dear child. I am here to guide you on the path of dharma and self-realization. Through yoga and devotion, we can achieve moksha and understand the true nature of karma.",
  einstein: "Hello, my friend. Let us explore the mysteries of the universe together. The theory of relativity shows us that spacetime is curved, and quantum mechanics reveals the probabilistic nature of reality.",
  lincoln: "Greetings, fellow citizen. I am here to discuss the principles of democracy and freedom. The Gettysburg Address reminds us that government of the people, by the people, and for the people shall not perish from the earth.",
  marcus_aurelius: "Welcome, seeker of wisdom. Let us contemplate the virtues of stoic philosophy together. Through virtue and logos, we can achieve ataraxia and live according to nature's design."
};

interface VoiceTestingInterfaceProps {
  onPersonalitySelect?: (personality: Personality) => void;
}

const VoiceTestingInterface: React.FC<VoiceTestingInterfaceProps> = ({
  onPersonalitySelect
}) => {
  const [selectedPersonality, setSelectedPersonality] = useState<Personality>(TEST_PERSONALITIES[0]);
  const [customText, setCustomText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceSettings, setVoiceSettings] = useState(selectedPersonality.voice_settings);

  const handlePersonalitySelect = (personality: Personality) => {
    setSelectedPersonality(personality);
    setVoiceSettings(personality.voice_settings);
    if (onPersonalitySelect) {
      onPersonalitySelect(personality);
    }
  };

  const applyPronunciationGuide = (text: string, personality: Personality): string => {
    let processedText = text;
    const pronunciationGuide = personality.pronunciation_guide;
    
    Object.entries(pronunciationGuide).forEach(([term, guide]) => {
      const regex = new RegExp(`\\b${term}\\b`, 'gi');
      processedText = processedText.replace(regex, guide.phonetic);
    });
    
    return processedText;
  };

  const speakText = (text: string) => {
    if (!window.speechSynthesis || isSpeaking) return;

    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    const processedText = applyPronunciationGuide(text, selectedPersonality);
    const utterance = new SpeechSynthesisUtterance(processedText);
    
    // Apply voice settings
    utterance.rate = voiceSettings.speaking_rate;
    utterance.pitch = 1.0 + (voiceSettings.pitch / 10);
    utterance.volume = voiceSettings.volume;
    utterance.lang = voiceSettings.language;
    
    // Find appropriate voice
    const voices = window.speechSynthesis.getVoices();
    const targetLang = voiceSettings.language.split('-')[0];
    
    let preferredVoice = null;
    
    if (voiceSettings.voice_name) {
      preferredVoice = voices.find(voice => voice.name.includes(voiceSettings.voice_name!));
    }
    
    if (!preferredVoice) {
      const genderPreference = voiceSettings.voice_characteristics.gender;
      preferredVoice = voices.find(voice => {
        const voiceName = voice.name.toLowerCase();
        const langMatch = voice.lang.startsWith(targetLang);
        const genderMatch = genderPreference === 'female' ? 
          voiceName.includes('female') || voiceName.includes('woman') :
          voiceName.includes('male') || voiceName.includes('man') || !voiceName.includes('female');
        
        return langMatch && genderMatch;
      });
    }
    
    if (!preferredVoice) {
      preferredVoice = voices.find(voice => voice.lang.startsWith(targetLang));
    }
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const handleVoiceSettingChange = (setting: string, value: number) => {
    setVoiceSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  return (
    <div className="voice-testing-interface max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Voice Testing Interface</h2>
        <p className="text-gray-600">Test and compare different personality voices with sample texts and adjustable settings.</p>
      </div>

      {/* Personality Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Select Personality</h3>
        <PersonalityVoiceSelector
          personalities={TEST_PERSONALITIES}
          selectedPersonality={selectedPersonality}
          onPersonalitySelect={handlePersonalitySelect}
          onVoicePreview={(personality) => speakText(SAMPLE_TEXTS[personality.id as keyof typeof SAMPLE_TEXTS])}
        />
      </div>

      {/* Voice Settings Adjustment */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Voice Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speaking Rate: {voiceSettings.speaking_rate}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={voiceSettings.speaking_rate}
              onChange={(e) => handleVoiceSettingChange('speaking_rate', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Pitch: {voiceSettings.pitch > 0 ? '+' : ''}{voiceSettings.pitch}
            </label>
            <input
              type="range"
              min="-2"
              max="2"
              step="0.1"
              value={voiceSettings.pitch}
              onChange={(e) => handleVoiceSettingChange('pitch', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Volume: {Math.round(voiceSettings.volume * 100)}%
            </label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={voiceSettings.volume}
              onChange={(e) => handleVoiceSettingChange('volume', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Sample Text Testing */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Sample Text</h3>
        <div className="p-4 bg-blue-50 rounded-lg mb-3">
          <p className="text-gray-800 leading-relaxed">
            {SAMPLE_TEXTS[selectedPersonality.id as keyof typeof SAMPLE_TEXTS]}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => speakText(SAMPLE_TEXTS[selectedPersonality.id as keyof typeof SAMPLE_TEXTS])}
            disabled={isSpeaking}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isSpeaking ? '🔊 Speaking...' : '🔊 Test Sample'}
          </button>
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              🔇 Stop
            </button>
          )}
        </div>
      </div>

      {/* Custom Text Testing */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Custom Text</h3>
        <textarea
          value={customText}
          onChange={(e) => setCustomText(e.target.value)}
          placeholder="Enter custom text to test with the selected personality voice..."
          className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={4}
        />
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => speakText(customText)}
            disabled={!customText.trim() || isSpeaking}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {isSpeaking ? '🔊 Speaking...' : '🔊 Test Custom'}
          </button>
          {isSpeaking && (
            <button
              onClick={stopSpeaking}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              🔇 Stop
            </button>
          )}
        </div>
      </div>

      {/* Pronunciation Guide Display */}
      {Object.keys(selectedPersonality.pronunciation_guide).length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Pronunciation Guide</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(selectedPersonality.pronunciation_guide).map(([term, guide]) => (
              <div key={term} className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="font-medium text-yellow-800">{term}</div>
                <div className="text-sm text-yellow-600">→ {guide.phonetic}</div>
                <div className="text-xs text-yellow-500 mt-1">{guide.language}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Voice Characteristics Display */}
      <div className="p-4 bg-gray-100 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Current Voice Profile</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Gender:</span>
            <div className="text-gray-600">{selectedPersonality.voice_settings.voice_characteristics.gender}</div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Age:</span>
            <div className="text-gray-600">{selectedPersonality.voice_settings.voice_characteristics.age}</div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Tone:</span>
            <div className="text-gray-600">{selectedPersonality.voice_settings.voice_characteristics.tone}</div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Domain:</span>
            <div className="text-gray-600">{selectedPersonality.domain}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceTestingInterface;