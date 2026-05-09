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
||||||| f285896f1
        uint256 score,
        string calldata domain,
        bytes calldata evidence
    ) external returns (uint256) {
        scores[agentId] = score;
    }

    function getReputation(uint256 agentId) external view returns (uint8) {
        return scores[agentId];
    }
}
