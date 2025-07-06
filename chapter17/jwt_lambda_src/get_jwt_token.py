import json
import boto3
import requests
import hmac
import hashlib
import base64
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function to authenticate with Cognito and call protected API
    """
    # Get parameters from event or environment variables
    username = event.get('username') or os.environ.get('COGNITO_USERNAME')
    book_id = event.get('book_id') or event.get('pathParameters', {}).get('id')
    
    client_id = os.environ['COGNITO_CLIENT_ID']
    api_base_url = os.environ['API_BASE_URL']
    secret_arn = os.environ['SECRET_ARN']
    
    try:
        # Get credentials from Secrets Manager
        credentials = get_secret(secret_arn)
        password = credentials.get('password')
        client_secret = credentials.get('client_secret')
        
        # Authenticate with Cognito
        jwt_token = authenticate_cognito(username, password, client_id, client_secret)
        
        # Call protected API
        result = call_protected_api(api_base_url, jwt_token, book_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def authenticate_cognito(username, password, client_id, client_secret):
    """Get JWT token from Cognito with client secret"""
    cognito_client = boto3.client('cognito-idp')
    
    # Generate SECRET_HASH
    message = username + client_id
    secret_hash = base64.b64encode(
        hmac.new(client_secret.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    
    response = cognito_client.initiate_auth(
        ClientId=client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password,
            'SECRET_HASH': secret_hash
        }
    )
    
    return response['AuthenticationResult']['IdToken']

def call_protected_api(api_base_url, jwt_token, book_id):
    """Call the protected API endpoint"""
    headers = {'Authorization': f'Bearer {jwt_token}'}
    # Ensure URL ends with /Prod if not already included
    if not api_base_url.endswith('/Prod'):
        api_base_url = api_base_url.rstrip('/') + '/Prod'
    response = requests.get(f'{api_base_url}/books/{book_id}', headers=headers)
    response.raise_for_status()
    return response.json()

def get_secret(secret_arn):
    """Retrieve credentials from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
    except ClientError as e:
        raise e
    
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)
