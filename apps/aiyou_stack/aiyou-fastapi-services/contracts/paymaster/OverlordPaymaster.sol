// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IEntryPoint.sol";
import "../interfaces/IERC8004Reputation.sol";
import "../interfaces/IERC6551Account.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

abstract contract BasePaymaster is Ownable {
    IEntryPoint public immutable entryPoint;

    constructor(IEntryPoint _entryPoint) Ownable(msg.sender) {
        entryPoint = _entryPoint;
    }

    function validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) external returns (bytes memory context, uint256 validationData) {
        require(msg.sender == address(entryPoint), "Sender not EntryPoint");
        return _validatePaymasterUserOp(userOp, userOpHash, maxCost);
    }

    function _validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 userOpHash,
        uint256 maxCost
    ) internal virtual returns (bytes memory context, uint256 validationData);

    function postOp(
        uint8 mode,
        bytes calldata context,
        uint256 actualGasCost
    ) external virtual {}

    function deposit() public payable {
        entryPoint.depositTo{value: msg.value}(address(this));
    }

    function withdrawTo(address payable withdrawAddress, uint256 amount) public onlyOwner {
        // entryPoint.withdrawTo(withdrawAddress, amount);
        // Note: IEntryPoint interface might need withdrawTo, but for now we rely on deposit
    }
}

contract OverlordPaymaster is BasePaymaster {
    address public immutable OVERLORD;
    IERC8004Reputation public immutable REPUTATION;
    address public immutable AGENT_NFT;

    constructor(
        IEntryPoint _entryPoint,
        address _overlord,
        address _reputation,
        address _agentNft
    ) BasePaymaster(_entryPoint) {
        OVERLORD = _overlord;
        REPUTATION = IERC8004Reputation(_reputation);
        AGENT_NFT = _agentNft;
    }

    function _validatePaymasterUserOp(
        UserOperation calldata userOp,
        bytes32 /*userOpHash*/,
        uint256 /*maxCost*/
    ) internal view override returns (bytes memory context, uint256 validationData) {
        address sender = userOp.sender;

        // Free gas IF: sender is a ShadowTagAI TBA AND has >= 70 rep
        if (isTrustedAgent(sender)) {
            return ("", 0); // 100% sponsored, signature valid, valid until 0 (forever)
        }

        // Otherwise: reject (return 1 for sig failure)
        return ("", 1);
    }

    function isTrustedAgent(address tba) public view returns (bool) {
        // 1. Check if TBA is valid (this is a simplification, ideally we check registry)
        try IERC6551Account(payable(tba)).token() returns (uint256, address tokenContract, uint256 tokenId) {
            if (tokenContract != AGENT_NFT) return false;

            // 2. Check reputation
            if (address(REPUTATION) != address(0)) {
                return REPUTATION.getReputation(tokenId) >= 70;
            }
            return true; // If no reputation registry, assume trusted for now (or false, depending on policy)
        } catch {
            return false;
        }
    }
}
