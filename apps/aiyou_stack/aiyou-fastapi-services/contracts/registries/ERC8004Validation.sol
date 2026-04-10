// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "../interfaces/IERC8004Validation.sol";

contract ERC8004Validation is IERC8004Validation, Ownable {
    // taskHash => verified boolean
    mapping(bytes32 => bool) private _verifiedTasks;

    event TaskValidated(bytes32 indexed taskHash, string taskURI, bool success);

    constructor() Ownable(msg.sender) {}

    function validateTask(bytes calldata proof, string calldata taskURI) external override returns (bool) {
        // In production, this would verify a ZK proof or check a TEE attestation.
        // For the ShadowTagAI prototype/simulation, we accept the proof if it's non-empty.
        // We can also restrict this to specific validators (or the Overlord).

        require(proof.length > 0, "Empty proof");

        bytes32 taskHash = keccak256(abi.encodePacked(taskURI, proof));

        // Logic to verify proof...
        bool isValid = true; // Simulated validity

        if (isValid) {
            _verifiedTasks[taskHash] = true;
            emit TaskValidated(taskHash, taskURI, true);
            return true;
        }

        return false;
    }

    function isVerified(bytes32 taskHash) external view override returns (bool) {
        return _verifiedTasks[taskHash];
    }
}
