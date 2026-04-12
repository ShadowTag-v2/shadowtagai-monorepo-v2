// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC8004Identity {
    function register(uint256 agentId, string calldata agentCardURI) external;
    function getAgentCardURI(uint256 agentId) external view returns (string memory);
}
