import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  RefreshCw, 
  Clock, 
  Monitor,
  TrendingUp,
  Activity,
  Zap
} from 'lucide-react';
import { adminService } from '../../services/adminService';

interface TestResult {
  id: string;
  name: string;
  status: 'running' | 'passed' | 'failed' | 'pending';
  duration?: number;
  lastRun?: string;
  errorMessage?: string;
  details?: any;
}

interface SystemMetric {
  name: string;
  value: string | number;
  status: 'healthy' | 'warning' | 'critical';
  trend?: 'up' | 'down' | 'stable';
  description: string;
}

interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime?: string;
  endTime?: string;
  type: 'content_processing' | 'validation' | 'migration' | 'optimization';
}

const TestingMonitoring: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric[]>([]);
  const [activeTasks, setActiveTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'tests' | 'metrics' | 'tasks'>('tests');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadAllData();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(loadAllData, 10000); // Refresh every 10 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadAllData = async () => {
    try {
      setError(null);
      
      // Load content overview for basic metrics
      const overview = await adminService.getContentOverview();
      
      // Mock test data (replace with real API calls when available)
      setTestResults([
        {
          id: 'personality_validation',
          name: 'Personality Content Validation',
          status: overview.success_rate > 80 ? 'passed' : 'failed',
          duration: 2500,
          lastRun: new Date().toISOString(),
          details: {
            personalities_tested: overview.total_personalities,
            success_rate: overview.success_rate,
            rag_ready: overview.rag_ready
          }
        },
        {
          id: 'vector_db_test',
          name: 'Vector Database Connectivity',
          status: overview.total_personalities > 0 ? 'passed' : 'failed',
          duration: 1200,
          lastRun: new Date().toISOString(),
          details: {
            total_vectors: overview.total_personalities * 1000, // Estimated
            connection_status: 'healthy'
          }
        },
        {
          id: 'embedding_service',
          name: 'Embedding Service Health',
          status: 'passed',
          duration: 800,
          lastRun: new Date().toISOString(),
          details: {
            service: 'Gemini Embedding',
            dimension: 768,
            response_time: '< 100ms'
          }
        },
        {
          id: 'cosmos_db_test',
          name: 'Cosmos DB Integration',
          status: overview.total_personalities > 0 ? 'passed' : 'failed',
          duration: 1500,
          lastRun: new Date().toISOString(),
          details: {
            database: 'vimarsh-multi-personality',
            containers: ['personality_vectors'],
            status: 'connected'
          }
        }
      ]);

      // Mock system metrics
      setSystemMetrics([
        {
          name: 'Cosmos DB RU/s',
          value: '400/1000',
          status: 'healthy',
          trend: 'stable',
          description: 'Request units consumed per second'
        },
        {
          name: 'Vector Search Latency',
          value: '45ms',
          status: 'healthy',
          trend: 'down',
          description: 'Average response time for vector searches'
        },
        {
          name: 'Personality Success Rate',
          value: `${overview.success_rate}%`,
          status: overview.success_rate > 80 ? 'healthy' : 'warning',
          trend: overview.success_rate > 80 ? 'up' : 'down',
          description: 'Percentage of personalities ready for RAG'
        },
        {
          name: 'Active Personalities',
          value: `${overview.rag_ready}/${overview.total_personalities}`,
          status: overview.rag_ready > 5 ? 'healthy' : 'warning',
          trend: 'stable',
          description: 'Personalities ready for production use'
        },
        {
          name: 'Memory Usage',
          value: '68%',
          status: 'healthy',
          trend: 'stable',
          description: 'System memory utilization'
        },
        {
          name: 'Storage Usage',
          value: '2.4GB',
          status: 'healthy',
          trend: 'up',
          description: 'Vector and content storage consumed'
        }
      ]);

      // Mock active tasks
      setActiveTasks([
        {
          id: 'content_sync_' + Date.now(),
          name: 'Content Synchronization',
          status: 'running',
          progress: 65,
          startTime: new Date(Date.now() - 300000).toISOString(),
          type: 'content_processing'
        },
        {
          id: 'vector_optimization_' + Date.now(),
          name: 'Vector Index Optimization',
          status: 'pending',
          progress: 0,
          type: 'optimization'
        }
      ]);

    } catch (err) {
      console.error('❌ Failed to load monitoring data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load monitoring data');
    } finally {
      setLoading(false);
    }
  };

  const runTest = async (testId: string) => {
    setTestResults(prev => prev.map(test => 
      test.id === testId 
        ? { ...test, status: 'running', errorMessage: undefined }
        : test
    ));

    // Simulate test execution
    setTimeout(() => {
      setTestResults(prev => prev.map(test => 
        test.id === testId 
          ? { 
              ...test, 
              status: Math.random() > 0.2 ? 'passed' : 'failed',
              lastRun: new Date().toISOString(),
              duration: Math.floor(Math.random() * 3000) + 500
            }
          : test
      ));
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
      case 'completed':
      case 'healthy':
        return '#10B981';
      case 'running':
      case 'pending':
        return '#F59E0B';
      case 'failed':
      case 'critical':
        return '#EF4444';
      case 'warning':
        return '#F59E0B';
      default:
        return '#6B7280';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
      case 'completed':
      case 'healthy':
        return <CheckCircle size={16} style={{ color: '#10B981' }} />;
      case 'running':
        return <RefreshCw size={16} style={{ color: '#F59E0B', animation: 'spin 1s linear infinite' }} />;
      case 'pending':
        return <Clock size={16} style={{ color: '#F59E0B' }} />;
      case 'failed':
      case 'critical':
        return <XCircle size={16} style={{ color: '#EF4444' }} />;
      case 'warning':
        return <AlertTriangle size={16} style={{ color: '#F59E0B' }} />;
      default:
        return <Monitor size={16} style={{ color: '#6B7280' }} />;
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp size={12} style={{ color: '#10B981' }} />;
      case 'down':
        return <TrendingUp size={12} style={{ color: '#EF4444', transform: 'rotate(180deg)' }} />;
      case 'stable':
        return <Activity size={12} style={{ color: '#6B7280' }} />;
      default:
        return null;
    }
  };

  if (loading && testResults.length === 0) {
    return (
      <div className="vimarsh-admin-loading" style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="loading-spinner"></div>
        <p style={{ marginLeft: '1rem' }}>Loading monitoring data...</p>
      </div>
    );
  }

  return (
    <div className="vimarsh-admin-dashboard">
      {/* Header */}
      <div className="vimarsh-admin-header">
        <div>
          <h1>📊 Testing & Monitoring</h1>
          <p style={{ color: '#6b7280', marginTop: '0.5rem' }}>
            System health, test results, and active task monitoring
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <button 
            className="vimarsh-btn-secondary"
            onClick={loadAllData}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="vimarsh-admin-tabs">
        <button
          className={`tab ${activeTab === 'tests' ? 'active' : ''}`}
          onClick={() => setActiveTab('tests')}
        >
          🧪 Tests ({testResults.length})
        </button>
        <button
          className={`tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          📈 Metrics ({systemMetrics.length})
        </button>
        <button
          className={`tab ${activeTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setActiveTab('tasks')}
        >
          ⚡ Tasks ({activeTasks.length})
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="vimarsh-admin-error" style={{ marginBottom: '1.5rem' }}>
          <AlertTriangle size={20} />
          <div>
            <strong>Monitoring Error</strong>
            <p>{error}</p>
          </div>
          <button 
            className="vimarsh-btn-secondary" 
            onClick={loadAllData}
            style={{ marginLeft: 'auto' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Tests Tab */}
      {activeTab === 'tests' && (
        <div className="vimarsh-admin-card">
          <div className="card-header">
            <h3>🧪 System Tests</h3>
            <button 
              className="vimarsh-btn-primary"
              onClick={() => testResults.forEach(test => runTest(test.id))}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <Play size={16} />
              Run All Tests
            </button>
          </div>
          
          <div style={{ padding: '1rem' }}>
            <div style={{ display: 'grid', gap: '1rem' }}>
              {testResults.map((test) => (
                <div
                  key={test.id}
                  style={{
                    border: `1px solid ${getStatusColor(test.status)}40`,
                    borderRadius: '0.75rem',
                    padding: '1.5rem',
                    backgroundColor: `${getStatusColor(test.status)}05`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      {getStatusIcon(test.status)}
                      <div>
                        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>
                          {test.name}
                        </h4>
                        <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: '#6b7280' }}>
                          {test.lastRun && `Last run: ${new Date(test.lastRun).toLocaleString()}`}
                          {test.duration && ` • Duration: ${test.duration}ms`}
                        </p>
                      </div>
                    </div>
                    <button
                      className="vimarsh-btn-secondary"
                      onClick={() => runTest(test.id)}
                      disabled={test.status === 'running'}
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '0.5rem',
                        opacity: test.status === 'running' ? 0.6 : 1
                      }}
                    >
                      {test.status === 'running' ? <RefreshCw size={14} /> : <Play size={14} />}
                      {test.status === 'running' ? 'Running...' : 'Run Test'}
                    </button>
                  </div>

                  {test.details && (
                    <div style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.7)',
                      borderRadius: '0.5rem',
                      padding: '1rem',
                      fontSize: '0.875rem'
                    }}>
                      <strong>Test Details:</strong>
                      <pre style={{ 
                        margin: '0.5rem 0 0 0', 
                        fontSize: '0.75rem',
                        color: '#374151',
                        overflow: 'auto'
                      }}>
                        {JSON.stringify(test.details, null, 2)}
                      </pre>
                    </div>
                  )}

                  {test.errorMessage && (
                    <div style={{
                      backgroundColor: '#FEF2F2',
                      border: '1px solid #FECACA',
                      borderRadius: '0.5rem',
                      padding: '1rem',
                      marginTop: '1rem',
                      fontSize: '0.875rem',
                      color: '#DC2626'
                    }}>
                      <strong>Error:</strong> {test.errorMessage}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div className="vimarsh-admin-card">
          <div className="card-header">
            <h3>📈 System Metrics</h3>
          </div>
          
          <div style={{ padding: '1rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
              {systemMetrics.map((metric) => (
                <div
                  key={metric.name}
                  style={{
                    border: `1px solid ${getStatusColor(metric.status)}40`,
                    borderRadius: '0.75rem',
                    padding: '1.5rem',
                    backgroundColor: `${getStatusColor(metric.status)}05`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h4 style={{ margin: 0, fontSize: '0.875rem', fontWeight: '600', color: '#374151' }}>
                      {metric.name}
                    </h4>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {getTrendIcon(metric.trend)}
                      {getStatusIcon(metric.status)}
                    </div>
                  </div>
                  
                  <div style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: '700',
                    color: getStatusColor(metric.status),
                    marginBottom: '0.5rem'
                  }}>
                    {metric.value}
                  </div>
                  
                  <p style={{ 
                    margin: 0, 
                    fontSize: '0.75rem', 
                    color: '#6b7280',
                    lineHeight: '1.4'
                  }}>
                    {metric.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className="vimarsh-admin-card">
          <div className="card-header">
            <h3>⚡ Active Tasks</h3>
          </div>
          
          <div style={{ padding: '1rem' }}>
            {activeTasks.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                <Zap size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
                <p>No active tasks at the moment.</p>
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '1rem' }}>
                {activeTasks.map((task) => (
                  <div
                    key={task.id}
                    style={{
                      border: `1px solid ${getStatusColor(task.status)}40`,
                      borderRadius: '0.75rem',
                      padding: '1.5rem',
                      backgroundColor: `${getStatusColor(task.status)}05`
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        {getStatusIcon(task.status)}
                        <div>
                          <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: '600' }}>
                            {task.name}
                          </h4>
                          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: '#6b7280' }}>
                            Type: {task.type.replace('_', ' ')}
                            {task.startTime && ` • Started: ${new Date(task.startTime).toLocaleString()}`}
                          </p>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '1.25rem', fontWeight: '600', color: getStatusColor(task.status) }}>
                          {task.progress}%
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div style={{
                      width: '100%',
                      height: '8px',
                      backgroundColor: '#f3f4f6',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div
                        style={{
                          height: '100%',
                          backgroundColor: getStatusColor(task.status),
                          width: `${task.progress}%`,
                          transition: 'width 0.3s ease'
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* CSS for spinning animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default TestingMonitoring;
