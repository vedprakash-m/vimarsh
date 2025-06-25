// PWA utilities for service worker registration and install prompts
// Handles offline detection, install prompts, and service worker lifecycle

import React from 'react';

export interface PWAConfig {
  enableNotifications: boolean;
  enableBackgroundSync: boolean;
  cacheStrategy: 'cacheFirst' | 'networkFirst' | 'staleWhileRevalidate';
  offlineIndicator: boolean;
}

export interface InstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

class PWAManager {
  private registration: ServiceWorkerRegistration | null = null;
  private deferredPrompt: InstallPromptEvent | null = null;
  private config: PWAConfig;
  private isOnline: boolean = navigator.onLine;
  private installPromptShown: boolean = false;

  constructor(config: PWAConfig) {
    this.config = config;
    this.initializePWA();
  }

  private async initializePWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      try {
        this.registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        });
        
        console.log('[PWA] Service worker registered successfully');
        
        // Handle service worker updates
        this.handleServiceWorkerUpdates();
        
        // Setup background sync if supported
        if (this.config.enableBackgroundSync && 'sync' in window.ServiceWorkerRegistration.prototype) {
          this.setupBackgroundSync();
        }
        
        // Setup push notifications if supported
        if (this.config.enableNotifications && 'PushManager' in window) {
          this.setupPushNotifications();
        }
      } catch (error) {
        console.error('[PWA] Service worker registration failed:', error);
      }
    }

    // Setup install prompt handling
    this.setupInstallPrompt();
    
    // Setup offline detection
    this.setupOfflineDetection();
    
    // Handle app shortcuts
    this.handleAppShortcuts();
  }

  private handleServiceWorkerUpdates() {
    if (!this.registration) return;

    this.registration.addEventListener('updatefound', () => {
      const newWorker = this.registration!.installing;
      if (!newWorker) return;

      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // New version available
          this.showUpdateAvailable();
        }
      });
    });
  }

  private setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('[PWA] Install prompt triggered');
      e.preventDefault();
      this.deferredPrompt = e as InstallPromptEvent;
      
      // Show custom install prompt after a delay
      setTimeout(() => {
        this.showInstallPrompt();
      }, 10000); // Show after 10 seconds
    });

    window.addEventListener('appinstalled', () => {
      console.log('[PWA] App was installed');
      this.deferredPrompt = null;
      this.installPromptShown = true;
      
      // Track installation
      this.trackEvent('pwa_installed');
    });
  }

  private setupOfflineDetection() {
    window.addEventListener('online', () => {
      console.log('[PWA] Back online');
      this.isOnline = true;
      this.handleOnlineStatusChange(true);
      
      // Trigger background sync
      if (this.registration && 'serviceWorker' in navigator && (this.registration as any).sync) {
        (this.registration as any).sync.register('background-sync-messages');
      }
    });

    window.addEventListener('offline', () => {
      console.log('[PWA] Gone offline');
      this.isOnline = false;
      this.handleOnlineStatusChange(false);
    });
  }

  private setupBackgroundSync() {
    // Background sync will be handled by the service worker
    console.log('[PWA] Background sync enabled');
  }

  private async setupPushNotifications() {
    try {
      const permission = await Notification.requestPermission();
      if (permission === 'granted' && this.registration) {
        console.log('[PWA] Push notifications enabled');
        
        // Subscribe to push notifications
        const vapidKey = process.env.REACT_APP_VAPID_PUBLIC_KEY;
        const subscription = await this.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: vapidKey ? this.urlB64ToUint8Array(vapidKey) as BufferSource : undefined
        });
        
        // Send subscription to server
        await this.sendSubscriptionToServer(subscription);
      }
    } catch (error) {
      console.error('[PWA] Push notification setup failed:', error);
    }
  }

  private handleAppShortcuts() {
    // Handle URL parameters for app shortcuts
    const urlParams = new URLSearchParams(window.location.search);
    const action = urlParams.get('action');
    
    if (action) {
      console.log('[PWA] App opened with shortcut action:', action);
      
      switch (action) {
        case 'new':
          this.handleNewConversationShortcut();
          break;
        case 'history':
          this.handleHistoryShortcut();
          break;
      }
    }
  }

  // Public methods

  public async showInstallPrompt(): Promise<boolean> {
    if (!this.deferredPrompt || this.installPromptShown) {
      return false;
    }

    try {
      await this.deferredPrompt.prompt();
      const { outcome } = await this.deferredPrompt.userChoice;
      
      console.log('[PWA] Install prompt outcome:', outcome);
      this.trackEvent('pwa_install_prompt', { outcome });
      
      this.deferredPrompt = null;
      this.installPromptShown = true;
      
      return outcome === 'accepted';
    } catch (error) {
      console.error('[PWA] Install prompt failed:', error);
      return false;
    }
  }

  public canInstall(): boolean {
    return !!this.deferredPrompt && !this.installPromptShown;
  }

  public isInstalled(): boolean {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.matchMedia('(display-mode: fullscreen)').matches ||
           (window.navigator as any).standalone === true;
  }

  public isOnlineStatus(): boolean {
    return this.isOnline;
  }

  public async updateServiceWorker(): Promise<void> {
    if (this.registration && this.registration.waiting) {
      this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }

  public async requestNotificationPermission(): Promise<NotificationPermission> {
    if ('Notification' in window) {
      return await Notification.requestPermission();
    }
    return 'default';
  }

  public async scheduleBackgroundSync(tag: string): Promise<void> {
    if (this.registration && 'serviceWorker' in navigator && (this.registration as any).sync) {
      try {
        await (this.registration as any).sync.register(tag);
        console.log('[PWA] Background sync scheduled:', tag);
      } catch (error) {
        console.error('[PWA] Background sync failed:', error);
      }
    }
  }

  public async cacheConversation(conversationData: any): Promise<void> {
    try {
      const cache = await caches.open('vimarsh-conversations');
      const response = new Response(JSON.stringify(conversationData), {
        headers: { 'Content-Type': 'application/json' }
      });
      await cache.put(`/conversation/${conversationData.id}`, response);
      console.log('[PWA] Conversation cached offline');
    } catch (error) {
      console.error('[PWA] Failed to cache conversation:', error);
    }
  }

  // Private helper methods

  private showUpdateAvailable() {
    const event = new CustomEvent('pwa-update-available');
    window.dispatchEvent(event);
  }

  private handleOnlineStatusChange(isOnline: boolean) {
    const event = new CustomEvent('pwa-online-status-change', {
      detail: { isOnline }
    });
    window.dispatchEvent(event);
  }

  private handleNewConversationShortcut() {
    const event = new CustomEvent('pwa-shortcut-new-conversation');
    window.dispatchEvent(event);
  }

  private handleHistoryShortcut() {
    const event = new CustomEvent('pwa-shortcut-history');
    window.dispatchEvent(event);
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

  private async sendSubscriptionToServer(subscription: PushSubscription): Promise<void> {
    try {
      await fetch('/api/push-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscription),
      });
      console.log('[PWA] Push subscription sent to server');
    } catch (error) {
      console.error('[PWA] Failed to send subscription to server:', error);
    }
  }

  private trackEvent(event: string, data?: any) {
    // Integration with analytics would go here
    console.log('[PWA] Event tracked:', event, data);
  }
}

// Default configuration
const defaultConfig: PWAConfig = {
  enableNotifications: true,
  enableBackgroundSync: true,
  cacheStrategy: 'networkFirst',
  offlineIndicator: true
};

// Create and export PWA manager instance
export const pwaManager = new PWAManager(defaultConfig);

// Export PWA hooks for React components
export const usePWA = () => {
  const [canInstall, setCanInstall] = React.useState(pwaManager.canInstall());
  const [isInstalled, setIsInstalled] = React.useState(pwaManager.isInstalled());
  const [isOnline, setIsOnline] = React.useState(pwaManager.isOnlineStatus());
  const [updateAvailable, setUpdateAvailable] = React.useState(false);

  React.useEffect(() => {
    const handleUpdateAvailable = () => setUpdateAvailable(true);
    const handleOnlineStatusChange = (e: any) => setIsOnline(e.detail.isOnline);
    const handleInstallPrompt = () => setCanInstall(pwaManager.canInstall());

    window.addEventListener('pwa-update-available', handleUpdateAvailable);
    window.addEventListener('pwa-online-status-change', handleOnlineStatusChange);
    window.addEventListener('beforeinstallprompt', handleInstallPrompt);
    window.addEventListener('appinstalled', () => {
      setIsInstalled(true);
      setCanInstall(false);
    });

    return () => {
      window.removeEventListener('pwa-update-available', handleUpdateAvailable);
      window.removeEventListener('pwa-online-status-change', handleOnlineStatusChange);
      window.removeEventListener('beforeinstallprompt', handleInstallPrompt);
    };
  }, []);

  return {
    canInstall,
    isInstalled,
    isOnline,
    updateAvailable,
    showInstallPrompt: () => pwaManager.showInstallPrompt(),
    updateApp: () => pwaManager.updateServiceWorker(),
    requestNotifications: () => pwaManager.requestNotificationPermission()
  };
};

export default pwaManager;
