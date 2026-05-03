import { Resend } from 'resend';
import { env } from '../env.mjs';

const resend = new Resend(env.RESEND_API_KEY);
export async function safeAction<T>(
  actionName: string,
  fn: () => Promise<T>,
): Promise<{ data?: T; error?: string }> {
  try {
    return { data: await fn() };
  } catch (error: any) {
    if (process.env.NODE_ENV === 'production') {
      await resend.emails
        .send({
          from: 'alerts@counselconduit.com',
          to: 'engineering@counselconduit.com',
          subject: `🚨 2AM PROD ALERT: Silent Failure in ${actionName}`,
          text: `Error details: ${error.message}\nStack: ${error.stack}`,
        })
        .catch(console.error);
    }
    return { error: 'An unexpected error occurred. Engineering has been notified.' };
  }
}
