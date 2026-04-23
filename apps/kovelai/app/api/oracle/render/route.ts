/**
 * Oracle Memo PDF Render Pipeline
 *
 * Item #12: Server-side PDF generation for Oracle Memos.
 *
 * Uses a lightweight HTML-to-PDF approach:
 * 1. Generate HTML from Zod-validated memo data
 * 2. POST to Cloud Run function with puppeteer for rendering
 * 3. Return signed URL for download
 *
 * In dev mode, returns HTML directly for preview.
 *
 * @see lib/oracle/memo-pdf.ts
 */

import { type NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { generateMemoPDFTemplate, OracleMemoSchema, renderMemoHTML } from '@/lib/oracle/memo-pdf';

// ─── Request Schema ─────────────────────────────────────────────────

const RenderRequestSchema = z.object({
  memo: OracleMemoSchema,
  format: z.enum(['html', 'pdf_url']).default('html'),
});

// ─── Handler ────────────────────────────────────────────────────────

export async function POST(req: NextRequest): Promise<NextResponse> {
  try {
    const body = await req.json();
    const { memo, format } = RenderRequestSchema.parse(body);

    if (format === 'html') {
      // Dev mode: return HTML for preview
      const html = renderMemoHTML(memo);
      return new NextResponse(html, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'X-Privilege-Shield': 'kovel-doctrine-active',
          'Cache-Control': 'no-store, private',
        },
      });
    }

    // Production: delegate to Cloud Run PDF renderer
    const pdfServiceUrl = process.env.PDF_RENDERER_URL;
    if (!pdfServiceUrl) {
      // Fallback: return template data for client-side rendering
      const template = generateMemoPDFTemplate(memo);
      return NextResponse.json({
        template,
        fallback: true,
        message: 'PDF service not configured. Use template data for client-side rendering.',
      });
    }

    const pdfRes = await fetch(pdfServiceUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.PDF_RENDERER_TOKEN ?? ''}`,
      },
      body: JSON.stringify({
        html: renderMemoHTML(memo),
        options: {
          format: 'letter',
          margin: { top: '0.5in', bottom: '0.5in', left: '0.5in', right: '0.5in' },
          printBackground: true,
        },
      }),
      signal: AbortSignal.timeout(30000),
    });

    if (!pdfRes.ok) {
      return NextResponse.json(
        { error: 'PDF rendering failed', status: pdfRes.status },
        { status: 502 },
      );
    }

    const pdfUrl = (await pdfRes.json()).url;

    return NextResponse.json({
      pdfUrl,
      expiresIn: 3600,
      memoId: memo.memoId,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid memo data', details: error.errors },
        { status: 400 },
      );
    }
    return NextResponse.json({ error: 'Memo rendering failed' }, { status: 500 });
  }
}
