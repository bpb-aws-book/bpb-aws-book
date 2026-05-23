import streamlit as st
import boto3
import json
import requests

st.set_page_config(page_title="Chapter 25 Bedrock Playground", layout="wide")

st.title("Chapter 25 Bedrock Playground")

st.markdown(
    "**⚠️ WARNING: Do not supply any Personally Identifiable Information (PII) "
    "in any of the input fields below. This is a testing environment and inputs "
    "are not encrypted or protected for sensitive data.**"
)

st.divider()


def get_instance_region():
    """Get the region from EC2 instance metadata."""
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2,
        ).text
        region = requests.get(
            "http://169.254.169.254/latest/meta-data/placement/region",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=2,
        ).text
        return region
    except Exception:
        return "us-east-1"


# Initialize Bedrock clients with region from instance metadata
region = get_instance_region()
bedrock_client = boto3.client("bedrock-runtime", region_name=region)
bedrock_mgmt_client = boto3.client("bedrock", region_name=region)

# Model ID for Global Anthropic Claude Opus 4 inference profile
MODEL_ID = "global.anthropic.claude-opus-4-6-v1"


@st.cache_data(ttl=300)
def get_guardrails():
    """Fetch all guardrails in the account and region."""
    guardrails = []
    try:
        paginator = bedrock_mgmt_client.get_paginator("list_guardrails")
        for page in paginator.paginate():
            for guardrail in page.get("guardrails", []):
                guardrails.append(
                    {
                        "name": guardrail["name"],
                        "id": guardrail["id"],
                        "version": guardrail.get("version", "DRAFT"),
                    }
                )
    except Exception as e:
        st.error(f"Error fetching guardrails: {e}")
    return guardrails


# Input controls
col1, col2 = st.columns(2)

with col1:
    system_prompt = st.text_area(
        "System Prompt",
        height=150,
        placeholder="Enter a system prompt to guide the model's behavior...",
    )

    context = st.text_area(
        "Context",
        height=200,
        placeholder="Enter context information for the model to reference...",
    )

with col2:
    user_prompt = st.text_area(
        "Prompt",
        height=150,
        placeholder="Enter your prompt here...",
    )

    # Guardrail dropdown
    guardrails = get_guardrails()
    guardrail_options = ["None"] + [
        f"{g['name']} ({g['id']})" for g in guardrails
    ]
    selected_guardrail = st.selectbox("Bedrock Guardrail", guardrail_options)

    # Prompt caching checkbox
    enable_prompt_caching = st.checkbox("Enable Prompt Caching", value=False)

st.divider()

# Invoke button
if st.button("Invoke Bedrock", type="primary", use_container_width=True):
    if not user_prompt.strip():
        st.warning("Please enter a prompt before invoking.")
    else:
        with st.spinner("Invoking Claude Opus 4 via Converse API..."):
            try:
                # Build messages
                messages = []

                # Combine context and user prompt into user message
                user_content = []
                if context.strip():
                    user_content.append({"text": f"Context:\n{context.strip()}"})
                    if enable_prompt_caching:
                        user_content.append({"cachePoint": {"type": "default"}})
                user_content.append({"text": user_prompt.strip()})

                messages.append({"role": "user", "content": user_content})

                # Build request parameters
                request_params = {
                    "modelId": MODEL_ID,
                    "messages": messages,
                }

                # Add system prompt if provided
                if system_prompt.strip():
                    system_content = [{"text": system_prompt.strip()}]
                    if enable_prompt_caching:
                        system_content.append({"cachePoint": {"type": "default"}})
                    request_params["system"] = system_content

                # Add guardrail config if selected
                if selected_guardrail != "None":
                    selected_idx = guardrail_options.index(selected_guardrail) - 1
                    guardrail_info = guardrails[selected_idx]
                    request_params["guardrailConfig"] = {
                        "guardrailIdentifier": guardrail_info["id"],
                        "guardrailVersion": guardrail_info["version"],
                        "trace": "enabled",
                    }

                # Invoke the model
                response = bedrock_client.converse(**request_params)

                # Display response
                st.subheader("Response")
                output_message = response.get("output", {}).get("message", {})
                response_text = ""
                for block in output_message.get("content", []):
                    if "text" in block:
                        response_text += block["text"]

                st.markdown(response_text)

                # Display metadata
                with st.expander("Response Metadata"):
                    usage = response.get("usage", {})
                    st.json(
                        {
                            "stopReason": response.get("stopReason", "N/A"),
                            "inputTokens": usage.get("inputTokens", 0),
                            "outputTokens": usage.get("outputTokens", 0),
                            "cacheReadInputTokens": usage.get(
                                "cacheReadInputTokens", 0
                            ),
                            "cacheWriteInputTokens": usage.get(
                                "cacheWriteInputTokens", 0
                            ),
                        }
                    )

                # Display guardrail trace if available
                if "trace" in response:
                    with st.expander("Guardrail Trace"):
                        st.json(response["trace"])

            except Exception as e:
                st.error(f"Error invoking Bedrock: {e}")
