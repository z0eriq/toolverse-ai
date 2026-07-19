import { z } from "zod";

export const hashSchema = z.object({
  input: z.string(),
  algorithm: z.enum(["SHA-1", "SHA-256", "SHA-512"]),
});

export type HashInput = z.infer<typeof hashSchema>;
