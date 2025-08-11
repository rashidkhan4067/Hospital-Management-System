/**
 * Premium HMS Service Worker
 * Provides offline functionality and caching for the hospital management system
 */

const CACHE_NAME = 'premium-hms-v2.0.0';
const STATIC_CACHE = 'premium-hms-static-v2.0.0';
const DYNAMIC_CACHE = 'premium-hms-dynamic-v2.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/static/css/premium-core.css',
    '/static/css/premium-components.css',
    '/static/css/premium-animations.css',
    '/static/js/premium-core.js',
    '/static/js/premium-components.js',
    '/static/images/logo.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    /\/api\/v1\/dashboard\/stats\//,
    /\/api\/v1\/notifications\/unread-count\//,
    /\/api\/v1\/patients\/\d+\//,
    /\/api\/v1\/doctors\/\d+\//,
    /\/api\/v1\/appointments\/\d+\//
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('📦 Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('✅ Service Worker installed successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ Service Worker installation failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('🔧 Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('🗑️ Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker activated successfully');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle network requests
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle different types of requests
    if (isStaticFile(request)) {
        event.respondWith(handleStaticFile(request));
    } else if (isAPIRequest(request)) {
        event.respondWith(handleAPIRequest(request));
    } else if (isPageRequest(request)) {
        event.respondWith(handlePageRequest(request));
    } else {
        event.respondWith(handleOtherRequest(request));
    }
});

// Check if request is for a static file
function isStaticFile(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/static/') || 
           url.hostname !== self.location.hostname;
}

// Check if request is for API
function isAPIRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/');
}

// Check if request is for a page
function isPageRequest(request) {
    return request.headers.get('accept')?.includes('text/html');
}

// Handle static file requests (cache first strategy)
async function handleStaticFile(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('Static file fetch failed:', error);
        
        // Return cached version if available
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline fallback
        return new Response('Offline - Static resource not available', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Handle API requests (network first with cache fallback)
async function handleAPIRequest(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful GET responses for specific endpoints
        if (networkResponse.ok && shouldCacheAPI(request)) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('API request failed:', error);
        
        // Try to return cached version
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            // Add offline indicator header
            const response = cachedResponse.clone();
            response.headers.set('X-Served-From-Cache', 'true');
            return response;
        }
        
        // Return offline response
        return new Response(JSON.stringify({
            error: 'Offline - API not available',
            message: 'You are currently offline. Some features may not be available.',
            offline: true
        }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
}

// Handle page requests (network first with offline fallback)
async function handlePageRequest(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful page responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('Page request failed:', error);
        
        // Try to return cached version
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return caches.match('/offline.html') || new Response(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Offline - Premium HMS</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .offline-container { max-width: 500px; margin: 0 auto; }
                    .offline-icon { font-size: 64px; margin-bottom: 20px; }
                    h1 { color: #333; margin-bottom: 20px; }
                    p { color: #666; line-height: 1.6; }
                    .retry-btn { 
                        background: #007bff; color: white; border: none; 
                        padding: 12px 24px; border-radius: 6px; cursor: pointer;
                        font-size: 16px; margin-top: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="offline-container">
                    <div class="offline-icon">📡</div>
                    <h1>You're Offline</h1>
                    <p>It looks like you've lost your internet connection. Don't worry, you can still access some features of Premium HMS while offline.</p>
                    <button class="retry-btn" onclick="window.location.reload()">Try Again</button>
                </div>
            </body>
            </html>
        `, {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'text/html'
            }
        });
    }
}

// Handle other requests
async function handleOtherRequest(request) {
    try {
        return await fetch(request);
    } catch (error) {
        console.error('Other request failed:', error);
        
        // Try cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Check if API endpoint should be cached
function shouldCacheAPI(request) {
    const url = new URL(request.url);
    return API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname));
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('🔄 Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    try {
        // Sync offline actions when connection is restored
        console.log('🔄 Performing background sync...');
        
        // This would sync any offline actions stored in IndexedDB
        // For example: offline form submissions, cached API calls, etc.
        
        console.log('✅ Background sync completed');
    } catch (error) {
        console.error('❌ Background sync failed:', error);
    }
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('📱 Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from Premium HMS',
        icon: '/static/images/logo.png',
        badge: '/static/images/badge.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Premium HMS', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('📱 Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        // Open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

console.log('🔧 Service Worker script loaded');
