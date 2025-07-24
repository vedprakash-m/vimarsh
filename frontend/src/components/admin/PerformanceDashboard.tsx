/**
 * Performance Dashboard Component for Vimarsh Admin Interface
 * 
 * Provides comprehensive performance monitoring including:
 * - Real-time performance metrics per personality
 * - Cache performance and optimization
 * - Performance alerts and recommendations
 * - System resource monitoring
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Speed as PerformanceIcon,
  Memory as CacheIcon,
  Warning as AlertIcon,
  TrendingUp as OptimizeIcon,
  Refresh as RefreshIcon,
  Timeline as MetricsIcon,
  Storage as StorageIcon,
  Psychology as PersonalityIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

// Types
interface PerformanceMetrics {
  personality_id?: string;
  total_requests: number;
  avg_response_time_ms: number;
  error_rate: number;
  cache_hit_rate: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
  active_users: number;
  requests_per_minute: number;
  last_updated: string;
}

interface CacheMetrics {
  personality_id?: string;
  hit_count: number;
  miss_count: number;
  hit_rate: number;
  cache_size_bytes: number;
  entry_count: number;
}

interface PerformanceAlert {
  alert_id: string;
  personality_id?: string;
  alert_type: string;
  severity: string;
  message: string;
  threshold_value: number;
  current_value: number;
  created_at: string;
}

interface OptimizationRecommendation {
  type: string;
  personality_id?: string;
  priority: string;
  title: string;
  description: string;
  recommendations: string[];
}

const PerformanceDashboard: React.FC = () => {
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedPersonality, setSelectedPersonality] = useState<string>('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // Data state
  const [performanceMetrics, setPerformanceMetrics] = useState<Record<string, PerformanceMetrics>>({});
  const [cacheMetrics, setCacheMetrics] = useState<Record<string, CacheMetrics>>({});
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [recommendations, setRecommendations] = useState<OptimizationRecommendation[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<any>(null);
  
  // Dialog state
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<PerformanceAlert | null>(null);
  const [cacheDialogOpen, setCacheDialogOpen] = useState(false);

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [metricsResponse, cacheResponse, alertsResponse, recommendationsResponse] = await Promise.all([
        fetch(`/admin/performance/metrics${selectedPersonality !== 'all' ? `?personality_id=${selectedPersonality}` : ''}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch(`/admin/performance/cache-metrics${selectedPersonality !== 'all' ? `?personality_id=${selectedPersonality}` : ''}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch(`/admin/performance/alerts${selectedPersonality !== 'all' ? `?personality_id=${selectedPersonality}` : ''}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch(`/admin/performance/recommendations${selectedPersonality !== 'all' ? `?personality_id=${selectedPersonality}` : ''}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        })
      ]);

      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setPerformanceMetrics(metricsData.metrics || {});
        setSystemMetrics(metricsData.metrics?.system || null);
      }

      if (cacheResponse.ok) {
        const cacheData = await cacheResponse.json();
        setCacheMetrics(cacheData.cache_metrics || {});
      }

      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData.alerts || []);
      }

      if (recommendationsResponse.ok) {
        const recommendationsData = await recommendationsResponse.json();
        setRecommendations(recommendationsData.recommendations || []);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load performance data');
    } finally {
      setLoading(false);
    }
  }, [selectedPersonality]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      loadData();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, loadData]);

  // Helper functions
  const getPersonalityIcon = (personalityId: string) => {
    const icons: Record<string, string> = {
      'krishna': '🕉️',
      'einstein': '🔬',
      'lincoln': '🏛️',
      'marcus_aurelius': '🤔'
    };
    return icons[personalityId] || '🎭';
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  // Event handlers
  const handleResolveAlert = async (alertId: string) => {
    try {
      const response = await fetch('/admin/performance/alerts/resolve', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ alert_id: alertId })
      });

      if (response.ok) {
        setAlerts(prev => prev.filter(alert => alert.alert_id !== alertId));
        setAlertDialogOpen(false);
      } else {
        throw new Error('Failed to resolve alert');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve alert');
    }
  };

  const handleWarmCache = async (personalityId: string) => {
    try {
      const response = await fetch('/admin/performance/cache/warm', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ personality_id: personalityId })
      });

      if (response.ok) {
        // Refresh cache metrics
        loadData();
      } else {
        throw new Error('Failed to warm cache');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to warm cache');
    }
  };

  const handleOptimizeCache = async () => {
    try {
      const response = await fetch('/admin/performance/cache/optimize', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Refresh metrics
        loadData();
      } else {
        throw new Error('Failed to optimize cache');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to optimize cache');
    }
  };

  const openAlertDialog = (alert: PerformanceAlert) => {
    setSelectedAlert(alert);
    setAlertDialogOpen(true);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Performance Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Personality</InputLabel>
            <Select
              value={selectedPersonality}
              onChange={(e) => setSelectedPersonality(e.target.value)}
              label="Personality"
            >
              <MenuItem value="all">All Personalities</MenuItem>
              <MenuItem value="krishna">🕉️ Krishna</MenuItem>
              <MenuItem value="einstein">🔬 Einstein</MenuItem>
              <MenuItem value="lincoln">🏛️ Lincoln</MenuItem>
              <MenuItem value="marcus_aurelius">🤔 Marcus Aurelius</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadData}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant={autoRefresh ? 'contained' : 'outlined'}
            onClick={() => setAutoRefresh(!autoRefresh)}
            size="small"
          >
            Auto-refresh
          </Button>
        </Box>
      </Box>

      {/* Alerts Banner */}
      {alerts.length > 0 && (
        <Alert 
          severity="warning" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => setSelectedTab(2)}>
              View All ({alerts.length})
            </Button>
          }
        >
          {alerts.length} active performance alert{alerts.length !== 1 ? 's' : ''} require attention
        </Alert>
      )}

      {/* Tabs */}
      <Tabs
        value={selectedTab}
        onChange={(_, newValue) => setSelectedTab(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab icon={<MetricsIcon />} label="Performance Metrics" />
        <Tab icon={<CacheIcon />} label="Cache Performance" />
        <Tab icon={<AlertIcon />} label={`Alerts (${alerts.length})`} />
        <Tab icon={<OptimizeIcon />} label={`Recommendations (${recommendations.length})`} />
      </Tabs>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Tab Content */}
      {!loading && (
        <>
          {/* Performance Metrics Tab */}
          {selectedTab === 0 && (
            <Grid container spacing={3}>
              {/* System Overview */}
              {systemMetrics && (
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        System Overview
                      </Typography>
                      <Grid container spacing={3}>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary">
                              {systemMetrics.total_requests || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Total Requests
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary">
                              {formatDuration(systemMetrics.avg_response_time_ms || 0)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Avg Response Time
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color={systemMetrics.global_error_rate > 5 ? 'error' : 'primary'}>
                              {(systemMetrics.global_error_rate || 0).toFixed(1)}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Error Rate
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={3}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="h4" color="primary">
                              {systemMetrics.active_personalities || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Active Personalities
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Personality Metrics */}
              {Object.entries(performanceMetrics).map(([personalityId, metrics]) => (
                personalityId !== 'system' && (
                  <Grid item xs={12} md={6} key={personalityId}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                          <span style={{ fontSize: '1.5rem' }}>
                            {getPersonalityIcon(personalityId)}
                          </span>
                          <Typography variant="h6">
                            {personalityId.charAt(0).toUpperCase() + personalityId.slice(1)}
                          </Typography>
                        </Box>
                        
                        <Grid container spacing={2}>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Requests
                            </Typography>
                            <Typography variant="h6">
                              {metrics.total_requests}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Avg Response Time
                            </Typography>
                            <Typography variant="h6">
                              {formatDuration(metrics.avg_response_time_ms)}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Error Rate
                            </Typography>
                            <Typography variant="h6" color={metrics.error_rate > 5 ? 'error.main' : 'inherit'}>
                              {metrics.error_rate.toFixed(1)}%
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2" color="text.secondary">
                              Cache Hit Rate
                            </Typography>
                            <Typography variant="h6" color={metrics.cache_hit_rate < 50 ? 'warning.main' : 'success.main'}>
                              {metrics.cache_hit_rate.toFixed(1)}%
                            </Typography>
                          </Grid>
                        </Grid>

                        {/* Performance Bars */}
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Memory Usage: {formatBytes(metrics.memory_usage_mb * 1024 * 1024)}
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={Math.min((metrics.memory_usage_mb / 1024) * 100, 100)}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              ))}
            </Grid>
          )}

          {/* Cache Performance Tab */}
          {selectedTab === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6">
                        Cache Performance
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => setCacheDialogOpen(true)}
                        >
                          Cache Actions
                        </Button>
                        <Button
                          variant="contained"
                          size="small"
                          onClick={handleOptimizeCache}
                        >
                          Optimize Cache
                        </Button>
                      </Box>
                    </Box>

                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Personality</TableCell>
                            <TableCell>Hit Rate</TableCell>
                            <TableCell>Entries</TableCell>
                            <TableCell>Size</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(cacheMetrics).map(([personalityId, metrics]) => (
                            <TableRow key={personalityId}>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <span>{getPersonalityIcon(personalityId)}</span>
                                  <Typography variant="body2">
                                    {personalityId.charAt(0).toUpperCase() + personalityId.slice(1)}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography variant="body2">
                                    {metrics.hit_rate.toFixed(1)}%
                                  </Typography>
                                  <LinearProgress
                                    variant="determinate"
                                    value={metrics.hit_rate}
                                    sx={{ width: 60, height: 4 }}
                                  />
                                </Box>
                              </TableCell>
                              <TableCell>{metrics.entry_count}</TableCell>
                              <TableCell>{formatBytes(metrics.cache_size_bytes)}</TableCell>
                              <TableCell>
                                <Button
                                  size="small"
                                  onClick={() => handleWarmCache(personalityId)}
                                >
                                  Warm Cache
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Alerts Tab */}
          {selectedTab === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Active Performance Alerts
                    </Typography>
                    
                    {alerts.length === 0 ? (
                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <SuccessIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
                        <Typography variant="h6" color="success.main">
                          No Active Alerts
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          All systems are performing within normal parameters
                        </Typography>
                      </Box>
                    ) : (
                      <List>
                        {alerts.map((alert, index) => (
                          <React.Fragment key={alert.alert_id}>
                            <ListItem
                              button
                              onClick={() => openAlertDialog(alert)}
                            >
                              <ListItemIcon>
                                <AlertIcon color={getSeverityColor(alert.severity) as any} />
                              </ListItemIcon>
                              <ListItemText
                                primary={
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Typography variant="subtitle2">
                                      {alert.message}
                                    </Typography>
                                    <Chip
                                      label={alert.severity}
                                      size="small"
                                      color={getSeverityColor(alert.severity) as any}
                                    />
                                  </Box>
                                }
                                secondary={
                                  <Box>
                                    <Typography variant="body2" color="text.secondary">
                                      {alert.personality_id && `${alert.personality_id} • `}
                                      Current: {alert.current_value.toFixed(1)} | 
                                      Threshold: {alert.threshold_value.toFixed(1)}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      {new Date(alert.created_at).toLocaleString()}
                                    </Typography>
                                  </Box>
                                }
                              />
                            </ListItem>
                            {index < alerts.length - 1 && <Divider />}
                          </React.Fragment>
                        ))}
                      </List>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}

          {/* Recommendations Tab */}
          {selectedTab === 3 && (
            <Grid container spacing={3}>
              {recommendations.length === 0 ? (
                <Grid item xs={12}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center', py: 4 }}>
                      <OptimizeIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
                      <Typography variant="h6" color="success.main">
                        No Optimization Needed
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Your system is performing optimally
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ) : (
                recommendations.map((recommendation, index) => (
                  <Grid item xs={12} md={6} key={index}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                          <OptimizeIcon color={getPriorityColor(recommendation.priority) as any} />
                          <Box>
                            <Typography variant="h6">
                              {recommendation.title}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <Chip
                                label={recommendation.priority}
                                size="small"
                                color={getPriorityColor(recommendation.priority) as any}
                              />
                              <Chip
                                label={recommendation.type}
                                size="small"
                                variant="outlined"
                              />
                              {recommendation.personality_id && (
                                <Chip
                                  label={recommendation.personality_id}
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </Box>
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {recommendation.description}
                        </Typography>
                        
                        <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                          Recommendations:
                        </Typography>
                        <List dense>
                          {recommendation.recommendations.map((rec, recIndex) => (
                            <ListItem key={recIndex} sx={{ pl: 0 }}>
                              <ListItemText
                                primary={
                                  <Typography variant="body2">
                                    • {rec}
                                  </Typography>
                                }
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                ))
              )}
            </Grid>
          )}
        </>
      )}

      {/* Alert Detail Dialog */}
      <Dialog
        open={alertDialogOpen}
        onClose={() => setAlertDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Performance Alert Details
        </DialogTitle>
        <DialogContent>
          {selectedAlert && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Alert Type
                  </Typography>
                  <Typography variant="body1">
                    {selectedAlert.alert_type.replace('_', ' ')}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Severity
                  </Typography>
                  <Chip
                    label={selectedAlert.severity}
                    color={getSeverityColor(selectedAlert.severity) as any}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Current Value
                  </Typography>
                  <Typography variant="body1">
                    {selectedAlert.current_value.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Threshold
                  </Typography>
                  <Typography variant="body1">
                    {selectedAlert.threshold_value.toFixed(2)}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Message
                  </Typography>
                  <Typography variant="body1">
                    {selectedAlert.message}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Created At
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedAlert.created_at).toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlertDialogOpen(false)}>
            Close
          </Button>
          {selectedAlert && (
            <Button
              variant="contained"
              onClick={() => handleResolveAlert(selectedAlert.alert_id)}
            >
              Resolve Alert
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Cache Actions Dialog */}
      <Dialog
        open={cacheDialogOpen}
        onClose={() => setCacheDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Cache Management
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Manage cache operations for better performance
          </Typography>
          
          <List>
            <ListItem button onClick={handleOptimizeCache}>
              <ListItemIcon>
                <OptimizeIcon />
              </ListItemIcon>
              <ListItemText
                primary="Optimize Cache"
                secondary="Clean up expired entries and optimize memory usage"
              />
            </ListItem>
            
            {Object.keys(cacheMetrics).map((personalityId) => (
              <ListItem
                key={personalityId}
                button
                onClick={() => handleWarmCache(personalityId)}
              >
                <ListItemIcon>
                  <span>{getPersonalityIcon(personalityId)}</span>
                </ListItemIcon>
                <ListItemText
                  primary={`Warm ${personalityId} Cache`}
                  secondary="Preload common responses and data"
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCacheDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PerformanceDashboard;