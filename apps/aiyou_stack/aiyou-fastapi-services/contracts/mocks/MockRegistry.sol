// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC6551Registry.sol";

contract MockRegistry is IERC6551Registry {
    function createAccount(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId,
        bytes calldata /*initData*/
    ) external returns (address) {
        // Simple deterministic address generation for mock
        address createdAccount = address(uint160(uint256(keccak256(abi.encodePacked(implementation, chainId, tokenContract, tokenId, salt)))));
        emit ERC6551AccountCreated(createdAccount, implementation, salt, chainId, tokenContract, tokenId);
        return createdAccount;
    }

    function account(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId
    ) external view returns (address) {
        return address(uint160(uint256(keccak256(abi.encodePacked(implementation, chainId, tokenContract, tokenId, salt)))));
    }
}
