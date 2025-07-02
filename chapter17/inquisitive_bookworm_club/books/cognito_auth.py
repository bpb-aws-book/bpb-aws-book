import boto3
import hmac
import hashlib
import base64
from django.conf import settings

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        self.client_secret = getattr(settings, 'COGNITO_CLIENT_SECRET', None)
    
    def get_secret_hash(self, username):
        if not self.client_secret:
            return None
        message = username + self.client_id
        dig = hmac.new(self.client_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def authenticate(self, username, password):
        try:
            auth_params = {
                'USERNAME': username,
                'PASSWORD': password
            }
            
            if self.client_secret:
                auth_params['SECRET_HASH'] = self.get_secret_hash(username)
            
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters=auth_params
            )
            
            # Handle password change challenge
            if 'ChallengeName' in response and response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                return False, 'Password change required. Please contact administrator.'
            
            if 'AuthenticationResult' in response:
                return True, response['AuthenticationResult']
            else:
                return False, 'Authentication failed'
                
        except self.client.exceptions.NotAuthorizedException:
            return False, 'Invalid username or password'
        except self.client.exceptions.UserNotFoundException:
            return False, 'User not found'
        except Exception as e:
            return False, f'Authentication error: {str(e)}'
