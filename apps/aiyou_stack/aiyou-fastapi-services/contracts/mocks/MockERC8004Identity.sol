// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC8004Identity.sol";

contract MockERC8004Identity is IERC8004Identity {
    mapping(uint256 => string) public uris;

    function register(uint256 agentId, string calldata agentCardURI) external {
        uris[agentId] = agentCardURI;
    }

    function getAgentCardURI(uint256 agentId) external view returns (string memory) {
        return uris[agentId];
    }

    // Alias for backward compatibility with tests
    function getAgentURI(uint256 agentId) external view returns (string memory) {
        return uris[agentId];
    }
}
