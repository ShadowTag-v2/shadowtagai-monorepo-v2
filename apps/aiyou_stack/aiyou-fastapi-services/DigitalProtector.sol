// DigitalProtector.sol - The Immortal Governance Layer
pragma solidity ^0.8.0;

contract DigitalProtector {
    address public foundationWallet;
    address[] public councilMembers;
    uint256 public requiredSignatures;

    struct Proposal {
        bytes32 dataHash;
        uint256 signatures;
        bool executed;
        mapping(address => bool) signed;
    }

    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;

    event ProposalCreated(uint256 indexed id, bytes32 dataHash);
    event ProposalExecuted(uint256 indexed id);

    modifier onlyCouncil() {
        bool isMember = false;
        for(uint i=0; i<councilMembers.length; i++) {
            if(councilMembers[i] == msg.sender) isMember = true;
        }
        require(isMember, "Not a council member");
        _;
    }

    constructor(address[] memory _members, uint256 _required) {
        councilMembers = _members;
        requiredSignatures = _required;
    }

    function submitProposal(bytes32 _dataHash) public onlyCouncil {
        uint256 id = proposalCount++;
        Proposal storage p = proposals[id];
        p.dataHash = _dataHash;
        emit ProposalCreated(id, _dataHash);
    }

    function signProposal(uint256 _id) public onlyCouncil {
        Proposal storage p = proposals[_id];
        require(!p.signed[msg.sender], "Already signed");
        p.signed[msg.sender] = true;
        p.signatures++;

        if(p.signatures >= requiredSignatures && !p.executed) {
            p.executed = true;
            emit ProposalExecuted(_id);
            // Logic to execute the transaction/governance action
        }
    }
}
