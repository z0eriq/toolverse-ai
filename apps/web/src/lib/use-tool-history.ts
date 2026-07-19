"use client";

import { useCallback } from "react";
import { api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { trackToolUse } from "@/lib/analytics";

/**
 * Records tool usage to the history API when the user is logged in,
 * and always emits a lightweight analytics event.
 */
export function useToolHistory(toolId: string) {
  const record = useCallback(
    async (action = "run", meta: Record<string, unknown> = {}) => {
      trackToolUse(toolId, action);
      if (!isAuthenticated()) return;
      try {
        await api.recordHistory(toolId, action, meta);
      } catch {
        // History is best-effort; never block the tool UX.
      }
    },
    [toolId],
  );

  return { record };
}
