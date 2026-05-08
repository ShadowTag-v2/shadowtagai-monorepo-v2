// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC8004Validation.sol";

contract MockERC8004Validation is IERC8004Validation {
    mapping(bytes32 => bool) public verified;

    function validateTask(bytes calldata /* proof */, string calldata taskURI) external returns (bool) {
        bytes32 taskHash = keccak256(bytes(taskURI));
        verified[taskHash] = true;
        return true;
    }

    function isVerified(bytes32 taskHash) external view returns (bool) {
        return verified[taskHash];
    }
}
