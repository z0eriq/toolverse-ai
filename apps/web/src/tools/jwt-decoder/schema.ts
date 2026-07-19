import { z } from "zod";

export const jwtSchema = z.object({
  token: z.string().min(1),
});

export type JwtInput = z.infer<typeof jwtSchema>;
