import json
import boto3
import uuid

def lambda_handler(event, context):
    agent_core_client = boto3.client('bedrock-agentcore', region_name='YOUR_AWS_REGION')
    print(f"Boto3 version: {boto3.__version__}")
    
    session_id = str(uuid.uuid4())
    
    # Don't use json.dumps - pass dict directly
    payload = json.dumps({"input": {"prompt": event.get("prompt")}})
    
    try:
        response = agent_core_client.invoke_agent_runtime(
            agentRuntimeArn='arn:aws:bedrock-agentcore:YOUR_AWS_REGION:YOUR_AWS_ACCOUNT:runtime/hosted_agent_xxxxxxxx',
            runtimeSessionId=session_id,
            payload=payload,
            contentType='application/json'
        )
        
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        print(response_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Success',
                'agentResponse': response_data
            })
        }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error response: {json.dumps(e.response, default=str)}")
        raise
