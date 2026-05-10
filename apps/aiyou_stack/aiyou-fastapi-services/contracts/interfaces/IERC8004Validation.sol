// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC8004Validation {
    function validateTask(bytes calldata proof, string calldata taskURI) external returns (bool);
    function isVerified(bytes32 taskHash) external view returns (bool);
}
