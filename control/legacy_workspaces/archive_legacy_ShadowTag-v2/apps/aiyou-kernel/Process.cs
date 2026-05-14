using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Process;
using System.ComponentModel;
using System.Text.Json;

namespace AiYou.Kernel;

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
// STEP 3: HUMAN GATE (The "Brakes")
// ---------------------------------------------------------
public class HumanGateStep : KernelProcessStep
{
    // This step waits for an external event (human click in Admin UI)
    [KernelFunction]
    public async Task AwaitApprovalAsync(KernelProcessStepContext context, RiskAssessment risk)
    {
        Console.WriteLine($"[HumanGate] PAUSED. Risk: {risk.Level}. Waiting for Approval...");
        // In reality, this persists state to Postgres and sleeps until API wake-up
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
        var human = builder.AddStepFromType<HumanGateStep>("HumanGate");
        var enforce = builder.AddStepFromType<EnforcementStep>("Enforcer");

        // The Directed Graph (The "Flow")
        builder.OnInputEvent("Start")
            .SendEventTo(new ProcessFunctionTargetBuilder(compress, nameof(CompressionStep.ExtractFeaturesAsync), "rawInput"));

        compress.OnEvent("FeaturesExtracted")
            .SendEventTo(new ProcessFunctionTargetBuilder(risk, nameof(RiskStep.EvaluateRiskAsync), "features"));

        // Branching Logic (The "Intelligence")
        risk.OnEvent("RiskLow")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        risk.OnEvent("RiskModerate")
            .SendEventTo(new ProcessFunctionTargetBuilder(human, nameof(HumanGateStep.AwaitApprovalAsync), "risk"));

        risk.OnEvent("RiskPreclusive")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Block), "risk"));

        // Human Loop Closure
        // Fixed: Use OnInputEvent (SK 1.74.0+, renamed from OnExternalEvent) because
        // The external system (API/UI) must fire "HumanApprovalReceived" with the RiskAssessment object.
        builder.OnInputEvent("HumanApprovalReceived")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        return builder.Build();
    }
}
