/**
 * Personality Selector Component for Vimarsh User Interface
 * 
 * Allows users to browse, discover, and select AI personalities for conversations.
 * Features:
 * - Personality browsing with domain filtering
 * - Personality cards with rich information
 * - Search and recommendation system
 * - Personality comparison
 * - Favorites and recent selections
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  Avatar,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Rating,
  Divider
} from '@mui/material';
import {
  Psychology as PersonalityIcon,
  Science as ScienceIcon,
  History as HistoryIcon,
  MenuBook as PhilosophyIcon,
  AutoStories as LiteraryIcon,
  Gavel as PoliticalIcon,
  Search as SearchIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Info as InfoIcon,
  Chat as ChatIcon,
  Close as CloseIcon
} from '@mui/icons-material';

// Types
interface Personality {
  id: string;
  name: string;
  display_name: string;
  domain: 'spiritual' | 'scientific' | 'historical' | 'philosophical' | 'literary' | 'political';
  time_period: string;
  description: string;
  expertise_areas: string[];
  cultural_context: string;
  quality_score: number;
  usage_count: number;
  is_active: boolean;
  tags: string[];
}

interface PersonalitySelectorProps {
  selectedPersonalityId?: string;
  onPersonalitySelect: (personality: Personality) => void;
  onClose?: () => void;
  showAsDialog?: boolean;
}

const PersonalitySelector: React.FC<PersonalitySelectorProps> = ({
  selectedPersonalityId,
  onPersonalitySelect,
  onClose,
  showAsDialog = false
}) => {
  // State
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState<string>('all');
  const [selectedTab, setSelectedTab] = useState(0);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedPersonality, setSelectedPersonality] = useState<Personality | null>(null);
  const [favorites, setFavorites] = useState<string[]>([]);

  // Domain configuration
  const domains = [
    { value: 'all', label: 'All Domains', icon: <PersonalityIcon /> },
    { value: 'spiritual', label: 'Spiritual', icon: <PersonalityIcon /> },
    { value: 'scientific', label: 'Scientific', icon: <ScienceIcon /> },
    { value: 'historical', label: 'Historical', icon: <HistoryIcon /> },
    { value: 'philosophical', label: 'Philosophical', icon: <PhilosophyIcon /> },
    { value: 'literary', label: 'Literary', icon: <LiteraryIcon /> },
    { value: 'political', label: 'Political', icon: <PoliticalIcon /> }
  ];

  // Get domain icon
  const getDomainIcon = (domain: string) => {
    const domainConfig = domains.find(d => d.value === domain);
    return domainConfig?.icon || <PersonalityIcon />;
  };

  // Get domain color
  const getDomainColor = (domain: string) => {
    switch (domain) {
      case 'spiritual': return '#9c27b0';
      case 'scientific': return '#2196f3';
      case 'historical': return '#ff9800';
      case 'philosophical': return '#4caf50';
      case 'literary': return '#e91e63';
      case 'political': return '#f44336';
      default: return '#757575';
    }
  };

  // Load personalities
  const loadPersonalities = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append('active_only', 'true');
      if (selectedDomain !== 'all') {
        params.append('domain', selectedDomain);
      }
      if (searchQuery) {
        params.append('q', searchQuery);
      }

      // Import API base URL
      const { getApiBaseUrl } = await import('../config/environment');
      const apiBaseUrl = getApiBaseUrl();
      
      const response = await fetch(`${apiBaseUrl}/personalities/active?${params.toString()}`);
      
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
  };

  // Load favorites from localStorage
  const loadFavorites = () => {
    try {
      const saved = localStorage.getItem('vimarsh_favorite_personalities');
      if (saved) {
        setFavorites(JSON.parse(saved));
      }
    } catch (error) {
      console.error('Failed to load favorites:', error);
    }
  };

  // Save favorites to localStorage
  const saveFavorites = (newFavorites: string[]) => {
    try {
      localStorage.setItem('vimarsh_favorite_personalities', JSON.stringify(newFavorites));
      setFavorites(newFavorites);
    } catch (error) {
      console.error('Failed to save favorites:', error);
    }
  };

  // Toggle favorite
  const toggleFavorite = (personalityId: string) => {
    const newFavorites = favorites.includes(personalityId)
      ? favorites.filter(id => id !== personalityId)
      : [...favorites, personalityId];
    saveFavorites(newFavorites);
  };

  // Load data on mount
  useEffect(() => {
    loadPersonalities();
    loadFavorites();
  }, [selectedDomain, searchQuery]);

  // Filter personalities based on selected tab
  const getFilteredPersonalities = () => {
    switch (selectedTab) {
      case 0: // All
        return personalities;
      case 1: // Favorites
        return personalities.filter(p => favorites.includes(p.id));
      case 2: // Popular
        return personalities.sort((a, b) => b.usage_count - a.usage_count);
      case 3: // Highest Rated
        return personalities.sort((a, b) => b.quality_score - a.quality_score);
      default:
        return personalities;
    }
  };

  // Handle personality selection
  const handlePersonalitySelect = (personality: Personality) => {
    onPersonalitySelect(personality);
    if (showAsDialog && onClose) {
      onClose();
    }
  };

  // Show personality details
  const showPersonalityDetails = (personality: Personality) => {
    setSelectedPersonality(personality);
    setDetailsOpen(true);
  };

  // Personality card component
  const PersonalityCard: React.FC<{ personality: Personality }> = ({ personality }) => (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        border: selectedPersonalityId === personality.id ? 2 : 0,
        borderColor: 'primary.main',
        '&:hover': {
          boxShadow: 4
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar 
            sx={{ 
              bgcolor: getDomainColor(personality.domain), 
              mr: 2,
              width: 48,
              height: 48
            }}
          >
            {getDomainIcon(personality.domain)}
          </Avatar>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="h3" gutterBottom>
              {personality.display_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {personality.time_period}
            </Typography>
          </Box>
          <IconButton
            size="small"
            onClick={() => toggleFavorite(personality.id)}
            color={favorites.includes(personality.id) ? 'error' : 'default'}
          >
            {favorites.includes(personality.id) ? <FavoriteIcon /> : <FavoriteBorderIcon />}
          </IconButton>
        </Box>

        <Chip
          label={personality.domain}
          size="small"
          sx={{ 
            bgcolor: getDomainColor(personality.domain),
            color: 'white',
            mb: 2
          }}
        />

        <Typography variant="body2" color="text.secondary" paragraph>
          {personality.description.length > 120 
            ? `${personality.description.substring(0, 120)}...`
            : personality.description
          }
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Expertise:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
            {personality.expertise_areas.slice(0, 3).map((area, index) => (
              <Chip
                key={index}
                label={area}
                size="small"
                variant="outlined"
              />
            ))}
            {personality.expertise_areas.length > 3 && (
              <Chip
                label={`+${personality.expertise_areas.length - 3} more`}
                size="small"
                variant="outlined"
                color="primary"
              />
            )}
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Rating
              value={personality.quality_score / 20}
              precision={0.1}
              size="small"
              readOnly
            />
            <Typography variant="caption">
              ({personality.quality_score.toFixed(1)})
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            {personality.usage_count.toLocaleString()} conversations
          </Typography>
        </Box>
      </CardContent>

      <CardActions>
        <Button
          size="small"
          startIcon={<InfoIcon />}
          onClick={() => showPersonalityDetails(personality)}
        >
          Details
        </Button>
        <Button
          size="small"
          variant="contained"
          startIcon={<ChatIcon />}
          onClick={() => handlePersonalitySelect(personality)}
          sx={{ ml: 'auto' }}
        >
          Chat
        </Button>
      </CardActions>
    </Card>
  );

  const content = (
    <Box sx={{ height: showAsDialog ? 'auto' : '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h1">
            Choose Your Conversation Partner
          </Typography>
          {showAsDialog && onClose && (
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          )}
        </Box>

        {/* Search and Filters */}
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              size="small"
              label="Search personalities"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                endAdornment: (
                  <IconButton size="small">
                    <SearchIcon />
                  </IconButton>
                )
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Domain</InputLabel>
              <Select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                label="Domain"
              >
                {domains.map((domain) => (
                  <MenuItem key={domain.value} value={domain.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {domain.icon}
                      {domain.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Tabs
          value={selectedTab}
          onChange={(_, newValue) => setSelectedTab(newValue)}
          sx={{ mt: 2 }}
        >
          <Tab label="All" />
          <Tab label={`Favorites (${favorites.length})`} />
          <Tab label="Popular" />
          <Tab label="Highest Rated" />
        </Tabs>
      </Box>

      {/* Content */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 3 }}>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Loading */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Personalities Grid */}
        {!loading && (
          <Grid container spacing={3}>
            {getFilteredPersonalities().map((personality) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={personality.id}>
                <PersonalityCard personality={personality} />
              </Grid>
            ))}
          </Grid>
        )}

        {/* Empty State */}
        {!loading && getFilteredPersonalities().length === 0 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <PersonalityIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No personalities found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedTab === 1 
                ? 'You haven\'t favorited any personalities yet.'
                : 'Try adjusting your search or filter criteria.'
              }
            </Typography>
          </Box>
        )}
      </Box>

      {/* Personality Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {selectedPersonality && (
              <>
                <Avatar sx={{ bgcolor: getDomainColor(selectedPersonality.domain) }}>
                  {getDomainIcon(selectedPersonality.domain)}
                </Avatar>
                <Box>
                  <Typography variant="h6">
                    {selectedPersonality.display_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {selectedPersonality.time_period}
                  </Typography>
                </Box>
              </>
            )}
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedPersonality && (
            <Box>
              <Typography variant="body1" paragraph>
                {selectedPersonality.description}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                Cultural Context
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedPersonality.cultural_context}
              </Typography>

              <Typography variant="subtitle2" gutterBottom>
                Areas of Expertise
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {selectedPersonality.expertise_areas.map((area, index) => (
                  <Chip key={index} label={area} variant="outlined" />
                ))}
              </Box>

              <Typography variant="subtitle2" gutterBottom>
                Tags
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {selectedPersonality.tags.map((tag, index) => (
                  <Chip key={index} label={tag} size="small" color="primary" />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>
            Close
          </Button>
          {selectedPersonality && (
            <Button
              variant="contained"
              startIcon={<ChatIcon />}
              onClick={() => {
                handlePersonalitySelect(selectedPersonality);
                setDetailsOpen(false);
              }}
            >
              Start Conversation
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );

  if (showAsDialog) {
    return (
      <Dialog
        open={true}
        onClose={onClose}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { height: '90vh' }
        }}
      >
        {content}
      </Dialog>
    );
  }

  return content;
};

export default PersonalitySelector;