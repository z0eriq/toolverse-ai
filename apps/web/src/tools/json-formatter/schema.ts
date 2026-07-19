import { z } from "zod";

export const jsonFormatterSchema = z.object({
  input: z.string(),
  indent: z.union([z.literal(2), z.literal(4)]),
});

export type JsonFormatterInput = z.infer<typeof jsonFormatterSchema>;
