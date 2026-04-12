import json
import random
import time
import urllib.request


def generate_local_image(prompt: str) -> str:
    """Sends a generation request to the local ComfyUI instance and returns the image URL."""

    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": random.randint(1, 1000000000),
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
        },
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "text, watermark, bad anatomy, blurry", "clip": ["4", 1]},
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "ShadowTag-v2_agent", "images": ["8", 0]},
        },
    }

    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            prompt_id = result.get("prompt_id")

        # Poll the ComfyUI history endpoint to wait for the generation to finish
        for _ in range(30):  # Wait up to 60 seconds
            time.sleep(2)
            hist_req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
            with urllib.request.urlopen(hist_req) as hist_res:
                history = json.loads(hist_res.read())
                if prompt_id in history:
                    # Generation is done! Extract the filename.
                    outputs = history[prompt_id].get("outputs", {})
                    for _node_id, node_output in outputs.items():
                        if "images" in node_output:
                            filename = node_output["images"][0]["filename"]
                            # Return the exact relative URL we exposed in the backend
                            return f"Image generated successfully!\n\n![Generated Image](/images/{filename})"

        return "Image generation timed out or is taking too long."
    except Exception as e:
        return f"Failed to connect to ComfyUI. Is the server running on http://127.0.0.1:8188? Error: {str(e)}"


def search_workspace_knowledge(workspace_id: int, query: str) -> str:
    """Delegates to LanceDB."""
    try:
        from vector_db import search_workspace_knowledge as vdb_search

        return vdb_search(workspace_id, query)
    except ImportError:
        return "Vector database module not initialized."


COMFYUI_IMAGE_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_local_image",
        "description": "Generates a high-quality image locally using ComfyUI. Use this tool WHENEVER the user asks you to create, draw, generate, or render a picture/image. Pass their descriptive request directly into the prompt parameter.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "A highly descriptive, comma-separated list of visual keywords to generate the image (e.g., 'cyberpunk city, neon lights, 4k, masterpiece, highly detailed').",
                }
            },
            "required": ["prompt"],
        },
    },
}

WORKSPACE_SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_workspace_knowledge",
        "description": "Searches the private workspace knowledge base. Use this FIRST whenever the user asks about proprietary data, uploaded documents, internal company policies, or specific workspace context.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The semantic search query to find relevant documents.",
                }
            },
            "required": ["query"],
        },
    },
}
