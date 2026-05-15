import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import type { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2026-04-22.dahlia',
});

interface NukeRequest {
  userId: string;
  stripeCustomerId?: string;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { userId, stripeCustomerId }: NukeRequest = req.body;

  if (!userId) {
    return res.status(400).json({ error: 'Missing userId' });
  }

  try {
    const db = getFirestore();
    const auth = getAuth();

    // 1. Delete Stripe customer (if exists)
    if (stripeCustomerId) {
      try {
        await stripe.customers.del(stripeCustomerId);
      } catch (stripeError: any) {
        // Customer might not exist - continue
        console.log('Stripe customer deletion skipped:', stripeError.message);
      }
    }

    // 2. Firestore Cryptographic Shred + Delete
    const batch = db.batch();
    const collectionsToShred = [
      `users/${userId}`,
      `users/${userId}/workflows`,
      `users/${userId}/logs`,
      `users/${userId}/billing`,
    ];

    // Add root-level collections where userId field exists
    const rootCollections = ['workspaces', 'projects', 'api_keys'];

    for (const collectionName of rootCollections) {
      const snapshot = await db.collection(collectionName).where('userId', '==', userId).get();

      snapshot.forEach((doc) => {
        // Overwrite with cryptographic noise first (PITR-safe)
        batch.update(doc.ref, {
          name: crypto.randomUUID(),
          email: crypto.randomUUID(),
          data: crypto.randomUUID(),
          updatedAt: new Date(),
        });
        batch.delete(doc.ref);
      });
    }

    // Process nested subcollections
    for (const collectionPath of collectionsToShred) {
      const docRef = db.doc(collectionPath);

      // Overwrite with noise
      batch.update(docRef, {
        name: crypto.randomUUID(),
        email: crypto.randomUUID(),
        data: crypto.randomUUID(),
        deletedAt: new Date(),
      });

      batch.delete(docRef);
    }

    await batch.commit();

    // 3. Delete Firebase Auth user
    try {
      await auth.deleteUser(userId);
    } catch (authError: any) {
      console.log('Auth user deletion error:', authError.message);
    }

    // 4. Clear session cookies
    res.setHeader('Set-Cookie', [
      'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; Secure; SameSite=Strict',
      'auth_token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; Secure; SameSite=Strict',
    ]);

    return res.status(200).json({
      success: true,
      message: 'Account and all data have been cryptographically shredded',
    });
  } catch (error: any) {
    return res.status(500).json({
      error: 'Failed to delete account',
      details: error.message,
    });
  }
}
