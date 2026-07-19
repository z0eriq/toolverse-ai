import { z } from "zod";

export const colorSchema = z.object({
  hex: z.string(),
});

export type ColorInput = z.infer<typeof colorSchema>;
