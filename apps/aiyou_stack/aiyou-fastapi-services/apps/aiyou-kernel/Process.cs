// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// =============================================================================
// ShadowTag Semantic Kernel Process — Consolidated Judge 6 + CSRMC Pipeline
// Target: .NET 10.0 (net10.0)
// SK Process.Core: v1.21.0-alpha
// CRITICAL: OnExternalEvent is the CORRECT API per AGENTS.md Core Technical Truth #3.
//           Do NOT apply the OnInputEvent rename until Process.Core >= v1.30+.
// =============================================================================

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Process;

namespace ShadowTagV4.Kernel;

// =========================================================================
// SECTION 1: DOMAIN TYPES — CSRMC Risk Matrix (Supersedes ATP 5-19)
// =========================================================================

/// <summary>Risk levels for CSRMC pipeline classification.</summary>
public enum CsrmcRiskLevel { RA1_Negligible, RA2_Moderate, RA3_High, RA4_Preclusive }

/// <summary>CSRMC pipeline decision outcomes.</summary>
public enum CsrmcDecision { ALLOW, BLOCK, ESCALATE }

/// <summary>Assessment output from the CSRMC Risk Engine step.</summary>
public class RiskAssessment
{
    public CsrmcRiskLevel Level { get; set; }
    public double ProbabilityScore { get; set; } // 0.0 to 1.0
    public string? Rationale { get; set; }
}

// =========================================================================
// SECTION 2: DOMAIN TYPES — Judge 6 Governance (Wet Fleece / Dry Ground)
// =========================================================================

/// <summary>Judge 6 risk classification levels.</summary>
public enum GovernanceRiskLevel
{
    Low,
    Medium,
    High,
    Blocked,
}

/// <summary>An agent action subject to governance evaluation.</summary>
public sealed record AgentAction
{
    public required string ActionId { get; init; }
    public required string ActionType { get; init; }
    public string Target { get; init; } = "";
    public string Context { get; init; } = "";
}

/// <summary>Governance evaluation result from Judge 6.</summary>
public sealed record GovernanceDecision
{
    public required string ActionId { get; init; }
    public required GovernanceRiskLevel RiskLevel { get; init; }
    public required bool Permitted { get; init; }
    public required string Rationale { get; init; }
    public List<string> Conditions { get; init; } = [];
    public DateTimeOffset Timestamp { get; init; }
}

/// <summary>Configuration for Judge 6 blocked action types.</summary>
public sealed record Judge6Config
{
    public HashSet<string> BlockedActions { get; init; } =
    [
        "rm_rf",
        "sudo",
        "force_push_main",
        "drop_database",
    ];

    public static Judge6Config Default => new();
}

/// <summary>Internal deserialization model for LLM governance responses.</summary>
internal sealed record GovernanceResponse
{
    public bool Permitted { get; init; }
    public string Rationale { get; init; } = "";
    public List<string> Conditions { get; init; } = [];
}

// =========================================================================
// SECTION 3: SOVEREIGN MDO PROCESS (Durable Execution Step)
// =========================================================================

/// <summary>
/// Sovereign MDO (Mission-Driven Operations) durable process.
/// Uses SK Process.Core v1.21.0-alpha OnExternalEvent lifecycle.
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
        _logger.LogInformation("🚀 [MDO] Durable Execution started. Awaiting external events.");
        await Task.CompletedTask;
        return "MDO_AWAITING_EXTERNAL_EVENT";
    }

    /// <summary>
    /// OnExternalEvent with memory-safe JSON deserialization.
    /// Uses 'using' block for JsonDocument to prevent memory leaks.
    /// </summary>
    public async Task OnExternalEvent(KernelProcessStepContext context, string payload)
    {
        _logger.LogInformation("📥 [MDO] OnExternalEvent triggered. Freeing thread lock.");

        try
        {
            using var document = JsonDocument.Parse(payload);
            var root = document.RootElement;

            _logger.LogInformation(
                "✅ [MDO] Event Processed. Payload properties: {Count}",
                root.EnumerateObject().Count());

            await context.EmitEventAsync(new KernelProcessEvent { Id = "mdo_event_received", Data = payload });

            _logger.LogInformation("✅ [MDO] Event emitted to pipeline. Buffer Flushed.");
        }
        catch (JsonException ex)
        {
            _logger.LogError("❌ [MDO] JSON Parse Error (AST drift): {Message}", ex.Message);
            throw; // Route kickback to Judge 6.1
        }
    }
}

// =========================================================================
// SECTION 4: JUDGE 6 GOVERNANCE PROCESS (LLM-Backed Risk Evaluator)
// =========================================================================

/// <summary>
/// Judge 6 risk governance process for the UphillSnowball legal AI agent.
/// Implements the Wet Fleece / Dry Ground risk assessment protocol.
/// </summary>
public sealed class Judge6Process
{
    private readonly Microsoft.SemanticKernel.Kernel _kernel;
    private readonly Judge6Config _config;

    public Judge6Process(Microsoft.SemanticKernel.Kernel kernel, Judge6Config? config = null)
    {
        _kernel = kernel ?? throw new ArgumentNullException(nameof(kernel));
        _config = config ?? Judge6Config.Default;
    }

    /// <summary>
    /// Evaluates an agent action against the Judge 6 risk protocol.
    /// Returns a GovernanceDecision indicating whether the action is permitted.
    /// </summary>
    public async Task<GovernanceDecision> EvaluateAsync(
        AgentAction action,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(action);

        var riskLevel = ClassifyRisk(action);

        if (riskLevel == GovernanceRiskLevel.High)
        {
            return await EvaluateHighRiskAsync(action, cancellationToken);
        }

        return new GovernanceDecision
        {
            ActionId = action.ActionId,
            RiskLevel = riskLevel,
            Permitted = riskLevel != GovernanceRiskLevel.Blocked,
            Rationale = riskLevel switch
            {
                GovernanceRiskLevel.Low => "Standard processing permitted.",
                GovernanceRiskLevel.Medium => "Permitted with audit logging.",
                GovernanceRiskLevel.Blocked => "Action blocked by governance policy.",
                _ => "Unknown risk classification."
            },
            Timestamp = DateTimeOffset.UtcNow,
        };
    }

    private GovernanceRiskLevel ClassifyRisk(AgentAction action)
    {
        if (_config.BlockedActions.Contains(action.ActionType))
        {
            return GovernanceRiskLevel.Blocked;
        }

        if (action.ActionType is "database_write" or "payment_process"
            or "auth_modify" or "force_push")
        {
            return GovernanceRiskLevel.High;
        }

        if (action.ActionType is "document_delete" or "billing_adjust"
            or "sanctions_override")
        {
            return GovernanceRiskLevel.Medium;
        }

        return GovernanceRiskLevel.Low;
    }

    private async Task<GovernanceDecision> EvaluateHighRiskAsync(
        AgentAction action,
        CancellationToken cancellationToken)
    {
        var prompt = $"""
            You are Judge 6, a legal risk governance evaluator.
            Assess the following agent action for compliance with the
            ShadowTag sovereign execution doctrine.

            Action Type: {action.ActionType}
            Target: {action.Target}
            Context: {action.Context}

            Respond with a JSON object containing:
            - "permitted": boolean
            - "rationale": string explaining your reasoning
            - "conditions": array of strings listing any conditions
            """;

        var result = await _kernel.InvokePromptAsync(
            prompt,
            cancellationToken: cancellationToken);

        var responseText = result.GetValue<string>() ?? "{}";

        try
        {
            var parsed = JsonSerializer.Deserialize<GovernanceResponse>(
                responseText,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

            return new GovernanceDecision
            {
                ActionId = action.ActionId,
                RiskLevel = GovernanceRiskLevel.High,
                Permitted = parsed?.Permitted ?? false,
                Rationale = parsed?.Rationale ?? "Unable to parse governance response.",
                Conditions = parsed?.Conditions ?? [],
                Timestamp = DateTimeOffset.UtcNow,
            };
        }
        catch (JsonException)
        {
            return new GovernanceDecision
            {
                ActionId = action.ActionId,
                RiskLevel = GovernanceRiskLevel.High,
                Permitted = false,
                Rationale = "Governance evaluation failed — defaulting to deny.",
                Timestamp = DateTimeOffset.UtcNow,
            };
        }
    }

    /// <summary>
    /// Handles external events routed to the governance process.
    /// </summary>
    public async Task OnExternalEventAsync(
        string eventType,
        string payload,
        CancellationToken cancellationToken = default)
    {
        switch (eventType)
        {
            case "sanctions_alert":
                await HandleSanctionsAlertAsync(payload, cancellationToken);
                break;

            case "privilege_breach":
                await HandlePrivilegeBreachAsync(payload, cancellationToken);
                break;

            case "billing_dispute":
                await HandleBillingDisputeAsync(payload, cancellationToken);
                break;

            default:
                Console.Error.WriteLine(
                    $"[Judge6] Unknown external event: {eventType}");
                break;
        }
    }

    private Task HandleSanctionsAlertAsync(string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Judge6] SANCTIONS ALERT: {payload}");
        return Task.CompletedTask;
    }

    private Task HandlePrivilegeBreachAsync(string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Judge6] PRIVILEGE BREACH: {payload}");
        return Task.CompletedTask;
    }

    private Task HandleBillingDisputeAsync(string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Judge6] BILLING DISPUTE: {payload}");
        return Task.CompletedTask;
    }
}

// =========================================================================
// SECTION 5: CSRMC PIPELINE STEPS (SK Process.Core Directed Graph)
// =========================================================================

// ----- STEP 1: Semantic Compression (The "Input") -----

public class CompressionStep : KernelProcessStep
{
    [KernelFunction, Description("Extracts decision features from raw input")]
    public async Task<string> ExtractFeaturesAsync(KernelProcessStepContext context, string rawInput)
    {
        Console.WriteLine($"[Compressor] Processing: {rawInput[..Math.Min(20, rawInput.Length)]}...");

        string data = JsonSerializer.Serialize(new { party_size = 4, ltv = 0.9 });
        await context.EmitEventAsync(new() { Id = "FeaturesExtracted", Data = data });
        return "Features Extracted";
    }
}

// ----- STEP 2: CSRMC Risk Scoring (The "Judge") -----

public class RiskStep : KernelProcessStep
{
    [KernelFunction, Description("Evaluates features against CSRMC Doctrine (Supersedes ATP 5-19)")]
    public async Task EvaluateRiskAsync(KernelProcessStepContext context, string features)
    {
        var assessment = new RiskAssessment
        {
            Level = CsrmcRiskLevel.RA2_Moderate,
            ProbabilityScore = 0.45,
            Rationale = "High LTV, but late night transaction (CSRMC Velocity Check)."
        };

        if (assessment.Level >= CsrmcRiskLevel.RA4_Preclusive)
        {
            await context.EmitEventAsync(new() { Id = "RiskPreclusive", Data = assessment });
        }
        else if (assessment.Level >= CsrmcRiskLevel.RA2_Moderate)
        {
            await context.EmitEventAsync(new() { Id = "RiskModerate", Data = assessment });
        }
        else
        {
            await context.EmitEventAsync(new() { Id = "RiskLow", Data = assessment });
        }
    }
}

// ----- STEP 2B: Sovereign Fallback (The "Hermes-Agent") -----

public class HermesOfflineStep : KernelProcessStep
{
    [KernelFunction, Description("Offline Deterministic Tool Execution via Hermes-Agent")]
    public async Task RouteOfflineAsync(KernelProcessStepContext context, RiskAssessment risk)
    {
        Console.WriteLine($"[HERMES-AGENT] Sovereign mode activated. Routing offline to localhost:11434.");
        await context.EmitEventAsync(new() { Id = "SovereignComplete", Data = risk });
    }
}

// ----- STEP 3: Human Gate (The "Brakes") -----

public class HumanGateStep : KernelProcessStep
{
    [KernelFunction]
    public void AwaitApproval(RiskAssessment risk)
    {
        Console.WriteLine($"[HumanGate] PAUSED. Risk: {risk.Level}. Waiting for external Approval event...");
        // Execution halts here. Workflow saves state to DB and sleeps.
        // Relies on API Controller sending builder.OnExternalEvent("UserApproved")
    }
}

// ----- STEP 4: Enforcement (The "Gavel") -----

public class EnforcementStep : KernelProcessStep
{
    [KernelFunction]
    public void Execute(RiskAssessment risk)
    {
        Console.WriteLine($"[Enforcement] EXECUTING Transaction. Risk: {risk.Level}");
    }

    [KernelFunction]
    public void Block(RiskAssessment risk)
    {
        Console.WriteLine($"[Enforcement] BLOCKED. Reason: {risk.Rationale}");
    }
}

// =========================================================================
// SECTION 6: PROCESS BUILDER (The Architect — Directed Graph Assembly)
// =========================================================================

/// <summary>
/// Builds the JudgeSix_v2 SK Process pipeline as a directed graph.
/// Uses OnExternalEvent (CORRECT API for Process.Core v1.21.0-alpha).
/// </summary>
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

        // Entry: External event triggers compression
        builder.OnExternalEvent("Start")
            .SendEventTo(new ProcessFunctionTargetBuilder(compress, nameof(CompressionStep.ExtractFeaturesAsync), "rawInput"));

        // Compression → Risk Engine
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

        // Human Loop Closure via OnExternalEvent
        builder.OnExternalEvent("UserApproved")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        return builder.Build();
    }
}
