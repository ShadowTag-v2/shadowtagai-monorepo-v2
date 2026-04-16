import { z } from "zod";

export const ContactRequestSchema = z.object({
  email: z.string().email(),
  company: z.string().min(1),
  status: z.enum(["queued", "processing", "completed"])
});
