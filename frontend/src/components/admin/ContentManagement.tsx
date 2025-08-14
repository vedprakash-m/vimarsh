import React, { useState, useEffect } from 'react';
import { useAdmin } from '../../contexts/AdminProviderContext';
import { adminService } from '../../services/adminService';
import { RefreshCw, Play, Trash2, Database, CheckCircle, Clock, AlertTriangle, Filter } from 'lucide-react';
import '../../styles/admin.css';

interface PersonalityInfo {
  id: string;
  name: string;
  domain: string;
  status: string;
  content_sources: number;
  total_chunks: number;
  rag_enabled: boolean;
  last_updated?: string;
}

interface ContentOverview {
  total_personalities: number;
  rag_ready: number;
  success_rate: string;
  personalities: PersonalityInfo[];
  last_updated: string;
}

interface TaskInfo {
  task_id: string;
  personality_id: string;
  task_type: string;
  status: string;
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
}

const ContentManagement = (): JSX.Element => {
  const { user } = useAdmin();
  const [contentOverview, setContentOverview] = useState<ContentOverview | null>(null);
  const [tasks, setTasks] = useState<TaskInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPersonality, setSelectedPersonality] = useState<PersonalityInfo | null>(null);
  const [processingPersonality, setProcessingPersonality] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'personalities' | 'tasks'>('overview');
  const [filter, setFilter] = useState({
    domain: '',
    status: '',
    search: ''
  });

  useEffect(() => {
    if (user?.permissions.can_access_admin_endpoints) {
      loadContentOverview();
      loadTasks();
    }
  }, [user]);

  const loadContentOverview = async () => {
    try {
      setLoading(true);
      const accessToken = await getAccessToken();
      const overview = await adminService.getContentOverview(accessToken);
      setContentOverview(overview);
    } catch (error) {
      console.error('Failed to load content overview:', error);
      setContentOverview(null);
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    try {
      const accessToken = await getAccessToken();
      const response = await adminService.getAllTasks(undefined, accessToken);
      setTasks(response.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      setTasks([]);
    }
  };

  const getAccessToken = async (): Promise<string> => {
    // Implementation would get token from MSAL
    return 'mock-token';
  };

  const handleProcessPersonality = async (personalityId: string, forceReprocess: boolean = false) => {
    try {
      setProcessingPersonality(personalityId);
      const accessToken = await getAccessToken();
      
      const response = await adminService.processPersonalityContent(personalityId, forceReprocess, accessToken);
      
      if (response.success) {
        console.log(`Processing started for ${personalityId}: ${response.task_id}`);
        await loadTasks();
      }
    } catch (error) {
      console.error(`Failed to process personality ${personalityId}:`, error);
    } finally {
      setProcessingPersonality(null);
    }
  };

  const handleDeletePersonalityContent = async (personalityId: string) => {
    if (!window.confirm(`Are you sure you want to delete all content for ${personalityId}?`)) {
      return;
    }

    try {
      const accessToken = await getAccessToken();
      const response = await adminService.deletePersonalityContent(personalityId, accessToken);
      
      if (response.success) {
        console.log(`Deleted content for ${personalityId}: ${response.deleted_count} items`);
        await loadContentOverview();
      }
    } catch (error) {
      console.error(`Failed to delete content for ${personalityId}:`, error);
    }
  };

  const handleRegenerateEmbeddings = async (personalityId: string) => {
    try {
      setProcessingPersonality(personalityId);
      const accessToken = await getAccessToken();
      
      const response = await adminService.regenerateEmbeddings(personalityId, accessToken);
      
      if (response.success) {
        console.log(`Embedding regeneration started for ${personalityId}: ${response.task_id}`);
        await loadTasks();
      }
    } catch (error) {
      console.error(`Failed to regenerate embeddings for ${personalityId}:`, error);
    } finally {
      setProcessingPersonality(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'rag_ready':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processed':
        return <Database className="w-5 h-5 text-blue-500" />;
      case 'processing':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'in_progress':
        return 'text-yellow-600 bg-yellow-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const filteredPersonalities = contentOverview?.personalities.filter(personality => {
    const matchesDomain = !filter.domain || personality.domain === filter.domain;
    const matchesStatus = !filter.status || personality.status === filter.status;
    const matchesSearch = !filter.search || 
      personality.name.toLowerCase().includes(filter.search.toLowerCase()) ||
      personality.id.toLowerCase().includes(filter.search.toLowerCase());
    
    return matchesDomain && matchesStatus && matchesSearch;
  }) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Loading content overview...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Content Management</h2>
        <button
          onClick={() => {
            loadContentOverview();
            loadTasks();
          }}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'overview', label: 'Overview', icon: Database },
            { key: 'personalities', label: 'Personalities', icon: CheckCircle },
            { key: 'tasks', label: 'Tasks', icon: Clock }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key as any)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && contentOverview && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <Database className="w-8 h-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Personalities</p>
                <p className="text-2xl font-semibold text-gray-900">{contentOverview.total_personalities}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">RAG Ready</p>
                <p className="text-2xl font-semibold text-gray-900">{contentOverview.rag_ready}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-yellow-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Success Rate</p>
                <p className="text-2xl font-semibold text-gray-900">{contentOverview.success_rate}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Personalities Tab */}
      {activeTab === 'personalities' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center space-x-4">
              <Filter className="w-5 h-5 text-gray-500" />
              <input
                type="text"
                placeholder="Search personalities..."
                value={filter.search}
                onChange={(e) => setFilter({ ...filter, search: e.target.value })}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
              />
              <select
                value={filter.domain}
                onChange={(e) => setFilter({ ...filter, domain: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">All Domains</option>
                <option value="spiritual">Spiritual</option>
                <option value="scientific">Scientific</option>
                <option value="philosophical">Philosophical</option>
                <option value="historical">Historical</option>
                <option value="literary">Literary</option>
              </select>
              <select
                value={filter.status}
                onChange={(e) => setFilter({ ...filter, status: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="">All Statuses</option>
                <option value="rag_ready">RAG Ready</option>
                <option value="processed">Processed</option>
                <option value="processing">Processing</option>
                <option value="not_acquired">Not Acquired</option>
              </select>
            </div>
          </div>

          {/* Personalities List */}
          <div className="space-y-3">
            {filteredPersonalities.map((personality) => (
              <div key={personality.id} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(personality.status)}
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{personality.name}</h3>
                      <p className="text-sm text-gray-500">
                        {personality.domain} • {personality.total_chunks} chunks • 
                        {personality.rag_enabled ? ' RAG Enabled' : ' RAG Disabled'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleProcessPersonality(personality.id)}
                      disabled={processingPersonality === personality.id}
                      className="flex items-center px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Process
                    </button>
                    
                    <button
                      onClick={() => handleRegenerateEmbeddings(personality.id)}
                      disabled={processingPersonality === personality.id}
                      className="flex items-center px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                    >
                      <RefreshCw className="w-4 h-4 mr-1" />
                      Regenerate
                    </button>
                    
                    <button
                      onClick={() => handleDeletePersonalityContent(personality.id)}
                      className="flex items-center px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow border overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Tasks</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {tasks.length === 0 ? (
                <div className="px-6 py-8 text-center text-gray-500">
                  No tasks found
                </div>
              ) : (
                tasks.map((task) => (
                  <div key={task.task_id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {task.task_type} - {task.personality_id}
                        </h4>
                        <p className="text-sm text-gray-500">{task.message}</p>
                        <p className="text-xs text-gray-400">
                          Created: {new Date(task.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTaskStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                        {task.status === 'in_progress' && (
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${task.progress}%` }}
                            ></div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentManagement;
