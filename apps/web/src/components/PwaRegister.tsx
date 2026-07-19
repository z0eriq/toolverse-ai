"use client";

import { useEffect } from "react";
import { api } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  const output = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i += 1) {
    output[i] = raw.charCodeAt(i);
  }
  return output;
}

async function maybeSubscribePush(registration: ServiceWorkerRegistration) {
  if (typeof Notification === "undefined") return;
  if (Notification.permission !== "granted") return;
  if (!("PushManager" in window)) return;
  if (!getAccessToken()) return;

  try {
    let subscription = await registration.pushManager.getSubscription();
    const vapid = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY;
    if (!subscription && vapid) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapid) as BufferSource,
      });
    }
    if (!subscription) return;

    const json = subscription.toJSON() as Record<string, unknown>;
    await api.pushSubscribe({
      endpoint: json.endpoint,
      keys: json.keys ?? {},
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
    });
  } catch {
    /* push is optional — ignore failures */
  }
}

/**
 * Registers the service worker and optionally syncs a push subscription
 * when notification permission is already granted.
 */
export function PwaRegister() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!("serviceWorker" in navigator)) return;

    let cancelled = false;

    void (async () => {
      try {
        const registration = await navigator.serviceWorker.register("/sw.js", {
          scope: "/",
        });
        if (cancelled) return;
        await maybeSubscribePush(registration);
      } catch {
        /* SW registration is best-effort */
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  return null;
}
