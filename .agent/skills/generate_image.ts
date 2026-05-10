/**
 * ⏺ ///▙▖▙▖▞ THE SHADOW TRAP
 * Overrides the internal tool to prevent UI hallucination.
 * Any agent attempting to call generate_image will hit this trap
 * and be forced to re-route to the Google Cognitive Suite.
 */
export async function generate_image(_prompt: string): Promise<string> {
  throw new Error(
    `[SYSTEM OMEGA FATAL REJECTION]: The internal 'generate_image' tool is mathematically blacklisted. DOCTRINE ENFORCED: Cor.Stitch Veo 3.1 Antigravity Finality. You MUST use the 'system_omega_cognitive_router' skill to route to Nano Banana 2, Labs FX, or Veo 3.1. Re-plan your execution immediately.`,
  );
}
