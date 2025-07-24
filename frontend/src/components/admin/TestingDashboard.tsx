/**
 * Testing Dashboard Component for Vimarsh Admin Interface
 * 
 * Comprehensive testing interface including:
 * - End-to-end testing of multi-personality functionality
 * - Performance testing and monitoring
 * - Bug tracking and resolution
 * - Browser compatibility testing
 */

import React, { useState, useEffect } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  PlayArrow as RunIcon,
  CheckCircle as PassIcon,
  Error as FailIcon,
  Warning as WarningIcon,
  BugReport as BugIcon,
  Speed as PerformanceIcon,
  Devices as CompatibilityIcon,
  Psychology as PersonalityIcon,
  ExpandMore as ExpandIcon,
  Refresh as RefreshIcon,
  GetApp as ExportIcon
} from '@mui/icons-material';

import testingService from '../../services/testingService';
import bugTrackingService from '../../services/bugTrackingService';
import LaunchReadinessChecklist from './LaunchReadinessChecklist';

interface TestResult {
  testName: string;
  status: 'pass' | 'fail' | 'warning' | 'running' | 'pending';
  message: string;
  duration?: number;
  details?: any;
  timestamp?: Date;
}

interface TestSuite {
  suiteName: string;
  tests: TestResult[];
  status: 'pass' | 'fail' | 'warning' | 'running' | 'pending';
  progress: number;
}

const TestingDashboard: React.FC = () => {
  // State
  const [selectedTab, setSelectedTab] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [bugReport, setBugReport] = useState<any>(null);
  const [selectedTest, setSelectedTest] = useState<TestResult | null>(null);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);

  // Load initial data
  useEffect(() => {
    loadBugReport();
    initializeTestSuites();
  }, []);

  const loadBugReport = () => {
    const report = bugTrackingService.getBugReport();
    setBugReport(report);
  };

  const initializeTestSuites = () => {
    const suites: TestSuite[] = [
      {
        suiteName: 'Personality Functionality',
        status: 'pending',
        progress: 0,
        tests: [
          { testName: 'Load Krishna Personality', status: 'pending', message: '' },
          { testName: 'Load Einstein Personality', status: 'pending', message: '' },
          { testName: 'Load Lincoln Personality', status: 'pending', message: '' },
          { testName: 'Load Marcus Aurelius Personality', status: 'pending', message: '' },
          { testName: 'Personality Switching', status: 'pending', message: '' },
          { testName: 'Conversation Continuity', status: 'pending', message: '' },
          { testName: 'Response Authenticity', status: 'pending', message: '' }
        ]
      },
      {
        suiteName: 'Voice Interface',
        status: 'pending',
        progress: 0,
        tests: [
          { testName: 'Voice Recognition', status: 'pending', message: '' },
          { testName: 'Text-to-Speech', status: 'pending', message: '' },
          { testName: 'Personality Voice Switching', status: 'pending', message: '' },
          { testName: 'Pronunciation Guide', status: 'pending', message: '' }
        ]
      },
      {
        suiteName: 'Performance',
        status: 'pending',
        progress: 0,
        tests: [
          { testName: 'Response Times', status: 'pending', message: '' },
          { testName: 'Memory Usage', status: 'pending', message: '' },
          { testName: 'Cache Performance', status: 'pending', message: '' },
          { testName: 'Concurrent Users', status: 'pending', message: '' }
        ]
      },
      {
        suiteName: 'Browser Compatibility',
        status: 'pending',
        progress: 0,
        tests: [
          { testName: 'Browser Features', status: 'pending', message: '' },
          { testName: 'Mobile Responsiveness', status: 'pending', message: '' },
          { testName: 'Accessibility Features', status: 'pending', message: '' }
        ]
      }
    ];
    setTestSuites(suites);
  };

  // Event handlers
  const runAllTests = async () => {
    setIsRunning(true);
    setOverallProgress(0);

    try {
      const updatedSuites = [...testSuites];
      let totalTests = 0;
      let completedTests = 0;

      // Count total tests
      updatedSuites.forEach(suite => {
        totalTests += suite.tests.length;
      });

      // Run each test suite
      for (let suiteIndex = 0; suiteIndex < updatedSuites.length; suiteIndex++) {
        const suite = updatedSuites[suiteIndex];
        suite.status = 'running';
        setTestSuites([...updatedSuites]);

        let suiteResults: TestResult[] = [];

        // Run tests based on suite type
        switch (suite.suiteName) {
          case 'Personality Functionality':
            suiteResults = await testingService.testPersonalityFunctionality();
            break;
          case 'Voice Interface':
            suiteResults = await testingService.testVoiceInterface();
            break;
          case 'Performance':
            suiteResults = await testingService.testPerformance();
            break;
          case 'Browser Compatibility':
            suiteResults = await testingService.testBrowserCompatibility();
            break;
        }

        // Update suite with results
        suite.tests = suiteResults;
        suite.progress = 100;
        
        // Determine suite status
        const hasFailures = suiteResults.some(test => test.status === 'fail');
        const hasWarnings = suiteResults.some(test => test.status === 'warning');
        suite.status = hasFailures ? 'fail' : hasWarnings ? 'warning' : 'pass';

        completedTests += suiteResults.length;
        setOverallProgress((completedTests / totalTests) * 100);
        setTestSuites([...updatedSuites]);
      }

      // Run automated bug detection
      bugTrackingService.runAutomatedBugDetection();
      loadBugReport();

    } catch (error) {
      console.error('Test execution failed:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const runSingleSuite = async (suiteIndex: number) => {
    const updatedSuites = [...testSuites];
    const suite = updatedSuites[suiteIndex];
    
    suite.status = 'running';
    setTestSuites([...updatedSuites]);

    try {
      let suiteResults: TestResult[] = [];

      switch (suite.suiteName) {
        case 'Personality Functionality':
          suiteResults = await testingService.testPersonalityFunctionality();
          break;
        case 'Voice Interface':
          suiteResults = await testingService.testVoiceInterface();
          break;
        case 'Performance':
          suiteResults = await testingService.testPerformance();
          break;
        case 'Browser Compatibility':
          suiteResults = await testingService.testBrowserCompatibility();
          break;
      }

      suite.tests = suiteResults;
      suite.progress = 100;
      
      const hasFailures = suiteResults.some(test => test.status === 'fail');
      const hasWarnings = suiteResults.some(test => test.status === 'warning');
      suite.status = hasFailures ? 'fail' : hasWarnings ? 'warning' : 'pass';

      setTestSuites([...updatedSuites]);
    } catch (error) {
      suite.status = 'fail';
      console.error(`Suite ${suite.suiteName} failed:`, error);
    }
  };

  const openTestDetails = (test: TestResult) => {
    setSelectedTest(test);
    setTestDialogOpen(true);
  };

  const exportTestResults = () => {
    const results = {
      timestamp: new Date().toISOString(),
      overallProgress,
      testSuites,
      bugReport
    };

    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vimarsh-test-results-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <PassIcon color="success" />;
      case 'fail': return <FailIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'running': return <CircularProgress size={20} />;
      default: return <CircularProgress size={20} color="inherit" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass': return 'success';
      case 'fail': return 'error';
      case 'warning': return 'warning';
      case 'running': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Testing Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<ExportIcon />}
            onClick={exportTestResults}
          >
            Export Results
          </Button>
          <Button
            variant="contained"
            startIcon={<RunIcon />}
            onClick={runAllTests}
            disabled={isRunning}
          >
            {isRunning ? 'Running Tests...' : 'Run All Tests'}
          </Button>
        </Box>
      </Box>

      {/* Overall Progress */}
      {isRunning && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Overall Test Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={overallProgress}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {overallProgress.toFixed(1)}% Complete
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs
        value={selectedTab}
        onChange={(_, newValue) => setSelectedTab(newValue)}
        sx={{ mb: 3 }}
      >
        <Tab icon={<PersonalityIcon />} label="Test Suites" />
        <Tab icon={<BugIcon />} label={`Bug Report (${bugReport?.openBugs || 0})`} />
        <Tab icon={<PerformanceIcon />} label="Performance" />
        <Tab icon={<CompatibilityIcon />} label="Compatibility" />
        <Tab icon={<RunIcon />} label="Launch Readiness" />
      </Tabs>

      {/* Test Suites Tab */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          {testSuites.map((suite, index) => (
            <Grid item xs={12} md={6} key={suite.suiteName}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      {suite.suiteName}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getStatusIcon(suite.status)}
                      <Button
                        size="small"
                        onClick={() => runSingleSuite(index)}
                        disabled={isRunning}
                      >
                        Run
                      </Button>
                    </Box>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={suite.progress}
                    sx={{ mb: 2, height: 6, borderRadius: 3 }}
                  />

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {suite.tests.filter(t => t.status === 'pass').length} / {suite.tests.length} tests passed
                  </Typography>

                  <List dense>
                    {suite.tests.slice(0, 3).map((test, testIndex) => (
                      <ListItem
                        key={testIndex}
                        button
                        onClick={() => openTestDetails(test)}
                      >
                        <ListItemIcon>
                          {getStatusIcon(test.status)}
                        </ListItemIcon>
                        <ListItemText
                          primary={test.testName}
                          secondary={test.message}
                        />
                      </ListItem>
                    ))}
                    {suite.tests.length > 3 && (
                      <ListItem>
                        <ListItemText
                          primary={`+${suite.tests.length - 3} more tests`}
                          sx={{ fontStyle: 'italic', color: 'text.secondary' }}
                        />
                      </ListItem>
                    )}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Bug Report Tab */}
      {selectedTab === 1 && bugReport && (
        <Grid container spacing={3}>
          {/* Bug Summary */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bug Summary
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {bugReport.totalBugs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Bugs
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="warning.main">
                        {bugReport.openBugs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Open Bugs
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="error.main">
                        {bugReport.criticalBugs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Critical Bugs
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        {bugReport.totalBugs - bugReport.openBugs}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Resolved Bugs
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Bugs */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Bugs
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Title</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell>Category</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Created</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bugReport.recentBugs.map((bug: any) => (
                        <TableRow key={bug.id}>
                          <TableCell>{bug.title}</TableCell>
                          <TableCell>
                            <Chip
                              label={bug.severity}
                              size="small"
                              color={getStatusColor(bug.severity === 'critical' ? 'fail' : bug.severity === 'high' ? 'warning' : 'default') as any}
                            />
                          </TableCell>
                          <TableCell>{bug.category}</TableCell>
                          <TableCell>
                            <Chip
                              label={bug.status}
                              size="small"
                              color={getStatusColor(bug.status === 'resolved' ? 'pass' : 'warning') as any}
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(bug.createdAt).toLocaleDateString()}
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

      {/* Launch Readiness Tab */}
      {selectedTab === 4 && (
        <LaunchReadinessChecklist />
      )}

      {/* Test Details Dialog */}
      <Dialog
        open={testDialogOpen}
        onClose={() => setTestDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Test Details
        </DialogTitle>
        <DialogContent>
          {selectedTest && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Test Name
                  </Typography>
                  <Typography variant="body1">
                    {selectedTest.testName}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Status
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getStatusIcon(selectedTest.status)}
                    <Chip
                      label={selectedTest.status}
                      color={getStatusColor(selectedTest.status) as any}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Message
                  </Typography>
                  <Typography variant="body1">
                    {selectedTest.message}
                  </Typography>
                </Grid>
                {selectedTest.duration && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Duration
                    </Typography>
                    <Typography variant="body1">
                      {selectedTest.duration}ms
                    </Typography>
                  </Grid>
                )}
                {selectedTest.timestamp && (
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Timestamp
                    </Typography>
                    <Typography variant="body1">
                      {selectedTest.timestamp.toLocaleString()}
                    </Typography>
                  </Grid>
                )}
                {selectedTest.details && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Details
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                      <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                        {JSON.stringify(selectedTest.details, null, 2)}
                      </pre>
                    </Paper>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TestingDashboard;