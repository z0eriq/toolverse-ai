import { z } from "zod";

export const uuidSchema = z.object({
  count: z.number().int().min(1).max(200),
});

export type UuidInput = z.infer<typeof uuidSchema>;
