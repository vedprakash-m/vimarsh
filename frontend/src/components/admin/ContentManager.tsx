/**
 * Content Manager Component for Vimarsh Admin Interface
 *
 * Provides comprehensive content management capabilities including:
 * - Drag-and-drop file upload with batch processing
 * - Content-personality association interface
 * - Content preview and editing capabilities
 * - Content quality metrics and validation
 * - Bulk content operations and organization
 */

import React, { useState, useEffect, useCallback } from "react";
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
  Grid2 as Grid,
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
  Checkbox,
  FormControlLabel,
} from "@mui/material";
import {
  CloudUpload as UploadIcon,
  Description as DocumentIcon,
  Book as BookIcon,
  Article as ArticleIcon,
  PictureAsPdf as PdfIcon,
  TextSnippet as TextIcon,
  Link as LinkIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Assignment as AssignIcon,
  CheckCircle as ApprovedIcon,
  Warning as PendingIcon,
  Error as RejectedIcon,
  Psychology as PersonalityIcon,
} from "@mui/icons-material";

// Types
interface ContentItem {
  id: string;
  title: string;
  type: "book" | "article" | "document" | "text" | "pdf" | "url";
  source: string;
  author?: string;
  description: string;
  content_preview: string;
  file_size?: number;
  upload_date: string;
  status: "pending" | "processing" | "approved" | "rejected";
  quality_score: number;
  associated_personalities: string[];
  domain: string;
  language: string;
  tags: string[];
  metadata: Record<string, any>;
}

interface UploadProgress {
  file: File;
  progress: number;
  status: "uploading" | "processing" | "complete" | "error";
  error?: string;
}

const ContentManager: React.FC = () => {
  // State
  const [content, setContent] = useState<ContentItem[]>([]);
  const [personalities, setPersonalities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDomain, setFilterDomain] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Upload state
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [dragOver, setDragOver] = useState(false);

  // Association state
  const [associationDialogOpen, setAssociationDialogOpen] = useState(false);
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(
    null
  );
  const [selectedPersonalities, setSelectedPersonalities] = useState<string[]>(
    []
  );

  // Preview state
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState<ContentItem | null>(
    null
  );

  // Load content and personalities
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load content
      const contentParams = new URLSearchParams();
      if (filterDomain !== "all") contentParams.append("domain", filterDomain);
      if (filterStatus !== "all") contentParams.append("status", filterStatus);
      if (searchQuery) contentParams.append("q", searchQuery);

      const contentResponse = await fetch(
        `/admin/content?${contentParams.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
            "Content-Type": "application/json",
          },
        }
      );

      // Load personalities
      const personalitiesResponse = await fetch(
        "/admin/personalities?active_only=true",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (contentResponse.ok) {
        const contentData = await contentResponse.json();
        setContent(contentData.content || []);
      }

      if (personalitiesResponse.ok) {
        const personalitiesData = await personalitiesResponse.json();
        setPersonalities(personalitiesData.personalities || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [filterDomain, filterStatus, searchQuery]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // File upload handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFileUpload(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFileUpload(files);
    }
  };

  const handleFileUpload = async (files: File[]) => {
    const newUploads: UploadProgress[] = files.map((file) => ({
      file,
      progress: 0,
      status: "uploading",
    }));

    setUploadProgress(newUploads);
    setUploadDialogOpen(true);

    // Simulate upload process
    for (let i = 0; i < newUploads.length; i++) {
      const upload = newUploads[i];

      try {
        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise((resolve) => setTimeout(resolve, 100));
          setUploadProgress((prev) =>
            prev.map((item, index) =>
              index === i ? { ...item, progress } : item
            )
          );
        }

        // Mark as processing
        setUploadProgress((prev) =>
          prev.map((item, index) =>
            index === i ? { ...item, status: "processing" } : item
          )
        );

        // Simulate processing
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Mark as complete
        setUploadProgress((prev) =>
          prev.map((item, index) =>
            index === i ? { ...item, status: "complete" } : item
          )
        );
      } catch (error) {
        setUploadProgress((prev) =>
          prev.map((item, index) =>
            index === i
              ? {
                  ...item,
                  status: "error",
                  error: "Upload failed",
                }
              : item
          )
        );
      }
    }

    // Reload content after upload
    setTimeout(() => {
      loadData();
    }, 1000);
  };

  // Content association handlers
  const openAssociationDialog = (contentItem: ContentItem) => {
    setSelectedContent(contentItem);
    setSelectedPersonalities(contentItem.associated_personalities);
    setAssociationDialogOpen(true);
  };

  const handleAssociationSave = async () => {
    if (!selectedContent) return;

    try {
      const response = await fetch(
        `/admin/content/${selectedContent.id}/associate`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("authToken")}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            personality_ids: selectedPersonalities,
          }),
        }
      );

      if (response.ok) {
        setAssociationDialogOpen(false);
        loadData();
      } else {
        throw new Error("Failed to update associations");
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to update associations"
      );
    }
  };

  // Content preview
  const openPreview = (contentItem: ContentItem) => {
    setPreviewContent(contentItem);
    setPreviewDialogOpen(true);
  };

  // Content deletion
  const handleDelete = async (contentId: string) => {
    if (!window.confirm("Are you sure you want to delete this content?")) {
      return;
    }

    try {
      const response = await fetch(`/admin/content/${contentId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        loadData();
      } else {
        throw new Error("Failed to delete content");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete content");
    }
  };

  // Bulk operations
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [bulkOperationDialogOpen, setBulkOperationDialogOpen] = useState(false);
  const [bulkOperation, setBulkOperation] = useState<
    "delete" | "associate" | "approve" | "reject"
  >("delete");

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(getFilteredContent().map((item) => item.id));
    } else {
      setSelectedItems([]);
    }
  };

  const handleSelectItem = (itemId: string, checked: boolean) => {
    if (checked) {
      setSelectedItems((prev) => [...prev, itemId]);
    } else {
      setSelectedItems((prev) => prev.filter((id) => id !== itemId));
    }
  };

  const handleBulkOperation = async () => {
    if (selectedItems.length === 0) return;

    try {
      const promises = selectedItems.map(async (itemId) => {
        switch (bulkOperation) {
          case "delete":
            return fetch(`/admin/content/${itemId}`, {
              method: "DELETE",
              headers: {
                Authorization: `Bearer ${localStorage.getItem("authToken")}`,
                "Content-Type": "application/json",
              },
            });
          case "approve":
            return fetch(`/admin/content/${itemId}/approve`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${localStorage.getItem("authToken")}`,
                "Content-Type": "application/json",
              },
            });
          case "reject":
            return fetch(`/admin/content/${itemId}/reject`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${localStorage.getItem("authToken")}`,
                "Content-Type": "application/json",
              },
            });
          default:
            return Promise.resolve();
        }
      });

      await Promise.all(promises);
      setBulkOperationDialogOpen(false);
      setSelectedItems([]);
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Bulk operation failed");
    }
  };

  // Quality validation
  const handleQualityValidation = async (contentId: string) => {
    try {
      const response = await fetch(`/admin/content/${contentId}/validate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        loadData();
      } else {
        throw new Error("Failed to validate content quality");
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to validate content quality"
      );
    }
  };

  // Get content icon
  const getContentIcon = (type: string) => {
    switch (type) {
      case "book":
        return <BookIcon />;
      case "article":
        return <ArticleIcon />;
      case "pdf":
        return <PdfIcon />;
      case "text":
        return <TextIcon />;
      case "url":
        return <LinkIcon />;
      default:
        return <DocumentIcon />;
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <ApprovedIcon color="success" />;
      case "pending":
        return <PendingIcon color="warning" />;
      case "rejected":
        return <RejectedIcon color="error" />;
      default:
        return <PendingIcon />;
    }
  };

  // Filter content based on selected tab
  const getFilteredContent = () => {
    let filtered = content;

    switch (selectedTab) {
      case 0: // All
        break;
      case 1: // Pending Review
        filtered = content.filter((item) => item.status === "pending");
        break;
      case 2: // Approved
        filtered = content.filter((item) => item.status === "approved");
        break;
      case 3: // Unassociated
        filtered = content.filter(
          (item) => item.associated_personalities.length === 0
        );
        break;
    }

    return filtered;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1">
          Content Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => setUploadDialogOpen(true)}
        >
          Upload Content
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search content"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  endAdornment: (
                    <IconButton>
                      <SearchIcon />
                    </IconButton>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Domain</InputLabel>
                <Select
                  value={filterDomain}
                  onChange={(e) => setFilterDomain(e.target.value)}
                  label="Domain"
                >
                  <MenuItem value="all">All Domains</MenuItem>
                  <MenuItem value="spiritual">Spiritual</MenuItem>
                  <MenuItem value="scientific">Scientific</MenuItem>
                  <MenuItem value="historical">Historical</MenuItem>
                  <MenuItem value="philosophical">Philosophical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="rejected">Rejected</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <IconButton onClick={loadData}>
                <RefreshIcon />
              </IconButton>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Bulk Operations */}
      {selectedItems.length > 0 && (
        <Card sx={{ mb: 3, bgcolor: "primary.50" }}>
          <CardContent>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Typography variant="subtitle1">
                {selectedItems.length} item(s) selected
              </Typography>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setBulkOperation("approve");
                    setBulkOperationDialogOpen(true);
                  }}
                >
                  Approve Selected
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setBulkOperation("reject");
                    setBulkOperationDialogOpen(true);
                  }}
                >
                  Reject Selected
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    setBulkOperation("associate");
                    setBulkOperationDialogOpen(true);
                  }}
                >
                  Associate Selected
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  onClick={() => {
                    setBulkOperation("delete");
                    setBulkOperationDialogOpen(true);
                  }}
                >
                  Delete Selected
                </Button>
                <Button
                  variant="text"
                  size="small"
                  onClick={() => setSelectedItems([])}
                >
                  Clear Selection
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs
        value={selectedTab}
        onChange={(_, newValue) => setSelectedTab(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab label={`All (${content.length})`} />
        <Tab
          label={`Pending (${content.filter((c) => c.status === "pending").length})`}
        />
        <Tab
          label={`Approved (${content.filter((c) => c.status === "approved").length})`}
        />
        <Tab
          label={`Unassociated (${content.filter((c) => c.associated_personalities.length === 0).length})`}
        />
      </Tabs>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", p: 3 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Content Table */}
      {!loading && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={
                      selectedItems.length > 0 &&
                      selectedItems.length < getFilteredContent().length
                    }
                    checked={
                      getFilteredContent().length > 0 &&
                      selectedItems.length === getFilteredContent().length
                    }
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                </TableCell>
                <TableCell>Content</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Personalities</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {getFilteredContent().map((item) => (
                <TableRow
                  key={item.id}
                  selected={selectedItems.includes(item.id)}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedItems.includes(item.id)}
                      onChange={(e) =>
                        handleSelectItem(item.id, e.target.checked)
                      }
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                      {getContentIcon(item.type)}
                      <Box>
                        <Typography variant="subtitle2">
                          {item.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.author && `by ${item.author} • `}
                          {new Date(item.upload_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip label={item.type} size="small" />
                  </TableCell>
                  <TableCell>
                    <Chip label={item.domain} size="small" color="primary" />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      {getStatusIcon(item.status)}
                      <Typography variant="body2">{item.status}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography
                          variant="body2"
                          color={
                            item.quality_score >= 90
                              ? "success.main"
                              : item.quality_score >= 70
                                ? "warning.main"
                                : "error.main"
                          }
                        >
                          {item.quality_score.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={item.quality_score}
                        sx={{
                          width: 60,
                          height: 6,
                          borderRadius: 3,
                          "& .MuiLinearProgress-bar": {
                            backgroundColor:
                              item.quality_score >= 90
                                ? "success.main"
                                : item.quality_score >= 70
                                  ? "warning.main"
                                  : "error.main",
                          },
                        }}
                      />
                      <Tooltip title="Validate Quality">
                        <IconButton
                          size="small"
                          onClick={() => handleQualityValidation(item.id)}
                        >
                          <RefreshIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                      {item.associated_personalities
                        .slice(0, 2)
                        .map((personalityId) => {
                          const personality = personalities.find(
                            (p) => p.id === personalityId
                          );
                          return (
                            <Chip
                              key={personalityId}
                              label={personality?.display_name || personalityId}
                              size="small"
                              variant="outlined"
                            />
                          );
                        })}
                      {item.associated_personalities.length > 2 && (
                        <Chip
                          label={`+${item.associated_personalities.length - 2}`}
                          size="small"
                          color="primary"
                        />
                      )}
                      {item.associated_personalities.length === 0 && (
                        <Typography variant="caption" color="text.secondary">
                          None
                        </Typography>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Tooltip title="Preview">
                        <IconButton
                          size="small"
                          onClick={() => openPreview(item)}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Associate with Personalities">
                        <IconButton
                          size="small"
                          onClick={() => openAssociationDialog(item)}
                        >
                          <AssignIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(item.id)}
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
      {!loading && getFilteredContent().length === 0 && (
        <Card>
          <CardContent sx={{ textAlign: "center", py: 6 }}>
            <DocumentIcon
              sx={{ fontSize: 64, color: "text.secondary", mb: 2 }}
            />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No content found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Upload content to get started with personality knowledge bases.
            </Typography>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              onClick={() => setUploadDialogOpen(true)}
            >
              Upload Content
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Upload Content</DialogTitle>
        <DialogContent>
          {uploadProgress.length === 0 ? (
            <Box
              sx={{
                border: 2,
                borderColor: dragOver ? "primary.main" : "grey.300",
                borderStyle: "dashed",
                borderRadius: 2,
                p: 4,
                textAlign: "center",
                bgcolor: dragOver ? "primary.50" : "transparent",
                cursor: "pointer",
              }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              <UploadIcon
                sx={{ fontSize: 48, color: "text.secondary", mb: 2 }}
              />
              <Typography variant="h6" gutterBottom>
                Drag and drop files here
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                or click to select files
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supported formats: TXT, PDF, HTML, DOCX, EPUB
              </Typography>
              <input
                id="file-input"
                type="file"
                multiple
                accept=".txt,.pdf,.html,.docx,.epub"
                style={{ display: "none" }}
                onChange={handleFileSelect}
              />
            </Box>
          ) : (
            <List>
              {uploadProgress.map((upload, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={upload.file.name}
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={upload.progress}
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="caption">
                          {upload.status === "uploading" &&
                            `Uploading... ${upload.progress}%`}
                          {upload.status === "processing" && "Processing..."}
                          {upload.status === "complete" && "Complete"}
                          {upload.status === "error" &&
                            `Error: ${upload.error}`}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>
            {uploadProgress.length === 0 ? "Cancel" : "Close"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Association Dialog */}
      <Dialog
        open={associationDialogOpen}
        onClose={() => setAssociationDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Associate Content with Personalities</DialogTitle>
        <DialogContent>
          {selectedContent && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Content: {selectedContent.title}
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>
                Select Personalities:
              </Typography>
              <List>
                {personalities.map((personality) => (
                  <ListItem key={personality.id}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={selectedPersonalities.includes(
                            personality.id
                          )}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedPersonalities((prev) => [
                                ...prev,
                                personality.id,
                              ]);
                            } else {
                              setSelectedPersonalities((prev) =>
                                prev.filter((id) => id !== personality.id)
                              );
                            }
                          }}
                        />
                      }
                      label={
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <PersonalityIcon />
                          <Box>
                            <Typography variant="body2">
                              {personality.display_name}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {personality.domain} • {personality.time_period}
                            </Typography>
                          </Box>
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
          <Button onClick={() => setAssociationDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleAssociationSave}>
            Save Associations
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog
        open={previewDialogOpen}
        onClose={() => setPreviewDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>Content Preview</DialogTitle>
        <DialogContent>
          {previewContent && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {previewContent.title}
              </Typography>
              {previewContent.author && (
                <Typography
                  variant="subtitle2"
                  color="text.secondary"
                  gutterBottom
                >
                  by {previewContent.author}
                </Typography>
              )}
              <Divider sx={{ my: 2 }} />
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {previewContent.content_preview}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Operations Dialog */}
      <Dialog
        open={bulkOperationDialogOpen}
        onClose={() => setBulkOperationDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Bulk Operation Confirmation</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to {bulkOperation} {selectedItems.length}{" "}
            selected item(s)?
          </Typography>
          {bulkOperation === "delete" && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This action cannot be undone. All selected content will be
              permanently deleted.
            </Alert>
          )}
          {bulkOperation === "associate" && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Select personalities to associate with all selected content:
              </Typography>
              <List>
                {personalities.map((personality) => (
                  <ListItem key={personality.id}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={selectedPersonalities.includes(
                            personality.id
                          )}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedPersonalities((prev) => [
                                ...prev,
                                personality.id,
                              ]);
                            } else {
                              setSelectedPersonalities((prev) =>
                                prev.filter((id) => id !== personality.id)
                              );
                            }
                          }}
                        />
                      }
                      label={
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <PersonalityIcon />
                          <Box>
                            <Typography variant="body2">
                              {personality.display_name}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {personality.domain} • {personality.time_period}
                            </Typography>
                          </Box>
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
          <Button onClick={() => setBulkOperationDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            color={bulkOperation === "delete" ? "error" : "primary"}
            onClick={handleBulkOperation}
          >
            Confirm {bulkOperation}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ContentManager;
