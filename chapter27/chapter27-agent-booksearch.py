from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
from strands_tools import calculator, current_time
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
import os

app = FastAPI(title="Chapter27 Agent Server", version="1.0.0")

# Gateway configuration - set these as environment variables
GATEWAY_MCP_URL = os.getenv("GATEWAY_MCP_URL", "")  # e.g., https://gateway-xxxxx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
GATEWAY_AUTH_TYPE = os.getenv("GATEWAY_AUTH_TYPE", "OAUTH_IDENTITY")  # IAM, OAUTH_IDENTITY, or NONE

# OAuth Identity configuration (only needed if GATEWAY_AUTH_TYPE=OAUTH_IDENTITY)
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "")
COGNITO_CLIENT_SECRET = os.getenv("COGNITO_CLIENT_SECRET", "")
COGNITO_TOKEN_URL = os.getenv("COGNITO_TOKEN_URL", "")
COGNITO_SCOPE = os.getenv("COGNITO_SCOPE", "")  # e.g., "resource-server/read resource-server/write"

def fetch_oauth_token():
    """Fetch OAuth token directly from Cognito"""
    import requests
    
    # Build the request data
    data = f"grant_type=client_credentials&client_id={COGNITO_CLIENT_ID}&client_secret={COGNITO_CLIENT_SECRET}"
    if COGNITO_SCOPE:
        data += f"&scope={COGNITO_SCOPE}"
    
    response = requests.post(
        COGNITO_TOKEN_URL,
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code != 200:
        print(f"Error fetching token: {response.status_code} - {response.text}")
        raise Exception(f"Failed to fetch OAuth token: {response.text}")
    
    return response.json()['access_token']

def create_mcp_transport(mcp_url: str):
    """Create MCP transport based on auth type"""
    if GATEWAY_AUTH_TYPE == "OAUTH_IDENTITY":
        # Fetch OAuth token directly from Cognito
        access_token = fetch_oauth_token()
        return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})
    elif GATEWAY_AUTH_TYPE == "NONE":
        return streamablehttp_client(mcp_url)
    else:
        # For IAM auth, no additional headers needed
        return streamablehttp_client(mcp_url)

def get_gateway_tools():
    """Fetch tools from the gateway via MCP and return both tools and client"""
    if not GATEWAY_MCP_URL:
        return [], None
    
    try:
        mcp_client = MCPClient(lambda: create_mcp_transport(GATEWAY_MCP_URL))
        mcp_client.start()  # Start the client but don't use context manager
        
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
        print(f"Warning: Could not fetch gateway tools: {e}")
        return [], None

# Get gateway tools and keep the MCP client alive
gateway_tools, mcp_client = get_gateway_tools()
all_tools = [calculator, current_time] + gateway_tools

# Initialize Strands agent with built-in tools and gateway tools
chapter27_strands_agent = Agent(
    tools=all_tools,
    system_prompt="You are a helpful bookclub assistant with access to a calculator, current time, and book search. Use the search_books tool to help users find books by name or rental status."
)

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400, 
                detail="No prompt found in input. Please provide a 'prompt' key in the input."
            )

        result = chapter27_strands_agent(user_message)
        response = {
            "message": result.message,
            "timestamp": datetime.utcnow().isoformat()
        }

        return InvocationResponse(output=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

@app.get("/ping")
async def ping():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "Chapter27 Agent Server",
        "endpoints": {
            "POST /invocations": "Invoke the agent with JSON body: {\"input\": {\"prompt\": \"your question\"}}",
            "GET /ping": "Health check",
            "GET /test": "Interactive test page"
        }
    }

@app.get("/test")
async def test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            textarea { width: 100%; height: 100px; margin: 10px 0; padding: 10px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            button:hover { background: #0056b3; }
            #response { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>Chapter27 Agent Test</h1>
        <p>Try asking: "What is 25 * 17?", "What time is it?", or "Find if the book Clean Code is available to rent"</p>
        <textarea id="prompt" placeholder="Enter your question here...">Find me available books about software</textarea>
        <button onclick="testAgent()">Send to Agent</button>
        <div id="response"></div>
        
        <script>
            async function testAgent() {
                const prompt = document.getElementById('prompt').value;
                const responseDiv = document.getElementById('response');
                responseDiv.textContent = 'Processing...';
                
                try {
                    const response = await fetch('/invocations', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ input: { prompt: prompt } })
                    });
                    
                    const data = await response.json();
                    responseDiv.textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    responseDiv.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
