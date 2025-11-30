/**
 * Voice Configuration for Vimarsh Personalities
 * 
 * Each personality has specific voice settings that match their character:
 * - rate: Speaking speed (0.5 to 2.0, where 1.0 is normal)
 * - pitch: Voice pitch (0.5 to 2.0, where 1.0 is normal)
 * - voicePreference: Preferred voice characteristics for TTS selection
 */

export interface VoiceSettings {
  rate: number;
  pitch: number;
  voicePreference: 'male' | 'female';
  languageCode: string;
  emphasis: 'calm' | 'authoritative' | 'expressive' | 'scholarly' | 'passionate';
}

export interface PersonalityVoice {
  id: string;
  name: string;
  domain: string;
  settings: VoiceSettings;
  pronunciationNotes?: string[];
}

// Domain default settings
export const DOMAIN_VOICE_DEFAULTS: Record<string, Partial<VoiceSettings>> = {
  spiritual: {
    rate: 0.85,
    pitch: 0.9,
    emphasis: 'calm',
    voicePreference: 'male'
  },
  scientific: {
    rate: 0.9,
    pitch: 1.0,
    emphasis: 'scholarly',
    voicePreference: 'male'
  },
  philosophical: {
    rate: 0.85,
    pitch: 0.95,
    emphasis: 'calm',
    voicePreference: 'male'
  },
  leadership: {
    rate: 0.88,
    pitch: 0.95,
    emphasis: 'authoritative',
    voicePreference: 'male'
  },
  literary: {
    rate: 0.9,
    pitch: 1.05,
    emphasis: 'expressive',
    voicePreference: 'male'
  },
  psychology: {
    rate: 0.88,
    pitch: 0.95,
    emphasis: 'scholarly',
    voicePreference: 'male'
  },
  historical: {
    rate: 0.85,
    pitch: 0.9,
    emphasis: 'authoritative',
    voicePreference: 'male'
  }
};

// Individual personality voice configurations
export const PERSONALITY_VOICES: PersonalityVoice[] = [
  // ========== SPIRITUAL DOMAIN ==========
  {
    id: 'krishna',
    name: 'Lord Krishna',
    domain: 'spiritual',
    settings: {
      rate: 0.82,
      pitch: 0.88,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'calm'
    },
    pronunciationNotes: [
      'Dharma: DHAR-ma',
      'Karma: KAR-ma',
      'Yoga: YO-ga',
      'Arjuna: ar-JU-na',
      'Moksha: MOHK-sha',
      'Bhakti: BHAK-ti'
    ]
  },
  {
    id: 'buddha',
    name: 'Gautama Buddha',
    domain: 'spiritual',
    settings: {
      rate: 0.78,
      pitch: 0.85,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'calm'
    },
    pronunciationNotes: [
      'Nirvana: nir-VAH-na',
      'Samsara: sam-SAH-ra',
      'Dharma: DHAR-ma',
      'Sangha: SANG-ha',
      'Dukkha: DOOK-ka'
    ]
  },
  {
    id: 'jesus_christ',
    name: 'Jesus Christ',
    domain: 'spiritual',
    settings: {
      rate: 0.85,
      pitch: 1.0,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'passionate'
    }
  },
  {
    id: 'rumi',
    name: 'Rumi',
    domain: 'spiritual',
    settings: {
      rate: 0.88,
      pitch: 1.0,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'expressive'
    },
    pronunciationNotes: [
      'Masnavi: mas-na-VEE',
      'Shams: SHAHMS',
      'Dervish: DER-vish'
    ]
  },
  {
    id: 'swami_vivekananda',
    name: 'Swami Vivekananda',
    domain: 'spiritual',
    settings: {
      rate: 0.95,
      pitch: 1.1,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'passionate'
    },
    pronunciationNotes: [
      'Vedanta: vay-DAHN-ta',
      'Ramakrishna: ra-ma-KRISH-na',
      'Atman: AHT-man'
    ]
  },

  // ========== SCIENTIFIC DOMAIN ==========
  {
    id: 'albert_einstein',
    name: 'Albert Einstein',
    domain: 'scientific',
    settings: {
      rate: 0.9,
      pitch: 1.0,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    }
  },
  {
    id: 'isaac_newton',
    name: 'Isaac Newton',
    domain: 'scientific',
    settings: {
      rate: 0.85,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-GB',
      emphasis: 'scholarly'
    }
  },
  {
    id: 'nikola_tesla',
    name: 'Nikola Tesla',
    domain: 'scientific',
    settings: {
      rate: 0.9,
      pitch: 1.05,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'passionate'
    }
  },
  {
    id: 'archimedes',
    name: 'Archimedes',
    domain: 'scientific',
    settings: {
      rate: 0.88,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    },
    pronunciationNotes: [
      'Eureka: yoo-REE-ka',
      'Syracuse: SEER-a-kyoos'
    ]
  },
  {
    id: 'leonardo_da_vinci',
    name: 'Leonardo da Vinci',
    domain: 'scientific',
    settings: {
      rate: 0.9,
      pitch: 1.0,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'expressive'
    }
  },

  // ========== PHILOSOPHICAL DOMAIN ==========
  {
    id: 'marcus_aurelius',
    name: 'Marcus Aurelius',
    domain: 'philosophical',
    settings: {
      rate: 0.85,
      pitch: 0.9,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'calm'
    }
  },
  {
    id: 'socrates',
    name: 'Socrates',
    domain: 'philosophical',
    settings: {
      rate: 0.88,
      pitch: 1.0,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    }
  },
  {
    id: 'plato',
    name: 'Plato',
    domain: 'philosophical',
    settings: {
      rate: 0.85,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    }
  },
  {
    id: 'aristotle',
    name: 'Aristotle',
    domain: 'philosophical',
    settings: {
      rate: 0.88,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    }
  },
  {
    id: 'confucius',
    name: 'Confucius',
    domain: 'philosophical',
    settings: {
      rate: 0.82,
      pitch: 0.9,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'calm'
    },
    pronunciationNotes: [
      'Ren: REN (as in "wren")',
      'Li: LEE',
      'Analects: AN-a-lekts'
    ]
  },
  {
    id: 'lao_tzu',
    name: 'Lao Tzu',
    domain: 'philosophical',
    settings: {
      rate: 0.78,
      pitch: 0.85,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'calm'
    },
    pronunciationNotes: [
      'Tao: DOW (rhymes with "cow")',
      'Te: DEH',
      'Wu Wei: WOO WAY'
    ]
  },

  // ========== LEADERSHIP DOMAIN ==========
  {
    id: 'abraham_lincoln',
    name: 'Abraham Lincoln',
    domain: 'leadership',
    settings: {
      rate: 0.85,
      pitch: 0.9,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'authoritative'
    }
  },
  {
    id: 'george_washington',
    name: 'George Washington',
    domain: 'leadership',
    settings: {
      rate: 0.85,
      pitch: 0.9,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'authoritative'
    }
  },
  {
    id: 'mahatma_gandhi',
    name: 'Mahatma Gandhi',
    domain: 'leadership',
    settings: {
      rate: 0.8,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'calm'
    },
    pronunciationNotes: [
      'Ahimsa: a-HIM-sa',
      'Satyagraha: sat-ya-GRA-ha',
      'Ashram: ASH-rum'
    ]
  },
  {
    id: 'chanakya',
    name: 'Chanakya',
    domain: 'leadership',
    settings: {
      rate: 0.88,
      pitch: 0.9,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'authoritative'
    },
    pronunciationNotes: [
      'Arthashastra: ar-tha-SHAHS-tra',
      'Maurya: MOW-rya',
      'Kautilya: kow-TIL-ya'
    ]
  },
  {
    id: 'benjamin_franklin',
    name: 'Benjamin Franklin',
    domain: 'leadership',
    settings: {
      rate: 0.9,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    }
  },
  {
    id: 'martin_luther_king_jr',
    name: 'Martin Luther King Jr.',
    domain: 'leadership',
    settings: {
      rate: 0.9,
      pitch: 1.1,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'passionate'
    }
  },

  // ========== LITERARY DOMAIN ==========
  {
    id: 'william_shakespeare',
    name: 'William Shakespeare',
    domain: 'literary',
    settings: {
      rate: 0.88,
      pitch: 1.05,
      voicePreference: 'male',
      languageCode: 'en-GB',
      emphasis: 'expressive'
    }
  },
  {
    id: 'rabindranath_tagore',
    name: 'Rabindranath Tagore',
    domain: 'literary',
    settings: {
      rate: 0.85,
      pitch: 1.0,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'expressive'
    },
    pronunciationNotes: [
      'Gitanjali: gi-TAHN-ja-li',
      'Shantiniketan: shan-ti-ni-KAY-tan'
    ]
  },

  // ========== PSYCHOLOGY DOMAIN ==========
  {
    id: 'sigmund_freud',
    name: 'Sigmund Freud',
    domain: 'psychology',
    settings: {
      rate: 0.88,
      pitch: 0.95,
      voicePreference: 'male',
      languageCode: 'en-US',
      emphasis: 'scholarly'
    }
  }
];

/**
 * Get voice settings for a specific personality
 */
export function getPersonalityVoiceSettings(personalityId: string): VoiceSettings {
  const normalizedId = personalityId.toLowerCase().replace(/\s+/g, '_');
  const personality = PERSONALITY_VOICES.find(p => p.id === normalizedId);
  
  if (personality) {
    return personality.settings;
  }

  // Return default settings
  return {
    rate: 0.9,
    pitch: 1.0,
    voicePreference: 'male',
    languageCode: 'en-US',
    emphasis: 'calm'
  };
}

/**
 * Get domain default voice settings
 */
export function getDomainVoiceSettings(domain: string): Partial<VoiceSettings> {
  return DOMAIN_VOICE_DEFAULTS[domain] || DOMAIN_VOICE_DEFAULTS.spiritual;
}

/**
 * Get all personalities for a specific domain
 */
export function getPersonalitiesByDomain(domain: string): PersonalityVoice[] {
  return PERSONALITY_VOICES.filter(p => p.domain === domain);
}

/**
 * Get pronunciation notes for a personality
 */
export function getPronunciationNotes(personalityId: string): string[] {
  const normalizedId = personalityId.toLowerCase().replace(/\s+/g, '_');
  const personality = PERSONALITY_VOICES.find(p => p.id === normalizedId);
  return personality?.pronunciationNotes || [];
}

export default {
  PERSONALITY_VOICES,
  DOMAIN_VOICE_DEFAULTS,
  getPersonalityVoiceSettings,
  getDomainVoiceSettings,
  getPersonalitiesByDomain,
  getPronunciationNotes
};
