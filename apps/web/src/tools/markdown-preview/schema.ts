import { z } from "zod";

export const markdownSchema = z.object({
  input: z.string(),
});

export type MarkdownInput = z.infer<typeof markdownSchema>;
