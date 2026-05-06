import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

// Note: Replace with actual service account credentials path
const serviceAccount = require('../../secrets/serviceAccountKey.json');

initializeApp({
  credential: cert(serviceAccount)
});

const db = getFirestore();

async function seed() {
  console.log('🌱 Seeding HeadFade Truth Oracle database...');

  const videosRef = db.collection('videos');
  
  await videosRef.doc('demo-123').set({
    hdiScore: 95,
    modelsUsed: ['Veo 3.1', 'Gemini 3.1'],
    parentCreatorId: 'orig_123',
    remixTree: [],
    createdAt: new Date(),
    title: 'Synthetic Aurora'
  });

  console.log('✅ Seed complete!');
}

seed().catch(console.error);
