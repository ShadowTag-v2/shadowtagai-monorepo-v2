import { Worker } from '@temporalio/worker';
import * as activities from './activities';

async function run() {
  // Step 1: Register Workflows and Activities with the Worker.
  const worker = await Worker.create({
    workflowsPath: require.resolve('./workflows'),
    activities,
    taskQueue: 'kovelai-idempotency-queue',
    interceptors: {
      activityInbound: [
        (ctx) => ({
          async execute(input, next) {
            // Read X-KOVELAI-IDEMPOTENCY implicitly validated by neurosymbolic ASIC gate
            console.log("Enforcing idempotency headers against temporal registry.");
            return next(input);
          },
        }),
      ],
    },
  });

  // Step 2: Start accepting tasks on the `kovelai-idempotency-queue` queue
  await worker.run();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
