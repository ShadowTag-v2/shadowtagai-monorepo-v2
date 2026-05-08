Object.defineProperty(exports, '__esModule', { value: true });
exports.checkIdempotency = void 0;
const firestore_1 = require('firebase-admin/firestore');
/**
 * Ensures idempotency using Firestore transactions.
 * Designed to replace Redis-based caching to align with enterprise infrastructure.
 *
 * @param idempotencyKey - Unique string derived from the client request (e.g., hash of payload + timestamp within 5 mins).
 * @param operationName - Context string to group keys in the database.
 * @returns boolean - True if operation is fresh and should proceed. False if already completed.
 */
async function checkIdempotency(idempotencyKey, operationName) {
  const db = (0, firestore_1.getFirestore)();
  const docRef = db.collection('system_idempotency_keys').doc(`${operationName}_${idempotencyKey}`);
  try {
    const isFresh = await db.runTransaction(async (transaction) => {
      const doc = await transaction.get(docRef);
      if (doc.exists) {
        // Key already exists, this is a duplicate request
        return false;
      }
      // Lock the key so subsequent immediate parallel requests fail
      transaction.set(docRef, {
        createdAt: new Date(),
        operation: operationName,
        status: 'LOCK_ACQUIRED',
      });
      return true;
    });
    return isFresh;
  } catch (_e) {
    // Fail-safe open on DB error, or modify depending on risk tolerance
    return true;
  }
}
exports.checkIdempotency = checkIdempotency;
//# sourceMappingURL=idempotency.js.map
