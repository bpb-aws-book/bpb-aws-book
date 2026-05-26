"""
Lambda 1: InvokeModel vs Converse API
=======================================
Shows that InvokeModel requires model-specific schemas while Converse uses
a unified schema across all models.

- Two InvokeModel calls (Claude + Llama) with DIFFERENT request schemas
- Two Converse calls (Claude + Llama) with the SAME request schema
"""

import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime")

PROMPT = "Explain what cloud computing is in exactly two sentences."
CLAUDE_MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
LLAMA_MODEL_ID = "meta.llama3-8b-instruct-v1:0"


# ============================================================
# INVOKE MODEL — Each model needs a DIFFERENT request schema
# ============================================================

def invoke_model_claude(prompt):
    """Claude InvokeModel schema: anthropic_version + messages + max_tokens"""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model(
        modelId=CLAUDE_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )
    response_body = json.loads(response["body"].read())

    return {
        "model": "Claude Haiku 4.5",
        "api": "InvokeModel",
        "request_body_sent": {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "..."}],
            "max_tokens": 200,
            "temperature": 0.5
        },
        "output": response_body["content"][0]["text"],
        "usage": response_body["usage"]
    }


def invoke_model_llama(prompt):
    """Llama InvokeModel schema: prompt + max_gen_len + temperature"""
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 200,
        "temperature": 0.5
    })

    response = bedrock_runtime.invoke_model(
        modelId=LLAMA_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )
    response_body = json.loads(response["body"].read())

    return {
        "model": "Llama 3 8B Instruct",
        "api": "InvokeModel",
        "request_body_sent": {
            "prompt": "...",
            "max_gen_len": 200,
            "temperature": 0.5
        },
        "output": response_body["generation"],
        "usage": {
            "prompt_token_count": response_body.get("prompt_token_count"),
            "generation_token_count": response_body.get("generation_token_count")
        }
    }


# ============================================================
# CONVERSE — Same schema for ALL models, only modelId changes
# ============================================================

def converse_model(model_id, model_name, prompt):
    """Converse API: identical code for any model"""
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[
            {"role": "user", "content": [{"text": prompt}]}
        ],
        inferenceConfig={"maxTokens": 200, "temperature": 0.5}
    )

    return {
        "model": model_name,
        "api": "Converse",
        "request_body_sent": {
            "messages": [{"role": "user", "content": [{"text": "..."}]}],
            "inferenceConfig": {"maxTokens": 200, "temperature": 0.5}
        },
        "output": response["output"]["message"]["content"][0]["text"],
        "usage": response["usage"],
        "stop_reason": response["stopReason"]
    }


# ============================================================
# HANDLER
# ============================================================

def lambda_handler(event, context):
    results = {
        "tutorial": "InvokeModel vs Converse API",
        "prompt": PROMPT,
        "key_lesson": (
            "InvokeModel requires a DIFFERENT request schema for each model. "
            "Converse uses the SAME schema for all models — only modelId changes."
        ),
        "invoke_model_results": [],
        "converse_results": []
    }

    # InvokeModel — two models, two different schemas
    try:
        results["invoke_model_results"].append(invoke_model_claude(PROMPT))
    except Exception as e:
        results["invoke_model_results"].append({"model": "Claude Haiku 4.5", "error": str(e)})

    try:
        results["invoke_model_results"].append(invoke_model_llama(PROMPT))
    except Exception as e:
        results["invoke_model_results"].append({"model": "Llama 3 8B Instruct", "error": str(e)})

    # Converse — two models, SAME schema
    try:
        results["converse_results"].append(converse_model(CLAUDE_MODEL_ID, "Claude Haiku 4.5", PROMPT))
    except Exception as e:
        results["converse_results"].append({"model": "Claude Haiku 4.5", "error": str(e)})

    try:
        results["converse_results"].append(converse_model(LLAMA_MODEL_ID, "Llama 3 8B Instruct", PROMPT))
    except Exception as e:
        results["converse_results"].append({"model": "Llama 3 8B Instruct", "error": str(e)})

    # Side-by-side schema comparison
    results["schema_comparison"] = {
        "InvokeModel_Claude": "anthropic_version + messages[{role, content}] + max_tokens",
        "InvokeModel_Llama": "prompt (string) + max_gen_len + temperature",
        "Converse_Claude": "messages[{role, content[{text}]}] + inferenceConfig{maxTokens}",
        "Converse_Llama": "messages[{role, content[{text}]}] + inferenceConfig{maxTokens}",
        "verdict": "Converse schemas are IDENTICAL. InvokeModel schemas are DIFFERENT."
    }

    return results
