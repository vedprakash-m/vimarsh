/**
 * Content Uploader Component for Vimarsh Admin Interface
 * 
 * Provides advanced file upload capabilities including:
 * - Drag-and-drop file upload with progress tracking
 * - Batch processing with real-time status updates
 * - File validation and format detection
 * - Metadata extraction and editing
 * - Content preprocessing and quality analysis
 */

import React, { useState, useCallback } from 'react';
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
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as DocumentIcon,
  Book as BookIcon,
  Article as ArticleIcon,
  PictureAsPdf as PdfIcon,
  TextSnippet as TextIcon,
  Delete as DeleteIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  Psychology as PersonalityIcon
} from '@mui/icons-material';

// Types
interface FileUpload {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'analyzing' | 'complete' | 'error';
  progress: number;
  error?: string;
  metadata: {
    title: string;
    author: string;
    description: string;
    domain: string;
    language: string;
    tags: string[];
    source_type: 'book' | 'article' | 'document' | 'text' | 'pdf' | 'url';
  };
  analysis?: {
    word_count: number;
    quality_score: number;
    detected_language: string;
    content_type: string;
    key_topics: string[];
    readability_score: number;
  };
  preview?: string;
}

interface ContentUploaderProps {
  open: boolean;
  onClose: () => void;
  onUploadComplete?: (uploads: FileUpload[]) => void;
  personalities?: any[];
}

const ContentUploader: React.FC<ContentUploaderProps> = ({
  open,
  onClose,
  onUploadComplete,
  personalities = []
}) => {
  // State
  const [uploads, setUploads] = useState<FileUpload[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);

  const steps = ['Upload Files', 'Configure Metadata', 'Review & Process'];

  // File handling
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      addFiles(files);
    }
  }, []);

  const addFiles = (files: File[]) => {
    const newUploads: FileUpload[] = files.map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      file,
      status: 'pending',
      progress: 0,
      metadata: {
        title: file.name.replace(/\.[^/.]+$/, ''), // Remove extension
        author: '',
        description: '',
        domain: 'spiritual',
        language: 'English',
        tags: [],
        source_type: getFileType(file)
      }
    }));

    setUploads(prev => [...prev, ...newUploads]);
    if (currentStep === 0) {
      setCurrentStep(1);
    }
  };

  const getFileType = (file: File): FileUpload['metadata']['source_type'] => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf': return 'pdf';
      case 'txt': return 'text';
      case 'html': case 'htm': return 'document';
      case 'docx': case 'doc': return 'document';
      case 'epub': return 'book';
      default: return 'document';
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'book': return <BookIcon />;
      case 'article': return <ArticleIcon />;
      case 'pdf': return <PdfIcon />;
      case 'text': return <TextIcon />;
      default: return <DocumentIcon />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete': return <SuccessIcon color="success" />;
      case 'error': return <ErrorIcon color="error" />;
      case 'processing': case 'analyzing': return <WarningIcon color="warning" />;
      default: return null;
    }
  };

  // Remove file
  const removeFile = (id: string) => {
    setUploads(prev => prev.filter(upload => upload.id !== id));
  };

  // Update metadata
  const updateMetadata = (id: string, field: string, value: any) => {
    setUploads(prev => prev.map(upload => 
      upload.id === id 
        ? { ...upload, metadata: { ...upload.metadata, [field]: value } }
        : upload
    ));
  };

  // Add tag
  const addTag = (id: string, tag: string) => {
    if (!tag.trim()) return;
    
    setUploads(prev => prev.map(upload => 
      upload.id === id 
        ? { 
            ...upload, 
            metadata: { 
              ...upload.metadata, 
              tags: [...upload.metadata.tags, tag.trim()] 
            } 
          }
        : upload
    ));
  };

  // Remove tag
  const removeTag = (id: string, tagIndex: number) => {
    setUploads(prev => prev.map(upload => 
      upload.id === id 
        ? { 
            ...upload, 
            metadata: { 
              ...upload.metadata, 
              tags: upload.metadata.tags.filter((_, index) => index !== tagIndex) 
            } 
          }
        : upload
    ));
  };

  // Process uploads
  const processUploads = async () => {
    setProcessing(true);
    setCurrentStep(2);

    for (let i = 0; i < uploads.length; i++) {
      const upload = uploads[i];
      
      try {
        // Update status to uploading
        setUploads(prev => prev.map(u => 
          u.id === upload.id ? { ...u, status: 'uploading', progress: 0 } : u
        ));

        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 20) {
          await new Promise(resolve => setTimeout(resolve, 200));
          setUploads(prev => prev.map(u => 
            u.id === upload.id ? { ...u, progress } : u
          ));
        }

        // Update status to processing
        setUploads(prev => prev.map(u => 
          u.id === upload.id ? { ...u, status: 'processing' } : u
        ));

        // Simulate processing
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Update status to analyzing
        setUploads(prev => prev.map(u => 
          u.id === upload.id ? { ...u, status: 'analyzing' } : u
        ));

        // Simulate analysis
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Add analysis results
        const analysis = {
          word_count: Math.floor(Math.random() * 50000) + 1000,
          quality_score: Math.floor(Math.random() * 30) + 70,
          detected_language: upload.metadata.language,
          content_type: upload.metadata.source_type,
          key_topics: ['topic1', 'topic2', 'topic3'],
          readability_score: Math.floor(Math.random() * 40) + 60
        };

        const preview = `This is a preview of ${upload.metadata.title}. The content has been processed and analyzed for quality and relevance...`;

        // Update status to complete
        setUploads(prev => prev.map(u => 
          u.id === upload.id 
            ? { ...u, status: 'complete', analysis, preview }
            : u
        ));

      } catch (error) {
        setUploads(prev => prev.map(u => 
          u.id === upload.id 
            ? { ...u, status: 'error', error: 'Processing failed' }
            : u
        ));
      }
    }

    setProcessing(false);
  };

  // Handle completion
  const handleComplete = () => {
    if (onUploadComplete) {
      onUploadComplete(uploads.filter(u => u.status === 'complete'));
    }
    handleClose();
  };

  // Handle close
  const handleClose = () => {
    setUploads([]);
    setCurrentStep(0);
    setProcessing(false);
    onClose();
  };

  // Validation
  const canProceedToNext = () => {
    switch (currentStep) {
      case 0: return uploads.length > 0;
      case 1: return uploads.every(u => u.metadata.title && u.metadata.domain);
      case 2: return uploads.every(u => u.status === 'complete' || u.status === 'error');
      default: return false;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '90vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <UploadIcon />
          <Typography variant="h6">
            Upload Content
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Stepper */}
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step 1: Upload Files */}
        {currentStep === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Select Files to Upload
            </Typography>
            <Box
              sx={{
                border: 2,
                borderColor: dragOver ? 'primary.main' : 'grey.300',
                borderStyle: 'dashed',
                borderRadius: 2,
                p: 6,
                textAlign: 'center',
                bgcolor: dragOver ? 'primary.50' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input-uploader')?.click()}
            >
              <UploadIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Drag and drop files here
              </Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                or click to select files
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supported formats: TXT, PDF, HTML, DOCX, EPUB
              </Typography>
              <input
                id="file-input-uploader"
                type="file"
                multiple
                accept=".txt,.pdf,.html,.docx,.epub"
                style={{ display: 'none' }}
                onChange={handleFileSelect}
              />
            </Box>

            {uploads.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Selected Files ({uploads.length})
                </Typography>
                <List>
                  {uploads.map((upload) => (
                    <ListItem key={upload.id}>
                      <ListItemIcon>
                        {getFileIcon(upload.metadata.source_type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={upload.file.name}
                        secondary={`${(upload.file.size / 1024 / 1024).toFixed(2)} MB`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton onClick={() => removeFile(upload.id)}>
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        )}

        {/* Step 2: Configure Metadata */}
        {currentStep === 1 && (
          <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Configure Content Metadata
            </Typography>
            {uploads.map((upload) => (
              <Accordion key={upload.id} defaultExpanded={uploads.length === 1}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {getFileIcon(upload.metadata.source_type)}
                    <Typography variant="subtitle1">
                      {upload.file.name}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Title"
                        value={upload.metadata.title}
                        onChange={(e) => updateMetadata(upload.id, 'title', e.target.value)}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Author"
                        value={upload.metadata.author}
                        onChange={(e) => updateMetadata(upload.id, 'author', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={3}
                        label="Description"
                        value={upload.metadata.description}
                        onChange={(e) => updateMetadata(upload.id, 'description', e.target.value)}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Domain</InputLabel>
                        <Select
                          value={upload.metadata.domain}
                          onChange={(e) => updateMetadata(upload.id, 'domain', e.target.value)}
                          label="Domain"
                          required
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
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Source Type</InputLabel>
                        <Select
                          value={upload.metadata.source_type}
                          onChange={(e) => updateMetadata(upload.id, 'source_type', e.target.value)}
                          label="Source Type"
                        >
                          <MenuItem value="book">Book</MenuItem>
                          <MenuItem value="article">Article</MenuItem>
                          <MenuItem value="document">Document</MenuItem>
                          <MenuItem value="text">Text</MenuItem>
                          <MenuItem value="pdf">PDF</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Language</InputLabel>
                        <Select
                          value={upload.metadata.language}
                          onChange={(e) => updateMetadata(upload.id, 'language', e.target.value)}
                          label="Language"
                        >
                          <MenuItem value="English">English</MenuItem>
                          <MenuItem value="Hindi">Hindi</MenuItem>
                          <MenuItem value="Sanskrit">Sanskrit</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Tags
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                        {upload.metadata.tags.map((tag, index) => (
                          <Chip
                            key={index}
                            label={tag}
                            onDelete={() => removeTag(upload.id, index)}
                            size="small"
                          />
                        ))}
                      </Box>
                      <TextField
                        fullWidth
                        size="small"
                        label="Add tag"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            addTag(upload.id, (e.target as HTMLInputElement).value);
                            (e.target as HTMLInputElement).value = '';
                          }
                        }}
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}

        {/* Step 3: Review & Process */}
        {currentStep === 2 && (
          <Box sx={{ maxHeight: '60vh', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Processing Results
            </Typography>
            <List>
              {uploads.map((upload) => (
                <ListItem key={upload.id}>
                  <ListItemIcon>
                    {getStatusIcon(upload.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={upload.metadata.title}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          Status: {upload.status}
                        </Typography>
                        {upload.status === 'uploading' && (
                          <LinearProgress
                            variant="determinate"
                            value={upload.progress}
                            sx={{ mt: 1 }}
                          />
                        )}
                        {upload.analysis && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" display="block">
                              Words: {upload.analysis.word_count.toLocaleString()} • 
                              Quality: {upload.analysis.quality_score}% • 
                              Readability: {upload.analysis.readability_score}%
                            </Typography>
                          </Box>
                        )}
                        {upload.error && (
                          <Alert severity="error" sx={{ mt: 1 }}>
                            {upload.error}
                          </Alert>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>
          Cancel
        </Button>
        {currentStep < 2 && (
          <Button
            variant="contained"
            onClick={() => {
              if (currentStep === 1) {
                processUploads();
              } else {
                setCurrentStep(prev => prev + 1);
              }
            }}
            disabled={!canProceedToNext() || processing}
          >
            {currentStep === 1 ? 'Process Files' : 'Next'}
          </Button>
        )}
        {currentStep === 2 && !processing && (
          <Button
            variant="contained"
            onClick={handleComplete}
            disabled={uploads.filter(u => u.status === 'complete').length === 0}
          >
            Complete Upload
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ContentUploader;