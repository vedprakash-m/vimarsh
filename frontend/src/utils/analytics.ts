// Analytics utilities for Vimarsh application

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
}

export const trackEvent = (event: AnalyticsEvent): void => {
  // In development mode, just log to console
  if (process.env.NODE_ENV === 'development') {
    console.log('📊 Analytics:', event);
    return;
  }
  
  // TODO: Implement Application Insights tracking for production
  // Example: appInsights.trackEvent(event.name, event.properties);
};

export const trackPageView = (pageName: string): void => {
  if (process.env.NODE_ENV === 'development') {
    console.log('📄 Page View:', pageName);
    return;
  }
  
  // TODO: Implement Application Insights page tracking for production
  // Example: appInsights.trackPageView({ name: pageName });
};

export const trackUserAction = (action: string, context?: Record<string, any>): void => {
  trackEvent({
    name: 'user_action',
    properties: {
      action,
      ...context,
      timestamp: new Date().toISOString()
    }
  });
};

// Export empty object to make this a module
export {};