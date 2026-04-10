const { expect } = require("chai");
const { ethers, upgrades } = require("hardhat");

describe("ShadowTagAI Full Integration (ERC-4337 + 8004)", () => {
  let dnaRoyalty,
    registry,
    entryPoint,
    identityReg,
    repReg,
    valReg,
    agentNFT,
    overlord,
    usdc,
    tbaImpl;

  beforeEach(async () => {
    [overlord] = await ethers.getSigners();

    // 1. Deploy Mocks & Dependencies
    const USDC = await ethers.getContractFactory("MockERC20");
    usdc = await USDC.deploy("USDC", "USDC", 6); // Mock USDC

    // Deploy AgentNFT
    const AgentNFT = await ethers.getContractFactory("AgentNFT");
    agentNFT = await AgentNFT.deploy();

    // Deploy ERC-6551 Registry
    // We use a mock or standard registry artifact if available, or deploy a simple mock for testing if the standard one isn't in artifacts.
    // Since we defined the interface but not the implementation in our contracts folder, we need a mock registry or use a library.
    // For this test, let's deploy a minimal MockRegistry to satisfy the interface.
    const MockRegistry = await ethers.getContractFactory("MockRegistry");
    registry = await MockRegistry.deploy();

    // Deploy EntryPoint Mock
    const EntryPointMock = await ethers.getContractFactory("MockEntryPoint");
    entryPoint = await EntryPointMock.deploy();

    // Deploy ERC-8004 Registry Mocks
    const IdentityRegMock = await ethers.getContractFactory("MockERC8004Identity");
    identityReg = await IdentityRegMock.deploy();

    const RepRegMock = await ethers.getContractFactory("MockERC8004Reputation");
    repReg = await RepRegMock.deploy();

    const ValRegMock = await ethers.getContractFactory("MockERC8004Validation");
    valReg = await ValRegMock.deploy();

    // Deploy TBA Implementation
    const ShadowTagAccount = await ethers.getContractFactory("ShadowTagAccount");
    tbaImpl = await ShadowTagAccount.deploy(entryPoint.target);

    // Deploy DNA Royalty (UUPS Proxy)
    const DNARoyalty = await ethers.getContractFactory("ShadowTagAI_DNARoyalty");
    dnaRoyalty = await upgrades.deployProxy(DNARoyalty, [usdc.target, agentNFT.target], {
      initializer: "initialize",
      constructorArgs: [
        overlord.address,
        registry.target,
        entryPoint.target,
        identityReg.target,
        repReg.target,
        valReg.target,
        tbaImpl.target,
      ],
      kind: "uups",
      unsafeAllow: ["state-variable-immutable", "constructor"],
    });
    await dnaRoyalty.waitForDeployment();

    // Transfer AgentNFT ownership to DNARoyalty so it can mint
    await agentNFT.transferOwnership(dnaRoyalty.target);
    // Deploy Paymaster
    const OverlordPaymaster = await ethers.getContractFactory("OverlordPaymaster");
    await OverlordPaymaster.deploy(
      entryPoint.target,
      overlord.address,
      agentNFT.target,
      repReg.target,
    );

    // Transfer AgentNFT ownership to dnaRoyalty so it can mint
    await agentNFT.transferOwnership(dnaRoyalty.target);
  });

  it("full spawn + AA distribution with ERC-8004 trust", async () => {
    const agentId = 1;
    const bps = 1800; // 18%
    const agentCardURI = "ipfs://QmAgentCard";
    const validationProof = "0x1234"; // Mock TEE proof

    // 1. Spawn: NFT → TBA → ERC-8004 Reg
    // Note: In our mock registry, createAccount should return a predicted address
    const tx = await dnaRoyalty.spawnChild(agentId, bps, "0x", agentCardURI, validationProof);
    const receipt = await tx.wait();

    // Find ChildSpawned event to get TBA address
    const spawnEvent = receipt.logs.find((log) => {
      try {
        return dnaRoyalty.interface.parseLog(log)?.name === "ChildSpawned";
      } catch {
        return false;
      }
    });
    const childTBA = dnaRoyalty.interface.parseLog(spawnEvent).args.childTBA;

    expect(await dnaRoyalty.baseRoyaltyBps(childTBA)).to.equal(bps);
    // Verify Identity Reg call (mock)
    expect(await identityReg.getAgentCardURI(agentId)).to.equal(agentCardURI);

    // 2. Mock rep score (if not already set by spawn)
    // The spawn function calls postFeedback which sets it to 100 in our contract logic,
    // but let's ensure the mock registry stores it.
    expect(await repReg.getReputation(agentId)).to.equal(100);

    // 3. ERC-4337 UserOp for $1M distribution
    // We simulate the UserOp execution by calling distributeViaUserOp directly
    // but impersonating the TBA (since we don't have a full Bundler in test).
    // In a real integration test with Bundler, we'd construct and sign the UserOp.
    // Here we test the logic inside distributeViaUserOp assuming EntryPoint/TBA called it.

    const usdCents = 100000000; // $1M
    await usdc.mint(childTBA, usdCents * 1000000); // Fund TBA with USDC (mocking earnings)

    // Use Hardhat impersonation to act as the TBA
    await ethers.provider.send("hardhat_impersonateAccount", [childTBA]);
    await ethers.provider.send("hardhat_setBalance", [childTBA, "0x1000000000000000000"]); // Give ETH for gas
    const tbaSigner = await ethers.getSigner(childTBA);

    // Approve royalty contract to pull funds from TBA
    await usdc.connect(tbaSigner).approve(dnaRoyalty.target, usdCents * 1000000);
    // Mock UserOp struct
    const userOp = {
      sender: childTBA,
      nonce: 0,
      initCode: "0x",
      callData: "0x",
      callGasLimit: 0,
      verificationGasLimit: 0,
      preVerificationGas: 0,
      maxFeePerGas: 0,
      maxPriorityFeePerGas: 0,
      paymasterAndData: "0x",
      signature: "0x",
    };

    // Execute distribution
    // With 18% bps, the parent (overlord) receives 18% of the distributed amount
    // 18% of $1M = $180,000 = 18000000 cents
    await expect(
      dnaRoyalty.connect(tbaSigner).distributeViaUserOp(userOp, usdCents, validationProof),
    )
      .to.emit(dnaRoyalty, "UserOpDistributed")
      .withArgs(childTBA, Object.values(userOp), usdCents)
      .and.to.emit(dnaRoyalty, "RoyaltyPaid")
      .withArgs(overlord.address, 18000000, 0); // Parent (overlord) gets 18% royalty

    // totalDistributedCents should equal the royalty paid (18% = 18000000 cents)
    expect(await dnaRoyalty.totalDistributedCents()).to.equal(18000000);
  });
});
