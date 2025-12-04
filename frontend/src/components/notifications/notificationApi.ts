/**
 * Notification API Service
 * Frontend client for notification endpoints
 */

import { getApiBaseUrl } from '../../config/environment';
import { getAuthHeaders } from '../../auth/authService';
import type { 
  NotificationPreferences, 
  NotificationStatus,
  NotificationPreferencesUpdate,
  PushSubscription
} from './types';

const API_BASE = getApiBaseUrl();

/**
 * Subscribe to push notifications
 */
export async function subscribeToNotifications(
  subscription: PushSubscription
): Promise<{ success: boolean; subscription_id?: string; message?: string }> {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_BASE}/api/notifications/subscribe`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: JSON.stringify({ subscription })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to subscribe');
  }
  
  return response.json();
}

/**
 * Unsubscribe from push notifications
 */
export async function unsubscribeFromNotifications(
  endpoint?: string
): Promise<{ success: boolean; message?: string }> {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_BASE}/api/notifications/unsubscribe`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: endpoint ? JSON.stringify({ endpoint }) : undefined
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to unsubscribe');
  }
  
  return response.json();
}

/**
 * Get notification preferences
 */
export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_BASE}/api/notifications/preferences`, {
    method: 'GET',
    headers
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get preferences');
  }
  
  return response.json();
}

/**
 * Update notification preferences
 */
export async function updateNotificationPreferences(
  updates: NotificationPreferencesUpdate
): Promise<{ success: boolean; preferences: NotificationPreferences }> {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_BASE}/api/notifications/preferences`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...headers
    },
    body: JSON.stringify(updates)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to update preferences');
  }
  
  return response.json();
}

/**
 * Get notification status
 */
export async function getNotificationStatus(): Promise<NotificationStatus> {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_BASE}/api/notifications/status`, {
    method: 'GET',
    headers
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get status');
  }
  
  return response.json();
}

/**
 * Send a test notification
 */
export async function sendTestNotification(): Promise<{ 
  success: boolean; 
  message: string;
  details?: Record<string, unknown>;
}> {
  const headers = await getAuthHeaders();
  
  const response = await fetch(`${API_BASE}/api/notifications/test`, {
    method: 'POST',
    headers
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to send test notification');
  }
  
  return response.json();
}

export const notificationApi = {
  subscribe: subscribeToNotifications,
  unsubscribe: unsubscribeFromNotifications,
  getPreferences: getNotificationPreferences,
  updatePreferences: updateNotificationPreferences,
  getStatus: getNotificationStatus,
  sendTest: sendTestNotification
};
