import { z } from "zod";

export const loremSchema = z.object({
  paragraphs: z.number().int().min(1).max(20),
});

export type LoremInput = z.infer<typeof loremSchema>;
