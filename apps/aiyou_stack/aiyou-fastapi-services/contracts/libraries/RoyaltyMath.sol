// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

library RoyaltyMath {
    uint16 public constant MIN_ROYALTY_BPS = 50; // 0.5%

    event RoyaltyPaid(address indexed ancestorTBA, uint256 cents, uint8 generation);

    function distributeRecursive(
        address from,
        uint256 usdCents,
        mapping(address => address) storage parentOf,
        mapping(address => uint16) storage baseRoyaltyBps,
        mapping(address => uint256) storage claimedCents,
        address overlord
    ) internal returns (
        uint256 totalPaid,
        address[] memory recipients,
        uint256[] memory amounts,
        uint8[] memory generations
    ) {
        address current = from;
        uint256 remaining = usdCents;
        totalPaid = 0;

        // Pre-allocate arrays (max 10 levels)
        recipients = new address[](10);
        amounts = new uint256[](10);
        generations = new uint8[](10);
        uint256 count = 0;

        // Safety loop to prevent infinite recursion (max depth 10)
        for (uint256 i = 0; i < 10; i++) {
            // If current is Overlord, it gets everything remaining
            if (current == overlord) {
                 claimedCents[overlord] += remaining;
                 emit RoyaltyPaid(overlord, remaining, uint8(i));
                 totalPaid += remaining;
                 break;
            }

            address parent = parentOf[current];

            // If no parent, stop
            if (parent == address(0)) {
||||||| f285896f1
            // If no parent or we reached the Overlord, stop
            if (parent == address(0) || parent == overlord) {
                break;
            }

            uint16 bps = baseRoyaltyBps[current];
            if (bps > 0) {
                uint256 cut = (remaining * bps) / 10000;
                if (cut > 0) {
                    claimedCents[parent] += cut;
                    recipients[count] = parent;
                    amounts[count] = cut;
                    generations[count] = uint8(i);
                    count++;
                    totalPaid += cut;
                    remaining -= cut;
                }
            }

            // Check AFTER distributing - if parent is overlord, we're done
            if (parent == overlord) {
                break;
||||||| f285896f1
            if (bps == 0) {
                current = parent;
                continue;
            }

            uint256 cut = (remaining * bps) / 10000;
            if (cut > 0) {
                claimedCents[parent] += cut;
                totalPaid += cut;
                remaining -= cut;
            }

            current = parent;
        }

        // Resize arrays to actual count using assembly
        assembly {
            mstore(recipients, count)
            mstore(amounts, count)
            mstore(generations, count)
        }
    }
}
