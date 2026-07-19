"use client";

import { useEffect, useState } from "react";
import type { ExperimentAssignResult } from "@/lib/api";
import { useExperimentContext } from "./experiment-context";

/**
 * Sticky A/B assignment for `key` (cookie `tv_exp_<key>`).
 * Returns variant payload from the assign API.
 */
export function useExperiment(key: string) {
  const { assign, track, getCached } = useExperimentContext();
  const [assignment, setAssignment] = useState<ExperimentAssignResult | null>(
    () => getCached(key),
  );
  const [isLoading, setIsLoading] = useState(!getCached(key));

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      setIsLoading(true);
      const result = await assign(key);
      if (!cancelled) {
        setAssignment(result);
        setIsLoading(false);
        if (result) void track(key, "view");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [assign, key, track]);

  const variantId =
    typeof assignment?.variant === "string" ? assignment.variant : "";

  return {
    assignment,
    variantId,
    /** Variant key string from sticky assignment (cookie `tv_exp_<key>`). */
    payload: { variant: variantId },
    isLoading,
    trackClick: () => track(key, "click"),
    trackConvert: () => track(key, "convert"),
  };
}
