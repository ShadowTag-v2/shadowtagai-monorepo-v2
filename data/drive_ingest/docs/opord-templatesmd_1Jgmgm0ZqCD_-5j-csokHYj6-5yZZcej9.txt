# OPORD Template Examples

## Example 1: Backend API Development

```markdown
# OPORD 00142 - Implement ERC-8004 Reputation API

## 1. SITUATION
**Enemy Forces**:
- No existing reputation tracking in current API
- Blockchain integration complexity
- Gas cost optimization required

**Friendly Forces**:
- Shift 1 (200 agents): 50 Python experts, 30 blockchain specialists
- Existing ERC8004Reputation.sol contract deployed
- FastAPI framework in place

**Attachments/Detachments**:
- Web3.py library
- Ethers.js for frontend integration

**Civil Considerations**:
- Users need real-time reputation scores
- Must support 10k+ requests/minute

## 2. MISSION
**WHO**: Shift 1, Squad Alpha (agents 200-250)
**WHAT**: Implement REST API endpoints for ERC-8004 reputation queries
**WHEN**: Complete by 2025-11-23 0800 UTC (16 hours)
**WHERE**: `src/aiyou/routers/reputation.py`, `src/aiyou/services/reputation_service.py`
**WHY**: Enable reputation-based access control for $100M revenue milestone

## 3. EXECUTION
**Commander's Intent**:
Create production-ready API that queries on-chain reputation data with <100ms p99 latency.

**Concept of Operations**:
Phase 1: Design API schema (2h)
Phase 2: Implement service layer with caching (6h)
Phase 3: Add endpoints and validation (4h)
Phase 4: Testing and optimization (4h)

**Tasks to Subordinate Units**:
- **Squad Alpha (agents 200-210)**: API schema design, Pydantic models
- **Squad Bravo (agents 211-220)**: Service layer, Web3 integration
- **Squad Charlie (agents 221-230)**: Caching strategy (Redis)
- **Squad Delta (agents 231-240)**: Testing, load testing
- **Squad Echo (agents 241-250)**: Documentation, deployment

**Coordinating Instructions**:
- **Phase Line GREEN**: Schema approved by architect agent
- **Phase Line AMBER**: Service layer passes unit tests
- **Phase Line RED**: Load test achieves <100ms p99
- **Consolidation**: Merge to `main` after all quality gates pass

## 4. SERVICE SUPPORT
**Logistics**:
- Dependencies: `web3>=6.0.0`, `redis>=5.0.0`
- Infura API key for Ethereum RPC
- Redis instance on port 6379

**Personnel**:
- Lead: agent_205 (PhD Distributed Systems, 15 years)
- Blockchain SME: agent_217 (JD + Solidity expert)
- Testing Lead: agent_235 (PhD Software Engineering)

**Medical** (Error Handling):
- Rollback: Git revert if deployment fails
- Circuit breaker: Disable reputation checks if blockchain RPC down
- Sentry alerts for all exceptions

## 5. COMMAND & SIGNAL
**Command**:
- OIC: SwarmOrchestrator (Level 5 Overlord mode)
- Quality Gates: BarExamProtocol (must pass mypy, ruff, pytest)
- Approval Authority: Judge#6 for security review

**Signal**:
- Context Index: Log all decisions to `context_index.db`
- Slack: #swarm-shift-1 for real-time updates
- GitHub: PR #847 for code review

**Succession of Command**:
1. Primary: agent_205
2. Alternate: agent_217
3. Emergency: SwarmOrchestrator escalates to human

---

**ACKNOWLEDGE**:
- agent_205: ✓ Received OPORD 00142
- agent_217: ✓ Received OPORD 00142
- agent_235: ✓ Received OPORD 00142

**TIME HACK**: 2025-11-22 1600 UTC
```

---

## Example 2: Smart Contract Security Audit

```markdown
# OPORD 00143 - Security Audit: ShadowTagAccount.sol

## 1. SITUATION
**Enemy Forces**:
- Potential reentrancy vulnerabilities
- Access control gaps
- Gas optimization opportunities

**Friendly Forces**:
- Shift 2 (200 agents): 40 security auditors, 35 Solidity experts
- Slither static analyzer
- Mythril symbolic execution

**Attachments/Detachments**:
- OpenZeppelin security patterns
- Trail of Bits audit checklist

**Civil Considerations**:
- Contract holds user funds (high risk)
- Mainnet deployment planned for 2025-12-01

## 2. MISSION
**WHO**: Shift 2, Security Squad (agents 400-450)
**WHAT**: Conduct comprehensive security audit of ShadowTagAccount.sol
**WHEN**: Complete by 2025-11-23 0000 UTC (8 hours)
**WHERE**: `contracts/tba/ShadowTagAccount.sol`
**WHY**: Prevent exploits that could drain user funds, protect $100M revenue goal

## 3. EXECUTION
**Commander's Intent**:
Identify and fix all critical/high vulnerabilities before mainnet deployment.

**Concept of Operations**:
Phase 1: Automated scanning (1h)
Phase 2: Manual code review (4h)
Phase 3: Exploit development (2h)
Phase 4: Remediation verification (1h)

**Tasks to Subordinate Units**:
- **Red Team (agents 400-415)**: Attempt exploits, write PoCs
- **Blue Team (agents 416-430)**: Code review, pattern matching
- **Tool Team (agents 431-440)**: Run Slither, Mythril, Echidna
- **Doc Team (agents 441-450)**: Generate audit report

**Coordinating Instructions**:
- **Phase Line SECURE**: All automated scans complete
- **Phase Line HARDENED**: Manual review findings documented
- **Phase Line VERIFIED**: All critical issues fixed and retested

## 4. SERVICE SUPPORT
**Logistics**:
- Tools: Slither, Mythril, Echidna, Foundry
- Test network: Sepolia testnet
- Gas budget: 10 ETH for testing

**Personnel**:
- Lead Auditor: agent_405 (PhD Cryptography, OSCP)
- Solidity Expert: agent_420 (10 years smart contract dev)
- Exploit Dev: agent_408 (Black Hat speaker)

**Medical**:
- If critical vuln found: Halt deployment immediately
- Escalation: Notify human security team within 15 minutes
- Backup: External audit firm on standby

## 5. COMMAND & SIGNAL
**Command**:
- OIC: blockchain-security-auditor agent
- Approval: Judge#6 must approve before mainnet
- Final Authority: Human CTO for critical findings

**Signal**:
- Context Index: Tag all findings with "security", "critical", "high", "medium", "low"
- GitHub: Create security advisory for each critical issue
- Encrypted comms: Use Signal for sensitive findings

**Succession of Command**:
1. Primary: agent_405
2. Alternate: agent_420
3. Emergency: Escalate to human security team

---

**ACKNOWLEDGE**:
- agent_405: ✓ OPORD 00143 received, beginning Phase 1
- agent_420: ✓ Standing by for manual review
- agent_408: ✓ Exploit dev environment ready

**TIME HACK**: 2025-11-22 1600 UTC
```

---

## Atomic Thread Format (Simplified for Quick Tasks)

For smaller tasks, use abbreviated OPORD:

```markdown
# OPORD [NUM] - [TASK]

**MISSION**: [One sentence]
**AGENTS**: [IDs]
**EXECUTION**: [3-5 bullet points]
**CHECKPOINTS**: [Quality gates]
**SIGNAL**: [Context Index tag]

---
**ACK**: [Agent IDs]
**TIME**: [UTC timestamp]
```

## Usage Guidelines

1. **Always use OPORD format** for tasks involving 5+ agents
2. **Abbreviated format** acceptable for <5 agents or <2 hour tasks
3. **Log every OPORD** to Context Index with unique number
4. **Increment OPORD counter** globally across all shifts
5. **Archive completed OPORDs** after 30 days to `dev/archive/opords/`
