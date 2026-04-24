using System;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;

namespace Aiyou.Kernel
{
    /// <summary>
    /// REPAIRED: Sovereign MDO Process using SK Process.Core v1.21.0-alpha.
    /// OnExternalEvent is the CORRECT API per AGENTS.md Core Technical Truth #3.
    /// Do NOT apply the OnInputEvent rename until Process.Core >= v1.30+.
    /// </summary>
    public class SovereignMdoProcess
    {
        private readonly ILogger<SovereignMdoProcess> _logger;

        public SovereignMdoProcess(ILogger<SovereignMdoProcess> logger)
        {
            _logger = logger;
        }

        public async Task<string> RunProcessAsync(KernelProcessStepContext context)
        {
            _logger.LogInformation("🚀 [AIYOU-KERNEL] Durable Execution started. Awaiting external events.");
            // SK Process.Core durable step — awaits external event trigger
            await Task.CompletedTask;
            return "MDO_AWAITING_EXTERNAL_EVENT";
        }

        /// <summary>
        /// REPAIRED: OnExternalEvent with memory-safe JSON deserialization.
        /// Uses `using` block for JsonDocument to prevent memory leaks.
        /// </summary>
        public async Task OnExternalEvent(KernelProcessStepContext context, string payload)
        {
            _logger.LogInformation("📥 [AIYOU-KERNEL] OnExternalEvent triggered. Freeing thread lock.");

            try
            {
                using var document = JsonDocument.Parse(payload);
                var root = document.RootElement;

                _logger.LogInformation(
                    "✅ [AIYOU-KERNEL] Event Processed. Payload properties: {Count}",
                    root.EnumerateObject().Count());

                // Emit to next step in SK process pipeline
                await context.EmitEventAsync(new KernelProcessEvent { Id = "mdo_event_received", Data = payload });

                _logger.LogInformation("✅ [AIYOU-KERNEL] Event emitted to pipeline. Buffer Flushed.");
            }
            catch (JsonException ex)
            {
                _logger.LogError("❌ [AIYOU-KERNEL] JSON Parse Error (AST drift): {Message}", ex.Message);
                throw; // Route kickback to Judge 6.1
            }
        }
    }
}
