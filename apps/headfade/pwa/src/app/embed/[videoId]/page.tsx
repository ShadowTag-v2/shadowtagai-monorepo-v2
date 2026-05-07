import EmbedPlayerClient from './EmbedPlayerClient';

/* =======================================================================
 * Server Page Wrapper — generateStaticParams lives here (no 'use client')
 * Delegates all rendering to the client component.
 *
 * At build time, generateStaticParams fetches all video document IDs from
 * Firestore via the REST API so Next.js can pre-render every embed page
 * as static HTML — eliminating per-request server latency and maximising
 * SEO crawlability.
 * ======================================================================= */

/** Firestore REST endpoint for the `videos` collection. */
const FIRESTORE_BASE =
  'https://firestore.googleapis.com/v1/projects/shadowtag-omega-v4/databases/(default)/documents';

export async function generateStaticParams(): Promise<{ videoId: string }[]> {
  try {
    const url = `${FIRESTORE_BASE}/videos?pageSize=500&mask.fieldPaths=__name__`;
    const res = await fetch(url, { next: { revalidate: 3600 } }); // ISR: re-fetch every hour
    if (!res.ok) {
      console.warn('[embed/generateStaticParams] Firestore fetch failed:', res.status);
      return [{ videoId: 'demo' }];
    }
    const json = (await res.json()) as { documents?: { name: string }[] };
    const docs = json.documents ?? [];
    const ids = docs.map((d) => {
      // name format: "projects/.../documents/videos/{videoId}"
      const parts = d.name.split('/');
      return { videoId: parts[parts.length - 1] };
    });
    // Always include demo as a fallback
    if (!ids.find((x) => x.videoId === 'demo')) {
      ids.unshift({ videoId: 'demo' });
    }
    console.log(`[embed/generateStaticParams] Pre-rendering ${ids.length} video embed pages`);
    return ids;
  } catch (err) {
    console.error('[embed/generateStaticParams] Error:', err);
    return [{ videoId: 'demo' }];
  }
}

export default async function EmbedPage({ params }: { params: Promise<{ videoId: string }> }) {
  const { videoId } = await params;
  return <EmbedPlayerClient videoId={videoId} />;
}
