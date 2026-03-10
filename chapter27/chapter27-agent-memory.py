from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
from strands.hooks import AgentInitializedEvent, HookProvider, MessageAddedEvent
from strands_tools import calculator, current_time
from bedrock_agentcore.memory import MemoryClient
import os

app = FastAPI(title="Chapter27 Agent Server with Memory", version="1.0.0")

# Memory configuration - set MEMORY_ID as environment variable
MEMORY_ID = os.getenv("MEMORY_ID", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Initialize memory client
memory_client = MemoryClient(region_name=AWS_REGION) if MEMORY_ID else None

# Simple shared session tracker (JSONSerializableDict doesn't support assignment)
current_session_id = "default"

class MemoryHook(HookProvider):
    """
    Automatically handles memory operations:
    - Loads previous conversation when agent starts
    - Saves each message after it's processed
    """

    def on_agent_initialized(self, event):
        """Loads conversation history from memory when agent starts"""
        if not MEMORY_ID:
            return

        try:
            session_id = current_session_id
        except Exception:
            session_id = "default"
        turns = memory_client.get_last_k_turns(
            memory_id=MEMORY_ID,
            actor_id="user",
            session_id=session_id,
            k=5
        )

        # Retrieve extracted long-term memories
        extracted = memory_client.retrieve_memories(
            memory_id=MEMORY_ID,
            namespace=f"/strategies/default/actors/user/",
            query=f"session {session_id}",
            actor_id="user"
        )

        context_parts = []
        if turns:
            turn_context = "\n".join([
                f"{m['role']}: {m['content']['text']}"
                for t in turns for m in t
            ])
            context_parts.append(f"Recent conversation:\n{turn_context}")

        if extracted:
            mem_context = "\n".join([str(m) for m in extracted])
            context_parts.append(f"Extracted memories:\n{mem_context}")

        if context_parts:
            event.agent.system_prompt += "\n\n" + "\n\n".join(context_parts)

    def on_message_added(self, event):
        """Saves each message to memory after it's processed"""
        if not MEMORY_ID:
            return

        try:
            session_id = current_session_id
        except Exception:
            session_id = "default"
        msg = event.agent.messages[-1]
        memory_client.create_event(
            memory_id=MEMORY_ID,
            actor_id="user",
            session_id=session_id,
            messages=[(str(msg["content"]), msg["role"])]
        )

    def register_hooks(self, registry):
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        registry.add_callback(MessageAddedEvent, self.on_message_added)

# Initialize Strands agent with memory hooks and tools
chapter27_strands_agent = Agent(
    tools=[calculator, current_time],
    system_prompt="You are a helpful assistant with access to a calculator and current time. You have memory of previous conversations and can recall past interactions.",
    hooks=[MemoryHook()] if MEMORY_ID else []
)

class InvocationRequest(BaseModel):
    input: Dict[str, Any]
    session_id: str = "default"

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

        # Set session_id so MemoryHook can use it
        global current_session_id
        current_session_id = request.session_id

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
        "message": "Chapter27 Agent Server with Memory",
        "endpoints": {
            "POST /invocations": "Invoke the agent with JSON body: {\"input\": {\"prompt\": \"your question\"}, \"session_id\": \"optional-session-id\"}",
            "GET /ping": "Health check",
            "GET /test": "Interactive test page"
        },
        "memory": "Agent remembers previous conversations per session_id. Set MEMORY_ID env var to enable."
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
        <h1>Chapter27 Agent Test (with Memory)</h1>
        <p>Try asking: "What is 25 * 17?" or "What time is it?"</p>
        <label for="session_id">Session ID:</label>
        <input type="text" id="session_id" value="test-session-1" style="width: 100%; padding: 8px; margin: 5px 0 10px 0;">
        <textarea id="prompt" placeholder="Enter your question here...">What is the square root of 144?</textarea>
        <button onclick="testAgent()">Send to Agent</button>
        <div id="response"></div>
        
        <script>
            async function testAgent() {
                const prompt = document.getElementById('prompt').value;
                const sessionId = document.getElementById('session_id').value;
                const responseDiv = document.getElementById('response');
                responseDiv.textContent = 'Processing...';
                
                try {
                    const response = await fetch('/invocations', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ input: { prompt: prompt }, session_id: sessionId })
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
