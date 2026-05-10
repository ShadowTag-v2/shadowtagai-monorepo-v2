// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IEntryPoint.sol";

contract MockEntryPoint is IEntryPoint {
    mapping(address => uint256) public deposits;

    function handleOps(
        UserOperation[] calldata /* ops */,
        address payable /* beneficiary */
    ) external returns (uint256) {
        return 0;
    }

    function depositTo(address account) external payable {
        deposits[account] += msg.value;
    }

    function getNonce(address /* sender */, uint192 /* key */) external view returns (uint256 nonce) {
        return 0;
    }

    function depositTo(address account) external payable {}
}
