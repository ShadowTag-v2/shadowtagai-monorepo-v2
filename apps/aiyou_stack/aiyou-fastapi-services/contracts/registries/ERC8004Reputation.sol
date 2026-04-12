// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC8004Reputation.sol";

contract ERC8004Reputation is IERC8004Reputation, Ownable {
    struct Feedback {
        uint8 score; // 0-100
        string context;
        string proofURI;
        uint256 timestamp;
    }

    // agentId => list of feedback
    mapping(uint256 => Feedback[]) private _feedbacks;

    // agentId => current average reputation
    mapping(uint256 => uint8) private _reputation;

    event FeedbackPosted(uint256 indexed agentId, uint8 score, address indexed reviewer);

    constructor() Ownable(msg.sender) {}

    function postFeedback(
        uint256 agentId,
        uint8 score,
        string calldata context,
        string calldata proofURI
    ) external override {
        // In a real system, we'd restrict who can post feedback (e.g. only parent, or valid task requesters).
        // For ShadowTagAI swarm, the DNA contract calls this on spawn (score 100).
        // We'll restrict to owner (System/DNA contract) for now to prevent spam.
        require(msg.sender == owner(), "Only system can post feedback");
        require(score <= 100, "Score > 100");

        _feedbacks[agentId].push(Feedback({
            score: score,
            context: context,
            proofURI: proofURI,
            timestamp: block.timestamp
        }));

        // Recalculate average (simplified moving average or just simple average)
        // For gas efficiency, we might want a running average.
        // NewAvg = ((OldAvg * Count) + NewScore) / (Count + 1)

        uint256 count = _feedbacks[agentId].length;
        if (count == 1) {
            _reputation[agentId] = score;
        } else {
            uint256 oldAvg = _reputation[agentId];
            // Approximation to avoid overflow with large counts, though count won't be that huge for agents
            uint256 newAvg = ((oldAvg * (count - 1)) + score) / count;
            _reputation[agentId] = uint8(newAvg);
        }

        emit FeedbackPosted(agentId, score, msg.sender);
    }

    function getReputation(uint256 agentId) external view override returns (uint8) {
        return _reputation[agentId];
    }
}
