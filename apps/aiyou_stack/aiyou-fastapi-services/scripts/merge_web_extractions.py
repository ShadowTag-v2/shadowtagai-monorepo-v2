import argparse
import json
import logging
from pathlib import Path
from typing import Any

# Configure basic logging to provide clear feedback during execution
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DEFAULT_EXCLUDE_KEYWORDS = [
    "personal",
    "family",
    "medical",
    "password",
    "secret",
    "private",
    "bank",
    "credit card",
    "ssn",
    "social security",
    "confidential",
]


def find_extraction_files(input_dir: Path, pattern: str) -> list[Path]:
    """Finds all files in the input directory matching the given pattern."""
    logging.info(f"Searching for files matching '{pattern}' in '{input_dir}'...")
    if not input_dir.is_dir():
        logging.error(f"Input directory not found: {input_dir}")
        return []
    files = sorted(list(input_dir.glob(pattern)))
    logging.info(f"Found {len(files)} files to merge.")
    if not files:
        logging.warning("No extraction files found. The output file will be empty.")
    return files


def extract_conversations_from_data(data: Any, filename: str) -> list[dict[str, Any]]:
    """Intelligently extracts conversation lists from various extraction formats.
    """
    conversations = []

    # Case 1: Direct list (Legacy/Simple format)
    if isinstance(data, list):
        logging.info(f"File '{filename}' is a direct list. Assuming conversations.")
        return data

    if not isinstance(data, dict):
        logging.warning(f"File '{filename}' has unknown structure (not list or dict). Skipping.")
        return []

    # Case 2: ChatGPT Extractor (v1.0)
    # Structure: { data: { api_conversations: [], dom_elements: [] } }
    if "data" in data and "api_conversations" in data["data"]:
        api_convs = data["data"].get("api_conversations", [])
        dom_convs = data["data"].get("dom_elements", [])
        logging.info(f"File '{filename}' recognized as ChatGPT extraction.")
        logging.info(f"  - API conversations: {len(api_convs)}")
        logging.info(f"  - DOM elements: {len(dom_convs)}")

        # tag source
        for c in api_convs:
            c["_source"] = "chatgpt_api"
        for c in dom_convs:
            c["_source"] = "chatgpt_dom"

        conversations.extend(api_convs)
        conversations.extend(dom_convs)
        return conversations

    # Case 3: Claude Extractor (v1.0)
    # Structure: { sources: { api: { conversations: [] }, dom: { data: [] }, ... } }
    if "sources" in data:
        logging.info(f"File '{filename}' recognized as Claude extraction.")
        sources = data["sources"]

        # API Data (Best quality)
        if "api" in sources and "conversations" in sources["api"]:
            # Some API data might be wrapped in another object or direct list
            api_data = sources["api"].get("conversations", [])
            if isinstance(api_data, list):
                logging.info(f"  - API conversations: {len(api_data)}")
                for c in api_data:
                    c["_source"] = "claude_api"
                conversations.extend(api_data)

        # DOM Data (Fallback)
        if "dom" in sources and "data" in sources["dom"]:
            dom_data = sources["dom"].get("data", [])
            logging.info(f"  - DOM conversations: {len(dom_data)}")
            for c in dom_data:
                c["_source"] = "claude_dom"
            conversations.extend(dom_data)

        # LocalStorage (Often messy, but includes keys)
        if "localStorage" in sources and "data" in sources["localStorage"]:
            ls_data = sources["localStorage"].get("data", {})
            # We treat each key as a potential record
            if isinstance(ls_data, dict):
                valid_records = []
                for k, v in ls_data.items():
                    if isinstance(v, (dict, list)):  # Only take structured data
                        record = {"key": k, "content": v, "_source": "claude_localstorage"}
                        valid_records.append(record)
                logging.info(f"  - LocalStorage records: {len(valid_records)}")
                conversations.extend(valid_records)

        return conversations

    # Case 4: Generic Dict - try to find any list values
    logging.warning(
        f"File '{filename}' structure unknown. Searching for lists within top-level keys.",
    )
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            logging.info(f"  - Found list in key '{key}': {len(value)} items")
            conversations.extend(value)

    return conversations


def filter_conversations(
    conversations: list[dict[str, Any]], exclude_keywords: list[str],
) -> list[dict[str, Any]]:
    """Filters out conversations that contain any of the exclusion keywords.
    """
    if not exclude_keywords:
        return conversations

    filtered = []
    skipped_count = 0

    logging.info(f"Filtering with {len(exclude_keywords)} keywords: {exclude_keywords}")

    for conv in conversations:
        # Flatten conversation to string for searching
        text_content = json.dumps(conv, ensure_ascii=False).lower()

        contains_keyword = False
        for keyword in exclude_keywords:
            if keyword.lower() in text_content:
                contains_keyword = True
                break

        if contains_keyword:
            skipped_count += 1
            continue

        filtered.append(conv)

    logging.info(
        f"Privacy Filter: Kept {len(filtered)}/{len(conversations)} conversations. (Excluded {skipped_count})",
    )
    return filtered


def merge_json_files(
    file_paths: list[Path], exclude_keywords: list[str] = [],
) -> list[dict[str, Any]]:
    """Merges content from a list of JSON files.
    """
    merged_data = []
    for file_path in file_paths:
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                file_conversations = extract_conversations_from_data(data, file_path.name)
                merged_data.extend(file_conversations)
        except json.JSONDecodeError:
            logging.exception(f"Error decoding JSON from '{file_path}'. Skipping this file.")
        except Exception as e:
            logging.exception(f"An unexpected error occurred with file '{file_path}': {e}")

    # Apply filtering
    if exclude_keywords:
        return filter_conversations(merged_data, exclude_keywords)

    return merged_data


def save_merged_data(output_file: Path, data: list[dict[str, Any]]):
    """Saves the merged data to a JSON file with pretty-printing."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved {len(data)} merged records to '{output_file}'.")
    except Exception as e:
        logging.exception(f"Failed to save merged data to '{output_file}': {e}")


def main():
    """Main function to orchestrate the file merging process."""
    parser = argparse.ArgumentParser(
        description="Merge multiple web extraction JSON files into a single file.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing the extraction files to merge.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        required=True,
        help="Path to the output file for the merged data.",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern to find input files (e.g., 'extraction_*.json').",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="Additional keywords to exclude (space separated). e.g. --exclude secret confidential",
    )
    parser.add_argument(
        "--no-defaults",
        action="store_true",
        help="Disable the default exclusion list (personal, family, medical, etc.)",
    )

    args = parser.parse_args()

    # Build exclusion list
    exclude_keywords = []
    if not args.no_defaults:
        exclude_keywords.extend(DEFAULT_EXCLUDE_KEYWORDS)

    if args.exclude:
        exclude_keywords.extend(args.exclude)

    extraction_files = find_extraction_files(args.input_dir, args.pattern)

    if not extraction_files:
        logging.warning("No files found to merge.")
        # We don't overwrite with empty unless explicitly desired, to prevent dataloss?
        # But per original logic, it might be expected.
        # Let's write an empty list if that's what was requested.
        save_merged_data(args.output_file, [])
        return

    merged_data = merge_json_files(extraction_files, exclude_keywords)

    # Remove duplicates based on ID if present
    unique_data = []
    seen_ids = set()
    for item in merged_data:
        # Try to find a stable ID
        item_id = item.get("id") or item.get("uuid") or item.get("conversation_id")
        if item_id:
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)
        unique_data.append(item)

    if len(unique_data) < len(merged_data):
        logging.info(
            f"Removed {len(merged_data) - len(unique_data)} duplicate records based on ID.",
        )

    save_merged_data(args.output_file, unique_data)


if __name__ == "__main__":
    main()
