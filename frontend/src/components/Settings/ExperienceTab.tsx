import React from 'react';
import { useSettings } from '../../contexts/SettingsContext';
import { usePersonality, Personality } from '../../contexts/PersonalityContext';

const ExperienceTab: React.FC = () => {
  const { settings, updateSettings } = useSettings();
  const { availablePersonalities } = usePersonality();

  if (!settings) {
    return <div className="text-gray-500">Loading preferences...</div>;
  }

  const { experience_preferences } = settings;

  const conversationStyles = [
    {
      value: 'brief' as const,
      label: 'Brief & Direct',
      description: 'Quick answers for specific questions',
      example: '2-3 sentence responses',
    },
    {
      value: 'balanced' as const,
      label: 'Balanced (Recommended)',
      description: 'Moderate depth with helpful context',
      example: '4-6 paragraph responses',
    },
    {
      value: 'detailed' as const,
      label: 'Detailed & Deep',
      description: 'Comprehensive wisdom with extended exploration',
      example: 'Full multi-paragraph discourse',
    },
  ];

  const formalityLevels = [
    { value: 'very_formal' as const, label: 'Very Formal (Maximum respect, traditional address)' },
    { value: 'respectful' as const, label: 'Respectful & Warm (Balanced, recommended)' },
    { value: 'friendly' as const, label: 'Friendly (Approachable, conversational)' },
    { value: 'casual' as const, label: 'Casual (Modern, relaxed tone)' },
  ];

  const themes = [
    { value: 'light' as const, label: 'Light' },
    { value: 'auto' as const, label: 'Auto (System)' },
    { value: 'dark' as const, label: 'Dark' },
  ];

  const textSizes = [
    { value: 'small' as const, label: 'Small' },
    { value: 'medium' as const, label: 'Medium' },
    { value: 'large' as const, label: 'Large' },
  ];

  const handleFavoriteToggle = (personalityId: string) => {
    const currentFavorites = experience_preferences.favorite_personalities || [];
    const isFavorite = currentFavorites.includes(personalityId);

    let newFavorites: string[];
    if (isFavorite) {
      newFavorites = currentFavorites.filter(id => id !== personalityId);
    } else {
      if (currentFavorites.length >= 5) {
        alert('You can only select up to 5 favorite personalities');
        return;
      }
      newFavorites = [...currentFavorites, personalityId];
    }

    updateSettings({
      experience_preferences: {
        ...experience_preferences,
        favorite_personalities: newFavorites,
      },
    });
  };

  // Group personalities by domain
  const groupedPersonalities = availablePersonalities.reduce((acc: Record<string, Personality[]>, p: Personality) => {
    if (!acc[p.domain]) {
      acc[p.domain] = [];
    }
    acc[p.domain].push(p);
    return acc;
  }, {} as Record<string, Personality[]>);

  return (
    <div className="space-y-8">
      {/* Conversation Style */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">💬 How should personalities respond?</h2>
        <div className="space-y-3">
          {conversationStyles.map((style) => (
            <label
              key={style.value}
              className={`
                block p-4 border-2 rounded-lg cursor-pointer transition-all
                ${experience_preferences.conversation_style === style.value
                  ? 'border-saffron-500 bg-saffron-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <div className="flex items-start gap-3">
                <input
                  type="radio"
                  name="conversation_style"
                  value={style.value}
                  checked={experience_preferences.conversation_style === style.value}
                  onChange={(e) =>
                    updateSettings({
                      experience_preferences: {
                        ...experience_preferences,
                        conversation_style: e.target.value as any,
                      },
                    })
                  }
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{style.label}</div>
                  <div className="text-sm text-gray-600 mt-1">{style.description}</div>
                  <div className="text-xs text-gray-500 mt-1">Example: {style.example}</div>
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Response Preferences */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🎭 Response Preferences</h2>
        
        {/* Language */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          <select
            value={experience_preferences.language}
            onChange={(e) =>
              updateSettings({
                experience_preferences: {
                  ...experience_preferences,
                  language: e.target.value as 'en' | 'hi',
                },
              })
            }
            className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saffron-500 focus:border-transparent"
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
          </select>
        </div>

        {/* Formality */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Formality
          </label>
          <select
            value={experience_preferences.formality}
            onChange={(e) =>
              updateSettings({
                experience_preferences: {
                  ...experience_preferences,
                  formality: e.target.value as any,
                },
              })
            }
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saffron-500 focus:border-transparent"
          >
            {formalityLevels.map((level) => (
              <option key={level.value} value={level.value}>
                {level.label}
              </option>
            ))}
          </select>

          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm font-medium text-blue-900">💡 How this affects personalities:</div>
            <ul className="text-sm text-blue-700 mt-2 space-y-1 ml-4">
              <li>• Spiritual figures use traditional address</li>
              <li>• Scientists use academic language</li>
              <li>• Philosophers employ classical terminology</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Favorite Personalities */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          ⭐ Favorite Personalities ({experience_preferences.favorite_personalities?.length || 0}/5 selected)
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Select up to 5 personalities for quick access. Your favorites appear first in the personality selector.
        </p>

        <div className="space-y-6">
          {Object.entries(groupedPersonalities).map(([domain, domainPersonalities]) => (
            <div key={domain}>
              <h3 className="text-sm font-semibold text-gray-700 mb-2 capitalize flex items-center gap-2">
                <span className="text-lg">🎭</span>
                {domain}
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {domainPersonalities.map((p: Personality) => (
                  <label
                    key={p.id}
                    className={`
                      flex items-center gap-2 p-3 border-2 rounded-lg cursor-pointer transition-all
                      ${experience_preferences.favorite_personalities?.includes(p.id)
                        ? 'border-saffron-500 bg-saffron-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }
                    `}
                  >
                    <input
                      type="checkbox"
                      checked={experience_preferences.favorite_personalities?.includes(p.id) || false}
                      onChange={() => handleFavoriteToggle(p.id)}
                      className="rounded text-saffron-500 focus:ring-saffron-500"
                    />
                    <span className="text-sm font-medium text-gray-900">{p.name}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Appearance */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🎨 Appearance</h2>

        {/* Theme */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Theme
          </label>
          <div className="flex gap-2">
            {themes.map((theme) => (
              <button
                key={theme.value}
                onClick={() =>
                  updateSettings({
                    experience_preferences: {
                      ...experience_preferences,
                      theme: theme.value,
                    },
                  })
                }
                className={`
                  px-4 py-2 rounded-lg font-medium transition-all
                  ${experience_preferences.theme === theme.value
                    ? 'bg-saffron-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                {theme.label}
              </button>
            ))}
          </div>
        </div>

        {/* Text Size */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Text Size
          </label>
          <div className="flex gap-2">
            {textSizes.map((size) => (
              <button
                key={size.value}
                onClick={() =>
                  updateSettings({
                    experience_preferences: {
                      ...experience_preferences,
                      text_size: size.value,
                    },
                  })
                }
                className={`
                  px-4 py-2 rounded-lg font-medium transition-all
                  ${experience_preferences.text_size === size.value
                    ? 'bg-saffron-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                {size.label}
              </button>
            ))}
          </div>
          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
            <div style={{
              fontSize: experience_preferences.text_size === 'small' ? '0.875rem' :
                        experience_preferences.text_size === 'large' ? '1.125rem' : '1rem'
            }}>
              Preview: This is how text will appear
            </div>
          </div>
        </div>

        {/* Reduce Animations */}
        <div>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={experience_preferences.reduce_animations}
              onChange={(e) =>
                updateSettings({
                  experience_preferences: {
                    ...experience_preferences,
                    reduce_animations: e.target.checked,
                  },
                })
              }
              className="rounded text-saffron-500 focus:ring-saffron-500"
            />
            <div>
              <div className="font-medium text-gray-900">Reduce animations</div>
              <div className="text-sm text-gray-600">Better for slower devices or motion sensitivity</div>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
};

export default ExperienceTab;
