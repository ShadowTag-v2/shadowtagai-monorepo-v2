// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC8004Identity.sol";
import "../token/AgentNFT.sol";

contract ERC8004Identity is IERC8004Identity, Ownable {
    AgentNFT public immutable AGENT_NFT;

    // Mapping from agentId to AgentCard URI
    mapping(uint256 => string) private _agentCards;

    event AgentRegistered(uint256 indexed agentId, string agentCardURI);

    constructor(address _agentNft) Ownable(msg.sender) {
        AGENT_NFT = AgentNFT(_agentNft);
    }

    function register(uint256 agentId, string calldata agentCardURI) external override {
        // Only the owner of the AgentNFT (or the contract itself if it's minting) can register
        // For simplicity in this swarm, we allow the Overlord/Admin (owner) or the AgentNFT owner to register.
        // In the DNA contract, spawnChild calls this. The DNA contract is the owner of this registry?
        // Or we allow the DNA contract to call this.

        // Check if caller is owner of the registry (Overlord/DNA contract) or owner of the token
        // If token doesn't exist yet, we might be in the spawn process.

        // For ShadowTagAI architecture:
        // The DNA contract calls register() during spawnChild.
        // So the caller will be the DNA contract.
        // We can restrict to onlyOwner (if DNA contract owns this) or just allow it.

        // Let's assume the DNA contract is the owner of this registry for now,
        // or we add a specific role. For simplicity: onlyOwner.
        // If the DNA contract is not the owner, we might need to transfer ownership or add an authorized caller.
        // But typically the deployer (user) owns it, and sets the DNA contract as a controller?
        // Let's stick to a simple permissionless-ish model where if you own the NFT, you can update the URI,
        // OR if you are the owner of this contract (system admin).

        try AGENT_NFT.ownerOf(agentId) returns (address tokenOwner) {
            require(msg.sender == owner() || msg.sender == tokenOwner, "Not authorized");
        } catch {
            require(msg.sender == owner(), "Not authorized (new spawn)");
        }

        _agentCards[agentId] = agentCardURI;
        emit AgentRegistered(agentId, agentCardURI);
    }

    function getAgentCardURI(uint256 agentId) external view override returns (string memory) {
        return _agentCards[agentId];
    }
}
