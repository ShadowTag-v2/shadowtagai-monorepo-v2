import * as admin from 'firebase-admin';
import { getFirestore } from 'firebase-admin/firestore';

admin.initializeApp({ projectId: "shadowtag-omega-v4" });

// Try initializing with DB ID
try {
  const db1 = getFirestore("shadowtag-engine");
  console.log("Success with string ID!");
} catch (e) {
  console.error("Failed string", e);
}

try {
  const db2 = getFirestore(admin.app(), "shadowtag-engine");
  console.log("Success with app + ID");
} catch (e) {
  console.error("Failed app+ID", e);
}
