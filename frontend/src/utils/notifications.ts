// Daily wisdom push notification service
// Manages subscription, scheduling, and delivery of spiritual notifications

import React from 'react';
import { pwaManager } from './pwa';

export interface WisdomNotification {
  id: string;
  title: string;
  body: string;
  icon?: string;
  badge?: string;
  data?: any;
  scheduledTime: Date;
  category: 'daily_wisdom' | 'meditation_reminder' | 'spiritual_quote' | 'teaching';
  source?: string; // Bhagavad Gita, Mahabharata, etc.
  language: 'en' | 'hi';
}

export interface NotificationPreferences {
  enabled: boolean;
  dailyWisdom: boolean;
  meditationReminders: boolean;
  spiritualQuotes: boolean;
  teachings: boolean;
  preferredTime: string; // HH:mm format
  timezone: string;
  language: 'en' | 'hi';
  frequency: 'daily' | 'every_other_day' | 'weekly';
}

class DailyWisdomNotificationService {
  private preferences: NotificationPreferences;
  private subscription: PushSubscription | null = null;
  private storageKey = 'vimarsh_notification_preferences';

  constructor() {
    this.preferences = this.loadPreferences();
    this.initializeService();
  }

  private loadPreferences(): NotificationPreferences {
    const stored = localStorage.getItem(this.storageKey);
    if (stored) {
      try {
        return { ...this.getDefaultPreferences(), ...JSON.parse(stored) };
      } catch (error) {
        console.error('[Notifications] Failed to parse preferences:', error);
      }
    }
    return this.getDefaultPreferences();
  }

  private getDefaultPreferences(): NotificationPreferences {
    return {
      enabled: false,
      dailyWisdom: true,
      meditationReminders: false,
      spiritualQuotes: true,
      teachings: true,
      preferredTime: '07:00', // 7 AM
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: 'en',
      frequency: 'daily'
    };
  }

  private savePreferences() {
    localStorage.setItem(this.storageKey, JSON.stringify(this.preferences));
  }

  private async initializeService() {
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
      console.warn('[Notifications] Push notifications not supported');
      return;
    }

    // Check if notifications are already enabled
    if (this.preferences.enabled && Notification.permission === 'granted') {
      await this.setupPushSubscription();
    }
  }

  // Public methods

  public async enableNotifications(): Promise<boolean> {
    try {
      const permission = await pwaManager.requestNotificationPermission();
      
      if (permission === 'granted') {
        this.preferences.enabled = true;
        this.savePreferences();
        
        await this.setupPushSubscription();
        await this.scheduleLocalNotifications();
        
        return true;
      } else {
        console.log('[Notifications] Permission denied');
        return false;
      }
    } catch (error) {
      console.error('[Notifications] Failed to enable notifications:', error);
      return false;
    }
  }

  public disableNotifications() {
    this.preferences.enabled = false;
    this.savePreferences();
    this.cancelAllNotifications();
  }

  public updatePreferences(newPreferences: Partial<NotificationPreferences>) {
    this.preferences = { ...this.preferences, ...newPreferences };
    this.savePreferences();
    
    if (this.preferences.enabled) {
      this.scheduleLocalNotifications();
    }
  }

  public getPreferences(): NotificationPreferences {
    return { ...this.preferences };
  }

  public async testNotification(): Promise<void> {
    if (!this.preferences.enabled || Notification.permission !== 'granted') {
      throw new Error('Notifications not enabled');
    }

    const wisdom = this.getRandomWisdom();
    const testNotification: WisdomNotification = {
      id: 'test_notification',
      title: wisdom.title,
      body: wisdom.body,
      scheduledTime: new Date(),
      category: 'daily_wisdom',
      source: wisdom.source,
      language: this.preferences.language
    };
    
    await this.showNotification(testNotification);
  }

  // Private implementation methods

  private async setupPushSubscription() {
    try {
      const registration = await navigator.serviceWorker.ready;
      
      this.subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlB64ToUint8Array(
          process.env.REACT_APP_VAPID_PUBLIC_KEY || ''
        ) as BufferSource
      });

      // Send subscription to server
      await this.sendSubscriptionToServer(this.subscription);
      
      console.log('[Notifications] Push subscription established');
    } catch (error) {
      console.error('[Notifications] Failed to setup push subscription:', error);
    }
  }

  private async scheduleLocalNotifications() {
    // Cancel existing notifications
    this.cancelAllNotifications();
    
    if (!this.preferences.enabled) return;

    // Schedule next few days of notifications
    const notifications = this.generateUpcomingNotifications(7);
    
    for (const notification of notifications) {
      await this.scheduleNotification(notification);
    }
  }

  private generateUpcomingNotifications(days: number): WisdomNotification[] {
    const notifications: WisdomNotification[] = [];
    const now = new Date();
    
    for (let i = 0; i < days; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() + i);
      
      // Set preferred time
      const [hours, minutes] = this.preferences.preferredTime.split(':');
      date.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      
      // Skip if frequency doesn't match
      if (this.preferences.frequency === 'every_other_day' && i % 2 !== 0) {
        continue;
      }
      if (this.preferences.frequency === 'weekly' && i % 7 !== 0) {
        continue;
      }
      
      // Generate notification for each enabled category
      if (this.preferences.dailyWisdom) {
        notifications.push(this.createWisdomNotification(date, 'daily_wisdom'));
      }
      
      if (this.preferences.meditationReminders) {
        const meditationTime = new Date(date);
        meditationTime.setHours(18, 0, 0, 0); // 6 PM
        notifications.push(this.createWisdomNotification(meditationTime, 'meditation_reminder'));
      }
    }
    
    return notifications.filter(n => n.scheduledTime > now);
  }

  private createWisdomNotification(scheduledTime: Date, category: WisdomNotification['category']): WisdomNotification {
    const wisdom = this.getRandomWisdom(category);
    
    return {
      id: `${category}_${scheduledTime.getTime()}`,
      title: wisdom.title,
      body: wisdom.body,
      icon: '/logo192.png',
      badge: '/logo192.png',
      scheduledTime,
      category,
      source: wisdom.source,
      language: this.preferences.language,
      data: {
        category,
        source: wisdom.source,
        timestamp: scheduledTime.getTime()
      }
    };
  }

  private async scheduleNotification(notification: WisdomNotification) {
    const delay = notification.scheduledTime.getTime() - Date.now();
    
    if (delay <= 0) return; // Skip past notifications
    
    setTimeout(async () => {
      await this.showNotification(notification);
    }, delay);
  }

  private async showNotification(notification: WisdomNotification) {
    if (Notification.permission !== 'granted') return;

    const options: NotificationOptions = {
      body: notification.body,
      icon: notification.icon || '/logo192.png',
      badge: notification.badge || '/logo192.png',
      data: notification.data,
      tag: notification.category,
      requireInteraction: false
    };

    const registration = await navigator.serviceWorker.ready;
    await registration.showNotification(notification.title, options);
    
    // Track notification shown
    this.trackNotificationEvent('notification_shown', notification);
  }

  private cancelAllNotifications() {
    navigator.serviceWorker.ready.then(registration => {
      registration.getNotifications().then(notifications => {
        notifications.forEach(notification => {
          if (notification.tag?.includes('vimarsh')) {
            notification.close();
          }
        });
      });
    });
  }

  private getRandomWisdom(category?: WisdomNotification['category']) {
    const wisdomData = this.getWisdomDatabase();
    const filtered = category ? wisdomData.filter(w => w.category === category) : wisdomData;
    const random = filtered[Math.floor(Math.random() * filtered.length)];
    
    // Return in preferred language
    return this.preferences.language === 'hi' ? random.hi : random.en;
  }

  private getWisdomDatabase() {
    return [
      {
        category: 'daily_wisdom',
        en: {
          title: 'Daily Wisdom from Krishna',
          body: 'You are what you believe in. You become that which you believe you can become.',
          source: 'Bhagavad Gita'
        },
        hi: {
          title: 'कृष्ण से दैनिक ज्ञान',
          body: 'तुम वही हो जो तुम मानते हो। तुम वही बन जाते हो जो तुम मानते हो कि तुम बन सकते हो।',
          source: 'श्रीमद्भगवद्गीता'
        }
      },
      {
        category: 'meditation_reminder',
        en: {
          title: 'Time for Meditation',
          body: 'A few minutes of meditation can bring peace to your mind and soul.',
          source: 'Vimarsh'
        },
        hi: {
          title: 'ध्यान का समय',
          body: 'कुछ मिनट का ध्यान आपके मन और आत्मा को शांति दे सकता है।',
          source: 'विमर्श'
        }
      },
      {
        category: 'spiritual_quote',
        en: {
          title: 'Spiritual Wisdom',
          body: 'The mind is everything. What you think you become.',
          source: 'Ancient Wisdom'
        },
        hi: {
          title: 'आध्यात्मिक ज्ञान',
          body: 'मन ही सब कुछ है। जो तुम सोचते हो, तुम वही बन जाते हो।',
          source: 'प्राचीन ज्ञान'
        }
      },
      {
        category: 'teachings',
        en: {
          title: 'Teaching from Scriptures',
          body: 'Set thy heart upon thy work, but never on its reward.',
          source: 'Bhagavad Gita 2.47'
        },
        hi: {
          title: 'शास्त्रों से शिक्षा',
          body: 'अपना हृदय अपने कार्य पर लगाओ, परंतु कभी उसके फल पर नहीं।',
          source: 'श्रीमद्भगवद्गीता 2.47'
        }
      }
    ];
  }

  private async sendSubscriptionToServer(subscription: PushSubscription) {
    try {
      // TODO: Implement push subscription endpoint in backend
      /*
      await fetch('/api/push-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          subscription,
          preferences: this.preferences
        }),
      });
      */
      console.log('[Notifications] Push subscription ready, backend endpoint needed');
    } catch (error) {
      console.error('[Notifications] Failed to send subscription to server:', error);
    }
  }

  private urlB64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  private trackNotificationEvent(event: string, notification?: WisdomNotification) {
    // Integration with analytics would go here
    console.log('[Notifications] Event:', event, notification);
  }
}

// Create and export notification service instance
export const dailyWisdomService = new DailyWisdomNotificationService();

// React hook for notification management
export const useNotifications = () => {
  const [preferences, setPreferences] = React.useState(dailyWisdomService.getPreferences());
  const [permissionStatus, setPermissionStatus] = React.useState<NotificationPermission>(
    'Notification' in window ? Notification.permission : 'default'
  );

  React.useEffect(() => {
    const updatePermissionStatus = () => {
      if ('Notification' in window) {
        setPermissionStatus(Notification.permission);
      }
    };

    // Check permission status periodically
    const interval = setInterval(updatePermissionStatus, 1000);
    
    return () => clearInterval(interval);
  }, []);

  const enableNotifications = async () => {
    const success = await dailyWisdomService.enableNotifications();
    if (success) {
      setPreferences(dailyWisdomService.getPreferences());
      setPermissionStatus(Notification.permission);
    }
    return success;
  };

  const disableNotifications = () => {
    dailyWisdomService.disableNotifications();
    setPreferences(dailyWisdomService.getPreferences());
  };

  const updatePreferences = (newPreferences: Partial<NotificationPreferences>) => {
    dailyWisdomService.updatePreferences(newPreferences);
    setPreferences(dailyWisdomService.getPreferences());
  };

  const testNotification = async () => {
    try {
      await dailyWisdomService.testNotification();
      return true;
    } catch (error) {
      console.error('Test notification failed:', error);
      return false;
    }
  };

  return {
    preferences,
    permissionStatus,
    isSupported: 'Notification' in window && 'serviceWorker' in navigator,
    enableNotifications,
    disableNotifications,
    updatePreferences,
    testNotification
  };
};

export default dailyWisdomService;
