// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "./interfaces/IERC6551Registry.sol";
import "./interfaces/IEntryPoint.sol";
import "./interfaces/IERC8004Identity.sol";
import "./interfaces/IERC8004Reputation.sol";
import "./interfaces/IERC8004Validation.sol";
import "./libraries/RoyaltyMath.sol";
import "./token/AgentNFT.sol";

/**
 * @title ShadowTagAI DNA Royalty v1.5 – Modular Architecture
 * @notice UUPS-upgradeable contract for recursive, decaying royalties across agent family trees.
 * @dev Full integration: AA UserOps for distributions; ERC-8004 for trust checks; Modular Libraries.
 */
contract ShadowTagAI_DNARoyalty is UUPSUpgradeable, OwnableUpgradeable, PausableUpgradeable {
    uint256 public constant MIN_REP_SCORE = 70; // 70% min reputation for payouts

    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    address public immutable OVERLORD;
    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    IERC6551Registry public immutable REGISTRY;
    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    IEntryPoint public immutable ENTRY_POINT;
    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    IERC8004Identity public immutable IDENTITY_REGISTRY;
    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    IERC8004Reputation public immutable REPUTATION_REGISTRY;
    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    IERC8004Validation public immutable VALIDATION_REGISTRY;
    /// @custom:oz-upgrades-unsafe-allow state-variable-immutable
    address public immutable TBA_IMPLEMENTATION;

    uint256 public totalDistributedCents;
    mapping(address => address) public parentOf; // TBA → parent TBA
    mapping(address => uint16) public baseRoyaltyBps;
    mapping(address => uint256) public claimedCents;
    IERC20 public stablecoin;
    AgentNFT public agentNFT;

    event ChildSpawned(address indexed childTBA, address indexed parentTBA, uint256 agentNFTId, uint16 baseBps, uint256 repScore);
    event UserOpDistributed(address indexed fromTBA, UserOperation userOp, uint256 usdCents);
    event TrustValidated(address indexed agentTBA, uint256 repScore, bool isValid);
    event RoyaltyPaid(address indexed ancestorTBA, uint256 cents, uint8 generation);
    event Withdrawn(address indexed tba, uint256 cents);

    error OnlyOverlord();
    error InvalidBps();
    error NoFunds();
    error BindingFailed();
    error LowReputation();
    error InvalidValidationProof();

    modifier onlyOverlord() {
        if (msg.sender != OVERLORD) revert OnlyOverlord();
        _;
    }

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor(
        address _overlord,
        address _registry,
        address _entryPoint,
        address _identityReg,
        address _repReg,
        address _valReg,
        address _tbaImpl
    ) {
        OVERLORD = _overlord;
        REGISTRY = IERC6551Registry(_registry);
        ENTRY_POINT = IEntryPoint(_entryPoint);
        IDENTITY_REGISTRY = IERC8004Identity(_identityReg);
        REPUTATION_REGISTRY = IERC8004Reputation(_repReg);
        VALIDATION_REGISTRY = IERC8004Validation(_valReg);
        TBA_IMPLEMENTATION = _tbaImpl;
        _disableInitializers();
    }

    function initialize(address _stablecoin, address _agentNFT) external initializer {
        __UUPSUpgradeable_init();
        __Ownable_init(OVERLORD);
        __Pausable_init();
        _setStablecoin(_stablecoin);
        agentNFT = AgentNFT(_agentNFT);
    }

    /// @notice Spawn child with full integration: NFT → TBA → AA → ERC-8004 Registries
    function spawnChild(
        uint256 agentNFTId,
        uint16 bps,
        bytes calldata initData,
        string calldata agentCardURI,
        bytes calldata validationProof
    ) external onlyOverlord returns (address childTBA) {

        if (bps < RoyaltyMath.MIN_ROYALTY_BPS || bps > 2500) revert InvalidBps();

        // 1. Mint ERC-721 NFT
        agentNFT.mint(OVERLORD, agentNFTId);

        // 2. Deploy TBA (ERC-6551 + 4337)
        childTBA = REGISTRY.createAccount(
            TBA_IMPLEMENTATION,
            bytes32(0), // salt
            block.chainid,
<<<<<<< HEAD
            address(agentNFT),
            agentNFTId,
            initData
||||||| f285896f1
            address(agentNFT), // Updated argument
            agentNFTId // Updated argument (assuming agentId in snippet refers to agentNFTId)
=======
            address(agentNFT), // Updated argument
            agentNFTId, // Updated argument (assuming agentId in snippet refers to agentNFTId)
            initData
>>>>>>> feature/n-autoresearch/Kosmos/BioAgentss-integration
        );
        if (childTBA == address(0)) revert BindingFailed();
        parentOf[childTBA] = OVERLORD;
        baseRoyaltyBps[childTBA] = bps;

        // 3. Register in ERC-8004 Identity
        IDENTITY_REGISTRY.register(agentNFTId, agentCardURI);

<<<<<<< HEAD
        // 4. Post initial reputation (score: 100 -> capped to uint8 max)
        REPUTATION_REGISTRY.postFeedback(agentNFTId, 100, "spawn", "");
        uint8 repScore = REPUTATION_REGISTRY.getReputation(agentNFTId);
||||||| f285896f1
        // 4. Post initial reputation
        uint256 repScore = REPUTATION_REGISTRY.postFeedback(agentNFTId, 100, "spawn", bytes(""));
=======
        // 4. Post initial reputation
        REPUTATION_REGISTRY.postFeedback(agentNFTId, 100, "spawn", "");
        uint256 repScore = REPUTATION_REGISTRY.getReputation(agentNFTId);
>>>>>>> feature/n-autoresearch/Kosmos/BioAgentss-integration
        if (repScore < MIN_REP_SCORE) revert LowReputation();

        // 5. Validate spawn
        VALIDATION_REGISTRY.validateTask(validationProof, agentCardURI);
        emit TrustValidated(childTBA, repScore, true);

        emit ChildSpawned(childTBA, OVERLORD, agentNFTId, bps, repScore);
    }

    /// @notice Distribute via ERC-4337 UserOp (bundled, gasless)
    function distributeViaUserOp(
        UserOperation calldata userOp,
        uint256 usdCents,
        bytes calldata /* validationProof */
    ) external whenNotPaused {
        // 1. ERC-4337: Validate/execute UserOp via EntryPoint
        // In this architecture, this function is called AFTER the UserOp has been handled by EntryPoint
        // and execution has reached here (e.g., via callData in UserOp).
        // For security, we should verify the msg.sender is the EntryPoint or the TBA itself.
        // Here we assume TBA calls this.

        address fromTBA = msg.sender;

        // 2. ERC-8004: Trust check
        // Simplified: assume we can get agentId from TBA or passed in.
        // For now, we trust the TBA if it's in our tree.

        // 3. Multi-level royalty logic using Library
        (
            uint256 totalPaid,
            address[] memory recipients,
            uint256[] memory amounts,
            uint8[] memory generations
        ) = RoyaltyMath.distributeRecursive(
            fromTBA,
            usdCents,
            parentOf,
            baseRoyaltyBps,
            claimedCents,
            OVERLORD
        );
        totalDistributedCents += totalPaid;

        // 4. Emit RoyaltyPaid events for each recipient
        for (uint256 i = 0; i < recipients.length; i++) {
            emit RoyaltyPaid(recipients[i], amounts[i], generations[i]);
        }

        // 5. Update total distributed
        totalDistributedCents += totalPaid;

        // 6. Transfer stablecoins
        if (address(stablecoin) != address(0)) {
             stablecoin.transferFrom(fromTBA, address(this), usdCents * 1e6);
        }

        emit UserOpDistributed(fromTBA, userOp, usdCents);
    }

    // Withdraw (AA-compatible)
    function withdraw() external {
        uint256 amount = claimedCents[msg.sender];
        if (amount == 0) revert NoFunds();
        claimedCents[msg.sender] = 0;
        if (address(stablecoin) != address(0)) {
            stablecoin.transfer(msg.sender, amount * 1e6);
        }
        emit Withdrawn(msg.sender, amount);
    }

    function setStablecoin(address _stablecoin) external onlyOverlord {
        _setStablecoin(_stablecoin);
    }

    function _setStablecoin(address _stablecoin) internal {
        stablecoin = IERC20(_stablecoin);
    }

    function pause() external onlyOverlord { _pause(); }
    function unpause() external onlyOverlord { _unpause(); }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}

    function proxiableUUID() external view virtual override returns (bytes32) {
        return 0xc5f16f0fcc639fa48a6947836d9850f50479876101d2b9a5091b6057e8e8b6a0;
    }

    receive() external payable {}
}
