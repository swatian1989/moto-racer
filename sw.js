/* Moto Racer — Coastline : offline service worker.
 *
 * Design rule: the Cache API is treated as an optional luxury. Storage can be
 * unavailable (quota exhausted, site data blocked, private browsing, some
 * embedded webviews) and when it is, `caches.open()` rejects. If that rejection
 * were allowed to escape into `respondWith()` every request would fail and the
 * game would be broken even with a perfectly good network. So every cache
 * access below is guarded and always degrades to a plain network fetch.
 */
const VERSION = '1';
const CACHE = 'moto-racer-' + VERSION;

/* Everything the game needs to run with no network at all.
   Relative paths resolve against the worker's scope, so this works on
   GitHub Pages under /moto-racer/ just as well as at a domain root. */
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon.svg',
  './vendor/three.min.js',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-192.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png'
];

async function openCache() {
  try {
    return await caches.open(CACHE);
  } catch (e) {
    console.warn('[sw] cache storage unavailable, serving network-only:', e);
    return null;
  }
}

async function safeMatch(cache, req) {
  if (!cache) return null;
  try { return await cache.match(req); } catch (e) { return null; }
}

async function safePut(cache, req, res) {
  if (!cache || !res) return;
  try { await cache.put(req, res); } catch (e) { /* quota or storage loss */ }
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await openCache();
    if (cache) {
      // Cache each asset independently: one bad entry must not void the whole
      // install, which would leave the game with no offline copy at all.
      const results = await Promise.allSettled(
        ASSETS.map((url) => cache.add(new Request(url, { cache: 'reload' })))
      );
      results.forEach((r, i) => {
        if (r.status === 'rejected') console.warn('[sw] precache miss:', ASSETS[i], r.reason);
      });
    }
    // Install even when nothing could be cached; the fetch handler is still
    // useful and the next visit may have storage back.
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    try {
      const names = await caches.keys();
      await Promise.all(
        names.filter((n) => n.startsWith('moto-racer-') && n !== CACHE)
             .map((n) => caches.delete(n))
      );
    } catch (e) { /* nothing to clean up if storage is unavailable */ }
    if (self.registration.navigationPreload) {
      try { await self.registration.navigationPreload.enable(); } catch (e) {}
    }
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  let url;
  try { url = new URL(req.url); } catch (e) { return; }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  // Navigations: prefer the network so a redeploy is picked up promptly, but
  // never strand the player — fall back to the cached shell when offline.
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const preload = await event.preloadResponse;
        if (preload) return preload;
        return await fetch(req);
      } catch (e) {
        const cache = await openCache();
        return (await safeMatch(cache, './index.html')) ||
               (await safeMatch(cache, './')) ||
               new Response('<h1>Offline</h1><p>Open the game once while online to install it.</p>',
                            { status: 503, headers: { 'Content-Type': 'text/html' } });
      }
    })());
    return;
  }

  // Same-origin assets: serve instantly from cache, refresh in the background.
  if (url.origin === self.location.origin) {
    event.respondWith((async () => {
      const cache = await openCache();
      const hit = await safeMatch(cache, req);
      if (hit) {
        event.waitUntil((async () => {
          try {
            const fresh = await fetch(req);
            if (fresh && fresh.ok && fresh.type === 'basic') await safePut(cache, req, fresh.clone());
          } catch (e) { /* offline: the cached copy stands */ }
        })());
        return hit;
      }
      const res = await fetch(req);
      if (res && res.ok && res.type === 'basic') await safePut(cache, req, res.clone());
      return res;
    })());
    return;
  }

  // Cross-origin (the CDN fallback): network first, cache as a backup.
  event.respondWith((async () => {
    const cache = await openCache();
    try {
      const res = await fetch(req);
      if (res && (res.ok || res.type === 'opaque')) await safePut(cache, req, res.clone());
      return res;
    } catch (e) {
      const hit = await safeMatch(cache, req);
      if (hit) return hit;
      throw e;
    }
  })());
});
