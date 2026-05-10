// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IERC6551Account.sol";
import "../interfaces/IEntryPoint.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/interfaces/IERC1271.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

contract ShadowTagAccount is IERC6551Account, IERC1271, ERC165 {
    using ECDSA for bytes32;
    using MessageHashUtils for bytes32;

    uint256 public state;
    IEntryPoint public immutable entryPoint;

    receive() external payable {}

    constructor(address _entryPoint) {
        entryPoint = IEntryPoint(_entryPoint);
    }

    function execute(address to, uint256 value, bytes calldata data, uint8 operation)
        external
        payable
        returns (bytes memory result)
    {
        require(_isValidSigner(msg.sender), "Invalid signer");
        require(operation == 0, "Only call operations supported");
        ++state;
        bool success;
        (success, result) = to.call{value: value}(data);
        require(success, "Execution failed");
    }

    function token()
        external
        view
        returns (
            uint256,
            address,
            uint256
        )
    {
        bytes memory footer = new bytes(0x60);
        assembly {
            extcodecopy(address(), add(footer, 0x20), 0x2d, 0x60)
        }
        return abi.decode(footer, (uint256, address, uint256));
    }

    function isValidSigner(address signer, bytes calldata) external view returns (bytes4) {
        if (_isValidSigner(signer)) {
            return IERC6551Account.isValidSigner.selector;
        }
        return bytes4(0);
    }

    function isValidSignature(bytes32 hash, bytes memory signature)
        external
        view
        returns (bytes4 magicValue)
    {
        address signer = hash.recover(signature);
        if (_isValidSigner(signer)) {
            return IERC1271.isValidSignature.selector;
        }
        return bytes4(0);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC165) returns (bool) {
        return
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(IERC6551Account).interfaceId ||
            interfaceId == type(IERC1271).interfaceId;
    }

    function _isValidSigner(address signer) internal view returns (bool) {
        (, address tokenContract, uint256 tokenId) = this.token();
        if (tokenContract.code.length == 0) return false;
        try IERC721(tokenContract).ownerOf(tokenId) returns (address owner) {
            return signer == owner;
        } catch {
            return false;
        }
    }

    // ERC-4337 Support (Simplified)
    function validateUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 missingAccountFunds
    ) external returns (uint256 validationData) {
        require(msg.sender == address(entryPoint), "Only EntryPoint");

        // Verify signature
        bytes32 hash = userOpHash.toEthSignedMessageHash();
        address signer = hash.recover(userOp.signature);

        if (!_isValidSigner(signer)) {
            return 1; // SIG_VALIDATION_FAILED
        }

        // Pay prefund
        if (missingAccountFunds > 0) {
            (bool success, ) = payable(msg.sender).call{value: missingAccountFunds}("");
            (success);
        }

        return 0;
    }
}
