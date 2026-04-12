"""
TruthLedger - Hashes analysis data and mints ERC-721 Verification tokens.
"""

import hashlib
import json
import os

from web3 import Web3


class TruthLedger:
    def __init__(self):
        provider_url = os.getenv("WEB3_PROVIDER_URL", "https://rpc-mumbai.maticvigil.com")
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.private_key = os.getenv("WALLET_PRIVATE_KEY")

        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
        else:
            self.account = None  # Read-only mode

    def hash_analysis(self, analysis_data: dict) -> str:
        """SHA-256 Fingerprint of the AI Analysis."""
        payload = json.dumps(analysis_data, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def upload_metadata_to_ipfs(self, analysis_data: dict, video_hash: str) -> str:
        """Stub for Pinata/IPFS upload."""
        print(f"///▞ STORAGE :: Pinned metadata for {video_hash[:8]}...")
        return "ipfs://QmStubHash123456789"

    def mint_verification_nft(self, user_wallet: str, analysis_data: dict):
        if not self.account:
            return {"status": "skipped", "reason": "No wallet key configured"}

        content_hash = self.hash_analysis(analysis_data)
        token_uri = self.upload_metadata_to_ipfs(analysis_data, content_hash)

        # Transaction logic (Stubbed for safety without ABI)
        print(f"///▞ BLOCKCHAIN :: Minted Verification NFT for {user_wallet}")

        return {"tx_hash": "0xMockTransactionHash", "token_uri": token_uri}
