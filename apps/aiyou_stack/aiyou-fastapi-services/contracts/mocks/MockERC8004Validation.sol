// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC8004Validation.sol";

contract MockERC8004Validation is IERC8004Validation {
<<<<<<< HEAD
    mapping(bytes32 => bool) public verified;

    function validateTask(bytes calldata /* proof */, string calldata taskURI) external returns (bool) {
        bytes32 taskHash = keccak256(bytes(taskURI));
        verified[taskHash] = true;
||||||| f285896f1
    function validateTask(uint256 agentId, bytes calldata proof) external {}
    function verifyProof(uint256 agentId, bytes calldata proof) external view returns (bool) {
=======
    function validateTask(bytes calldata proof, string calldata taskURI) external returns (bool) {
        return true;
    }
    function isVerified(bytes32 taskHash) external view returns (bool) {
>>>>>>> feature/n-autoresearch/Kosmos/BioAgentss-integration
        return true;
    }

    function isVerified(bytes32 taskHash) external view returns (bool) {
        return verified[taskHash];
    }
}
