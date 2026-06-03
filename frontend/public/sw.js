const CACHE_NAME = 'altixedu-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/assets/',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Installing and caching static assets');
      // Cache will be populated dynamically as resources are requested
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - network first with cache fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle API requests separately
  if (request.url.includes('/api/')) {
    event.respondWith(handleAPIRequest(request));
    return;
  }

  // Handle static assets and pages
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }

      return fetch(request).then((response) => {
        // Only cache successful responses
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }

        // Clone the response
        const responseToCache = response.clone();

        // Cache the response
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseToCache);
        });

        return response;
      }).catch(() => {
        // Offline fallback for pages
        if (request.headers.get('accept').includes('text/html')) {
          return caches.match('/index.html');
        }
        
        // Return a 404 response for other requests
        return new Response('Offline - Resource not available', {
          status: 404,
          statusText: 'Not Found'
        });
      });
    })
  );
});

// API request handler - stale while revalidate
function handleAPIRequest(request) {
  return fetch(request)
    .then((response) => {
      if (!response || response.status !== 200) {
        return response;
      }

      // Clone the response
      const responseToCache = response.clone();

      // Cache successful API responses
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(request, responseToCache);
      });

      return response;
    })
    .catch(() => {
      // Return cached version if network fails
      return caches.match(request).then((response) => {
        if (response) {
          console.log('[Service Worker] Returning cached API response:', request.url);
          return response;
        }

        // Return offline error response
        return new Response(
          JSON.stringify({ 
            error: 'Offline - API request unavailable',
            offline: true 
          }),
          {
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'application/json' }
          }
        );
      });
    });
}

// Message handler for cache control
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
