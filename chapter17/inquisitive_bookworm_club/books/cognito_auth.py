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
            # Check user status first
            status_success, user_status = self.get_user_status(username)
            if status_success and user_status == 'FORCE_CHANGE_PASSWORD':
                return 'FORCE_CHANGE_PASSWORD', username
            
            auth_params = {
                'USERNAME': username,
                'PASSWORD': password
            }
            
            if self.client_secret:
                auth_params['SECRET_HASH'] = self.get_secret_hash(username)
            
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters=auth_params
            )
            
            # Handle password change challenge
            if 'ChallengeName' in response and response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                return 'PASSWORD_RESET_REQUIRED', response['Session']
            
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
    
    def get_user_status(self, username):
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return True, response.get('UserStatus', 'UNKNOWN')
        except Exception as e:
            return False, f'Error getting user status: {str(e)}'
    
    def reset_password(self, username, new_password, session):
        try:
            challenge_params = {
                'USERNAME': username,
                'NEW_PASSWORD': new_password,
                'PASSWORD_PERMANENT': 'true'
            }
            
            if self.client_secret:
                challenge_params['SECRET_HASH'] = self.get_secret_hash(username)
            
            response = self.client.admin_respond_to_auth_challenge(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                Session=session,
                ChallengeResponses=challenge_params
            )
            
            if 'AuthenticationResult' in response:
                return True, response['AuthenticationResult']
            else:
                return False, 'Password reset failed'
                
        except Exception as e:
            return False, f'Password reset error: {str(e)}'
    
    def admin_set_permanent_password(self, username, password):
        try:
            self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=username,
                Password=password,
                Permanent=True
            )
            return True, 'Password set as permanent'
        except Exception as e:
            return False, f'Error setting permanent password: {str(e)}'
