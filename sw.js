// Progressive Web App Service Worker
const CACHE_NAME = 'quiz-system-cache-v1';
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
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    }).catch(() => caches.match('./index.html'))
  );
});
