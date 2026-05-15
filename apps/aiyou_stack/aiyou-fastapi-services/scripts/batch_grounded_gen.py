import argparse
import asyncio
import json
import time

import aiohttp

# Configuration
API_URL = "http://localhost:8000/api/v1/grounded-generation/generate"


async def process_prompt(session: aiohttp.ClientSession, prompt: str, model_id: str) -> dict:
    start_time = time.time()
    payload = {"prompt": prompt, "model_id": model_id}
    try:
        async with session.post(API_URL, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                result["status"] = "success"
            else:
                error_text = await response.text()
                result = {"status": "error", "error": error_text, "prompt": prompt}
    except Exception as e:
        result = {"status": "error", "error": str(e), "prompt": prompt}

    result["latency"] = time.time() - start_time
    return result


async def run_batch(
    input_file: str,
    output_file: str,
    model_id: str,
    concurrency: int,
    template: str = None,
):
    # Read input
    try:
        with open(input_file) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        raise SystemExit(1) from e

    # Generate prompts
    prompt_texts = []

    if template:
        # Template mode: input file is a list of variable dictionaries
        if not isinstance(data, list):
            print("Error: When using --template, input file must be a JSON list of objects.")
            raise SystemExit(1)

        print(f"Using template: '{template}'")
        for item in data:
            try:
                # Simple python string formatting
                p = template.format(**item)
                prompt_texts.append(p)
            except KeyError as e:
                print(f"Warning: Missing key {e} in item {item}. Skipping.")
            except Exception as e:
                print(f"Warning: Error formatting item {item}: {e}. Skipping.")
    else:
        # Direct mode: input file is list of strings or objects with 'text'/'prompt'
        if isinstance(data, list):
            prompts = data
        elif isinstance(data, dict) and "prompts" in data:
            prompts = data["prompts"]
        else:
            print(
                "Error: Input file must be a JSON list of strings/objects, or a dict with a 'prompts' key.",
            )
            raise SystemExit(1)

        for p in prompts:
            if isinstance(p, str):
                prompt_texts.append(p)
            elif isinstance(p, dict) and "text" in p:
                prompt_texts.append(p["text"])
            elif isinstance(p, dict) and "prompt" in p:
                prompt_texts.append(p["prompt"])
            else:
                print(f"Skipping invalid prompt format: {p}")

    if not prompt_texts:
        print("No valid prompts found. Exiting.")
        raise SystemExit(0)

    print(
        f"Loaded {len(prompt_texts)} prompts. Starting batch processing with concurrency {concurrency}...",
    )

    results = []
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [process_prompt(session, p, model_id) for p in prompt_texts]
        for i, future in enumerate(asyncio.as_completed(tasks)):
            result = await future
            results.append(result)
            print(
                f"[{i + 1}/{len(prompt_texts)}] Processed: {result.get('status')} ({result.get('latency', 0):.2f}s)",
            )

    # Save results
    try:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run batch grounded generation.")
    parser.add_argument(
        "input_file",
        help="Path to JSON input file containing prompts or variables.",
    )
    parser.add_argument(
        "--output_file",
        default="batch_results.json",
        help="Path to output JSON file.",
    )
    parser.add_argument(
        "--model_id", default="gemini-3.1-flash-lite-preview", help="Model ID to use."
    )
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent requests.")
    parser.add_argument(
        "--template",
        help="Prompt template string (e.g., 'Tell me about {topic}'). If provided, input_file should be a list of dicts.",
    )

    args = parser.parse_args()

    asyncio.run(
        run_batch(
            args.input_file, args.output_file, args.model_id, args.concurrency, args.template
        ),
    )
