"""
Bedrock InvokeModel Demo
=========================
This function demonstrates that InvokeModel requires MODEL-SPECIFIC request schemas.
The same prompt must be formatted differently for each model provider.

Key takeaway: You must know the exact JSON structure each model expects.
"""

import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime")

PROMPT = "Explain what cloud computing is in exactly two sentences."


def invoke_claude(prompt):
    """
    InvokeModel with Anthropic Claude.
    Claude expects: {"anthropic_version", "messages", "max_tokens"}
    """
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 200,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )

    response_body = json.loads(response["body"].read())

    # Claude-specific response parsing
    return {
        "model": "Claude Haiku 4.5",
        "api": "InvokeModel",
        "request_schema_note": "Uses anthropic_version, messages array with role/content, max_tokens",
        "output": response_body["content"][0]["text"],
        "usage": {
            "input_tokens": response_body["usage"]["input_tokens"],
            "output_tokens": response_body["usage"]["output_tokens"]
        }
    }


def invoke_llama(prompt):
    """
    InvokeModel with Meta Llama.
    Llama expects: {"prompt", "max_gen_len", "temperature"}
    Completely different schema from Claude!
    """
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 200,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model(
        modelId="meta.llama3-8b-instruct-v1:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )

    response_body = json.loads(response["body"].read())

    # Llama-specific response parsing
    return {
        "model": "Llama 3 8B Instruct",
        "api": "InvokeModel",
        "request_schema_note": "Uses prompt (string), max_gen_len, temperature — completely different from Claude",
        "output": response_body["generation"],
        "usage": {
            "prompt_token_count": response_body.get("prompt_token_count"),
            "generation_token_count": response_body.get("generation_token_count")
        }
    }


def invoke_claude_streaming(prompt):
    """
    InvokeModelWithResponseStream with Claude.
    Same request schema as InvokeModel, but response comes in chunks.
    """
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 200,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )

    # Collect streamed chunks
    full_response = ""
    chunk_count = 0
    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            full_response += chunk["delta"]["text"]
            chunk_count += 1

    return {
        "model": "Claude Haiku 4.5",
        "api": "InvokeModelWithResponseStream",
        "note": "Same request schema as InvokeModel, but response arrives in chunks",
        "output": full_response,
        "chunks_received": chunk_count
    }


def lambda_handler(event, context):
    """
    Demonstrates that InvokeModel requires different request/response schemas per model.
    """
    results = {
        "tutorial": "InvokeModel API Demo",
        "key_lesson": (
            "InvokeModel requires you to format requests differently for each model. "
            "Claude uses 'messages' array with 'anthropic_version'. "
            "Llama uses a flat 'prompt' string with 'max_gen_len'. "
            "You must also parse responses differently for each model."
        ),
        "prompt_used": PROMPT,
        "results": []
    }

    # 1. InvokeModel with Claude
    try:
        results["results"].append(invoke_claude(PROMPT))
    except Exception as e:
        results["results"].append({"model": "Claude Haiku 4.5", "error": str(e)})

    # 2. InvokeModel with Llama (different schema!)
    try:
        results["results"].append(invoke_llama(PROMPT))
    except Exception as e:
        results["results"].append({"model": "Llama 3 8B Instruct", "error": str(e)})

    # 3. InvokeModelWithResponseStream with Claude
    try:
        results["results"].append(invoke_claude_streaming(PROMPT))
    except Exception as e:
        results["results"].append({"model": "Claude Haiku 4.5 (streaming)", "error": str(e)})

    return results
