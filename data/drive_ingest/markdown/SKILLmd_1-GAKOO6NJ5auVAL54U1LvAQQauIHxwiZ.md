# Blockchain Development Guidelines - Solidity Smart Contracts

**Version**: 1.0
**Last Updated**: 2025-11-22
**Scope**: Solidity development for ERC-6551, ERC-4337, ERC-8004 patterns

## Overview

This skill enforces security-first Solidity development for ShadowTagAI's smart contract system. Focus on **Token-Bound Accounts (TBA)**, **Account Abstraction (AA)**, and **Reputation/Identity** standards.

## Core Patterns

### ERC-6551 Token-Bound Accounts
```solidity
// Every NFT gets its own smart contract wallet
contract ShadowTagAccount is IERC6551Account {
    function executeCall(
        address to,
        uint256 value,
        bytes calldata data
    ) external payable returns (bytes memory) {
        require(msg.sender == owner(), "Not authorized");
        (bool success, bytes memory result) = to.call{value: value}(data);
        require(success, "Call failed");
        return result;
    }
}
```

### ERC-4337 Account Abstraction
```solidity
// Gasless transactions via paymasters
function validateUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 missingAccountFunds
) external returns (uint256 validationData) {
    _requireFromEntryPoint();
    // Validate signature, nonce, etc.
    return 0; // Success
}
```

### ERC-8004 Reputation/Identity
```solidity
// On-chain reputation tracking
function updateReputation(
    address account,
    int256 delta,
    string calldata reason
) external onlyAuthorized {
    reputation[account] += delta;
    emit ReputationUpdated(account, reputation[account], reason);
}
```

## Security Checklist

### 1. Reentrancy Protection
```solidity
// ✅ Good: Checks-Effects-Interactions (CEI) pattern
function withdraw(uint256 amount) external nonReentrant {
    require(balances[msg.sender] >= amount, "Insufficient balance");
    balances[msg.sender] -= amount;  // Effect BEFORE interaction
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}
```

### 2. Access Control
```solidity
// Use OpenZeppelin's AccessControl
import "@openzeppelin/contracts/access/AccessControl.sol";

contract MyContract is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    modifier onlyAdmin() {
        require(hasRole(ADMIN_ROLE, msg.sender), "Not admin");
        _;
    }
}
```

### 3. Integer Overflow (Solidity 0.8+)
```solidity
// ✅ Solidity 0.8+ has built-in overflow checks
uint256 total = a + b;  // Reverts on overflow

// For unchecked math (gas optimization):
unchecked {
    counter++;  // Only if you're SURE it won't overflow
}
```

### 4. Gas Optimization
```solidity
// ✅ Pack storage variables
struct Agent {
    uint128 id;        // 16 bytes
    uint64 timestamp;  // 8 bytes
    uint32 level;      // 4 bytes
    uint32 reputation; // 4 bytes
    // Total: 32 bytes (1 storage slot)
}

// ✅ Use calldata for read-only arrays
function process(uint256[] calldata ids) external {
    // calldata is cheaper than memory
}

// ✅ Cache storage reads
uint256 cachedValue = storageVariable;  // Read once
for (uint i = 0; i < 10; i++) {
    doSomething(cachedValue);  // Use cached value
}
```

## Royalty Distribution Pattern

From `RoyaltyMath.sol`:
```solidity
function calculateRoyalties(
    uint256 amount,
    uint8 generation
) public pure returns (RoyaltyDistribution memory) {
    uint256 parentShare = (amount * 18) / 100;    // 18%
    uint256 grandparentShare = generation >= 2 ? (amount * 8) / 100 : 0;
    uint256 greatGrandparentShare = generation >= 3 ? (amount * 5) / 100 : 0;

    uint256 childShare = amount - parentShare - grandparentShare - greatGrandparentShare;

    return RoyaltyDistribution({
        child: childShare,
        parent: parentShare,
        grandparent: grandparentShare,
        greatGrandparent: greatGrandparentShare
    });
}
```

## Testing Requirements

```solidity
// Use Foundry for testing
contract ShadowTagAccountTest is Test {
    function testExecuteCall() public {
        // Setup
        ShadowTagAccount account = new ShadowTagAccount();

        // Execute
        bytes memory result = account.executeCall(
            address(target),
            0,
            abi.encodeWithSignature("someFunction()")
        );

        // Assert
        assertEq(result, expectedResult);
    }

    function testReentrancyProtection() public {
        // Attempt reentrancy attack
        vm.expectRevert("ReentrancyGuard: reentrant call");
        attacker.attack();
    }
}
```

## Resources

- [security.md](resources/security.md) - Comprehensive security patterns
- [erc6551.md](resources/erc6551.md) - TBA implementation details
- [erc4337.md](resources/erc4337.md) - Account abstraction patterns
- [gas-optimization.md](resources/gas-optimization.md) - Gas saving techniques
- [testing.md](resources/testing.md) - Foundry test patterns

## Enforcement

This skill auto-activates when:
- Keywords: `solidity`, `erc`, `smart contract`, `blockchain`, `pragma`, `payable`
- File paths: `contracts/**/*.sol`
- Intent: Smart contract development, security audits
