"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { api, type ExperimentAssignResult } from "@/lib/api";

const COOKIE_PREFIX = "tv_exp_";

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));
  if (!match) return null;
  return decodeURIComponent(match.split("=").slice(1).join("="));
}

function writeCookie(name: string, value: string, days = 365) {
  if (typeof document === "undefined") return;
  const maxAge = days * 24 * 60 * 60;
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

function subjectCookieName(key: string) {
  return `${COOKIE_PREFIX}${key}`;
}

interface ExperimentContextValue {
  assign: (key: string) => Promise<ExperimentAssignResult | null>;
  track: (
    key: string,
    eventName: "view" | "click" | "convert",
    properties?: Record<string, unknown>,
  ) => Promise<void>;
  getCached: (key: string) => ExperimentAssignResult | null;
}

const ExperimentContext = createContext<ExperimentContextValue | null>(null);

export function ExperimentProvider({ children }: { children: ReactNode }) {
  const cacheRef = useRef<Map<string, ExperimentAssignResult>>(new Map());
  const [, bump] = useState(0);

  const assign = useCallback(async (key: string) => {
    const cached = cacheRef.current.get(key);
    if (cached) return cached;
    const cookieSubject = readCookie(subjectCookieName(key));
    try {
      const result = await api.experiments.assign(key, cookieSubject ?? undefined);
      writeCookie(subjectCookieName(key), result.subject_key);
      cacheRef.current.set(key, result);
      bump((n) => n + 1);
      return result;
    } catch {
      return null;
    }
  }, []);

  const track = useCallback(
    async (
      key: string,
      eventName: "view" | "click" | "convert",
      properties?: Record<string, unknown>,
    ) => {
      let assignment = cacheRef.current.get(key);
      if (!assignment) {
        assignment = (await assign(key)) ?? undefined;
      }
      if (!assignment) return;
      try {
        await api.experiments.track({
          key,
          subject_key: assignment.subject_key,
          event_name: eventName,
          properties,
        });
      } catch {
        // Tracking must never block UI
      }
    },
    [assign],
  );

  const getCached = useCallback((key: string) => {
    return cacheRef.current.get(key) ?? null;
  }, []);

  const value = useMemo(
    () => ({ assign, track, getCached }),
    [assign, track, getCached],
  );

  return (
    <ExperimentContext.Provider value={value}>
      {children}
    </ExperimentContext.Provider>
  );
}

export function useExperimentContext() {
  const ctx = useContext(ExperimentContext);
  if (!ctx) {
    throw new Error("useExperimentContext requires ExperimentProvider");
  }
  return ctx;
}
