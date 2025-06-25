// Service Worker for Vimarsh PWA
// Provides offline caching, background sync, and push notifications

const CACHE_NAME = 'vimarsh-v1.0.0';
const STATIC_CACHE_NAME = 'vimarsh-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'vimarsh-dynamic-v1.0.0';

// Resources to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png',
  // Google Fonts for Sanskrit/Devanagari support
  'https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@300;400;500;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600;700&display=swap'
];

// API endpoints that can be cached
const CACHEABLE_API_ENDPOINTS = [
  '/api/spiritual-guidance',
  '/api/conversation-history'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch((error) => {
        console.error('[SW] Failed to cache static assets:', error);
      })
  );
  
  // Skip waiting to activate immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== STATIC_CACHE_NAME && 
                     cacheName !== DYNAMIC_CACHE_NAME;
            })
            .map((cacheName) => {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
  );
  
  // Claim all clients immediately
  self.clients.claim();
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (isStaticAsset(request)) {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE_NAME));
  } else if (isAPIRequest(request)) {
    event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE_NAME));
  } else if (isNavigationRequest(request)) {
    event.respondWith(navigationStrategy(request));
  } else {
    event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE_NAME));
  }
});

// Background sync for offline message queue
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'background-sync-messages') {
    event.waitUntil(syncOfflineMessages());
  }
});

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  let notificationData = {
    title: 'Vimarsh',
    body: 'New spiritual wisdom awaits you',
    icon: '/logo192.png',
    badge: '/logo192.png',
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
      category: 'daily_wisdom',
      url: '/'
    }
  };
  
  if (event.data) {
    try {
      const receivedData = event.data.json();
      notificationData = {
        ...notificationData,
        ...receivedData
      };
    } catch (error) {
      console.error('[SW] Failed to parse push data:', error);
    }
  }
  
  const options = {
    body: notificationData.body,
    icon: notificationData.icon,
    badge: notificationData.badge,
    data: notificationData.data,
    tag: notificationData.data.category || 'vimarsh',
    requireInteraction: false,
    silent: false,
    actions: [
      {
        action: 'open',
        title: 'Open Vimarsh'
      },
      {
        action: 'later',
        title: 'Later'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.action);
  
  event.notification.close();
  
  let targetUrl = '/';
  
  if (event.notification.data && event.notification.data.url) {
    targetUrl = event.notification.data.url;
  }
  
  if (event.action === 'open') {
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then((clientList) => {
          // Check if there's already a window/tab open
          for (const client of clientList) {
            if (client.url.includes(self.location.origin) && 'focus' in client) {
              client.focus();
              return client.navigate(targetUrl);
            }
          }
          // If no window is open, open a new one
          if (clients.openWindow) {
            return clients.openWindow(targetUrl);
          }
        })
    );
  } else if (event.action === 'later') {
    // Just close the notification - no action needed
    console.log('[SW] User chose to view later');
  } else {
    // Default action (clicking notification body)
    event.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true })
        .then((clientList) => {
          for (const client of clientList) {
            if (client.url.includes(self.location.origin) && 'focus' in client) {
              client.focus();
              return client.navigate(targetUrl);
            }
          }
          if (clients.openWindow) {
            return clients.openWindow(targetUrl);
          }
        })
    );
  }
  
  // Track notification interaction
  if (event.notification.data) {
    console.log('[SW] Notification interaction:', {
      action: event.action || 'default',
      category: event.notification.data.category,
      timestamp: Date.now()
    });
  }
});

// Helper functions

function isStaticAsset(request) {
  const url = new URL(request.url);
  return url.pathname.includes('/static/') || 
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.png') ||
         url.pathname.endsWith('.ico') ||
         url.hostname === 'fonts.googleapis.com' ||
         url.hostname === 'fonts.gstatic.com';
}

function isAPIRequest(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/api/') ||
         CACHEABLE_API_ENDPOINTS.some(endpoint => url.pathname.includes(endpoint));
}

function isNavigationRequest(request) {
  return request.mode === 'navigate';
}

// Cache strategies

async function cacheFirstStrategy(request, cacheName) {
  try {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('[SW] Serving from cache:', request.url);
      return cachedResponse;
    }
    
    console.log('[SW] Fetching from network:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache first strategy failed:', error);
    return new Response('Offline - Content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

async function networkFirstStrategy(request, cacheName) {
  try {
    console.log('[SW] Fetching from network:', request.url);
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for API requests
    if (isAPIRequest(request)) {
      return new Response(JSON.stringify({
        error: 'Offline',
        message: 'This feature requires an internet connection',
        offline: true
      }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Offline - Content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

async function navigationStrategy(request) {
  try {
    // Try network first for navigation
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    // Fallback to cached main page for SPA navigation
    const cache = await caches.open(STATIC_CACHE_NAME);
    const cachedResponse = await cache.match('/');
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response('Offline - App not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// Background sync for offline messages
async function syncOfflineMessages() {
  try {
    const cache = await caches.open(DYNAMIC_CACHE_NAME);
    const offlineMessages = await getOfflineMessages();
    
    for (const message of offlineMessages) {
      try {
        const response = await fetch('/api/spiritual-guidance', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(message)
        });
        
        if (response.ok) {
          await removeOfflineMessage(message.id);
          console.log('[SW] Synced offline message:', message.id);
        }
      } catch (error) {
        console.error('[SW] Failed to sync message:', message.id, error);
      }
    }
  } catch (error) {
    console.error('[SW] Background sync failed:', error);
  }
}

// Helper functions for offline message management
async function getOfflineMessages() {
  // This would integrate with IndexedDB in a real implementation
  return [];
}

async function removeOfflineMessage(messageId) {
  // This would remove from IndexedDB in a real implementation
  console.log('[SW] Removing offline message:', messageId);
}
