"""
AgentCore Runtime agent with book search via MCP Gateway.
Uses AgentCore Identity with @requires_access_token for M2M auth.
This version is designed to run ONLY on AgentCore Runtime.
"""
import asyncio
import os
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log all imports to diagnose container startup failures
try:
    from bedrock_agentcore import BedrockAgentCoreApp
    logger.info("Imported BedrockAgentCoreApp successfully")
except ImportError as e:
    logger.error(f"Failed to import BedrockAgentCoreApp: {e}")
    sys.exit(1)

try:
    from bedrock_agentcore.identity.auth import requires_access_token
    logger.info("Imported requires_access_token successfully")
except ImportError:
    try:
        from bedrock_agentcore.identity import requires_access_token
        logger.info("Imported requires_access_token from bedrock_agentcore.identity")
    except ImportError as e:
        logger.error(f"Failed to import requires_access_token: {e}")
        sys.exit(1)

try:
    from strands import Agent
    from strands_tools import calculator, current_time
    from strands.tools.mcp.mcp_client import MCPClient
    from mcp.client.streamable_http import streamablehttp_client
    logger.info("Imported strands and MCP dependencies successfully")
except Exception as e:
    logger.error(f"Failed to import strands/MCP: {e}")
    sys.exit(1)

logger.info("Creating BedrockAgentCoreApp...")
app = BedrockAgentCoreApp()
logger.info("BedrockAgentCoreApp created")

# Gateway configuration
GATEWAY_MCP_URL = os.getenv("GATEWAY_MCP_URL", "")
IDENTITY_PROVIDER_NAME = os.getenv("IDENTITY_PROVIDER_NAME", "")
logger.info(f"GATEWAY_MCP_URL={'SET' if GATEWAY_MCP_URL else 'EMPTY'}")
logger.info(f"IDENTITY_PROVIDER_NAME={'SET' if IDENTITY_PROVIDER_NAME else 'EMPTY'}")

# Holds the token fetched by the decorator
token_holder = {"access_token": None}

logger.info("Applying @requires_access_token decorator...")
try:
    @requires_access_token(
        provider_name=IDENTITY_PROVIDER_NAME,
        scopes=[],
        auth_flow="M2M",
    )
    async def fetch_m2m_token(*, access_token: str):
        """Fetch M2M OAuth token via AgentCore Identity"""
        token_holder["access_token"] = access_token
        return access_token
    logger.info("Decorator applied successfully")
except Exception as e:
    logger.error(f"Decorator failed: {e}")
    sys.exit(1)

def create_mcp_transport(mcp_url: str, token: str):
    """Create MCP transport with the provided OAuth token"""
    return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {token}"})

def get_gateway_tools(token: str):
    """Fetch tools from the gateway via MCP using provided token"""
    if not GATEWAY_MCP_URL:
        return [], None
    try:
        mcp_client = MCPClient(lambda: create_mcp_transport(GATEWAY_MCP_URL, token))
        mcp_client.start()
        tools = []
        pagination_token = None
        while True:
            result = mcp_client.list_tools_sync(pagination_token=pagination_token)
            tools.extend(result)
            if result.pagination_token is None:
                break
            pagination_token = result.pagination_token
        return tools, mcp_client
    except Exception as e:
        logger.warning(f"Could not fetch gateway tools: {e}")
        return [], None

@app.entrypoint
def invoke(payload):
    """Main entrypoint for AgentCore Runtime"""
    user_message = payload.get("prompt", "Hello!")

    # Step 1: Get M2M token via AgentCore Identity
    try:
        asyncio.run(fetch_m2m_token())
        token = token_holder["access_token"]
    except Exception as e:
        logger.error(f"Failed to get M2M token: {e}")
        return {"error": f"Authentication failed: {str(e)}"}

    # Step 2: Connect to gateway and get tools
    gateway_tools, mcp_client = get_gateway_tools(token)
    all_tools = [calculator, current_time] + gateway_tools

    # Step 3: Run the agent
    try:
        agent = Agent(
            tools=all_tools,
            system_prompt="You are a helpful bookclub assistant with access to a calculator, current time, and book search. Use the search_books tool to help users find books by name or rental status."
        )
        result = agent(user_message)
        return {"message": result.message}
    except Exception as e:
        logger.error(f"Agent processing failed: {e}")
        return {"error": f"Agent processing failed: {str(e)}"}
    finally:
        if mcp_client:
            try:
                mcp_client.stop()
            except Exception:
                pass

if __name__ == "__main__":
    logger.info("Starting app.run()...")
    app.run()

