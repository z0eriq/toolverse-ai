"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, type AsyncJob, type AsyncJobStatus } from "./api";

const TERMINAL: AsyncJobStatus[] = ["succeeded", "failed"];

export interface UseJobPollOptions {
  intervalMs?: number;
  enabled?: boolean;
  onComplete?: (job: AsyncJob) => void;
}

export interface UseJobPollResult {
  job: AsyncJob | null;
  error: string | null;
  isPolling: boolean;
  start: (jobId: string) => void;
  stop: () => void;
  reset: () => void;
}

/**
 * Polls `api.getJob` until status is succeeded or failed.
 */
export function useJobPoll(options: UseJobPollOptions = {}): UseJobPollResult {
  const { intervalMs = 1500, enabled = true, onComplete } = options;
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<AsyncJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const stop = useCallback(() => {
    setJobId(null);
    setIsPolling(false);
  }, []);

  const reset = useCallback(() => {
    setJobId(null);
    setJob(null);
    setError(null);
    setIsPolling(false);
  }, []);

  const start = useCallback((id: string) => {
    setError(null);
    setJob(null);
    setJobId(id);
    setIsPolling(true);
  }, []);

  useEffect(() => {
    if (!enabled || !jobId) return;

    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function tick() {
      try {
        const next = await api.getJob(jobId!);
        if (cancelled) return;
        setJob(next);
        if (TERMINAL.includes(next.status)) {
          setIsPolling(false);
          onCompleteRef.current?.(next);
          return;
        }
        timer = setTimeout(() => {
          void tick();
        }, intervalMs);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to poll job");
        setIsPolling(false);
      }
    }

    setIsPolling(true);
    void tick();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [enabled, jobId, intervalMs]);

  return { job, error, isPolling, start, stop, reset };
}
