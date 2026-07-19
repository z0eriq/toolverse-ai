"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState, type ReactNode } from "react";
import { AuthProvider } from "@/features/auth/auth-context";
import { ExperimentProvider } from "@/features/experiments/experiment-context";
import { PwaRegister } from "@/components/PwaRegister";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      }),
  );

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ExperimentProvider>
            <PwaRegister />
            {children}
          </ExperimentProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
