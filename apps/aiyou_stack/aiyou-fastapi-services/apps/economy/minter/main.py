import logging

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NFTMinter")

app = FastAPI(title="Antigravity NFT Minter", version="1.0.0")


class MintRequest(BaseModel):
    recipient_address: str
    token_uri: str
    metadata: dict | None = None


class MintResponse(BaseModel):
    status: str
    tx_hash: str
    token_id: int | None = None


def process_minting(request: MintRequest, task_id: str):
    """
    Background task to handle the actual blockchain interaction.
    """
    logger.info(f"[{task_id}] Starting mint for {request.recipient_address}")
    # TODO: Integrate Web3.py for real signing
    # For now, simulate latency and success
    import time

    time.sleep(2)
    logger.info(f"[{task_id}] Mint successful. TxHash: 0xMOCK...")


@app.post("/mint", response_model=MintResponse)
async def mint_nft(request: MintRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to trigger an NFT mint.
    """
    logger.info(f"Received mint request for {request.recipient_address}")

    # Generate a Mock Tx Hash
    mock_tx_hash = f"0x{hash(request.recipient_address + request.token_uri)}"

    # Offload the heavy signing to background
    background_tasks.add_task(process_minting, request, mock_tx_hash)

    return MintResponse(status="queued", tx_hash=mock_tx_hash)


@app.get("/health")
def health_check():
    return {"status": "active", "service": "nft-minter"}
