"""
Lambda 2: Streaming vs Non-Streaming
======================================
Demonstrates the difference between streaming and non-streaming responses
using the Converse API.

Pass {"streaming": true} or {"streaming": false} in the event payload
to see each behavior separately.

NOTE: InvokeModel also supports both streaming and non-streaming:
  - Non-streaming: bedrock_runtime.invoke_model(...)
  - Streaming:     bedrock_runtime.invoke_model_with_response_stream(...)
This function uses Converse APIs for simplicity:
  - Non-streaming: bedrock_runtime.converse(...)
  - Streaming:     bedrock_runtime.converse_stream(...)
"""

import json
import boto3
import time

bedrock_runtime = boto3.client("bedrock-runtime")

PROMPT = "Write a paragraph with ten sentences about why we should learn multiple languages"
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


def converse_non_streaming(prompt):
    """
    Converse (non-streaming):
    Sends the request and waits for the ENTIRE response to be generated.
    You get nothing until the model finishes — then you get everything at once.
    """
    start_time = time.time()

    response = bedrock_runtime.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.5}
    )

    elapsed = round(time.time() - start_time, 2)

    return {
        "api": "Converse (non-streaming)",
        "behavior": "Waited for the ENTIRE response before returning. Nothing received until model finished.",
        "wait_time_seconds": elapsed,
        "output": response["output"]["message"]["content"][0]["text"],
        "usage": response["usage"],
        "stop_reason": response["stopReason"]
    }


def converse_streaming(prompt):
    """
    ConverseStream (streaming):
    Returns text in small chunks AS the model generates tokens.
    In a real UI, you would display each chunk immediately — giving a typing effect.
    """
    start_time = time.time()
    time_to_first_chunk = None

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
            if time_to_first_chunk is None:
                time_to_first_chunk = round(time.time() - start_time, 2)
        elif "metadata" in event:
            usage = event["metadata"].get("usage", {})

    total_time = round(time.time() - start_time, 2)

    return {
        "api": "ConverseStream (streaming)",
        "behavior": "Received text in small chunks AS the model generated them. First chunk arrived quickly.",
        "time_to_first_chunk_seconds": time_to_first_chunk,
        "total_time_seconds": total_time,
        "total_chunks_received": len(chunks),
        "first_5_chunks": chunks[:5],
        "last_3_chunks": chunks[-3:] if len(chunks) >= 3 else chunks,
        "full_output": full_response,
        "usage": usage,
        "note": "In a chatbot UI, each chunk would be displayed immediately — users see text appear word by word instead of waiting for the full response."
    }


def lambda_handler(event, context):
    """
    Pass {"streaming": true} to see streaming behavior.
    Pass {"streaming": false} to see non-streaming behavior.
    Pass {} (empty) to see both side by side.
    """
    streaming_flag = event.get("streaming")

    result = {
        "tutorial": "Streaming vs Non-Streaming",
        "model": MODEL_ID,
        "prompt": PROMPT,
        "event_received": event
    }

    # If streaming flag is explicitly set, run only that mode
    if streaming_flag is True:
        try:
            result["streaming_result"] = converse_streaming(PROMPT)
        except Exception as e:
            result["streaming_result"] = {"error": str(e)}

    elif streaming_flag is False:
        try:
            result["non_streaming_result"] = converse_non_streaming(PROMPT)
        except Exception as e:
            result["non_streaming_result"] = {"error": str(e)}

    else:
        # No flag passed — run both for comparison
        try:
            result["non_streaming_result"] = converse_non_streaming(PROMPT)
        except Exception as e:
            result["non_streaming_result"] = {"error": str(e)}

        try:
            result["streaming_result"] = converse_streaming(PROMPT)
        except Exception as e:
            result["streaming_result"] = {"error": str(e)}

        result["comparison"] = {
            "non_streaming": "You wait for the full response. Simple but slow for the user.",
            "streaming": "You get chunks immediately. Better UX for chatbots and real-time apps.",
            "when_to_use_non_streaming": "Batch processing, background jobs, short responses",
            "when_to_use_streaming": "Chatbots, long responses, any UI where users are waiting"
        }

    return result
