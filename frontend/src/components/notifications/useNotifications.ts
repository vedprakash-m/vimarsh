/**
 * useNotifications Hook
 * React hook for managing notification state and actions
 */

import { useState, useEffect, useCallback } from 'react';
import { pushNotificationService } from './pushNotificationService';
import { notificationApi } from './notificationApi';
import type { NotificationPreferences, NotificationStatus } from './types';

interface UseNotificationsResult {
  // State
  isSupported: boolean;
  permission: NotificationPermission;
  isSubscribed: boolean;
  isLoading: boolean;
  error: string | null;
  preferences: NotificationPreferences | null;
  status: NotificationStatus | null;

  // Actions
  requestPermission: () => Promise<NotificationPermission>;
  subscribe: () => Promise<boolean>;
  unsubscribe: () => Promise<boolean>;
  updatePreferences: (updates: Partial<NotificationPreferences>) => Promise<boolean>;
  sendTest: () => Promise<boolean>;
  refresh: () => Promise<void>;
}

export function useNotifications(): UseNotificationsResult {
  const [isSupported, setIsSupported] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [status, setStatus] = useState<NotificationStatus | null>(null);

  // Initialize state
  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      try {
        // Check browser support
        const supported = pushNotificationService.isSupported();
        setIsSupported(supported);

        if (supported) {
          // Get current permission
          setPermission(pushNotificationService.getPermissionState());

          // Check if already subscribed
          const subscribed = await pushNotificationService.isSubscribed();
          setIsSubscribed(subscribed);

          // Load status from backend
          try {
            const statusData = await notificationApi.getStatus();
            setStatus(statusData);
            setIsSubscribed(statusData.is_subscribed);
          } catch {
            // Backend may not be available
            console.log('Could not fetch notification status');
          }

          // Load preferences
          try {
            const prefsData = await notificationApi.getPreferences();
            setPreferences(prefsData);
          } catch {
            console.log('Could not fetch notification preferences');
          }
        }
      } catch (err) {
        console.error('Notification init error:', err);
        setError(err instanceof Error ? err.message : 'Failed to initialize');
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, []);

  // Request permission
  const requestPermission = useCallback(async () => {
    setError(null);
    const result = await pushNotificationService.requestPermission();
    setPermission(result);
    return result;
  }, []);

  // Subscribe to notifications
  const subscribe = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await pushNotificationService.subscribe();
      if (result.success) {
        setIsSubscribed(true);
        setPermission('granted');
        
        // Refresh status
        try {
          const statusData = await notificationApi.getStatus();
          setStatus(statusData);
        } catch {
          // Ignore
        }
        
        return true;
      } else {
        setError(result.error || 'Failed to subscribe');
        return false;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to subscribe';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Unsubscribe from notifications
  const unsubscribe = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await pushNotificationService.unsubscribe();
      if (result.success) {
        setIsSubscribed(false);
        
        // Refresh status
        try {
          const statusData = await notificationApi.getStatus();
          setStatus(statusData);
        } catch {
          // Ignore
        }
        
        return true;
      } else {
        setError(result.error || 'Failed to unsubscribe');
        return false;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to unsubscribe';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update preferences
  const updatePreferences = useCallback(async (updates: Partial<NotificationPreferences>) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await notificationApi.updatePreferences(updates);
      if (result.success) {
        setPreferences(result.preferences);
        return true;
      }
      return false;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update preferences';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Send test notification
  const sendTest = useCallback(async () => {
    setError(null);
    try {
      const result = await notificationApi.sendTest();
      return result.success;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to send test';
      setError(message);
      return false;
    }
  }, []);

  // Refresh all state
  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const [statusData, prefsData] = await Promise.all([
        notificationApi.getStatus().catch(() => null),
        notificationApi.getPreferences().catch(() => null)
      ]);
      
      if (statusData) {
        setStatus(statusData);
        setIsSubscribed(statusData.is_subscribed);
      }
      if (prefsData) {
        setPreferences(prefsData);
      }
    } catch (err) {
      console.error('Refresh error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isSupported,
    permission,
    isSubscribed,
    isLoading,
    error,
    preferences,
    status,
    requestPermission,
    subscribe,
    unsubscribe,
    updatePreferences,
    sendTest,
    refresh
  };
}
