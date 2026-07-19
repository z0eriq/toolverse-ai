import { z } from "zod";

export const wordCounterSchema = z.object({
  input: z.string(),
});

export type WordCounterInput = z.infer<typeof wordCounterSchema>;
