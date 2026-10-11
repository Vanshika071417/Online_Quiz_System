// Progressive Web App Service Worker
const CACHE_NAME = 'quiz-system-cache-v3-join-roster';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './assets/css/variables.css',
  './assets/css/main.css',
  './assets/css/components.css',
  './assets/css/examiner.css',
  './assets/css/quiz-taker.css',
  './assets/js/quiz-data.js',
  './assets/js/firebase-config.js',
  './assets/js/quiz-engine.js',
  './assets/js/examiner.js',
  './assets/js/certificates.js',
  './assets/js/app.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Network first for real-time updates, fallback to cache offline
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && event.request.method === 'GET') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseToCache));
        }
        return networkResponse;
      })
      .catch(() => caches.match(event.request).then((cached) => cached || caches.match('./index.html')))
  );
});
