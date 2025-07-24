/**
 * Expert Review Component for Vimarsh Admin Interface
 * 
 * Provides comprehensive expert review interface including:
 * - Domain-specific review queues and assignment logic
 * - Expert feedback collection and processing workflows
 * - Content flagging and escalation workflows
 * - Review analytics and reporting system
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Rating,
  TextareaAutosize,
  FormControlLabel,
  Checkbox,
  Badge
} from '@mui/material';
import {
  Assignment as ReviewIcon,
  Person as ExpertIcon,
  Schedule as PendingIcon,
  RateReview as InReviewIcon,
  CheckCircle as ApprovedIcon,
  Cancel as RejectedIcon,
  Warning as EscalatedIcon,
  Analytics as AnalyticsIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Flag as FlagIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as TimeIcon,
  Psychology as PersonalityIcon,
  Science as ScienceIcon,
  History as HistoryIcon,
  MenuBook as PhilosophyIcon,
  Church as SpiritualIcon
} from '@mui/icons-material';

// Types
interface ReviewItem {
  review_id: string;
  content_id: string;
  content_type: string;
  content_title: string;
  content_preview: string;
  domain: 'spiritual' | 'historical' | 'scientific' | 'philosophical';
  personality_id: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'in_review' | 'approved' | 'rejected' | 'escalated' | 'requires_revision';
  assigned_expert_id?: string;
  created_at: string;
  assigned_at?: string;
  due_date: string;
  completed_at?: string;
  metadata: Record<string, any>;
}

interface ExpertProfile {
  expert_id: string;
  name: string;
  email: string;
  domains: string[];
  expertise_level: string;
  specializations: string[];
  languages: string[];
  max_concurrent_reviews: number;
  current_workload: number;
  quality_score: number;
  is_active: boolean;
}

interface ExpertFeedback {
  feedback_id: string;
  review_id: string;
  expert_id: string;
  accuracy_score: number;
  authenticity_score: number;
  appropriateness_score: number;
  overall_score: number;
  feedback_text: string;
  suggested_improvements: string[];
  flags: string[];
  recommendation: string;
  confidence_level: number;
  time_spent_minutes: number;
  created_at: string;
}

interface ReviewQueue {
  domain: string;
  pending_count: number;
  in_review_count: number;
  overdue_count: number;
  avg_review_time_hours: number;
  expert_availability: number;
}

const ExpertReview: React.FC = () => {
  // State
  const [reviewItems, setReviewItems] = useState<ReviewItem[]>([]);
  const [experts, setExperts] = useState<ExpertProfile[]>([]);
  const [reviewQueues, setReviewQueues] = useState<Record<string, ReviewQueue>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  
  // Dialog states
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [selectedReview, setSelectedReview] = useState<ReviewItem | null>(null);
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [assignmentDialogOpen, setAssignmentDialogOpen] = useState(false);
  
  // Feedback form state
  const [feedbackForm, setFeedbackForm] = useState({
    accuracy_score: 80,
    authenticity_score: 80,
    appropriateness_score: 80,
    feedback_text: '',
    suggested_improvements: [''],
    flags: [] as string[],
    recommendation: 'approved',
    confidence_level: 80,
    time_spent_minutes: 30
  });

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load review items
      const reviewParams = new URLSearchParams();
      if (selectedDomain !== 'all') reviewParams.append('domain', selectedDomain);
      if (selectedStatus !== 'all') reviewParams.append('status', selectedStatus);

      const [reviewResponse, expertsResponse, queuesResponse] = await Promise.all([
        fetch(`/admin/expert-review/items?${reviewParams.toString()}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch('/admin/expert-review/experts', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }),
        fetch('/admin/expert-review/queues', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        })
      ]);

      if (reviewResponse.ok) {
        const reviewData = await reviewResponse.json();
        setReviewItems(reviewData.reviews || []);
      }

      if (expertsResponse.ok) {
        const expertsData = await expertsResponse.json();
        setExperts(expertsData.experts || []);
      }

      if (queuesResponse.ok) {
        const queuesData = await queuesResponse.json();
        setReviewQueues(queuesData.queues || {});
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [selectedDomain, selectedStatus]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Helper functions
  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'spiritual': return <SpiritualIcon />;
      case 'historical': return <HistoryIcon />;
      case 'scientific': return <ScienceIcon />;
      case 'philosophical': return <PhilosophyIcon />;
      default: return <ReviewIcon />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <PendingIcon color="warning" />;
      case 'in_review': return <InReviewIcon color="info" />;
      case 'approved': return <ApprovedIcon color="success" />;
      case 'rejected': return <RejectedIcon color="error" />;
      case 'escalated': return <EscalatedIcon color="error" />;
      default: return <PendingIcon />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date();
  };

  // Event handlers
  const openReviewDialog = (review: ReviewItem) => {
    setSelectedReview(review);
    setReviewDialogOpen(true);
  };

  const openFeedbackDialog = (review: ReviewItem) => {
    setSelectedReview(review);
    setFeedbackDialogOpen(true);
  };

  const openAssignmentDialog = (review: ReviewItem) => {
    setSelectedReview(review);
    setAssignmentDialogOpen(true);
  };

  const handleAssignExpert = async (expertId: string) => {
    if (!selectedReview) return;

    try {
      const response = await fetch(`/admin/expert-review/assign`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          review_id: selectedReview.review_id,
          expert_id: expertId
        })
      });

      if (response.ok) {
        setAssignmentDialogOpen(false);
        loadData();
      } else {
        throw new Error('Failed to assign expert');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign expert');
    }
  };

  const handleSubmitFeedback = async () => {
    if (!selectedReview) return;

    try {
      const response = await fetch(`/admin/expert-review/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          review_id: selectedReview.review_id,
          ...feedbackForm,
          suggested_improvements: feedbackForm.suggested_improvements.filter(s => s.trim())
        })
      });

      if (response.ok) {
        setFeedbackDialogOpen(false);
        setFeedbackForm({
          accuracy_score: 80,
          authenticity_score: 80,
          appropriateness_score: 80,
          feedback_text: '',
          suggested_improvements: [''],
          flags: [],
          recommendation: 'approved',
          confidence_level: 80,
          time_spent_minutes: 30
        });
        loadData();
      } else {
        throw new Error('Failed to submit feedback');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
    }
  };

  const addSuggestion = () => {
    setFeedbackForm(prev => ({
      ...prev,
      suggested_improvements: [...prev.suggested_improvements, '']
    }));
  };

  const updateSuggestion = (index: number, value: string) => {
    setFeedbackForm(prev => ({
      ...prev,
      suggested_improvements: prev.suggested_improvements.map((s, i) => i === index ? value : s)
    }));
  };

  const removeSuggestion = (index: number) => {
    setFeedbackForm(prev => ({
      ...prev,
      suggested_improvements: prev.suggested_improvements.filter((_, i) => i !== index)
    }));
  };

  const toggleFlag = (flag: string) => {
    setFeedbackForm(prev => ({
      ...prev,
      flags: prev.flags.includes(flag) 
        ? prev.flags.filter(f => f !== flag)
        : [...prev.flags, flag]
    }));
  };

  // Filter reviews based on selected tab
  const getFilteredReviews = () => {
    let filtered = reviewItems;

    switch (selectedTab) {
      case 0: // All
        break;
      case 1: // Pending
        filtered = reviewItems.filter(item => item.status === 'pending');
        break;
      case 2: // In Review
        filtered = reviewItems.filter(item => item.status === 'in_review');
        break;
      case 3: // Overdue
        filtered = reviewItems.filter(item => isOverdue(item.due_date) && !['approved', 'rejected'].includes(item.status));
        break;
      case 4: // Completed
        filtered = reviewItems.filter(item => ['approved', 'rejected'].includes(item.status));
        break;
    }

    return filtered;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Expert Review System
        </Typography>
        <Button
          variant="contained"
          startIcon={<AnalyticsIcon />}
          onClick={() => {/* Open analytics dialog */}}
        >
          View Analytics
        </Button>
      </Box>

      {/* Queue Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {Object.entries(reviewQueues).map(([domain, queue]) => (
          <Grid item xs={12} md={3} key={domain}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  {getDomainIcon(domain)}
                  <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                    {domain}
                  </Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Pending
                    </Typography>
                    <Typography variant="h6">
                      {queue.pending_count}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      In Review
                    </Typography>
                    <Typography variant="h6">
                      {queue.in_review_count}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Overdue
                    </Typography>
                    <Typography variant="h6" color={queue.overdue_count > 0 ? 'error.main' : 'inherit'}>
                      {queue.overdue_count}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Experts
                    </Typography>
                    <Typography variant="h6">
                      {queue.expert_availability}
                    </Typography>
                  </Grid>
                </Grid>
                {queue.avg_review_time_hours > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Avg Review Time: {queue.avg_review_time_hours.toFixed(1)}h
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Domain</InputLabel>
                <Select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  label="Domain"
                >
                  <MenuItem value="all">All Domains</MenuItem>
                  <MenuItem value="spiritual">Spiritual</MenuItem>
                  <MenuItem value="historical">Historical</MenuItem>
                  <MenuItem value="scientific">Scientific</MenuItem>
                  <MenuItem value="philosophical">Philosophical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="in_review">In Review</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="rejected">Rejected</MenuItem>
                  <MenuItem value="escalated">Escalated</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                onClick={loadData}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs
        value={selectedTab}
        onChange={(_, newValue) => setSelectedTab(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab label={`All (${reviewItems.length})`} />
        <Tab label={`Pending (${reviewItems.filter(r => r.status === 'pending').length})`} />
        <Tab label={`In Review (${reviewItems.filter(r => r.status === 'in_review').length})`} />
        <Tab label={`Overdue (${reviewItems.filter(r => isOverdue(r.due_date) && !['approved', 'rejected'].includes(r.status)).length})`} />
        <Tab label={`Completed (${reviewItems.filter(r => ['approved', 'rejected'].includes(r.status)).length})`} />
      </Tabs>

      {/* Error Alert */}
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

      {/* Reviews Table */}
      {!loading && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Content</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Expert</TableCell>
                <TableCell>Due Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {getFilteredReviews().map((item) => {
                const expert = experts.find(e => e.expert_id === item.assigned_expert_id);
                const overdue = isOverdue(item.due_date);
                
                return (
                  <TableRow key={item.review_id} sx={{ bgcolor: overdue ? 'error.50' : 'inherit' }}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {getDomainIcon(item.domain)}
                        <Box>
                          <Typography variant="subtitle2">
                            {item.content_title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {item.content_type} • {item.personality_id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={item.domain} size="small" color="primary" />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={item.priority} 
                        size="small" 
                        color={getPriorityColor(item.priority) as any}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getStatusIcon(item.status)}
                        <Typography variant="body2">
                          {item.status.replace('_', ' ')}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {expert ? (
                        <Box>
                          <Typography variant="body2">
                            {expert.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {expert.expertise_level}
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Unassigned
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        color={overdue ? 'error.main' : 'text.primary'}
                      >
                        {new Date(item.due_date).toLocaleDateString()}
                      </Typography>
                      {overdue && (
                        <Typography variant="caption" color="error.main">
                          Overdue
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton size="small" onClick={() => openReviewDialog(item)}>
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        {item.status === 'pending' && (
                          <Tooltip title="Assign Expert">
                            <IconButton size="small" onClick={() => openAssignmentDialog(item)}>
                              <ExpertIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        {item.status === 'in_review' && item.assigned_expert_id && (
                          <Tooltip title="Submit Feedback">
                            <IconButton size="small" onClick={() => openFeedbackDialog(item)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Review Details Dialog */}
      <Dialog
        open={reviewDialogOpen}
        onClose={() => setReviewDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Review Details</DialogTitle>
        <DialogContent>
          {selectedReview && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    {selectedReview.content_title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {selectedReview.content_type} • {selectedReview.personality_id}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={selectedReview.domain} size="small" color="primary" />
                    <Chip label={selectedReview.priority} size="small" color={getPriorityColor(selectedReview.priority) as any} />
                    <Chip label={selectedReview.status.replace('_', ' ')} size="small" />
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Timeline
                  </Typography>
                  <Typography variant="body2">
                    Created: {new Date(selectedReview.created_at).toLocaleString()}
                  </Typography>
                  {selectedReview.assigned_at && (
                    <Typography variant="body2">
                      Assigned: {new Date(selectedReview.assigned_at).toLocaleString()}
                    </Typography>
                  )}
                  <Typography variant="body2">
                    Due: {new Date(selectedReview.due_date).toLocaleString()}
                  </Typography>
                  {selectedReview.completed_at && (
                    <Typography variant="body2">
                      Completed: {new Date(selectedReview.completed_at).toLocaleString()}
                    </Typography>
                  )}
                </Grid>
              </Grid>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Content Preview
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                {selectedReview.content_preview}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReviewDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Assignment Dialog */}
      <Dialog
        open={assignmentDialogOpen}
        onClose={() => setAssignmentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Assign Expert</DialogTitle>
        <DialogContent>
          {selectedReview && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Content: {selectedReview.content_title}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Domain: {selectedReview.domain} • Priority: {selectedReview.priority}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Available Experts
              </Typography>
              <List>
                {experts
                  .filter(expert => 
                    expert.domains.includes(selectedReview.domain) && 
                    expert.is_active &&
                    expert.current_workload < expert.max_concurrent_reviews
                  )
                  .map((expert) => (
                    <ListItem key={expert.expert_id}>
                      <ListItemText
                        primary={expert.name}
                        secondary={
                          <Box>
                            <Typography variant="caption">
                              {expert.expertise_level} • Quality Score: {expert.quality_score}%
                            </Typography>
                            <br />
                            <Typography variant="caption">
                              Workload: {expert.current_workload}/{expert.max_concurrent_reviews}
                            </Typography>
                            <br />
                            <Typography variant="caption">
                              Specializations: {expert.specializations.join(', ')}
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleAssignExpert(expert.expert_id)}
                        >
                          Assign
                        </Button>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignmentDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Feedback Dialog */}
      <Dialog
        open={feedbackDialogOpen}
        onClose={() => setFeedbackDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Submit Expert Feedback</DialogTitle>
        <DialogContent>
          {selectedReview && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                {selectedReview.content_title}
              </Typography>
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    Accuracy Score
                  </Typography>
                  <Rating
                    value={feedbackForm.accuracy_score / 20}
                    onChange={(_, value) => setFeedbackForm(prev => ({ ...prev, accuracy_score: (value || 0) * 20 }))}
                    max={5}
                    precision={0.5}
                  />
                  <Typography variant="body2">
                    {feedbackForm.accuracy_score}%
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    Authenticity Score
                  </Typography>
                  <Rating
                    value={feedbackForm.authenticity_score / 20}
                    onChange={(_, value) => setFeedbackForm(prev => ({ ...prev, authenticity_score: (value || 0) * 20 }))}
                    max={5}
                    precision={0.5}
                  />
                  <Typography variant="body2">
                    {feedbackForm.authenticity_score}%
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    Appropriateness Score
                  </Typography>
                  <Rating
                    value={feedbackForm.appropriateness_score / 20}
                    onChange={(_, value) => setFeedbackForm(prev => ({ ...prev, appropriateness_score: (value || 0) * 20 }))}
                    max={5}
                    precision={0.5}
                  />
                  <Typography variant="body2">
                    {feedbackForm.appropriateness_score}%
                  </Typography>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Detailed Feedback
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={feedbackForm.feedback_text}
                  onChange={(e) => setFeedbackForm(prev => ({ ...prev, feedback_text: e.target.value }))}
                  placeholder="Provide detailed feedback about the content..."
                />
              </Box>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Suggested Improvements
                </Typography>
                {feedbackForm.suggested_improvements.map((suggestion, index) => (
                  <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      value={suggestion}
                      onChange={(e) => updateSuggestion(index, e.target.value)}
                      placeholder="Suggestion..."
                    />
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => removeSuggestion(index)}
                      disabled={feedbackForm.suggested_improvements.length === 1}
                    >
                      Remove
                    </Button>
                  </Box>
                ))}
                <Button
                  variant="outlined"
                  size="small"
                  onClick={addSuggestion}
                >
                  Add Suggestion
                </Button>
              </Box>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Content Flags
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {['factual_error', 'tone_inappropriate', 'citation_missing', 'cultural_insensitive', 'outdated_information'].map((flag) => (
                    <FormControlLabel
                      key={flag}
                      control={
                        <Checkbox
                          checked={feedbackForm.flags.includes(flag)}
                          onChange={() => toggleFlag(flag)}
                        />
                      }
                      label={flag.replace('_', ' ')}
                    />
                  ))}
                </Box>
              </Box>

              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Recommendation</InputLabel>
                    <Select
                      value={feedbackForm.recommendation}
                      onChange={(e) => setFeedbackForm(prev => ({ ...prev, recommendation: e.target.value }))}
                      label="Recommendation"
                    >
                      <MenuItem value="approved">Approve</MenuItem>
                      <MenuItem value="rejected">Reject</MenuItem>
                      <MenuItem value="requires_revision">Requires Revision</MenuItem>
                      <MenuItem value="escalated">Escalate</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" gutterBottom>
                    Confidence Level: {feedbackForm.confidence_level}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={feedbackForm.confidence_level}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Time Spent (minutes)"
                    value={feedbackForm.time_spent_minutes}
                    onChange={(e) => setFeedbackForm(prev => ({ ...prev, time_spent_minutes: parseInt(e.target.value) || 0 }))}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSubmitFeedback}>
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExpertReview;