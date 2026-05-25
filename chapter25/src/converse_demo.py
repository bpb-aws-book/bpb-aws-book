"""
Bedrock Converse API Demo
==========================
This function demonstrates that the Converse API uses a UNIFIED schema
across all models. The same code works for Claude, Llama, and others.

Key takeaway: Write once, use with any model — just change the modelId.
"""

import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime")

PROMPT = "Explain what cloud computing is in exactly two sentences."


def converse_with_model(model_id, model_name, prompt):
    """
    Converse API — identical code structure regardless of model.
    The same request format works for Claude, Llama, Titan, Mistral, etc.
    """
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 200,
            "temperature": 0.5
        }
    )

    # Unified response format — same parsing for ALL models
    output_text = response["output"]["message"]["content"][0]["text"]
    usage = response["usage"]

    return {
        "model": model_name,
        "model_id": model_id,
        "api": "Converse",
        "request_schema_note": "Identical request structure for both models — only modelId changes",
        "output": output_text,
        "usage": {
            "inputTokens": usage["inputTokens"],
            "outputTokens": usage["outputTokens"]
        },
        "stop_reason": response["stopReason"]
    }


def converse_stream_with_model(model_id, model_name, prompt):
    """
    ConverseStream — same unified schema, but response arrives in chunks.
    Useful for real-time UIs where you want to display text as it generates.
    """
    response = bedrock_runtime.converse_stream(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 200,
            "temperature": 0.5
        }
    )

    # Collect streamed chunks
    full_response = ""
    chunk_count = 0
    usage = {}

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            full_response += event["contentBlockDelta"]["delta"]["text"]
            chunk_count += 1
        elif "metadata" in event:
            usage = event["metadata"].get("usage", {})

    return {
        "model": model_name,
        "model_id": model_id,
        "api": "ConverseStream",
        "note": "Same unified schema as Converse, but response streams in chunks",
        "output": full_response,
        "chunks_received": chunk_count,
        "usage": usage
    }


def lambda_handler(event, context):
    """
    Demonstrates that Converse API uses the SAME code for different models.
    Compare this with invoke_model_demo.py where each model needs different code.
    """
    results = {
        "tutorial": "Converse API Demo",
        "key_lesson": (
            "The Converse API uses an identical request/response schema for ALL models. "
            "You only change the modelId parameter. No need to learn model-specific formats. "
            "Compare this with InvokeModel where Claude needs 'anthropic_version' + 'messages' "
            "but Llama needs 'prompt' + 'max_gen_len'."
        ),
        "prompt_used": PROMPT,
        "results": []
    }

    # 1. Converse with Claude — same code structure
    try:
        results["results"].append(
            converse_with_model(
                "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                "Claude Haiku 4.5",
                PROMPT
            )
        )
    except Exception as e:
        results["results"].append({"model": "Claude Haiku 4.5", "error": str(e)})

    # 2. Converse with Llama — EXACT SAME code structure!
    try:
        results["results"].append(
            converse_with_model(
                "meta.llama3-8b-instruct-v1:0",
                "Llama 3 8B Instruct",
                PROMPT
            )
        )
    except Exception as e:
        results["results"].append({"model": "Llama 3 8B Instruct", "error": str(e)})

    # 3. ConverseStream with Claude
    try:
        results["results"].append(
            converse_stream_with_model(
                "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                "Claude Haiku 4.5",
                PROMPT
            )
        )
    except Exception as e:
        results["results"].append({"model": "Claude Haiku 4.5 (stream)", "error": str(e)})

    # Summary comparison
    results["comparison"] = {
        "InvokeModel": {
            "claude_request": '{"anthropic_version": "...", "messages": [...], "max_tokens": 200}',
            "llama_request": '{"prompt": "...", "max_gen_len": 200}',
            "verdict": "Different schema per model — you must maintain model-specific code"
        },
        "Converse": {
            "claude_request": '{"messages": [{"role": "user", "content": [{"text": "..."}]}], "inferenceConfig": {"maxTokens": 200}}',
            "llama_request": '{"messages": [{"role": "user", "content": [{"text": "..."}]}], "inferenceConfig": {"maxTokens": 200}}',
            "verdict": "IDENTICAL schema — just swap the modelId"
        }
    }

    return results
