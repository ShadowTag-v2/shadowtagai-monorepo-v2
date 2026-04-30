# The P.N.K.L.N Protocol: .NET 8 Semantic Kernel & MCP
**Doc ID:** Cor.58.5-NET-KERNEL-STRATEGY
**Version:** 1.0 (Gold Master)
**Date:** Feb 2, 2026
**Source:** "How to fold in Semantic Kernels and agents" (User Directive)

## 1. Executive Summary: The "Blueprint"
We are pivoting the Core Engine from a disparate Node.js/Python stack to a unified, military-grade **.NET 8 Host** running the **Microsoft Semantic Kernel Process Framework**.
*   **Mental Model**: Shift from "Agents" (Chatty/Nondeterministic) to "Processes" (Rigid/Auditable/Graph-based).
*   **Performance**: Dynamic PGO (.NET 8) = 15% free speedup.
*   **Architecture**: **P.N.K.L.N** (Postgres, .NET, Kernel, Liquid, Nvidia).

## 2. The Tech Stack (P.N.K.L.N v3.1)
1.  **P (Postgres)**: `pgvector` for "Doctrine Memory" (Rules/Precedents).
2.  **N (.NET 8)**: The Host Application (Console/Worker Service).
3.  **K (Kernel Process)**: Semantic Kernel Process Framework (Stateful Graph).
4.  **L (Liquid)**: Flutter Frontend (via gRPC/SignalR).
5.  **N (Nvidia)**: Inference via MCP (Model Context Protocol).

## 3. Judge #6 Evaluation Process
The "Judge" is no longer an LLM Prompter; it is a Compiled Process Graph.

### 3.1 The Steps (KernelProcessStep)
1.  **CompressionStep**: Extracts features (JSON) from raw input.
2.  **RiskStep**: Evaluates features against ATP 5-19 Doctrine (RA-1 to RA-4).
3.  **HumanGateStep**: Pauses execution for risk > RA-2 (Moderate).
4.  **EnforcementStep**: Executes or Blocks based on risk verdict.

### 3.2 The Graph (Directed Acyclic Graph)
```csharp
Start -> Compression -> Risk
Risk -> (Low) -> Enforcement.Execute
Risk -> (Moderate) -> HumanGate -> Enforcement.Execute
Risk -> (Preclusive) -> Enforcement.Block
```

## 4. MCP Integration (The "USB-C")
Instead of brittle API clients, we use **MCP Servers** for connectivity.
*   **SeatJudge.Inventory**: Manages table locks/inventory via a sidecar MCP server.
*   **Protocol**: Universal `mcp` socket connection managed by the Kernel.

## 5. Implementation Roadmap
1.  **Code**: Implement `ShadowTag-v2.Kernel/Process.cs` (The C# Graph).
2.  **Infra**: Deploy `SeatJudge.Inventory.Mcp` sidecar.
3.  **Business**: Vertical alignment (SeatJudge, FinJudge, ShadowTag).

## 6. Financial & Legal
*   **Thesis**: "Doctrine-as-a-Service". Rigid, safe decisions.
*   **Margin**: 92% (Target).
*   **IP**: Patent "Stateful Kernel Process for Regulatory Enforcement".

## 7. Immediate Directive
REPLACE all Node.js/Python "Judge" logic with this C# Process Engine.
