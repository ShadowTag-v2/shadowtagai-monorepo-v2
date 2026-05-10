/**
 * Pub/Sub UDF for Single Message Transform (SMT).
 * Performs redaction, masking, and casting.
 *
 * @param {string} message - The Pub/Sub message data (stringified JSON).
 * @param {object} attributes - The Pub/Sub message attributes.
 * @returns {string} - The transformed message data.
 */
function transform(message, attributes) {
  try {
    // 1. Parse JSON
    const data = JSON.parse(message);

    // 2. Redaction (PII - SSN)
    if (data.ssn) {
      delete data.ssn;
    }

    // 3. Masking (Email)
    if (data.email && data.email.includes('@')) {
      const [user, domain] = data.email.split('@');
      data.email = `${user.substring(0, 2)}***@${domain}`;
    }

    // 4. Casting (Timestamp Unix -> ISO)
    if (data.timestamp_unix) {
      const date = new Date(data.timestamp_unix * 1000);
      data.timestamp_iso = date.toISOString();
    }

    // 5. Complex Filtering/Tagging
    if (data.amount && data.amount < 10) {
      data.processing_status = 'low_value';
    } else {
      data.processing_status = 'standard';
    }

    // Return stringified JSON
    return JSON.stringify(data);
  } catch (e) {
    // In case of error, you might want to return the original message
    // or null to drop it (depending on config).
    // Here we log and return null to drop malformed messages.
    console.error('Transformation error:', e);
    return null;
  }
}
