#pragma warning disable SKEXP0080
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Process;
using System.ComponentModel;
using System.Text.Json;

namespace ShadowTagV4.Kernel;

// ---------------------------------------------------------
// DOMAIN: CSRMC RISK MATRIX (Supersedes ATP 5-19)
// ---------------------------------------------------------
public enum RiskLevel { RA1_Negligible, RA2_Moderate, RA3_High, RA4_Preclusive }
public enum Decision { ALLOW, BLOCK, ESCALATE }

public class RiskAssessment
{
    public RiskLevel Level { get; set; }
    public double ProbabilityScore { get; set; } // 0.0 to 1.0
    public string? Rationale { get; set; }
}

// ---------------------------------------------------------
// STEP 1: SEMANTIC COMPRESSION (The "Input")
// ---------------------------------------------------------
public class CompressionStep : KernelProcessStep
{
    [KernelFunction, Description("Extracts decision features from raw input")]
    public async Task<string> ExtractFeaturesAsync(KernelProcessStepContext context, string rawInput)
    {
        // Real implementation would use a small local model (e.g., Phi-3)
        // to strip noise and return a JSON feature vector.
        Console.WriteLine($"[Compressor] Processing: {rawInput.Substring(0, Math.Min(20, rawInput.Length))}...");

        // Mocking the feature extraction for the 'Gold Master' signal
        string data = JsonSerializer.Serialize(new { party_size = 4, ltv = 0.9 });
        await context.EmitEventAsync(new() { Id = "FeaturesExtracted", Data = data });
        return "Features Extracted";
    }
}

// ---------------------------------------------------------
// STEP 2: CSRMC RISK SCORING (The "Judge")
// ---------------------------------------------------------
public class RiskStep : KernelProcessStep
{
    [KernelFunction, Description("Evaluates features against CSRMC Doctrine (Supersedes ATP 5-19)")]
    public async Task EvaluateRiskAsync(KernelProcessStepContext context, string features)
    {
        // 1. Load Doctrine Rules (Vector Search from Postgres)
        // 2. Compare Features vs. Rules
        // 3. Output Score

        // Simulating a Moderate Risk assessment based on CSRMC criteria
        var assessment = new RiskAssessment
        {
            Level = RiskLevel.RA2_Moderate,
            ProbabilityScore = 0.45,
            Rationale = "High LTV, but late night transaction (CSRMC Velocity Check)."
        };

        if (assessment.Level >= RiskLevel.RA4_Preclusive)
        {
            await context.EmitEventAsync(new() { Id = "RiskPreclusive", Data = assessment });
        }
        else if (assessment.Level >= RiskLevel.RA2_Moderate)
        {
            await context.EmitEventAsync(new() { Id = "RiskModerate", Data = assessment });
        }
        else
        {
            await context.EmitEventAsync(new() { Id = "RiskLow", Data = assessment });
        }
    }
}

// ---------------------------------------------------------
// STEP 2B: SOVEREIGN FALLBACK (The "Hermes-Agent")
// ---------------------------------------------------------
public class HermesOfflineStep : KernelProcessStep
{
    [KernelFunction, Description("Offline Deterministic Tool Execution via Hermes-Agent")]
    public async Task RouteOfflineAsync(KernelProcessStepContext context, RiskAssessment risk)
    {
        Console.WriteLine($"[HERMES-AGENT] Sovereign mode activated. Routing offline to localhost:11434.");
        // This invokes the binary downloaded from NousResearch/hermes-agent
        await context.EmitEventAsync(new() { Id = "SovereignComplete", Data = risk });
    }
}

// ---------------------------------------------------------
// STEP 3: HUMAN GATE (The "Brakes")
// ---------------------------------------------------------
public class HumanGateStep : KernelProcessStep
{
    // This step waits for an external event (human click in Admin UI)
    [KernelFunction]
    public void AwaitApproval(RiskAssessment risk)
    {
        Console.WriteLine($"[HumanGate] PAUSED. Risk: {risk.Level}. Waiting for generic external Approval event...");
        // Execution halts here. The workflow saves state to DB and sleeps.
        // It relies on API Controller sending builder.OnExternalEvent("UserApproved")
    }
}

// ---------------------------------------------------------
// STEP 4: ENFORCEMENT (The "Gavel")
// ---------------------------------------------------------
public class EnforcementStep : KernelProcessStep
{
    [KernelFunction]
    public void Execute(RiskAssessment risk)
    {
        Console.WriteLine($"[Enforcement] EXECUTING Transaction. Risk: {risk.Level}");
        // Call MCP Tool (e.g., Stripe, POS) here
    }

    [KernelFunction]
    public void Block(RiskAssessment risk)
    {
        Console.WriteLine($"[Enforcement] BLOCKED. Reason: {risk.Rationale}");
    }
}

// ---------------------------------------------------------
// THE ARCHITECT (Process Builder)
// ---------------------------------------------------------
public static class JudgeProcessBuilder
{
    public static KernelProcess Build()
    {
        var builder = new ProcessBuilder("JudgeSix_v2");

        var compress = builder.AddStepFromType<CompressionStep>("Compressor");
        var risk = builder.AddStepFromType<RiskStep>("RiskEngine");
        var hermes = builder.AddStepFromType<HermesOfflineStep>("HermesFallback");
        var human = builder.AddStepFromType<HumanGateStep>("HumanGate");
        var enforce = builder.AddStepFromType<EnforcementStep>("Enforcer");

        // The Directed Graph (The "Flow")
        builder.OnExternalEvent("Start")
            .SendEventTo(new ProcessFunctionTargetBuilder(compress, nameof(CompressionStep.ExtractFeaturesAsync), "rawInput"));

        compress.OnEvent("FeaturesExtracted")
            .SendEventTo(new ProcessFunctionTargetBuilder(risk, nameof(RiskStep.EvaluateRiskAsync), "features"));

        // Branching Logic (The "Intelligence")
        risk.OnEvent("RiskLow")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        risk.OnEvent("RiskModerate")
            .SendEventTo(new ProcessFunctionTargetBuilder(human, nameof(HumanGateStep.AwaitApproval), "risk"));

        risk.OnEvent("RiskPreclusive")
            .SendEventTo(new ProcessFunctionTargetBuilder(hermes, nameof(HermesOfflineStep.RouteOfflineAsync), "risk"));

        // Hermes Output Closure
        hermes.OnEvent("SovereignComplete")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Block), "risk"));

        // Human Loop Closure via Proper OnExternalEvent
        // This accepts the "risk" parameter from the UI HTTP payload injected upon resuming
        builder.OnExternalEvent("UserApproved")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        return builder.Build();
    }
}
