import json
import os
import base64
import uuid
from urllib import request as urllib_request
from urllib.parse import urlencode, quote
from urllib.error import HTTPError
import http.client
import ssl

def get_cognito_token(cognito_domain, client_id, client_secret, scope):
    """
    Get an OAuth2 access token from Cognito using client_credentials grant.
    """
    token_url = f'{cognito_domain}/oauth2/token'

    credentials = f'{client_id}:{client_secret}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_credentials}'
    }

    data = {'grant_type': 'client_credentials'}
    if scope:
        data['scope'] = scope

    body = urlencode(data).encode('utf-8')
    req = urllib_request.Request(token_url, data=body, headers=headers, method='POST')

    try:
        with urllib_request.urlopen(req, timeout=10) as response:
            token_data = json.loads(response.read().decode('utf-8'))
            return token_data['access_token']
    except HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else 'No details'
        raise Exception(f'Cognito token error (HTTP {e.code}): {error_body}')


def invoke_agent_runtime_with_token(agent_runtime_arn, session_id, payload, token, region=YOUR_AWS_REGION):
    """
    Invoke AgentCore runtime via HTTPS request with Bearer token authentication.
    This is the required approach when using JWT/OAuth - boto3 SDK cannot be used.
    """
    host = f'bedrock-agentcore.{region}.amazonaws.com'
    encoded_arn = quote(agent_runtime_arn, safe='')
    path = f'/runtimes/{encoded_arn}/invocations'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
        'x-amzn-bedrock-agentcore-runtime-session-id': session_id
    }

    print(f'Calling AgentCore: https://{host}{path}')
    print(f'Session ID: {session_id}')

    context = ssl.create_default_context()
    conn = http.client.HTTPSConnection(host, timeout=120, context=context)

    try:
        conn.request('POST', path, body=payload, headers=headers)
        response = conn.getresponse()
        response_body = response.read().decode('utf-8')

        if response.status >= 400:
            raise Exception(f'AgentCore invoke error (HTTP {response.status}): {response_body}')

        return {
            'status': response.status,
            'body': response_body
        }
    finally:
        conn.close()


def lambda_handler(event, context):
    cognito_domain = os.environ['COGNITO_DOMAIN']
    client_id = os.environ['COGNITO_CLIENT_ID']
    client_secret = os.environ['COGNITO_CLIENT_SECRET']
    scope = os.environ.get('COGNITO_SCOPE', '')

    agent_runtime_arn = 'arn:aws:bedrock-agentcore:YOUR_AWS_REGION:YOUR_AWS_ACCOUNT:runtime/hosted_agent_xxxxxxxxxxxxx'
    
    # Generate unique session ID
    runtime_session_id = str(uuid.uuid4()).replace('-', '') + str(uuid.uuid4()).replace('-', '')[:10]
    
    # Prepare payload as JSON string
    payload = json.dumps({"input": {"prompt": "how can you help me?"}})
    
    try:
        # Step 1: Get Cognito access token
        print('Obtaining Cognito token...')
        token = get_cognito_token(cognito_domain, client_id, client_secret, scope)
        print('Successfully obtained Cognito token')
        print(f'Token (first 20 chars): {token[:20]}...')

        # Step 2: Call AgentCore runtime via HTTPS with Bearer token
        # Note: Cannot use boto3 SDK when using JWT/OAuth authentication
        print('Invoking AgentCore runtime via HTTPS...')
        response = invoke_agent_runtime_with_token(
            agent_runtime_arn=agent_runtime_arn,
            session_id=runtime_session_id,
            payload=payload,
            token=token
        )
        print('AgentCore response received')
        print(response)

        return {
            'statusCode': response['status'],
            'body': response['body']
        }

    except Exception as e:
        print(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
