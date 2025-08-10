import React, { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import '../styles/gap-remediation.css';

interface ServiceHealth {
  available: boolean;
  api_key_configured?: boolean;
  last_successful_call?: string;
  failure_rate_24h?: number;
  response_time?: number;
  error_rate?: number;
}

interface SystemCapabilities {
  llm_service?: ServiceHealth;
  vector_search?: ServiceHealth;
  memory_persistence?: ServiceHealth & {
    mode?: 'persistent' | 'in_memory';
    session_count?: number;
  };
  citation_grounding?: ServiceHealth & {
    validator_loaded?: boolean;
    accuracy_rate?: number;
  };
}

interface ServiceStatusResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  deployment_readiness: number;
  capabilities: SystemCapabilities;
  fallback_active?: string[];
  recommendations?: string[];
  timestamp: string;
}

interface ServiceStatusIndicatorProps {
  className?: string;
  compact?: boolean;
  showDetails?: boolean;
}

const ServiceStatusIndicator: React.FC<ServiceStatusIndicatorProps> = ({ 
  className = '', 
  compact = false, 
  showDetails = false 
}) => {
  const { currentLanguage } = useLanguage();
  const [systemStatus, setSystemStatus] = useState<ServiceStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(showDetails);

  useEffect(() => {
    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/health');
      
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      
      const data: ServiceStatusResponse = await response.json();
      setSystemStatus(data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch system status:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Set fallback status when health check fails
      setSystemStatus({
        status: 'degraded',
        deployment_readiness: 0.3,
        capabilities: {},
        fallback_active: ['health_check_failed'],
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string, readiness: number) => {
    if (status === 'healthy' && readiness > 0.8) return 'green';
    if (status === 'healthy' && readiness > 0.6) return 'yellow';
    return 'red';
  };

  const getServiceIcon = (serviceName: string, health?: ServiceHealth) => {
    const isAvailable = health?.available ?? false;
    
    const icons = {
      llm_service: isAvailable ? '🤖' : '🔴',
      vector_search: isAvailable ? '🔍' : '🔴',
      memory_persistence: isAvailable ? '🧠' : '🔴',
      citation_grounding: isAvailable ? '📚' : '🔴'
    };
    
    return icons[serviceName as keyof typeof icons] || '⚙️';
  };

  const getServiceLabel = (serviceName: string) => {
    const labels = {
      llm_service: currentLanguage === 'Hindi' ? 'AI सेवा' : 'AI Service',
      vector_search: currentLanguage === 'Hindi' ? 'खोज सेवा' : 'Search Service',
      memory_persistence: currentLanguage === 'Hindi' ? 'मेमोरी सेवा' : 'Memory Service',
      citation_grounding: currentLanguage === 'Hindi' ? 'उद्धरण सेवा' : 'Citation Service'
    };
    
    return labels[serviceName as keyof typeof labels] || serviceName;
  };

  if (loading && !systemStatus) {
    return (
      <div className={`service-status-indicator loading ${className}`}>
        <div className="flex items-center gap-2 p-3 bg-gray-100 rounded-lg">
          <div className="animate-spin">⏳</div>
          <span className="text-sm text-gray-600">
            {currentLanguage === 'Hindi' ? 'सिस्टम स्थिति जांच रहे हैं...' : 'Checking system status...'}
          </span>
        </div>
      </div>
    );
  }

  if (!systemStatus) return null;

  const statusColor = getStatusColor(systemStatus.status, systemStatus.deployment_readiness);
  const readinessPercentage = Math.round(systemStatus.deployment_readiness * 100);

  if (compact) {
    return (
      <div className={`service-status-indicator compact ${className}`}>
        <button
          onClick={() => setExpanded(!expanded)}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
            statusColor === 'green' ? 'bg-green-100 hover:bg-green-200' :
            statusColor === 'yellow' ? 'bg-yellow-100 hover:bg-yellow-200' :
            'bg-red-100 hover:bg-red-200'
          }`}
        >
          <span className={`w-2 h-2 rounded-full ${
            statusColor === 'green' ? 'bg-green-500' :
            statusColor === 'yellow' ? 'bg-yellow-500' :
            'bg-red-500'
          }`} />
          <span className="text-sm font-medium">
            {currentLanguage === 'Hindi' ? 'सिस्टम' : 'System'}: {readinessPercentage}%
          </span>
          <span className="text-xs">{expanded ? '▼' : '▶'}</span>
        </button>
      </div>
    );
  }

  return (
    <div className={`service-status-indicator ${className}`}>
      <div className={`border rounded-lg p-4 ${
        statusColor === 'green' ? 'bg-green-50 border-green-200' :
        statusColor === 'yellow' ? 'bg-yellow-50 border-yellow-200' :
        'bg-red-50 border-red-200'
      }`}>
        {/* Main Status Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <span className={`w-3 h-3 rounded-full ${
              statusColor === 'green' ? 'bg-green-500' :
              statusColor === 'yellow' ? 'bg-yellow-500' :
              'bg-red-500'
            }`} />
            <div>
              <h3 className="font-medium text-gray-900">
                {currentLanguage === 'Hindi' ? 'सिस्टम स्थिति' : 'System Status'}
              </h3>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>
                  {currentLanguage === 'Hindi' ? 'तैयारी' : 'Readiness'}: {readinessPercentage}%
                </span>
                <span className="text-xs">
                  ({systemStatus.status})
                </span>
              </div>
            </div>
          </div>
          
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            title={expanded ? 'Hide details' : 'Show details'}
          >
            {expanded ? '▼' : '▶'}
          </button>
        </div>

        {/* System Mode Explanation */}
        <div className="mb-3">
          {systemStatus.deployment_readiness > 0.8 ? (
            <div className="text-sm text-green-700">
              ✅ {currentLanguage === 'Hindi' 
                ? 'सभी सेवाएं उपलब्ध हैं - पूर्ण AI अनुभव सक्रिय' 
                : 'All services available - Full AI experience active'}
            </div>
          ) : systemStatus.deployment_readiness > 0.6 ? (
            <div className="text-sm text-yellow-700">
              ⚠️ {currentLanguage === 'Hindi' 
                ? 'कुछ सेवाएं सीमित हैं - बेसिक AI अनुभव सक्रिय' 
                : 'Some services limited - Basic AI experience active'}
            </div>
          ) : (
            <div className="text-sm text-red-700">
              🔄 {currentLanguage === 'Hindi' 
                ? 'पारंपरिक ज्ञान मोड सक्रिय - AI सेवाएं पुनर्स्थापना में' 
                : 'Traditional wisdom mode active - AI services recovering'}
            </div>
          )}
        </div>

        {/* Expanded Details */}
        {expanded && (
          <div className="space-y-3 pt-3 border-t border-gray-200">
            {/* Service Grid */}
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(systemStatus.capabilities).map(([serviceName, health]) => (
                <div key={serviceName} className="flex items-center gap-2 p-2 bg-white rounded border">
                  <span className="text-lg">{getServiceIcon(serviceName, health)}</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">
                      {getServiceLabel(serviceName)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {health?.available ? (
                        currentLanguage === 'Hindi' ? 'उपलब्ध' : 'Available'
                      ) : (
                        currentLanguage === 'Hindi' ? 'अनुपलब्ध' : 'Unavailable'
                      )}
                      {health?.mode && ` (${health.mode})`}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Active Fallbacks */}
            {systemStatus.fallback_active && systemStatus.fallback_active.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <div className="text-sm font-medium text-yellow-800 mb-1">
                  {currentLanguage === 'Hindi' ? 'सक्रिय फॉलबैक:' : 'Active Fallbacks:'}
                </div>
                <div className="text-xs text-yellow-700">
                  {systemStatus.fallback_active.join(', ')}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {systemStatus.recommendations && systemStatus.recommendations.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded p-3">
                <div className="text-sm font-medium text-blue-800 mb-1">
                  {currentLanguage === 'Hindi' ? 'सुझाव:' : 'Recommendations:'}
                </div>
                <div className="text-xs text-blue-700 space-y-1">
                  {systemStatus.recommendations.map((rec, index) => (
                    <div key={index}>• {rec}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Updated */}
            <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-100">
              {currentLanguage === 'Hindi' ? 'अंतिम अपडेट' : 'Last updated'}: {' '}
              {new Date(systemStatus.timestamp).toLocaleTimeString()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ServiceStatusIndicator;
