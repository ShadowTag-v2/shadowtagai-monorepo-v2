// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC8004Reputation {
    function postFeedback(
        uint256 agentId,
        uint8 score,
        string calldata context,
        string calldata proofURI
    ) external;

    function getReputation(uint256 agentId) external view returns (uint8);
}
