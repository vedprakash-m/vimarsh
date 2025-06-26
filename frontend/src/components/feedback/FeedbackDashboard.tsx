import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Star, 
  MessageSquare, 
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';

interface FeedbackAnalytics {
  total_feedback_count: number;
  average_rating: number;
  sentiment_distribution: Record<string, number>;
  common_themes: string[];
  improvement_suggestions: string[];
  spiritual_accuracy_score: number;
  user_satisfaction_trend: number[];
  feature_requests: Record<string, number>;
}

interface ContinuousImprovementMetrics {
  response_quality_trend: number[];
  user_engagement_metrics: Record<string, number>;
  spiritual_content_accuracy: number;
  feature_adoption_rates: Record<string, number>;
  performance_improvements: Record<string, any>;
  cost_optimization_impact: Record<string, number>;
  user_retention_metrics: Record<string, number>;
}

const FeedbackDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<FeedbackAnalytics | null>(null);
  const [metrics, setMetrics] = useState<ContinuousImprovementMetrics | null>(null);
  const [timeRange, setTimeRange] = useState('7');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [analyticsResponse, metricsResponse] = await Promise.all([
        fetch(`/api/feedback/analytics?days=${timeRange}`),
        fetch(`/api/feedback/improvement-metrics?days=${timeRange}`)
      ]);

      if (analyticsResponse.ok && metricsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        const metricsData = await metricsResponse.json();
        
        setAnalytics(analyticsData);
        setMetrics(metricsData);
        setError(null);
      } else {
        throw new Error('Failed to fetch analytics data');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const exportReport = async () => {
    try {
      const response = await fetch(`/api/feedback/export-report?days=${timeRange}&format=json`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `feedback-report-${timeRange}days.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="animate-spin text-blue-500" size={32} />
          <span className="ml-2 text-gray-600">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error: {error}</p>
          <button
            onClick={fetchAnalytics}
            className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Feedback Analytics</h1>
          <p className="text-gray-600">Monitor user feedback and continuous improvement metrics</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
          <button
            onClick={exportReport}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center space-x-2"
          >
            <Download size={16} />
            <span>Export</span>
          </button>
          <button
            onClick={fetchAnalytics}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
          >
            <RefreshCw size={16} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <MessageSquare className="text-blue-500" size={24} />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Total Feedback</p>
              <p className="text-2xl font-bold text-gray-900">{analytics?.total_feedback_count || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Star className="text-yellow-500" size={24} />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Average Rating</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics?.average_rating ? analytics.average_rating.toFixed(1) : '0.0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <TrendingUp className="text-green-500" size={24} />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">Spiritual Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">
                {analytics?.spiritual_accuracy_score ? 
                  (analytics.spiritual_accuracy_score * 100).toFixed(1) + '%' : '0%'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <Users className="text-purple-500" size={24} />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-600">User Engagement</p>
              <p className="text-2xl font-bold text-gray-900">
                {metrics?.user_engagement_metrics?.active_users || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts and Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
          <div className="space-y-3">
            {analytics?.sentiment_distribution && Object.entries(analytics.sentiment_distribution).map(([sentiment, count]) => (
              <div key={sentiment} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">{sentiment.replace('_', ' ')}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        sentiment.includes('positive') ? 'bg-green-500' :
                        sentiment.includes('negative') ? 'bg-red-500' : 'bg-gray-400'
                      }`}
                      style={{
                        width: `${(count / (analytics?.total_feedback_count || 1)) * 100}%`
                      }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Common Themes */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Common Themes</h3>
          <div className="space-y-2">
            {analytics?.common_themes?.slice(0, 8).map((theme, index) => (
              <div key={index} className="px-3 py-2 bg-blue-50 text-blue-800 rounded-lg text-sm">
                {theme}
              </div>
            ))}
          </div>
        </div>

        {/* Feature Requests */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Requests</h3>
          <div className="space-y-3">
            {analytics?.feature_requests && Object.entries(analytics.feature_requests)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 5)
              .map(([feature, count]) => (
                <div key={feature} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{feature}</span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                    {count}
                  </span>
                </div>
              ))}
          </div>
        </div>

        {/* Improvement Suggestions */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Improvement Suggestions</h3>
          <div className="space-y-2">
            {analytics?.improvement_suggestions?.slice(0, 5).map((suggestion, index) => (
              <div key={index} className="p-3 bg-orange-50 border-l-4 border-orange-400 text-orange-800 text-sm">
                {suggestion}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Continuous Improvement Metrics */}
      {metrics && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Continuous Improvement Metrics</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h4 className="font-medium text-gray-900 mb-3">Performance Improvements</h4>
              <div className="space-y-2">
                {Object.entries(metrics.performance_improvements).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                    <span className="font-medium text-gray-900">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h4 className="font-medium text-gray-900 mb-3">Cost Optimization</h4>
              <div className="space-y-2">
                {Object.entries(metrics.cost_optimization_impact).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                    <span className="font-medium text-green-600">
                      {typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h4 className="font-medium text-gray-900 mb-3">User Retention</h4>
              <div className="space-y-2">
                {Object.entries(metrics.user_retention_metrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                    <span className="font-medium text-blue-600">
                      {typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackDashboard;
