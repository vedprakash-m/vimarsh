/**
 * Personality Manager Component for Vimarsh Admin Interface
 * 
 * Provides comprehensive personality management capabilities including:
 * - CRUD operations for AI personalities
 * - Personality discovery and search
 * - Domain filtering and organization
 * - Personality testing and validation
 * - Bulk operations and management
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
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Psychology as PersonalityIcon,
  Science as ScienceIcon,
  History as HistoryIcon,
  MenuBook as PhilosophyIcon,
  Refresh as RefreshIcon,
  PlayArrow as TestIcon
} from '@mui/icons-material';

// Types
interface Personality {
  id: string;
  name: string;
  display_name: string;
  domain: 'spiritual' | 'scientific' | 'historical' | 'philosophical' | 'literary' | 'political';
  time_period: string;
  description: string;
  status: 'draft' | 'under_review' | 'approved' | 'active' | 'inactive' | 'archived';
  is_active: boolean;
  expertise_areas: string[];
  cultural_context: string;
  language_style: string;
  usage_count: number;
  quality_score: number;
  expert_approved: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  tags: string[];
}

interface PersonalityFilters {
  domain?: string;
  status?: string;
  is_active?: boolean;
  expert_approved?: boolean;
  search_query?: string;
}

const PersonalityManager: React.FC = () => {
  // State
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PersonalityFilters>({});
  const [selectedPersonality, setSelectedPersonality] = useState<Personality | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit' | 'create' | 'test'>('view');
  const [searchQuery, setSearchQuery] = useState('');

  // Domain icons mapping
  const getDomainIcon = (domain: string) => {
    switch (domain) {
      case 'spiritual': return <PersonalityIcon color="primary" />;
      case 'scientific': return <ScienceIcon color="secondary" />;
      case 'historical': return <HistoryIcon color="info" />;
      case 'philosophical': return <PhilosophyIcon color="warning" />;
      default: return <PersonalityIcon />;
    }
  };

  // Domain colors
  const getDomainColor = (domain: string) => {
    switch (domain) {
      case 'spiritual': return 'primary';
      case 'scientific': return 'secondary';
      case 'historical': return 'info';
      case 'philosophical': return 'warning';
      case 'literary': return 'success';
      case 'political': return 'error';
      default: return 'default';
    }
  };

  // Load personalities
  const loadPersonalities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query parameters
      const params = new URLSearchParams();
      if (filters.domain) params.append('domain', filters.domain);
      if (filters.status) params.append('status', filters.status);
      if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
      if (filters.expert_approved !== undefined) params.append('expert_approved', filters.expert_approved.toString());
      if (filters.search_query) params.append('q', filters.search_query);

      const response = await fetch(`/admin/personalities?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to load personalities: ${response.statusText}`);
      }

      const data = await response.json();
      setPersonalities(data.personalities || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load personalities');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Load personalities on mount and filter changes
  useEffect(() => {
    loadPersonalities();
  }, [loadPersonalities]);

  // Handle search
  const handleSearch = () => {
    setFilters(prev => ({ ...prev, search_query: searchQuery }));
  };

  // Handle filter changes
  const handleFilterChange = (key: keyof PersonalityFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({});
    setSearchQuery('');
  };

  // Open dialog
  const openDialog = (mode: typeof dialogMode, personality?: Personality) => {
    setDialogMode(mode);
    setSelectedPersonality(personality || null);
    setDialogOpen(true);
  };

  // Close dialog
  const closeDialog = () => {
    setDialogOpen(false);
    setSelectedPersonality(null);
  };

  // Delete personality
  const handleDelete = async (personality: Personality) => {
    if (!window.confirm(`Are you sure you want to delete ${personality.display_name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/admin/personalities/${personality.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to delete personality: ${response.statusText}`);
      }

      // Reload personalities
      await loadPersonalities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete personality');
    }
  };

  // Toggle personality active status
  const toggleActive = async (personality: Personality) => {
    try {
      const response = await fetch(`/admin/personalities/${personality.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          is_active: !personality.is_active
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to update personality: ${response.statusText}`);
      }

      // Reload personalities
      await loadPersonalities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update personality');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Personality Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => openDialog('create')}
        >
          Create Personality
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            {/* Search */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search personalities"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <IconButton onClick={handleSearch}>
                      <SearchIcon />
                    </IconButton>
                  )
                }}
              />
            </Grid>

            {/* Domain Filter */}
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Domain</InputLabel>
                <Select
                  value={filters.domain || ''}
                  onChange={(e) => handleFilterChange('domain', e.target.value || undefined)}
                  label="Domain"
                >
                  <MenuItem value="">All Domains</MenuItem>
                  <MenuItem value="spiritual">Spiritual</MenuItem>
                  <MenuItem value="scientific">Scientific</MenuItem>
                  <MenuItem value="historical">Historical</MenuItem>
                  <MenuItem value="philosophical">Philosophical</MenuItem>
                  <MenuItem value="literary">Literary</MenuItem>
                  <MenuItem value="political">Political</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Status Filter */}
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status || ''}
                  onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
                  label="Status"
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="under_review">Under Review</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="archived">Archived</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Active Filter */}
            <Grid item xs={12} md={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={filters.is_active === true}
                    onChange={(e) => handleFilterChange('is_active', e.target.checked ? true : undefined)}
                  />
                }
                label="Active Only"
              />
            </Grid>

            {/* Actions */}
            <Grid item xs={12} md={2}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<FilterIcon />}
                  onClick={clearFilters}
                >
                  Clear
                </Button>
                <IconButton onClick={loadPersonalities}>
                  <RefreshIcon />
                </IconButton>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

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

      {/* Personalities Table */}
      {!loading && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Personality</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Usage</TableCell>
                <TableCell>Expert Approved</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {personalities.map((personality) => (
                <TableRow key={personality.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      {getDomainIcon(personality.domain)}
                      <Box>
                        <Typography variant="subtitle2">
                          {personality.display_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {personality.time_period}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={personality.domain}
                      color={getDomainColor(personality.domain) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={personality.status}
                        color={personality.is_active ? 'success' : 'default'}
                        size="small"
                      />
                      <Switch
                        checked={personality.is_active}
                        onChange={() => toggleActive(personality)}
                        size="small"
                      />
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {personality.quality_score.toFixed(1)}%
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {personality.usage_count.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={personality.expert_approved ? 'Yes' : 'No'}
                      color={personality.expert_approved ? 'success' : 'warning'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="View">
                        <IconButton
                          size="small"
                          onClick={() => openDialog('view', personality)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => openDialog('edit', personality)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Test">
                        <IconButton
                          size="small"
                          onClick={() => openDialog('test', personality)}
                        >
                          <TestIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(personality)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Empty State */}
      {!loading && personalities.length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <PersonalityIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No personalities found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {Object.keys(filters).length > 0
                ? 'Try adjusting your filters or search criteria.'
                : 'Get started by creating your first personality.'}
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => openDialog('create')}
            >
              Create Personality
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Personality Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={closeDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' && 'Create New Personality'}
          {dialogMode === 'edit' && `Edit ${selectedPersonality?.display_name}`}
          {dialogMode === 'view' && `View ${selectedPersonality?.display_name}`}
          {dialogMode === 'test' && `Test ${selectedPersonality?.display_name}`}
        </DialogTitle>
        <DialogContent>
          {selectedPersonality && (
            <Box sx={{ pt: 2 }}>
              {/* Personality details would go here */}
              <Typography variant="body1">
                Personality details and forms will be implemented in PersonalityEditor component.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>
            {dialogMode === 'view' ? 'Close' : 'Cancel'}
          </Button>
          {(dialogMode === 'create' || dialogMode === 'edit') && (
            <Button variant="contained">
              Save
            </Button>
          )}
          {dialogMode === 'test' && (
            <Button variant="contained">
              Run Test
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PersonalityManager;