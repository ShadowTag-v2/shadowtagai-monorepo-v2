# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

import argparse
import glob
import json
import logging
import os
from dataclasses import dataclass
from typing import Any

import google.generativeai as genai

# Setup logging and configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    example_id: str
    prompt: str
    generated_answer: str
    gold_answer: str
    is_correct: bool
    score: float


class FactsBenchmark:
    def __init__(self, model_name: str, data_dir: str):
        self.model_name = model_name
        self.data_dir = data_dir
        self.model = genai.GenerativeModel(model_name)

    def load_data(self) -> list[dict[str, Any]]:
        files = glob.glob(os.path.join(self.data_dir, "*.jsonl"))
        if not files:
            logger.warning(f"No .jsonl files found in {self.data_dir}")
            return []

        data = []
        for fpath in files:
            with open(fpath) as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        return data

    def run(self) -> list[BenchmarkResult]:
        raise NotImplementedError

    def evaluate(self, generated: str, gold: str) -> float:
        # Simple exact match or F1 - can be overridden
        return 1.0 if generated.strip().lower() == gold.strip().lower() else 0.0


class ParametricBenchmark(FactsBenchmark):
    def run(self) -> list[BenchmarkResult]:
        data = self.load_data()
        results = []
        for item in data:
            prompt = item.get("question", "")
            if not prompt:
                continue

            try:
                response = self.model.generate_content(prompt)
                answer = response.text
            except Exception as e:
                logger.error(f"Error generating content: {e}")
                answer = ""

            gold = item.get("answer", "")
            score = self.evaluate(answer, gold)

            results.append(
                BenchmarkResult(
                    example_id=item.get("id", "unknown"),
                    prompt=prompt,
                    generated_answer=answer,
                    gold_answer=gold,
                    is_correct=score > 0.5,
                    score=score,
                ),
            )
            logger.info(f"Processed {item.get('id')}: Score={score}")

        return results


class GroundingBenchmark(FactsBenchmark):
    def run(self) -> list[BenchmarkResult]:
        data = self.load_data()
        results = []
        for item in data:
            context = item.get("context", "")
            question = item.get("question", "")
            prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"

            try:
                response = self.model.generate_content(prompt)
                answer = response.text
            except Exception as e:
                logger.error(f"Error generating content: {e}")
                answer = ""

            gold = item.get("answer", "")
            score = self.evaluate(answer, gold)

            results.append(
                BenchmarkResult(
                    example_id=item.get("id", "unknown"),
                    prompt=prompt,
                    generated_answer=answer,
                    gold_answer=gold,
                    is_correct=score > 0.5,
                    score=score,
                ),
            )
            logger.info(f"Processed {item.get('id')}: Score={score}")

        return results


class SearchBenchmark(FactsBenchmark):
    # Requires tool use implementation
    pass


class MultimodalBenchmark(FactsBenchmark):
    # Requires image handling
    pass


def main():
    parser = argparse.ArgumentParser(description="Run FACTS Benchmark Suite")
    parser.add_argument(
        "--benchmark",
        type=str,
        required=True,
        choices=["parametric", "grounding", "search", "multimodal", "all"],
    )
    parser.add_argument("--model", type=str, default="gemini-pro")
    parser.add_argument("--data_root", type=str, default="benchmarks/facts/data")
    parser.add_argument("--api_key", type=str, help="Google API Key")

    args = parser.parse_args()

    if args.api_key:
        genai.configure(api_key=args.api_key)
    elif not os.environ.get("GOOGLE_API_KEY"):
        logger.error("No API key provided. Set GOOGLE_API_KEY env var or use --api_key")
        return

    benchmarks_to_run = ["parametric", "grounding"] if args.benchmark == "all" else [args.benchmark]

    for name in benchmarks_to_run:
        logger.info(f"Starting {name} benchmark...")
        data_dir = os.path.join(args.data_root, name)

        if name == "parametric":
            benchmark = ParametricBenchmark(args.model, data_dir)
        elif name == "grounding":
            benchmark = GroundingBenchmark(args.model, data_dir)
        else:
            logger.warning(f"Benchmark {name} not yet fully implemented.")
            continue

        results = benchmark.run()

        # Calculate aggregate metrics
        total = len(results)
        if total > 0:
            avg_score = sum(r.score for r in results) / total
            logger.info(
                f"Benchmark {name} Complete. Average Score: {avg_score:.2f} ({total} examples)",
            )

            # Save detailed results
            output_file = f"facts_results_{name}_{args.model}.json"
            with open(output_file, "w") as f:
                json.dump([vars(r) for r in results], f, indent=2)
            logger.info(f"Results saved to {output_file}")
        else:
            logger.warning(f"No results for {name} (check data directory)")


if __name__ == "__main__":
    main()
