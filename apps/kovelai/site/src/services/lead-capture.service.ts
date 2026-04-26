/**
 * Lead Capture Service
 *
 * Client-side service abstraction for the KovelAI lead-capture Cloud Run endpoint.
 * Centralizes all outbound API calls for contact form submissions.
 */

const LEAD_CAPTURE_URL =
  process.env.NEXT_PUBLIC_LEAD_CAPTURE_URL ||
  'https://capturelead-767252945109.us-central1.run.app';

export interface LeadCapturePayload {
  name: string;
  email: string;
  company: string;
  phone?: string;
  message?: string;
}

/**
 * Submits a lead capture form to the Cloud Run endpoint.
 * Returns true on success, false on failure.
 */
export async function submitLeadCapture(payload: LeadCapturePayload): Promise<boolean> {
  try {
    const response = await fetch(LEAD_CAPTURE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return response.ok;
  } catch {
    return false;
  }
}
