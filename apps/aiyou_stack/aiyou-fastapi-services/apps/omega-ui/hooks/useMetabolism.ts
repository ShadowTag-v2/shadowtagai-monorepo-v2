import { aggregateQuery, collection, query, sum, where } from 'firebase/firestore';
import { firestore } from '@/lib/firebase';

export function useMetabolism(projectId: string) {
  // THE GOOGLE TRICK: Using "Pipeline" operations for server-side aggregation.
  // This avoids reading 10k documents to count costs. It's instant and cheap.
  const calculateBurn = async () => {
    const coll = collection(firestore, 'usage_logs');
    const q = query(coll, where('project_id', '==', projectId));

    // "Pipeline" query - New Firestore Engine Feature
    const snapshot = await aggregateQuery(q, {
      totalCost: sum('cost_micro_cents'),
    });

    return snapshot.data().totalCost / 1_000_000; // Returns USD
  };

  return { calculateBurn };
}
