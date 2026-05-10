// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC6551Registry.sol";
import "@openzeppelin/contracts/utils/Create2.sol";

contract ERC6551Registry is IERC6551Registry {
    error InitializationFailed();

    function createAccount(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId,
        bytes calldata /*initData*/
    ) external returns (address) {
        bytes memory code = _creationCode(implementation, chainId, tokenContract, tokenId, salt);

        address createdAccount = Create2.computeAddress(salt, keccak256(code));

        if (createdAccount.code.length != 0) return createdAccount;

        emit ERC6551AccountCreated(createdAccount, implementation, salt, chainId, tokenContract, tokenId);

        assembly {
            createdAccount := create2(0, add(code, 0x20), mload(code), salt)
        }

        if (createdAccount == address(0)) revert InitializationFailed();

        // Note: We are not calling initData on the account here for simplicity and gas.
        // If initData is needed, it should be called after creation.
        // Standard EIP-6551 registry doesn't necessarily call initData in createAccount,
        // but some implementations do. For now, we ignore it to match the minimal proxy pattern.

        return createdAccount;
    }

    function account(
        address implementation,
        bytes32 salt,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId
    ) external view returns (address) {
        bytes memory code = _creationCode(implementation, chainId, tokenContract, tokenId, salt);
        return Create2.computeAddress(salt, keccak256(code));
    }

    function _creationCode(
        address implementation,
        uint256 chainId,
        address tokenContract,
        uint256 tokenId,
        bytes32 salt
    ) internal pure returns (bytes memory) {
        return abi.encodePacked(
            hex"3d60ad80600a3d3981f3363d3d373d3d3d363d73",
            implementation,
            hex"5af43d82803e903d91602b57fd5bf3",
            abi.encode(salt, chainId, tokenContract, tokenId)
        );
    }
}
