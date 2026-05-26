"""
Lambda 2: Streaming vs Non-Streaming
======================================
Shows the difference between streaming and non-streaming responses
using both InvokeModel and Converse APIs with a single model (Claude).

4 calls total:
- InvokeModel (non-streaming)
- InvokeModelWithResponseStream (streaming)
- Converse (non-streaming)
- ConverseStream (streaming)
"""

import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime")

PROMPT = "Write a short paragraph about why the sky is blue."
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


# ============================================================
# INVOKE MODEL — Non-Streaming vs Streaming
# ============================================================

def invoke_model_non_streaming(prompt):
    """InvokeModel: waits for full response, returns it all at once."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )
    response_body = json.loads(response["body"].read())

    return {
        "api": "InvokeModel",
        "streaming": False,
        "behavior": "Waits until the entire response is generated, then returns it all at once",
        "output": response_body["content"][0]["text"],
        "usage": response_body["usage"]
    }


def invoke_model_streaming(prompt):
    """InvokeModelWithResponseStream: returns response in chunks as they generate."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )

    # Collect chunks as they arrive
    chunks = []
    full_response = ""
    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            text_piece = chunk["delta"]["text"]
            chunks.append(text_piece)
            full_response += text_piece

    return {
        "api": "InvokeModelWithResponseStream",
        "streaming": True,
        "behavior": "Returns response in chunks as tokens are generated — ideal for real-time UIs",
        "output": full_response,
        "total_chunks_received": len(chunks),
        "first_3_chunks": chunks[:3],
        "note": "Each chunk contains a small piece of text. In a UI, you would display each chunk immediately."
    }


# ============================================================
# CONVERSE — Non-Streaming vs Streaming
# ============================================================

def converse_non_streaming(prompt):
    """Converse: waits for full response, returns it all at once."""
    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.5}
    )

    return {
        "api": "Converse",
        "streaming": False,
        "behavior": "Waits until the entire response is generated, then returns it all at once",
        "output": response["output"]["message"]["content"][0]["text"],
        "usage": response["usage"],
        "stop_reason": response["stopReason"]
    }


def converse_streaming(prompt):
    """ConverseStream: returns response in chunks as they generate."""
    response = bedrock_runtime.converse_stream(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.5}
    )

    # Collect chunks as they arrive
    chunks = []
    full_response = ""
    usage = {}

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            text_piece = event["contentBlockDelta"]["delta"]["text"]
            chunks.append(text_piece)
            full_response += text_piece
        elif "metadata" in event:
            usage = event["metadata"].get("usage", {})

    return {
        "api": "ConverseStream",
        "streaming": True,
        "behavior": "Returns response in chunks as tokens are generated — ideal for real-time UIs",
        "output": full_response,
        "total_chunks_received": len(chunks),
        "first_3_chunks": chunks[:3],
        "usage": usage,
        "note": "Each chunk contains a small piece of text. In a UI, you would display each chunk immediately."
    }


# ============================================================
# HANDLER
# ============================================================

def lambda_handler(event, context):
    results = {
        "tutorial": "Streaming vs Non-Streaming",
        "model": MODEL_ID,
        "prompt": PROMPT,
        "key_lesson": (
            "Non-streaming APIs wait for the full response before returning. "
            "Streaming APIs return text in small chunks as tokens are generated. "
            "Use streaming for real-time UIs (chatbots, typing effects). "
            "Use non-streaming for batch processing or when you need the full response at once."
        ),
        "results": []
    }

    # 1. InvokeModel — non-streaming
    try:
        results["results"].append(invoke_model_non_streaming(PROMPT))
    except Exception as e:
        results["results"].append({"api": "InvokeModel", "streaming": False, "error": str(e)})

    # 2. InvokeModelWithResponseStream — streaming
    try:
        results["results"].append(invoke_model_streaming(PROMPT))
    except Exception as e:
        results["results"].append({"api": "InvokeModelWithResponseStream", "streaming": True, "error": str(e)})

    # 3. Converse — non-streaming
    try:
        results["results"].append(converse_non_streaming(PROMPT))
    except Exception as e:
        results["results"].append({"api": "Converse", "streaming": False, "error": str(e)})

    # 4. ConverseStream — streaming
    try:
        results["results"].append(converse_streaming(PROMPT))
    except Exception as e:
        results["results"].append({"api": "ConverseStream", "streaming": True, "error": str(e)})

    # Summary
    results["when_to_use"] = {
        "non_streaming": "Batch jobs, background processing, APIs that return complete responses",
        "streaming": "Chatbots, real-time UIs, long responses where users want to see progress"
    }

    return results
