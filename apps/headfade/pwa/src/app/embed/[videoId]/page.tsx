import EmbedPlayerClient from './EmbedPlayerClient';

/* =======================================================================
 * Server Page Wrapper — generateStaticParams lives here (no 'use client')
 * Delegates all rendering to the client component.
 * ======================================================================= */

export function generateStaticParams() {
  return [{ videoId: 'demo' }];
}

export default async function EmbedPage({ params }: { params: Promise<{ videoId: string }> }) {
  const { videoId } = await params;
  return <EmbedPlayerClient videoId={videoId} />;
}
