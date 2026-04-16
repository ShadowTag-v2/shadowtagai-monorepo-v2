import { useState } from 'react';

export function useCaptureLead() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const captureLead = async (payload: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/captureContact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        if (response.status === 400) {
          throw new Error(data.error || "Validation Failed. Please check the form parameters.");
        } else if (response.status === 429) {
          throw new Error("Too Many Requests. Please try again later.");
        }
        throw new Error("An unexpected error occurred.");
      }
      
      setSuccess(true);
      return data;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { captureLead, loading, error, success };
}
