/* ToolVerse AI service worker — cache shell + static; network-first for /api and /tools */
const CACHE_VERSION = "toolverse-v1";
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const STATIC_CACHE = `${CACHE_VERSION}-static`;

const SHELL_URLS = ["/", "/favicon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL_CACHE);
      try {
        await cache.addAll(SHELL_URLS);
      } catch {
        /* ignore missing assets during install */
      }
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((key) => key.startsWith("toolverse-") && key !== SHELL_CACHE && key !== STATIC_CACHE)
          .map((key) => caches.delete(key)),
      );
      await self.clients.claim();
    })(),
  );
});

function isNetworkFirst(url) {
  const { pathname } = url;
  if (pathname.startsWith("/api")) return true;
  if (pathname.includes("/tools")) return true;
  if (pathname.startsWith("/_next/data")) return true;
  return false;
}

function isStaticAsset(url) {
  const { pathname } = url;
  if (pathname.startsWith("/_next/static/")) return true;
  if (pathname === "/favicon.svg") return true;
  if (/\.(?:js|css|woff2?|png|jpg|jpeg|gif|svg|webp|avif|ico)$/i.test(pathname)) {
    return true;
  }
  return false;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  let url;
  try {
    url = new URL(request.url);
  } catch {
    return;
  }

  if (url.origin !== self.location.origin) return;

  if (isNetworkFirst(url)) {
    event.respondWith(
      (async () => {
        try {
          const network = await fetch(request);
          return network;
        } catch {
          const cached = await caches.match(request);
          if (cached) return cached;
          return new Response("Offline", { status: 503, statusText: "Offline" });
        }
      })(),
    );
    return;
  }

  if (isStaticAsset(url)) {
    event.respondWith(
      (async () => {
        const cached = await caches.match(request);
        if (cached) return cached;
        try {
          const network = await fetch(request);
          if (network.ok) {
            const cache = await caches.open(STATIC_CACHE);
            void cache.put(request, network.clone());
          }
          return network;
        } catch {
          return (
            (await caches.match(request)) ||
            new Response("Offline", { status: 503, statusText: "Offline" })
          );
        }
      })(),
    );
    return;
  }

  // Navigation / shell — stale-while-revalidate from shell cache
  event.respondWith(
    (async () => {
      const cached = await caches.match(request);
      const networkPromise = fetch(request)
        .then(async (network) => {
          if (network.ok && request.mode === "navigate") {
            const cache = await caches.open(SHELL_CACHE);
            void cache.put(request, network.clone());
          }
          return network;
        })
        .catch(() => null);

      if (cached) {
        void networkPromise;
        return cached;
      }

      const network = await networkPromise;
      if (network) return network;
      const fallback = await caches.match("/");
      return (
        fallback || new Response("Offline", { status: 503, statusText: "Offline" })
      );
    })(),
  );
});
