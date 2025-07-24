/**
 * Personality Voice Selector Component
 * 
 * Allows users to select and switch between different personality voices
 * with preview functionality and voice characteristics display.
 */

import React, { useState } from 'react';

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

interface PersonalityVoiceSelectorProps {
  personalities: Personality[];
  selectedPersonality?: Personality;
  onPersonalitySelect: (personality: Personality) => void;
  onVoicePreview?: (personality: Personality) => void;
  disabled?: boolean;
}

const PersonalityVoiceSelector: React.FC<PersonalityVoiceSelectorProps> = ({
  personalities,
  selectedPersonality,
  onPersonalitySelect,
  onVoicePreview,
  disabled = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getPersonalityIcon = (domain: string) => {
    switch (domain) {
      case 'spiritual': return '🕉️';
      case 'scientific': return '🔬';
      case 'historical': return '🏛️';
      case 'philosophical': return '🤔';
      default: return '🎭';
    }
  };

  const getDomainColor = (domain: string) => {
    switch (domain) {
      case 'spiritual': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'scientific': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'historical': return 'bg-green-100 text-green-800 border-green-200';
      case 'philosophical': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getVoiceCharacteristics = (personality: Personality) => {
    const chars = personality.voice_settings.voice_characteristics;
    return `${chars.gender} • ${chars.age} • ${chars.tone}`;
  };

  const handlePersonalitySelect = (personality: Personality) => {
    onPersonalitySelect(personality);
    setIsExpanded(false);
  };

  const handleVoicePreview = (personality: Personality, event: React.MouseEvent) => {
    event.stopPropagation();
    if (onVoicePreview) {
      onVoicePreview(personality);
    }
  };

  const getPreviewText = (personality: Personality) => {
    const sampleTexts = {
      krishna: "Namaste, dear child. I am here to guide you on the path of dharma and self-realization.",
      einstein: "Hello, my friend. Let us explore the mysteries of the universe together through the lens of science.",
      lincoln: "Greetings, fellow citizen. I am here to discuss the principles of democracy and freedom.",
      marcus_aurelius: "Welcome, seeker of wisdom. Let us contemplate the virtues of stoic philosophy together."
    };
    return sampleTexts[personality.id as keyof typeof sampleTexts] || 
           `Hello, I am ${personality.name}. How may I assist you today?`;
  };

  return (
    <div className="personality-voice-selector">
      {/* Current Selection Display */}
      <div 
        className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors ${
          disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white hover:bg-gray-50'
        }`}
        onClick={() => !disabled && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          {selectedPersonality ? (
            <>
              <span className="text-xl">{getPersonalityIcon(selectedPersonality.domain)}</span>
              <div>
                <div className="font-medium text-gray-900">
                  {selectedPersonality.name}
                </div>
                <div className="text-sm text-gray-600">
                  {getVoiceCharacteristics(selectedPersonality)}
                </div>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full border ${getDomainColor(selectedPersonality.domain)}`}>
                {selectedPersonality.domain}
              </span>
            </>
          ) : (
            <div className="text-gray-500">Select a personality voice...</div>
          )}
        </div>
        <div className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
          <span className="text-gray-400">▼</span>
        </div>
      </div>

      {/* Expanded Options */}
      {isExpanded && !disabled && (
        <div className="mt-2 border rounded-lg bg-white shadow-lg max-h-96 overflow-y-auto">
          {personalities.map((personality) => (
            <div
              key={personality.id}
              className={`p-3 border-b last:border-b-0 cursor-pointer transition-colors hover:bg-gray-50 ${
                selectedPersonality?.id === personality.id ? 'bg-blue-50' : ''
              }`}
              onClick={() => handlePersonalitySelect(personality)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-xl">{getPersonalityIcon(personality.domain)}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="font-medium text-gray-900">
                        {personality.name}
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full border ${getDomainColor(personality.domain)}`}>
                        {personality.domain}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {getVoiceCharacteristics(personality)}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Rate: {personality.voice_settings.speaking_rate}x • 
                      Pitch: {personality.voice_settings.pitch > 0 ? '+' : ''}{personality.voice_settings.pitch}
                    </div>
                  </div>
                </div>
                
                {/* Preview Button */}
                {onVoicePreview && (
                  <button
                    onClick={(e) => handleVoicePreview(personality, e)}
                    className="ml-2 px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                    title="Preview voice"
                  >
                    🔊 Preview
                  </button>
                )}
              </div>

              {/* Pronunciation Guide Preview */}
              {Object.keys(personality.pronunciation_guide).length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <div className="text-xs text-gray-500 mb-1">Specialized pronunciation:</div>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(personality.pronunciation_guide).slice(0, 3).map(([term, guide]) => (
                      <span key={term} className="bg-gray-100 px-2 py-1 rounded text-xs text-gray-600">
                        {term}
                      </span>
                    ))}
                    {Object.keys(personality.pronunciation_guide).length > 3 && (
                      <span className="text-xs text-gray-500">
                        +{Object.keys(personality.pronunciation_guide).length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Voice Settings Display */}
      {selectedPersonality && (
        <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
          <div className="font-medium text-gray-700 mb-1">Current Voice Settings:</div>
          <div className="grid grid-cols-2 gap-2 text-gray-600">
            <div>Speaking Rate: {selectedPersonality.voice_settings.speaking_rate}x</div>
            <div>Pitch: {selectedPersonality.voice_settings.pitch > 0 ? '+' : ''}{selectedPersonality.voice_settings.pitch}</div>
            <div>Volume: {Math.round(selectedPersonality.voice_settings.volume * 100)}%</div>
            <div>Language: {selectedPersonality.voice_settings.language}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalityVoiceSelector;