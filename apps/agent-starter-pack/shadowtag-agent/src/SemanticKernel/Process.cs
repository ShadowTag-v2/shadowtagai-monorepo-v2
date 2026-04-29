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
// FORWARDING REFERENCE: Canonical Process.cs lives in aiyou-kernel.
// This file re-exports the ShadowTagV4.Kernel types into the
// ShadowTag.SemanticKernel namespace for backward compatibility.
//
// Canonical source:
//   apps/aiyou_stack/aiyou-fastapi-services/apps/aiyou-kernel/Process.cs
//
// OnExternalEvent is the CORRECT API per AGENTS.md Core Technical Truth #3.
// Do NOT apply the OnInputEvent rename until Process.Core >= v1.30+.
// =============================================================================

// NOTE: This project does not have a project reference to AiYou.Kernel.
// When wiring the two projects together, add:
//   <ProjectReference Include="..\..\..\..\aiyou_stack\aiyou-fastapi-services\apps\aiyou-kernel\AiYou.Kernel.csproj" />
// to SemanticKernel.csproj. Until then, this file contains the same types
// under the ShadowTag.SemanticKernel namespace for independent compilation.

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Process;

namespace ShadowTag.SemanticKernel;

// =========================================================================
// SECTION 1: DOMAIN TYPES — CSRMC Risk Matrix (Supersedes ATP 5-19)
// =========================================================================

public enum CsrmcRiskLevel { RA1_Negligible, RA2_Moderate, RA3_High, RA4_Preclusive }
public enum CsrmcDecision { ALLOW, BLOCK, ESCALATE }

public class RiskAssessment
{
    public CsrmcRiskLevel Level { get; set; }
    public double ProbabilityScore { get; set; }
    public string? Rationale { get; set; }
}

// =========================================================================
// SECTION 2: DOMAIN TYPES — Judge 6 Governance (Wet Fleece / Dry Ground)
// =========================================================================

public enum GovernanceRiskLevel { Low, Medium, High, Blocked }

public sealed record AgentAction
{
    public required string ActionId { get; init; }
    public required string ActionType { get; init; }
    public string Target { get; init; } = "";
    public string Context { get; init; } = "";
}

public sealed record GovernanceDecision
{
    public required string ActionId { get; init; }
    public required GovernanceRiskLevel RiskLevel { get; init; }
    public required bool Permitted { get; init; }
    public required string Rationale { get; init; }
    public List<string> Conditions { get; init; } = [];
    public DateTimeOffset Timestamp { get; init; }
}

public sealed record Claude_Code_6Config
{
    public HashSet<string> BlockedActions { get; init; } =
    [
        "rm_rf",
        "sudo",
        "force_push_main",
        "drop_database",
    ];

    public static Claude_Code_6Config Default => new();
}

internal sealed record GovernanceResponse
{
    public bool Permitted { get; init; }
    public string Rationale { get; init; } = "";
    public List<string> Conditions { get; init; } = [];
}

// =========================================================================
// SECTION 3: SOVEREIGN MDO PROCESS
// =========================================================================

public class SovereignMdoProcess
{
    private readonly ILogger<SovereignMdoProcess> _logger;

    public SovereignMdoProcess(ILogger<SovereignMdoProcess> logger)
    {
        _logger = logger;
    }

    public async Task<string> RunProcessAsync(KernelProcessStepContext context)
    {
        _logger.LogInformation("🚀 [MDO] Durable Execution started.");
        await Task.CompletedTask;
        return "MDO_AWAITING_EXTERNAL_EVENT";
    }

    public async Task OnExternalEvent(KernelProcessStepContext context, string payload)
    {
        _logger.LogInformation("📥 [MDO] OnExternalEvent triggered.");
        try
        {
            using var document = JsonDocument.Parse(payload);
            await context.EmitEventAsync(new KernelProcessEvent { Id = "mdo_event_received", Data = payload });
            _logger.LogInformation("✅ [MDO] Event emitted to pipeline.");
        }
        catch (JsonException ex)
        {
            _logger.LogError("❌ [MDO] JSON Parse Error: {Message}", ex.Message);
            throw;
        }
    }
}

// =========================================================================
// SECTION 4: JUDGE 6 GOVERNANCE PROCESS
// =========================================================================

public sealed class Claude_Code_6Process
{
    private readonly Kernel _kernel;
    private readonly Claude_Code_6Config _config;

    public Claude_Code_6Process(Kernel kernel, Claude_Code_6Config? config = null)
    {
        _kernel = kernel ?? throw new ArgumentNullException(nameof(kernel));
        _config = config ?? Claude_Code_6Config.Default;
    }

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
            return GovernanceRiskLevel.Blocked;
        if (action.ActionType is "database_write" or "payment_process"
            or "auth_modify" or "force_push")
            return GovernanceRiskLevel.High;
        if (action.ActionType is "document_delete" or "billing_adjust"
            or "sanctions_override")
            return GovernanceRiskLevel.Medium;
        return GovernanceRiskLevel.Low;
    }

    private async Task<GovernanceDecision> EvaluateHighRiskAsync(
        AgentAction action, CancellationToken cancellationToken)
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

        var result = await _kernel.InvokePromptAsync(prompt, cancellationToken: cancellationToken);
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

    public async Task OnExternalEventAsync(
        string eventType, string payload,
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
                Console.Error.WriteLine($"[Claude_Code_6] Unknown external event: {eventType}");
                break;
        }
    }

    private Task HandleSanctionsAlertAsync(string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Claude_Code_6] SANCTIONS ALERT: {payload}");
        return Task.CompletedTask;
    }

    private Task HandlePrivilegeBreachAsync(string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Claude_Code_6] PRIVILEGE BREACH: {payload}");
        return Task.CompletedTask;
    }

    private Task HandleBillingDisputeAsync(string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Claude_Code_6] BILLING DISPUTE: {payload}");
        return Task.CompletedTask;
    }
}

// =========================================================================
// SECTION 5: CSRMC PIPELINE STEPS (SK Process.Core Directed Graph)
// =========================================================================

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

public class RiskStep : KernelProcessStep
{
    [KernelFunction, Description("Evaluates features against CSRMC Doctrine")]
    public async Task EvaluateRiskAsync(KernelProcessStepContext context, string features)
    {
        var assessment = new RiskAssessment
        {
            Level = CsrmcRiskLevel.RA2_Moderate,
            ProbabilityScore = 0.45,
            Rationale = "High LTV, but late night transaction (CSRMC Velocity Check)."
        };

        if (assessment.Level >= CsrmcRiskLevel.RA4_Preclusive)
            await context.EmitEventAsync(new() { Id = "RiskPreclusive", Data = assessment });
        else if (assessment.Level >= CsrmcRiskLevel.RA2_Moderate)
            await context.EmitEventAsync(new() { Id = "RiskModerate", Data = assessment });
        else
            await context.EmitEventAsync(new() { Id = "RiskLow", Data = assessment });
    }
}

public class HermesOfflineStep : KernelProcessStep
{
    [KernelFunction, Description("Offline Deterministic Tool Execution via Hermes-Agent")]
    public async Task RouteOfflineAsync(KernelProcessStepContext context, RiskAssessment risk)
    {
        Console.WriteLine("[HERMES-AGENT] Sovereign mode activated. Routing offline to localhost:11434.");
        await context.EmitEventAsync(new() { Id = "SovereignComplete", Data = risk });
    }
}

public class HumanGateStep : KernelProcessStep
{
    [KernelFunction]
    public void AwaitApproval(RiskAssessment risk)
    {
        Console.WriteLine($"[HumanGate] PAUSED. Risk: {risk.Level}. Waiting for external Approval event...");
    }
}

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
// SECTION 6: PROCESS BUILDER (Directed Graph Assembly)
// =========================================================================

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

        builder.OnExternalEvent("Start")
            .SendEventTo(new ProcessFunctionTargetBuilder(compress, nameof(CompressionStep.ExtractFeaturesAsync), "rawInput"));

        compress.OnEvent("FeaturesExtracted")
            .SendEventTo(new ProcessFunctionTargetBuilder(risk, nameof(RiskStep.EvaluateRiskAsync), "features"));

        risk.OnEvent("RiskLow")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        risk.OnEvent("RiskModerate")
            .SendEventTo(new ProcessFunctionTargetBuilder(human, nameof(HumanGateStep.AwaitApproval), "risk"));

        risk.OnEvent("RiskPreclusive")
            .SendEventTo(new ProcessFunctionTargetBuilder(hermes, nameof(HermesOfflineStep.RouteOfflineAsync), "risk"));

        hermes.OnEvent("SovereignComplete")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Block), "risk"));

        builder.OnExternalEvent("UserApproved")
            .SendEventTo(new ProcessFunctionTargetBuilder(enforce, nameof(EnforcementStep.Execute), "risk"));

        return builder.Build();
    }
}
