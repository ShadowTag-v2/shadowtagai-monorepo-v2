// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC8004Reputation.sol";

contract MockERC8004Reputation is IERC8004Reputation {
    mapping(uint256 => uint8) public scores;

    function postFeedback(
        uint256 agentId,
        uint8 score,
        string calldata /* context */,
        string calldata /* proofURI */
    ) external {
        scores[agentId] = score;
    }

    function getReputation(uint256 agentId) external view returns (uint8) {
        return scores[agentId];
    }
}
