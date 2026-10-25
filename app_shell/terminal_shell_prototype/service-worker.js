const CACHE_NAME = "coquery-pwa-v13";
const APP_SHELL = [
  "./",
  "./index.html",
  "./styles.css",
  "./onboarding.css?v=13",
  "./concept-puzzles.css",
  "./concept-puzzle-catalog.js",
  "./concept-puzzles.js",
  "./community-demo.html",
  "./community-demo.css",
  "./community-demo.js?v=12",

  "./app.js",
  "./onboarding.js?v=13",
  "./practice-focus.css",
  "./practice-focus.js",
  "./practice-result-visual.css",
  "./practice-result-visual.js",
  "./practice-query-flow.css",
  "./practice-query-flow.js",
  "./practice-result-explain.css",
  "./practice-result-explain.js",
  "./practice-result-views.css",
  "./practice-result-views.js",
  "./learning-path.css",
  "./learning-path.js",
  "./curriculum-expansion.js",
  "./pwa-runtime.js",
  "./dialect-learning.js",
  "./manifest.webmanifest",
  "./coquery-icon.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== "GET" || url.pathname.startsWith("/api/")) {
    return;
  }

  if (request.mode === "navigate") {
    // The simulation is a separate document, not a route of the SQL shell.
    const pageKey = url.pathname.endsWith("/community-demo.html")
      ? "./community-demo.html"
      : "./index.html";
    event.respondWith(
      fetch(request)
        .then(async (response) => {
          if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            await cache.put(pageKey, response.clone());
          }
          return response;
        })
        .catch(() => caches.match(pageKey))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        return cached;
      }
      return fetch(request).then((response) => {
        if (response.ok && response.type === "basic") {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      });
    })
  );
});
