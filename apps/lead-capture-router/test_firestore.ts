import * as admin from 'firebase-admin';
import { getFirestore } from 'firebase-admin/firestore';

admin.initializeApp({ projectId: 'shadowtag-omega-v4' });

// Try initializing with DB ID
try {
  const _db1 = getFirestore('shadowtag-engine');
  console.log('Success with string ID!');
} catch (_e) {}

try {
  const _db2 = getFirestore(admin.app(), 'shadowtag-engine');
  console.log('Success with app + ID');
} catch (_e) {}
