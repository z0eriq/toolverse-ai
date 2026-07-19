import { z } from "zod";

export const urlEncoderSchema = z.object({
  input: z.string(),
  mode: z.enum(["encode", "decode"]),
});

export type UrlEncoderInput = z.infer<typeof urlEncoderSchema>;
