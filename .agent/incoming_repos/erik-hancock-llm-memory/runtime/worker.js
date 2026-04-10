// File: runtime/worker.js
// Executes EdgeQueue commands in single invocation

export default {
  async fetch(request, env) {
    if (request.method !== 'POST' || new URL(request.url).pathname !== '/execute_queue') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const { commands } = await request.json();
    const results = [];
    const start_us = performance.now() * 1000;

    // Execute commands sequentially (NO additional HTTP calls)
    for (const cmd of commands) {
      switch (cmd.type) {
        case 'wait': {
          // Poll Durable Object signal (Simulated for prototype)
          // In real impl, this would call DO
          const target_value = cmd.args.value;
          await new Promise(r => setTimeout(r, 5)); // Simulate 5ms wait
          results.push({ type: 'wait', status: 'completed' });
          break;
        }

        case 'exec': {
          // Execute WASM policy
          const policy_name = cmd.args.policy_name;

          // Simulate WASM execution time (1-5ms)
          const exec_start_us = performance.now() * 1000;
          await new Promise(r => setTimeout(r, 2));
          const exec_end_us = performance.now() * 1000;

          // Random pass/fail
          const result = Math.random() > 0.1 ? 1 : 0;

          results.push({
            type: 'exec',
            policy: policy_name,
            result: result,
            latency_us: exec_end_us - exec_start_us
          });
          break;
        }

        case 'signal': {
          // Write signal value (Simulated)
          results.push({ type: 'signal', status: 'written' });
          break;
        }

        case 'timestamp': {
          const timestamp_us = performance.now() * 1000;
          results.push({ type: 'timestamp', timestamp_us });
          break;
        }

        default:
          // Ignore unknown for prototype
          break;
      }
    }

    const end_us = performance.now() * 1000;

    return Response.json({
      results,
      total_latency_us: end_us - start_us,
      command_count: commands.length
    });
  }
};
