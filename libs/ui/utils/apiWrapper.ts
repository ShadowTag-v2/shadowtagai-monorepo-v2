/**
 * Global Next.js Fetch Wrapper
 * Handles standard 500 server-side generic errors and structured JSON ingestion gracefully.
 */
export async function apiWrapper<T>(
  url: string,
  options?: RequestInit,
): Promise<{ data: T | null; error: string | null; status: number }> {
  try {
    const res = await fetch(url, options);

    let data = null;
    try {
      data = await res.json();
    } catch {
      // Unparseable JSON or empty response
    }

    if (!res.ok) {
      if (res.status >= 500) {
        return {
          data: null,
          error: 'Internal Server Error. Our team has been notified.',
          status: res.status,
        };
      }
      return { data: null, error: data?.error || `HTTP Error ${res.status}`, status: res.status };
    }

    return { data, error: null, status: res.status };
  } catch (_e: unknown) {
    return { data: null, error: 'Network Error. Please check your connection.', status: 0 };
  }
}
