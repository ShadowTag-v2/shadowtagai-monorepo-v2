// ============================================================================
// Google Apps Script — KovelAI & ShadowTagAI Form Submissions
// Deploy as Web App: Execute as Me, Access: Anyone
// Repository: ShadowTag-v2/Monorepo-Uphillsnowball
// ============================================================================
// Based on: github.com/jamiewilson/form-to-google-sheets
//           github.com/levinunnink/html-form-to-google-sheet
// ============================================================================

const scriptProp = PropertiesService.getScriptProperties();

/**
 * Run this function ONCE to bind the script to the active spreadsheet.
 * Go to Run > Run Function > initialSetup
 */
function _initialSetup() {
  const activeSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  scriptProp.setProperty('key', activeSpreadsheet.getId());
}

/**
 * Handles POST requests from the HTML contact forms.
 * Writes form data to the appropriate sheet and sends email notification.
 */
function _doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    const doc = SpreadsheetApp.openById(scriptProp.getProperty('key'));

    // Route to correct sheet based on hidden "sheet_name" field
    const sheetName = e.parameter.sheet_name || 'Sheet1';
    let sheet = doc.getSheetByName(sheetName);

    // Auto-create the sheet if it doesn't exist
    if (!sheet) {
      sheet = doc.insertSheet(sheetName);
      // Set default headers
      const defaultHeaders = [
        'id',
        'timestamp',
        'name',
        'email',
        'firm',
        'organization',
        'inquiry_type',
        'message',
        'source',
      ];
      sheet.getRange(1, 1, 1, defaultHeaders.length).setValues([defaultHeaders]);
    }

    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const nextRow = sheet.getLastRow() + 1;

    const newRow = headers.map((header) => {
      if (header === 'id') return Utilities.getUuid();
      if (header === 'timestamp') return new Date().toISOString();
      return sanitize(e.parameter[header] || '');
    });

    sheet.getRange(nextRow, 1, 1, newRow.length).setValues([newRow]);

    // Format as plain text to prevent formula injection
    sheet.getRange(nextRow, 1, 1, newRow.length).setNumberFormat('@');

    // ── Email notification ──
    sendNotification(e.parameter, sheetName, nextRow);

    // ── Auto-reply to submitter ──
    sendAutoReply(e.parameter, sheetName);

    return ContentService.createTextOutput(
      JSON.stringify({
        result: 'success',
        row: nextRow,
      }),
    ).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    // Send error notification
    sendErrorNotification(err, sheetName);

    return ContentService.createTextOutput(
      JSON.stringify({
        result: 'error',
        error: err.toString(),
      }),
    ).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

/**
 * Sanitize input: prepend single quote to values starting with
 * potentially dangerous characters (=, +, -, @) to prevent
 * CSV/formula injection in Google Sheets.
 */
function sanitize(value) {
  if (typeof value !== 'string') return value;
  const dangerousChars = ['=', '+', '-', '@'];
  if (dangerousChars.some((c) => value.startsWith(c))) {
    return `'${value}`;
  }
  return value;
}

/**
 * Send email notification to founder on new form submission.
 * Edit the recipient/senderName below for your setup.
 */
function sendNotification(params, sheetName, row) {
  // ── CONFIGURE THESE ──
  const recipients = {
    KovelAI: 'founder@kovelai.com',
    ShadowTagAI: 'founder@shadowtagai.com',
  };

  const recipient = recipients[sheetName] || 'founder@kovelai.com';
  const senderName = sheetName === 'ShadowTagAI' ? 'ShadowTag AI' : 'KovelAI';

  const subject = `${senderName} — New ${params.inquiry_type || 'Contact'} Inquiry from ${params.name || 'Unknown'}`;

  const body = `
    <div style="font-family: 'Inter', -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e0e0e0; padding: 32px; border-radius: 12px;">
      <div style="border-bottom: 2px solid #c9a96e; padding-bottom: 16px; margin-bottom: 24px;">
        <h2 style="color: #c9a96e; margin: 0; font-size: 20px;">${senderName} — New Inquiry</h2>
        <p style="color: #999; margin: 4px 0 0; font-size: 12px;">Row ${row} • ${new Date().toLocaleString()}</p>
      </div>
      <table style="width: 100%; border-collapse: collapse;">
        <tr><td style="padding: 8px 0; color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Name</td><td style="padding: 8px 0; color: #fff;">${params.name || '—'}</td></tr>
        <tr><td style="padding: 8px 0; color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Email</td><td style="padding: 8px 0; color: #c9a96e;">${params.email || '—'}</td></tr>
        <tr><td style="padding: 8px 0; color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Firm / Org</td><td style="padding: 8px 0; color: #fff;">${params.firm || params.organization || '—'}</td></tr>
        <tr><td style="padding: 8px 0; color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Type</td><td style="padding: 8px 0; color: #fff;">${params.inquiry_type || 'General'}</td></tr>
        <tr><td style="padding: 8px 0; color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; vertical-align: top;">Message</td><td style="padding: 8px 0; color: #fff; white-space: pre-wrap;">${params.message || '—'}</td></tr>
      </table>
      <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #333; font-size: 11px; color: #666;">
        Auto-forwarded via Google Apps Script • <a href="https://docs.google.com/spreadsheets" style="color: #c9a96e;">Open Spreadsheet</a>
      </div>
    </div>
  `;

  try {
    MailApp.sendEmail({
      to: recipient,
      subject: subject,
      htmlBody: body,
      name: senderName,
    });
  } catch (_mailErr) {}
}

/**
 * Send automated reply to the person who submitted the form.
 */
function sendAutoReply(params, sheetName) {
  if (!params.email) return;

  const senderName = sheetName === 'ShadowTagAI' ? 'ShadowTag AI' : 'KovelAI';
  const replyFrom = sheetName === 'ShadowTagAI' ? 'ShadowTag AI' : 'KovelAI';

  const subject = `Thank you for contacting ${senderName}`;

  const body = `
    <div style="font-family: 'Inter', -apple-system, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e0e0e0; padding: 32px; border-radius: 12px;">
      <div style="border-bottom: 2px solid #c9a96e; padding-bottom: 16px; margin-bottom: 24px;">
        <h2 style="color: #c9a96e; margin: 0; font-size: 20px;">Thank You, ${params.name || 'there'}</h2>
      </div>
      <p style="color: #e0e0e0; line-height: 1.6;">
        We have received your inquiry and a member of our team will respond within 24 hours during business days.
      </p>
      <p style="color: #999; font-size: 13px; margin-top: 24px;">
        — The ${senderName} Team
      </p>
      <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #333; font-size: 11px; color: #666;">
        This is an automated confirmation. Please do not reply to this email.
      </div>
    </div>
  `;

  try {
    MailApp.sendEmail({
      to: params.email,
      subject: subject,
      htmlBody: body,
      name: replyFrom,
    });
  } catch (_mailErr) {}
}

/**
 * Send error notification to admin.
 */
function sendErrorNotification(err, sheetName) {
  try {
    MailApp.sendEmail({
      to: 'founder@kovelai.com',
      subject: `[${sheetName || 'FormScript'}] Error in form submission`,
      body: `Form submission error:\n${err.toString()}`,
      name: 'Form Script Alert',
    });
  } catch (_mailErr) {}
}
