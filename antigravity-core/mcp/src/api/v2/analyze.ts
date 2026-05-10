import { z } from 'zod';
import { executeAnalyzeVideo } from '../../utils/v2/analyze-engine';

const AnalyzeInputSchema = z.object({
  videoUrl: z.string().url(),
  options: z
    .object({
      includeRemixTree: z.boolean().default(true),
      depth: z.number().min(1).max(10).default(5),
      models: z.array(z.string()).default(['all']),
    })
    .optional(),
});

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const input = AnalyzeInputSchema.parse(body);

    const result = await executeAnalyzeVideo(input);

    return Response.json({
      success: true,
      data: result,
      processingTimeMs: result.processingTimeMs,
    });
  } catch (error) {
    return Response.json(
      { success: false, error: error instanceof Error ? error.message : 'Unknown error' },
      { status: 400 },
    );
  }
}
```
