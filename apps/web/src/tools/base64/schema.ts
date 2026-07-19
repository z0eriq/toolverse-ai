import { z } from "zod";

export const base64Schema = z.object({
  input: z.string(),
  mode: z.enum(["encode", "decode"]),
});

export type Base64Input = z.infer<typeof base64Schema>;
