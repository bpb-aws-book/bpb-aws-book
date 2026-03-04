from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from strands import Agent
from strands_tools import calculator, current_time

# based on code samples at https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html

app = FastAPI(title="Chapter27 Agent Server", version="1.0.0")

# Initialize Strands agent with built-in tools from strands-agents-tools
chapter27_strands_agent = Agent(
    tools=[calculator, current_time],
    system_prompt="You are a helpful assistant with access to a calculator and current time. Use these tools when appropriate to answer user questions accurately."
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
        <p>Try asking: "What is 25 * 17?" or "What time is it?"</p>
        <textarea id="prompt" placeholder="Enter your question here...">What is the square root of 144?</textarea>
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
