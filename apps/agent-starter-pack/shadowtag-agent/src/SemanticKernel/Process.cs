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

// ShadowTag Semantic Kernel Process — Judge 6 Governance Layer
// Target: .NET 11.0 Preview 2 (11.0.100-preview.2.26159.112)
// Project: shadowtag-omega-v4

using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;

namespace ShadowTag.SemanticKernel;

/// <summary>
/// Judge 6 risk governance process for the UphillSnowball legal AI agent.
/// Implements the Wet Fleece / Dry Ground risk assessment protocol.
/// </summary>
public sealed class Judge6Process
{
    private readonly Kernel _kernel;
    private readonly Judge6Config _config;

    public Judge6Process(Kernel kernel, Judge6Config? config = null)
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

        // Phase 1: Static risk classification
        var riskLevel = ClassifyRisk(action);

        // Phase 2: If HIGH risk, invoke deeper LLM-based analysis
        if (riskLevel == RiskLevel.High)
        {
            return await EvaluateHighRiskAsync(action, cancellationToken);
        }

        // Phase 3: Return immediate decision for LOW/MEDIUM
        return new GovernanceDecision
        {
            ActionId = action.ActionId,
            RiskLevel = riskLevel,
            Permitted = riskLevel != RiskLevel.Blocked,
            Rationale = riskLevel switch
            {
                RiskLevel.Low => "Standard processing permitted.",
                RiskLevel.Medium => "Permitted with audit logging.",
                RiskLevel.Blocked => "Action blocked by governance policy.",
                _ => "Unknown risk classification."
            },
            Timestamp = DateTimeOffset.UtcNow,
        };
    }

    /// <summary>
    /// Classifies the static risk level of an agent action.
    /// </summary>
    private RiskLevel ClassifyRisk(AgentAction action)
    {
        // Blocked actions (never permitted)
        if (_config.BlockedActions.Contains(action.ActionType))
        {
            return RiskLevel.Blocked;
        }

        // High-risk patterns
        if (action.ActionType is "database_write" or "payment_process"
            or "auth_modify" or "force_push")
        {
            return RiskLevel.High;
        }

        // Medium-risk patterns
        if (action.ActionType is "document_delete" or "billing_adjust"
            or "sanctions_override")
        {
            return RiskLevel.Medium;
        }

        return RiskLevel.Low;
    }

    /// <summary>
    /// Performs deep LLM-based risk evaluation for high-risk actions.
    /// Uses the Semantic Kernel to invoke a structured analysis prompt.
    /// </summary>
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
                RiskLevel = RiskLevel.High,
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
                RiskLevel = RiskLevel.High,
                Permitted = false,
                Rationale = "Governance evaluation failed — defaulting to deny.",
                Timestamp = DateTimeOffset.UtcNow,
            };
        }
    }

    /// <summary>
    /// Handles external events routed to the governance process.
    /// Implements the OnExternalEvent lifecycle hook.
    /// </summary>
    public async Task OnExternalEventAsync(
        string eventType,
        string payload,
        CancellationToken cancellationToken = default)
    {
        switch (eventType)
        {
            case "sanctions_alert":
                // Immediately block all pending actions for the entity
                await HandleSanctionsAlertAsync(payload, cancellationToken);
                break;

            case "privilege_breach":
                // Escalate to senior counsel and lock the matter
                await HandlePrivilegeBreachAsync(payload, cancellationToken);
                break;

            case "billing_dispute":
                // Flag entries and pause billing
                await HandleBillingDisputeAsync(payload, cancellationToken);
                break;

            default:
                // Log unknown events for audit
                Console.Error.WriteLine(
                    $"[Judge6] Unknown external event: {eventType}");
                break;
        }
    }

    private Task HandleSanctionsAlertAsync(
        string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Judge6] SANCTIONS ALERT: {payload}");
        // TODO: Wire to Firestore uphillsnowball_screenings collection
        return Task.CompletedTask;
    }

    private Task HandlePrivilegeBreachAsync(
        string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Judge6] PRIVILEGE BREACH: {payload}");
        // TODO: Wire to notification pipeline
        return Task.CompletedTask;
    }

    private Task HandleBillingDisputeAsync(
        string payload, CancellationToken ct)
    {
        Console.WriteLine($"[Judge6] BILLING DISPUTE: {payload}");
        // TODO: Wire to uphillsnowball_billing status update
        return Task.CompletedTask;
    }
}

// ---------------------------------------------------------------------------
// Supporting Types
// ---------------------------------------------------------------------------

public enum RiskLevel
{
    Low,
    Medium,
    High,
    Blocked,
}

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
    public required RiskLevel RiskLevel { get; init; }
    public required bool Permitted { get; init; }
    public required string Rationale { get; init; }
    public List<string> Conditions { get; init; } = [];
    public DateTimeOffset Timestamp { get; init; }
}

public sealed record Judge6Config
{
    public HashSet<string> BlockedActions { get; init; } = [
        "rm_rf",
        "sudo",
        "force_push_main",
        "drop_database",
    ];

    public static Judge6Config Default => new();
}

// Internal deserialization model for LLM governance responses
internal sealed record GovernanceResponse
{
    public bool Permitted { get; init; }
    public string Rationale { get; init; } = "";
    public List<string> Conditions { get; init; } = [];
}
