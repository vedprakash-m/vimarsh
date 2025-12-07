import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, TrendingUp, Brain } from 'lucide-react';
import { useSettings } from '../../contexts/SettingsContext';

const MyProfileTab: React.FC = () => {
  const navigate = useNavigate();
  const { profile } = useSettings();

  if (!profile) {
    return <div className="text-gray-500">Loading profile...</div>;
  }

  const { user, journey_stats, ai_usage } = profile;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'well_within_limits':
        return 'text-green-600 bg-green-50';
      case 'approaching_limit':
        return 'text-yellow-600 bg-yellow-50';
      case 'at_limit':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'well_within_limits':
        return '✅ Well within limits';
      case 'approaching_limit':
        return '⚠️ Approaching limit';
      case 'at_limit':
        return '🚫 At limit';
      default:
        return 'Status unknown';
    }
  };

  const getTrendText = (trend: string) => {
    switch (trend) {
      case 'similar_to_last_month':
        return '📊 Similar to last month';
      case 'slightly_higher':
        return '📈 Slightly higher than usual';
      case 'much_higher':
        return '📈 Much higher than usual';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-8">
      {/* User Identity */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Information</h2>
        <div className="flex items-center gap-4">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={user.name}
              className="w-16 h-16 rounded-full"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-saffron-100 flex items-center justify-center text-2xl">
              {user.name.charAt(0).toUpperCase()}
            </div>
          )}
          <div>
            <h3 className="text-lg font-medium text-gray-900">{user.name}</h3>
            <p className="text-sm text-gray-600">{user.email}</p>
            <p className="text-xs text-gray-500 mt-1">
              Member since {new Date(user.member_since).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Journey Stats */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Wisdom Journey</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-orange-50 to-red-50 p-4 rounded-lg border border-orange-200">
            <div className="text-3xl mb-2">🔥</div>
            <div className="text-2xl font-bold text-orange-600">{journey_stats.current_streak} days</div>
            <div className="text-sm text-gray-600">Current Streak</div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
            <div className="text-3xl mb-2">💬</div>
            <div className="text-2xl font-bold text-blue-600">{journey_stats.total_conversations}</div>
            <div className="text-sm text-gray-600">Wisdom Sessions</div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200">
            <div className="text-3xl mb-2">🏆</div>
            <div className="text-2xl font-bold text-purple-600">{journey_stats.achievements_unlocked}</div>
            <div className="text-sm text-gray-600">Achievements</div>
          </div>
        </div>

        <div className="mt-4 p-4 bg-gradient-to-r from-saffron-50 to-amber-50 rounded-lg border border-saffron-200">
          <div className="text-lg font-medium text-saffron-700">{journey_stats.wisdom_level}</div>
          <div className="text-sm text-gray-600 mt-1">Your current wisdom level</div>
        </div>

        {/* Domain Exploration */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Domain Exploration</h3>
          <div className="space-y-2">
            {Object.entries(journey_stats.domain_exploration).map(([domain, percentage]) => (
              <div key={domain}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="capitalize text-gray-700">{domain}</span>
                  <span className="text-gray-600">{Math.round(percentage * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-saffron-500 h-2 rounded-full transition-all"
                    style={{ width: `${percentage * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Usage Transparency */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">💡 Your AI Usage</h2>
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-6 rounded-lg border border-blue-200">
          <div className="text-center mb-4">
            <div className="text-3xl font-bold text-blue-700">
              ${ai_usage.monthly_cost.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              We've covered this in AI costs for you this month
            </div>
          </div>

          <div className="flex items-center justify-center gap-4 mb-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ai_usage.status)}`}>
              {getStatusText(ai_usage.status)}
            </span>
            <span className="text-sm text-gray-600">
              {getTrendText(ai_usage.trend)}
            </span>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-500 h-3 rounded-full transition-all"
              style={{ width: `${(ai_usage.monthly_cost / ai_usage.monthly_limit) * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>$0</span>
            <span>${ai_usage.monthly_limit} monthly credit</span>
          </div>

          <div className="mt-4 text-xs text-gray-500 text-center">
            Your conversations help us improve Vimarsh for everyone
          </div>
        </div>
      </div>

      {/* Quick Access */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">🎯 Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/wisdom/archive')}
            className="p-4 bg-white border-2 border-gray-200 rounded-lg hover:border-saffron-300 hover:bg-saffron-50 transition-all text-left group"
          >
            <BookOpen className="w-8 h-8 text-saffron-600 mb-2 group-hover:scale-110 transition-transform" />
            <div className="font-medium text-gray-900">Wisdom Archive</div>
            <div className="text-sm text-gray-600 mt-1">View past conversations & bookmarks</div>
          </button>

          <button
            onClick={() => navigate('/memory')}
            className="p-4 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all text-left group"
          >
            <Brain className="w-8 h-8 text-blue-600 mb-2 group-hover:scale-110 transition-transform" />
            <div className="font-medium text-gray-900">Memory Dashboard</div>
            <div className="text-sm text-gray-600 mt-1">Your personality relationships</div>
          </button>

          <button
            onClick={() => navigate('/progress')}
            className="p-4 bg-white border-2 border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all text-left group"
          >
            <TrendingUp className="w-8 h-8 text-purple-600 mb-2 group-hover:scale-110 transition-transform" />
            <div className="font-medium text-gray-900">Progress Dashboard</div>
            <div className="text-sm text-gray-600 mt-1">Streaks & achievements</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MyProfileTab;
