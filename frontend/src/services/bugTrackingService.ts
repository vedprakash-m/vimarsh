/**
 * Bug Tracking and Resolution Service for Vimarsh Platform
 * 
 * Handles bug detection, tracking, and automated resolution
 * for multi-personality platform issues.
 */

interface Bug {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: 'personality' | 'voice' | 'ui' | 'performance' | 'compatibility';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  personalityId?: string;
  steps: string[];
  expectedBehavior: string;
  actualBehavior: string;
  environment: {
    browser: string;
    version: string;
    os: string;
    device: string;
  };
  createdAt: Date;
  resolvedAt?: Date;
  resolution?: string;
}

interface BugReport {
  totalBugs: number;
  openBugs: number;
  criticalBugs: number;
  bugsByCategory: Record<string, number>;
  bugsBySeverity: Record<string, number>;
  recentBugs: Bug[];
}

class BugTrackingService {
  private bugs: Bug[] = [];
  private knownIssues: Bug[] = [];

  constructor() {
    this.initializeKnownIssues();
    this.setupErrorHandling();
  }

  /**
   * Initialize known issues and their resolutions
   */
  private initializeKnownIssues(): void {
    this.knownIssues = [
      {
        id: 'bug_001',
        title: 'Personality switching delay in Safari',
        description: 'Personality switching takes longer than expected in Safari browser',
        severity: 'medium',
        category: 'personality',
        status: 'resolved',
        steps: [
          'Open application in Safari',
          'Select Krishna personality',
          'Switch to Einstein personality',
          'Observe delay'
        ],
        expectedBehavior: 'Personality should switch within 1 second',
        actualBehavior: 'Personality switching takes 3-5 seconds',
        environment: {
          browser: 'Safari',
          version: '14+',
          os: 'macOS',
          device: 'Desktop'
        },
        createdAt: new Date('2024-01-15'),
        resolvedAt: new Date('2024-01-16'),
        resolution: 'Optimized personality loading cache for Safari compatibility'
      },
      {
        id: 'bug_002',
        title: 'Voice recognition not working in Firefox',
        description: 'Speech recognition fails to initialize in Firefox browser',
        severity: 'high',
        category: 'voice',
        status: 'resolved',
        steps: [
          'Open application in Firefox',
          'Click voice input button',
          'Grant microphone permissions',
          'Attempt to speak'
        ],
        expectedBehavior: 'Voice recognition should capture speech',
        actualBehavior: 'Voice recognition fails to start',
        environment: {
          browser: 'Firefox',
          version: '90+',
          os: 'Windows',
          device: 'Desktop'
        },
        createdAt: new Date('2024-01-10'),
        resolvedAt: new Date('2024-01-12'),
        resolution: 'Added Firefox-specific speech recognition polyfill'
      },
      {
        id: 'bug_003',
        title: 'Mobile layout issues on small screens',
        description: 'UI elements overlap on screens smaller than 320px',
        severity: 'medium',
        category: 'ui',
        status: 'resolved',
        steps: [
          'Open application on mobile device',
          'Use screen width < 320px',
          'Navigate through interface'
        ],
        expectedBehavior: 'UI should be responsive and readable',
        actualBehavior: 'Text and buttons overlap',
        environment: {
          browser: 'Chrome Mobile',
          version: '90+',
          os: 'Android',
          device: 'Mobile'
        },
        createdAt: new Date('2024-01-08'),
        resolvedAt: new Date('2024-01-09'),
        resolution: 'Updated CSS media queries for ultra-small screens'
      }
    ];
  }

  /**
   * Setup global error handling
   */
  private setupErrorHandling(): void {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.reportBug({
        title: 'Unhandled Promise Rejection',
        description: event.reason?.message || 'Unknown promise rejection',
        severity: 'high',
        category: 'performance',
        steps: ['Automatic detection'],
        expectedBehavior: 'No unhandled promise rejections',
        actualBehavior: `Promise rejected: ${event.reason?.message}`,
        environment: this.getCurrentEnvironment()
      });
    });

    // Handle JavaScript errors
    window.addEventListener('error', (event) => {
      this.reportBug({
        title: 'JavaScript Error',
        description: event.message,
        severity: 'high',
        category: 'performance',
        steps: ['Automatic detection'],
        expectedBehavior: 'No JavaScript errors',
        actualBehavior: `Error: ${event.message} at ${event.filename}:${event.lineno}`,
        environment: this.getCurrentEnvironment()
      });
    });
  }

  /**
   * Report a new bug
   */
  reportBug(bugData: Omit<Bug, 'id' | 'status' | 'createdAt'>): string {
    const bug: Bug = {
      ...bugData,
      id: this.generateBugId(),
      status: 'open',
      createdAt: new Date()
    };

    this.bugs.push(bug);
    
    // Check for automatic resolution
    this.checkForAutoResolution(bug);
    
    console.warn('Bug reported:', bug);
    return bug.id;
  }

  /**
   * Get bug report summary
   */
  getBugReport(): BugReport {
    const totalBugs = this.bugs.length;
    const openBugs = this.bugs.filter(bug => bug.status === 'open').length;
    const criticalBugs = this.bugs.filter(bug => bug.severity === 'critical').length;

    const bugsByCategory = this.bugs.reduce((acc, bug) => {
      acc[bug.category] = (acc[bug.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const bugsBySeverity = this.bugs.reduce((acc, bug) => {
      acc[bug.severity] = (acc[bug.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recentBugs = this.bugs
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, 10);

    return {
      totalBugs,
      openBugs,
      criticalBugs,
      bugsByCategory,
      bugsBySeverity,
      recentBugs
    };
  }

  /**
   * Get bugs by category
   */
  getBugsByCategory(category: Bug['category']): Bug[] {
    return this.bugs.filter(bug => bug.category === category);
  }

  /**
   * Get bugs by personality
   */
  getBugsByPersonality(personalityId: string): Bug[] {
    return this.bugs.filter(bug => bug.personalityId === personalityId);
  }

  /**
   * Resolve a bug
   */
  resolveBug(bugId: string, resolution: string): boolean {
    const bug = this.bugs.find(b => b.id === bugId);
    if (bug) {
      bug.status = 'resolved';
      bug.resolvedAt = new Date();
      bug.resolution = resolution;
      return true;
    }
    return false;
  }

  /**
   * Get known issues and their resolutions
   */
  getKnownIssues(): Bug[] {
    return this.knownIssues;
  }

  /**
   * Check for personality-specific bugs
   */
  checkPersonalityBugs(personalityId: string): Bug[] {
    const personalityBugs: Bug[] = [];

    // Check for common personality issues
    try {
      // Test personality loading
      const personalityData = this.getPersonalityData(personalityId);
      if (!personalityData) {
        personalityBugs.push({
          id: this.generateBugId(),
          title: `${personalityId} personality data missing`,
          description: `Personality data for ${personalityId} could not be loaded`,
          severity: 'critical',
          category: 'personality',
          status: 'open',
          personalityId,
          steps: [`Load ${personalityId} personality`],
          expectedBehavior: 'Personality data should load successfully',
          actualBehavior: 'Personality data is null or undefined',
          environment: this.getCurrentEnvironment(),
          createdAt: new Date()
        });
      }

      // Check voice settings
      const voiceSettings = this.getPersonalityVoiceSettings(personalityId);
      if (!voiceSettings) {
        personalityBugs.push({
          id: this.generateBugId(),
          title: `${personalityId} voice settings missing`,
          description: `Voice settings for ${personalityId} are not configured`,
          severity: 'medium',
          category: 'voice',
          status: 'open',
          personalityId,
          steps: [`Load ${personalityId} voice settings`],
          expectedBehavior: 'Voice settings should be available',
          actualBehavior: 'Voice settings are missing',
          environment: this.getCurrentEnvironment(),
          createdAt: new Date()
        });
      }
    } catch (error) {
      personalityBugs.push({
        id: this.generateBugId(),
        title: `Error checking ${personalityId} personality`,
        description: `Exception occurred while checking ${personalityId}: ${error}`,
        severity: 'high',
        category: 'personality',
        status: 'open',
        personalityId,
        steps: [`Check ${personalityId} personality`],
        expectedBehavior: 'No errors during personality check',
        actualBehavior: `Error: ${error}`,
        environment: this.getCurrentEnvironment(),
        createdAt: new Date()
      });
    }

    return personalityBugs;
  }

  /**
   * Run automated bug detection
   */
  runAutomatedBugDetection(): Bug[] {
    const detectedBugs: Bug[] = [];

    // Check browser compatibility
    const compatibilityIssues = this.checkBrowserCompatibility();
    detectedBugs.push(...compatibilityIssues);

    // Check performance issues
    const performanceIssues = this.checkPerformanceIssues();
    detectedBugs.push(...performanceIssues);

    // Check accessibility issues
    const accessibilityIssues = this.checkAccessibilityIssues();
    detectedBugs.push(...accessibilityIssues);

    // Add detected bugs to the main list
    this.bugs.push(...detectedBugs);

    return detectedBugs;
  }

  /**
   * Check for automatic resolution of bugs
   */
  private checkForAutoResolution(bug: Bug): void {
    // Check if this is a known issue with a resolution
    const knownIssue = this.knownIssues.find(known => 
      known.title === bug.title || 
      known.description === bug.description
    );

    if (knownIssue && knownIssue.resolution) {
      bug.status = 'resolved';
      bug.resolvedAt = new Date();
      bug.resolution = `Auto-resolved: ${knownIssue.resolution}`;
    }
  }

  /**
   * Check browser compatibility issues
   */
  private checkBrowserCompatibility(): Bug[] {
    const issues: Bug[] = [];
    const userAgent = navigator.userAgent;

    // Check for unsupported browsers
    if (userAgent.includes('MSIE') || userAgent.includes('Trident')) {
      issues.push({
        id: this.generateBugId(),
        title: 'Internet Explorer not supported',
        description: 'Application may not work correctly in Internet Explorer',
        severity: 'high',
        category: 'compatibility',
        status: 'open',
        steps: ['Open application in Internet Explorer'],
        expectedBehavior: 'Application should work in all modern browsers',
        actualBehavior: 'Internet Explorer lacks required features',
        environment: this.getCurrentEnvironment(),
        createdAt: new Date()
      });
    }

    // Check for speech recognition support
    if (!window.SpeechRecognition && !(window as any).webkitSpeechRecognition) {
      issues.push({
        id: this.generateBugId(),
        title: 'Speech recognition not supported',
        description: 'Browser does not support speech recognition API',
        severity: 'medium',
        category: 'voice',
        status: 'open',
        steps: ['Try to use voice input'],
        expectedBehavior: 'Voice input should be available',
        actualBehavior: 'Speech recognition API not available',
        environment: this.getCurrentEnvironment(),
        createdAt: new Date()
      });
    }

    return issues;
  }

  /**
   * Check for performance issues
   */
  private checkPerformanceIssues(): Bug[] {
    const issues: Bug[] = [];

    // Check memory usage
    if ((performance as any).memory) {
      const memoryInfo = (performance as any).memory;
      const memoryUsage = memoryInfo.usedJSHeapSize / (1024 * 1024); // MB

      if (memoryUsage > 100) { // 100MB threshold
        issues.push({
          id: this.generateBugId(),
          title: 'High memory usage detected',
          description: `Memory usage is ${memoryUsage.toFixed(1)}MB, above 100MB threshold`,
          severity: 'medium',
          category: 'performance',
          status: 'open',
          steps: ['Use application normally'],
          expectedBehavior: 'Memory usage should stay below 100MB',
          actualBehavior: `Memory usage: ${memoryUsage.toFixed(1)}MB`,
          environment: this.getCurrentEnvironment(),
          createdAt: new Date()
        });
      }
    }

    return issues;
  }

  /**
   * Check for accessibility issues
   */
  private checkAccessibilityIssues(): Bug[] {
    const issues: Bug[] = [];

    // Check for missing alt text on images
    const images = document.querySelectorAll('img:not([alt])');
    if (images.length > 0) {
      issues.push({
        id: this.generateBugId(),
        title: 'Images missing alt text',
        description: `${images.length} images found without alt text`,
        severity: 'low',
        category: 'ui',
        status: 'open',
        steps: ['Navigate through application'],
        expectedBehavior: 'All images should have alt text',
        actualBehavior: `${images.length} images missing alt text`,
        environment: this.getCurrentEnvironment(),
        createdAt: new Date()
      });
    }

    return issues;
  }

  /**
   * Helper methods
   */
  private generateBugId(): string {
    return `bug_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentEnvironment(): Bug['environment'] {
    const userAgent = navigator.userAgent;
    let browser = 'Unknown';
    let version = 'Unknown';

    if (userAgent.includes('Chrome')) {
      browser = 'Chrome';
      version = userAgent.match(/Chrome\/(\d+)/)?.[1] || 'Unknown';
    } else if (userAgent.includes('Firefox')) {
      browser = 'Firefox';
      version = userAgent.match(/Firefox\/(\d+)/)?.[1] || 'Unknown';
    } else if (userAgent.includes('Safari')) {
      browser = 'Safari';
      version = userAgent.match(/Version\/(\d+)/)?.[1] || 'Unknown';
    } else if (userAgent.includes('Edge')) {
      browser = 'Edge';
      version = userAgent.match(/Edge\/(\d+)/)?.[1] || 'Unknown';
    }

    return {
      browser,
      version,
      os: navigator.platform,
      device: /Mobi|Android/i.test(userAgent) ? 'Mobile' : 'Desktop'
    };
  }

  private getPersonalityData(personalityId: string): any {
    // Mock personality data check
    const personalities = ['krishna', 'einstein', 'lincoln', 'marcus_aurelius'];
    return personalities.includes(personalityId) ? { id: personalityId } : null;
  }

  private getPersonalityVoiceSettings(personalityId: string): any {
    // Mock voice settings check
    const voiceSettings = {
      krishna: { rate: 0.75, pitch: -1.5 },
      einstein: { rate: 0.85, pitch: 0.0 },
      lincoln: { rate: 0.8, pitch: -0.5 },
      marcus_aurelius: { rate: 0.7, pitch: -1.0 }
    };
    return voiceSettings[personalityId as keyof typeof voiceSettings];
  }
}

export const bugTrackingService = new BugTrackingService();
export default bugTrackingService;