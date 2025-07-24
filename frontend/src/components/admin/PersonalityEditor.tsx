/**
 * Personality Editor Component for Vimarsh Admin Interface
 * 
 * Provides detailed personality editing capabilities including:
 * - Visual personality profile editor with real-time preview
 * - Form validation and error handling
 * - Domain-specific configuration options
 * - Voice settings and response patterns
 * - Knowledge base association
 * - Expert review integration
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  Button,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Rating
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Preview as PreviewIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  VolumeUp as VoiceIcon,
  Psychology as PersonalityIcon,
  Book as BookIcon,
  Star as StarIcon
} from '@mui/icons-material';

// Types
interface PersonalityFormData {
  name: string;
  display_name: string;
  domain: string;
  time_period: string;
  description: string;
  tone_characteristics: {
    formality: string;
    warmth: string;
    authority: string;
    teaching_style: string;
  };
  vocabulary_preferences: {
    [key: string]: boolean;
  };
  response_patterns: {
    greeting_style: string;
    explanation_approach: string;
    citation_style: string;
  };
  expertise_areas: string[];
  cultural_context: string;
  language_style: string;
  system_prompt: string;
  voice_settings: {
    language: string;
    voice_name: string;
    speaking_rate: number;
    pitch: number;
  };
  greeting_patterns: string[];
  farewell_patterns: string[];
  uncertainty_responses: string[];
  is_active: boolean;
  tags: string[];
}

interface PersonalityEditorProps {
  personality?: any;
  mode: 'create' | 'edit' | 'view';
  onSave?: (data: PersonalityFormData) => Promise<void>;
  onCancel?: () => void;
}

const PersonalityEditor: React.FC<PersonalityEditorProps> = ({
  personality,
  mode,
  onSave,
  onCancel
}) => {
  // State
  const [formData, setFormData] = useState<PersonalityFormData>({
    name: '',
    display_name: '',
    domain: 'spiritual',
    time_period: '',
    description: '',
    tone_characteristics: {
      formality: 'moderate',
      warmth: 'warm',
      authority: 'knowledgeable',
      teaching_style: 'explanatory'
    },
    vocabulary_preferences: {},
    response_patterns: {
      greeting_style: 'friendly',
      explanation_approach: 'step_by_step',
      citation_style: 'academic'
    },
    expertise_areas: [],
    cultural_context: '',
    language_style: '',
    system_prompt: '',
    voice_settings: {
      language: 'en-US',
      voice_name: 'en-US-Neural2-J',
      speaking_rate: 1.0,
      pitch: 0.0
    },
    greeting_patterns: [],
    farewell_patterns: [],
    uncertainty_responses: [],
    is_active: false,
    tags: []
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [newExpertiseArea, setNewExpertiseArea] = useState('');
  const [newTag, setNewTag] = useState('');
  const [newGreeting, setNewGreeting] = useState('');
  const [newFarewell, setNewFarewell] = useState('');
  const [newUncertainty, setNewUncertainty] = useState('');

  // Initialize form data
  useEffect(() => {
    if (personality) {
      setFormData({
        name: personality.name || '',
        display_name: personality.display_name || '',
        domain: personality.domain || 'spiritual',
        time_period: personality.time_period || '',
        description: personality.description || '',
        tone_characteristics: personality.tone_characteristics || formData.tone_characteristics,
        vocabulary_preferences: personality.vocabulary_preferences || {},
        response_patterns: personality.response_patterns || formData.response_patterns,
        expertise_areas: personality.expertise_areas || [],
        cultural_context: personality.cultural_context || '',
        language_style: personality.language_style || '',
        system_prompt: personality.system_prompt || '',
        voice_settings: personality.voice_settings || formData.voice_settings,
        greeting_patterns: personality.greeting_patterns || [],
        farewell_patterns: personality.farewell_patterns || [],
        uncertainty_responses: personality.uncertainty_responses || [],
        is_active: personality.is_active || false,
        tags: personality.tags || []
      });
    }
  }, [personality]);

  // Handle form field changes
  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Handle nested field changes
  const handleNestedFieldChange = (parent: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: {
        ...prev[parent as keyof PersonalityFormData] as any,
        [field]: value
      }
    }));
  };

  // Add item to array field
  const addToArrayField = (field: keyof PersonalityFormData, value: string) => {
    if (!value.trim()) return;
    
    setFormData(prev => ({
      ...prev,
      [field]: [...(prev[field] as string[]), value.trim()]
    }));
  };

  // Remove item from array field
  const removeFromArrayField = (field: keyof PersonalityFormData, index: number) => {
    setFormData(prev => ({
      ...prev,
      [field]: (prev[field] as string[]).filter((_, i) => i !== index)
    }));
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.display_name.trim()) {
      newErrors.display_name = 'Display name is required';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }

    if (formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters';
    }

    if (!formData.system_prompt.trim()) {
      newErrors.system_prompt = 'System prompt is required';
    }

    if (formData.system_prompt.length < 50) {
      newErrors.system_prompt = 'System prompt must be at least 50 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle save
  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      if (onSave) {
        await onSave(formData);
      }
    } catch (error) {
      console.error('Failed to save personality:', error);
    } finally {
      setLoading(false);
    }
  };

  // Domain-specific vocabulary options
  const getVocabularyOptions = (domain: string) => {
    switch (domain) {
      case 'spiritual':
        return ['sanskrit_terms', 'metaphorical_language', 'spiritual_concepts', 'devotional_language'];
      case 'scientific':
        return ['scientific_terms', 'mathematical_concepts', 'technical_language', 'research_terminology'];
      case 'historical':
        return ['historical_terms', 'period_language', 'formal_address', 'archaic_expressions'];
      case 'philosophical':
        return ['philosophical_terms', 'logical_language', 'abstract_concepts', 'ethical_terminology'];
      default:
        return ['formal_language', 'academic_terms', 'professional_vocabulary'];
    }
  };

  const isReadOnly = mode === 'view';

  return (
    <Box sx={{ maxHeight: '80vh', overflow: 'auto' }}>
      {/* Basic Information */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Basic Information</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                error={!!errors.name}
                helperText={errors.name}
                disabled={isReadOnly}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Display Name"
                value={formData.display_name}
                onChange={(e) => handleFieldChange('display_name', e.target.value)}
                error={!!errors.display_name}
                helperText={errors.display_name}
                disabled={isReadOnly}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Domain</InputLabel>
                <Select
                  value={formData.domain}
                  onChange={(e) => handleFieldChange('domain', e.target.value)}
                  label="Domain"
                  disabled={isReadOnly}
                >
                  <MenuItem value="spiritual">Spiritual</MenuItem>
                  <MenuItem value="scientific">Scientific</MenuItem>
                  <MenuItem value="historical">Historical</MenuItem>
                  <MenuItem value="philosophical">Philosophical</MenuItem>
                  <MenuItem value="literary">Literary</MenuItem>
                  <MenuItem value="political">Political</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Time Period"
                value={formData.time_period}
                onChange={(e) => handleFieldChange('time_period', e.target.value)}
                disabled={isReadOnly}
                placeholder="e.g., Ancient India (3000+ BCE)"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={formData.description}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                error={!!errors.description}
                helperText={errors.description}
                disabled={isReadOnly}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Cultural Context"
                value={formData.cultural_context}
                onChange={(e) => handleFieldChange('cultural_context', e.target.value)}
                disabled={isReadOnly}
                placeholder="e.g., Hindu philosophy and Vedic tradition"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Language Style"
                value={formData.language_style}
                onChange={(e) => handleFieldChange('language_style', e.target.value)}
                disabled={isReadOnly}
                placeholder="e.g., reverent and dignified"
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Personality Characteristics */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Personality Characteristics</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Formality</InputLabel>
                <Select
                  value={formData.tone_characteristics.formality}
                  onChange={(e) => handleNestedFieldChange('tone_characteristics', 'formality', e.target.value)}
                  label="Formality"
                  disabled={isReadOnly}
                >
                  <MenuItem value="casual">Casual</MenuItem>
                  <MenuItem value="moderate">Moderate</MenuItem>
                  <MenuItem value="formal">Formal</MenuItem>
                  <MenuItem value="elevated">Elevated</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Warmth</InputLabel>
                <Select
                  value={formData.tone_characteristics.warmth}
                  onChange={(e) => handleNestedFieldChange('tone_characteristics', 'warmth', e.target.value)}
                  label="Warmth"
                  disabled={isReadOnly}
                >
                  <MenuItem value="cold">Cold</MenuItem>
                  <MenuItem value="neutral">Neutral</MenuItem>
                  <MenuItem value="warm">Warm</MenuItem>
                  <MenuItem value="compassionate">Compassionate</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Authority</InputLabel>
                <Select
                  value={formData.tone_characteristics.authority}
                  onChange={(e) => handleNestedFieldChange('tone_characteristics', 'authority', e.target.value)}
                  label="Authority"
                  disabled={isReadOnly}
                >
                  <MenuItem value="humble">Humble</MenuItem>
                  <MenuItem value="knowledgeable">Knowledgeable</MenuItem>
                  <MenuItem value="authoritative">Authoritative</MenuItem>
                  <MenuItem value="divine">Divine</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Teaching Style</InputLabel>
                <Select
                  value={formData.tone_characteristics.teaching_style}
                  onChange={(e) => handleNestedFieldChange('tone_characteristics', 'teaching_style', e.target.value)}
                  label="Teaching Style"
                  disabled={isReadOnly}
                >
                  <MenuItem value="direct">Direct</MenuItem>
                  <MenuItem value="explanatory">Explanatory</MenuItem>
                  <MenuItem value="parabolic">Parabolic</MenuItem>
                  <MenuItem value="socratic">Socratic</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          {/* Vocabulary Preferences */}
          <Typography variant="subtitle1" gutterBottom>
            Vocabulary Preferences
          </Typography>
          <Grid container spacing={2}>
            {getVocabularyOptions(formData.domain).map((option) => (
              <Grid item xs={12} sm={6} md={4} key={option}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.vocabulary_preferences[option] || false}
                      onChange={(e) => handleNestedFieldChange('vocabulary_preferences', option, e.target.checked)}
                      disabled={isReadOnly}
                    />
                  }
                  label={option.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                />
              </Grid>
            ))}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* System Prompt */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">System Prompt</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <TextField
            fullWidth
            multiline
            rows={8}
            label="System Prompt"
            value={formData.system_prompt}
            onChange={(e) => handleFieldChange('system_prompt', e.target.value)}
            error={!!errors.system_prompt}
            helperText={errors.system_prompt || 'Define how the AI should behave and respond as this personality'}
            disabled={isReadOnly}
            required
          />
        </AccordionDetails>
      </Accordion>

      {/* Expertise Areas */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Expertise Areas</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {!isReadOnly && (
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                size="small"
                label="Add expertise area"
                value={newExpertiseArea}
                onChange={(e) => setNewExpertiseArea(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addToArrayField('expertise_areas', newExpertiseArea);
                    setNewExpertiseArea('');
                  }
                }}
              />
              <Button
                variant="outlined"
                onClick={() => {
                  addToArrayField('expertise_areas', newExpertiseArea);
                  setNewExpertiseArea('');
                }}
                disabled={!newExpertiseArea.trim()}
              >
                Add
              </Button>
            </Box>
          )}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {formData.expertise_areas.map((area, index) => (
              <Chip
                key={index}
                label={area}
                onDelete={isReadOnly ? undefined : () => removeFromArrayField('expertise_areas', index)}
                color="primary"
                variant="outlined"
              />
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Voice Settings */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Voice Settings</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={formData.voice_settings.language}
                  onChange={(e) => handleNestedFieldChange('voice_settings', 'language', e.target.value)}
                  label="Language"
                  disabled={isReadOnly}
                >
                  <MenuItem value="en-US">English (US)</MenuItem>
                  <MenuItem value="en-GB">English (UK)</MenuItem>
                  <MenuItem value="hi-IN">Hindi (India)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Voice Name"
                value={formData.voice_settings.voice_name}
                onChange={(e) => handleNestedFieldChange('voice_settings', 'voice_name', e.target.value)}
                disabled={isReadOnly}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Speaking Rate</Typography>
              <Slider
                value={formData.voice_settings.speaking_rate}
                onChange={(_, value) => handleNestedFieldChange('voice_settings', 'speaking_rate', value)}
                min={0.5}
                max={2.0}
                step={0.1}
                marks
                valueLabelDisplay="auto"
                disabled={isReadOnly}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Pitch</Typography>
              <Slider
                value={formData.voice_settings.pitch}
                onChange={(_, value) => handleNestedFieldChange('voice_settings', 'pitch', value)}
                min={-2.0}
                max={2.0}
                step={0.1}
                marks
                valueLabelDisplay="auto"
                disabled={isReadOnly}
              />
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Response Patterns */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Response Patterns</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {/* Greeting Patterns */}
          <Typography variant="subtitle2" gutterBottom>
            Greeting Patterns
          </Typography>
          {!isReadOnly && (
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                size="small"
                label="Add greeting pattern"
                value={newGreeting}
                onChange={(e) => setNewGreeting(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addToArrayField('greeting_patterns', newGreeting);
                    setNewGreeting('');
                  }
                }}
              />
              <Button
                variant="outlined"
                onClick={() => {
                  addToArrayField('greeting_patterns', newGreeting);
                  setNewGreeting('');
                }}
                disabled={!newGreeting.trim()}
              >
                Add
              </Button>
            </Box>
          )}
          <List dense>
            {formData.greeting_patterns.map((pattern, index) => (
              <ListItem key={index}>
                <ListItemText primary={pattern} />
                {!isReadOnly && (
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => removeFromArrayField('greeting_patterns', index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                )}
              </ListItem>
            ))}
          </List>

          <Divider sx={{ my: 2 }} />

          {/* Farewell Patterns */}
          <Typography variant="subtitle2" gutterBottom>
            Farewell Patterns
          </Typography>
          {!isReadOnly && (
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                size="small"
                label="Add farewell pattern"
                value={newFarewell}
                onChange={(e) => setNewFarewell(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addToArrayField('farewell_patterns', newFarewell);
                    setNewFarewell('');
                  }
                }}
              />
              <Button
                variant="outlined"
                onClick={() => {
                  addToArrayField('farewell_patterns', newFarewell);
                  setNewFarewell('');
                }}
                disabled={!newFarewell.trim()}
              >
                Add
              </Button>
            </Box>
          )}
          <List dense>
            {formData.farewell_patterns.map((pattern, index) => (
              <ListItem key={index}>
                <ListItemText primary={pattern} />
                {!isReadOnly && (
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => removeFromArrayField('farewell_patterns', index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                )}
              </ListItem>
            ))}
          </List>
        </AccordionDetails>
      </Accordion>

      {/* Settings */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Settings</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => handleFieldChange('is_active', e.target.checked)}
                    disabled={isReadOnly}
                  />
                }
                label="Active"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Tags
              </Typography>
              {!isReadOnly && (
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Add tag"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addToArrayField('tags', newTag);
                        setNewTag('');
                      }
                    }}
                  />
                  <Button
                    variant="outlined"
                    onClick={() => {
                      addToArrayField('tags', newTag);
                      setNewTag('');
                    }}
                    disabled={!newTag.trim()}
                  >
                    Add
                  </Button>
                </Box>
              )}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.tags.map((tag, index) => (
                  <Chip
                    key={index}
                    label={tag}
                    onDelete={isReadOnly ? undefined : () => removeFromArrayField('tags', index)}
                    color="secondary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* Action Buttons */}
      {!isReadOnly && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
          <Button onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="outlined"
            startIcon={<PreviewIcon />}
            onClick={() => setPreviewOpen(true)}
          >
            Preview
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save'}
          </Button>
        </Box>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Personality Preview</DialogTitle>
        <DialogContent>
          <Typography variant="h6" gutterBottom>
            {formData.display_name}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {formData.domain} • {formData.time_period}
          </Typography>
          <Typography variant="body1" paragraph>
            {formData.description}
          </Typography>
          <Typography variant="subtitle2" gutterBottom>
            System Prompt Preview:
          </Typography>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
            {formData.system_prompt}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PersonalityEditor;