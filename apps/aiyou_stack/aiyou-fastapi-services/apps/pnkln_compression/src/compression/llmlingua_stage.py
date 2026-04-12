import logging
import os
import time
from typing import Any

import torch
from llmlingua import PromptCompressor

# Logging setup for monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMLingua")


class PnklnCompressor:
    _instance = None

    def __init__(self, device_map: str = "cpu"):
        self.device = device_map
        self.compressor = None

        # CRITICAL: Prevent CPU thrashing in K8s containers
        if device_map == "cpu":
            torch.set_num_threads(2)
            os.environ["OMP_NUM_THREADS"] = "1"
            os.environ["MKL_NUM_THREADS"] = "1"

        try:
            logger.info(f"Loading XLM-RoBERTa on {device_map}...")
            self.compressor = PromptCompressor(
                model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
                use_llmlingua2=True,
                device_map=device_map,
            )
            self._warmup()
        except Exception as e:
            logger.error(f"Model load failed: {e}")
            raise e

    def _warmup(self):
        """Prevents first-request latency spikes"""
        try:
            _ = self.compressor.compress_prompt("warmup sequence", rate=0.5, force_tokens=["\n"])
            logger.info("Warmup complete.")
        except Exception:
            pass

    def compress_for_judge6(self, atp_extract: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()

        # Construct semantic prompt from extraction
        prompt = (
            f"RISK:{atp_extract['risk_level']} ({atp_extract['risk_probability']}/{atp_extract['risk_severity']})\n"
            f"ACTION:{atp_extract['action_requested']} ENTITY:{atp_extract['entity_type']}\n"
            f"VIOLATIONS:{','.join(atp_extract['violations']) or 'None'}\n"
            f"POLICIES:{','.join(atp_extract['policy_refs']) or 'None'}\n"
            f"CONTEXT:{atp_extract['compressed_context']}"
        )

        # Guardrails: Tokens we CANNOT lose
        force_tokens = ["ALLOW", "DENY", "RISK", "VIOLATIONS", "\n", ":", ".", "EH", "HIGH"]

        try:
            # Target 30% retention of the already filtered context
            result = self.compressor.compress_prompt(prompt, rate=0.3, force_tokens=force_tokens)
            elapsed = (time.perf_counter() - start) * 1000

            return {
                "compressed_text": result["compressed_prompt"],
                "latency_ms": elapsed,
                "sla_met": elapsed < 35,
            }
        except Exception as e:
            logger.error(f"Compression failure: {e}")
            # Fallback to truncated text on failure to preserve availability
            return {"compressed_text": prompt[:500], "latency_ms": 0, "sla_met": False}


def get_compressor(device: str = "cpu") -> PnklnCompressor:
    if PnklnCompressor._instance is None:
        PnklnCompressor._instance = PnklnCompressor(device_map=device)
    return PnklnCompressor._instance
