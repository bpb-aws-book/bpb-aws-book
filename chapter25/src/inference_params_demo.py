"""
Bedrock Inference Parameters Demo
==================================
This function demonstrates how temperature, topP, and topK affect model output.
It calls the same model with the same prompt but different parameter combinations
so you can observe the differences.

Key takeaways:
- Temperature controls randomness (0 = deterministic, 1 = maximum randomness)
- TopP (nucleus sampling) limits token selection to a cumulative probability threshold
- TopK limits token selection to the K most probable tokens
"""

import json
import boto3

bedrock_runtime = boto3.client("bedrock-runtime")

# Using a creative prompt where parameter differences are clearly visible
PROMPT = "Write a one-sentence tagline for a coffee shop on Mars."
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


def call_with_params(prompt, temperature, top_p, top_k=None, num_calls=3):
    """
    Calls the model multiple times with the same parameters to show variability.
    """
    outputs = []

    for i in range(num_calls):
        inference_config = {
            "maxTokens": 100,
        }
        if temperature is not None:
            inference_config["temperature"] = temperature
        if top_p is not None:
            inference_config["topP"] = top_p

        kwargs = {
            "modelId": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": inference_config
        }

        # topK is not part of the standard Converse inferenceConfig.
        # It must be passed via additionalModelRequestFields (model-specific).
        if top_k is not None:
            kwargs["additionalModelRequestFields"] = {"top_k": top_k}

        response = bedrock_runtime.converse(**kwargs)

        output_text = response["output"]["message"]["content"][0]["text"]
        outputs.append(output_text.strip())

    return outputs


def lambda_handler(event, context):
    """
    Runs the same prompt with different parameter settings to demonstrate their impact.
    """
    experiments = [
        {
            "title": "DETERMINISTIC (temperature=0)",
            "description": "Outputs should be identical across all calls",
            "temperature": 0.0,
            "top_p": None,
            "observation": "Temperature 0 always picks the highest-probability token. No randomness."
        },
        {
            "title": "MODERATE RANDOMNESS (temperature=0.5)",
            "description": "Outputs may show slight variations",
            "temperature": 0.5,
            "top_p": None,
            "observation": "Some randomness introduced. Model occasionally picks less probable tokens."
        },
        {
            "title": "HIGH RANDOMNESS (temperature=1.0)",
            "description": "Outputs should vary significantly between calls",
            "temperature": 1.0,
            "top_p": None,
            "observation": "Full randomness. Model samples freely — expect creative, diverse outputs."
        },
        {
            "title": "RESTRICTED POOL (topP=0.1 only)",
            "description": "TopP restricts choices to top 10% probability mass",
            "temperature": None,
            "top_p": 0.1,
            "observation": "Low topP limits available tokens to top 10% probability mass. Outputs are focused and similar."
        },
        {
            "title": "WIDE POOL (topP=0.99 only)",
            "description": "TopP allows nearly all tokens, full diversity",
            "temperature": None,
            "top_p": 0.99,
            "observation": "High topP makes nearly all tokens available. Expect more diverse outputs than topP=0.1."
        },
        {
            "title": "TOP_K RESTRICTIVE (topK=1, greedy decoding)",
            "description": "Only the single most probable token is considered each step",
            "temperature": None,
            "top_p": None,
            "top_k": 1,
            "observation": "topK=1 is greedy decoding — always picks the best token. Outputs should be identical. Passed via additionalModelRequestFields (not in standard inferenceConfig)."
        },
        {
            "title": "TOP_K MODERATE (topK=50)",
            "description": "Top 50 tokens considered at each step",
            "temperature": None,
            "top_p": None,
            "top_k": 50,
            "observation": "topK=50 allows moderate diversity. Passed via additionalModelRequestFields since topK is not part of the Converse API's standard inferenceConfig."
        },
        {
            "title": "TOP_K WIDE (topK=250)",
            "description": "Top 250 tokens considered at each step — high diversity",
            "temperature": None,
            "top_p": None,
            "top_k": 250,
            "observation": "topK=250 allows many token choices. More diverse than topK=50. Shows how additionalModelRequestFields enables model-specific params in the unified Converse API."
        }
    ]

    results = []

    for exp in experiments:
        try:
            outputs = call_with_params(
                PROMPT,
                temperature=exp["temperature"],
                top_p=exp["top_p"],
                top_k=exp.get("top_k")
            )

            unique_outputs = set(outputs)
            if len(unique_outputs) == 1:
                variability = "ALL IDENTICAL — deterministic"
            elif len(unique_outputs) == len(outputs):
                variability = "ALL DIFFERENT — high variability"
            else:
                variability = f"{len(unique_outputs)} unique out of {len(outputs)} — some variability"

            results.append({
                "experiment": exp["title"],
                "parameters": {
                    "temperature": exp["temperature"],
                    "topP": exp["top_p"],
                    "topK": exp.get("top_k"),
                    "topK_note": "passed via additionalModelRequestFields" if exp.get("top_k") else None
                },
                "call_1": outputs[0],
                "call_2": outputs[1],
                "call_3": outputs[2],
                "variability": variability,
                "explanation": exp["observation"]
            })
        except Exception as e:
            results.append({
                "experiment": exp["title"],
                "error": str(e)
            })

    response_body = {
        "tutorial": "Inference Parameters Demo",
        "model": MODEL_ID,
        "prompt": PROMPT,
        "note": "Claude Haiku 4.5 does not allow temperature and topP simultaneously. Use one or the other.",
        "experiments": results,
        "recommendations": {
            "factual_qa_code": "temperature=0",
            "balanced_responses": "temperature=0.3 to 0.5",
            "creative_writing": "temperature=0.7 to 1.0",
            "controlled_diversity": "topP=0.9 (without temperature)",
            "topK_usage": "topK via additionalModelRequestFields — not in standard inferenceConfig. Use topK=1 for greedy, topK=50-250 for diversity."
        }
    }

    return response_body
