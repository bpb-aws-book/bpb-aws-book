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
        
        response = self.client.initiate_auth(
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
            
    except self.client.exceptions.NotAuthorizedException as e:
        error_msg = str(e)
        if 'Password attempts exceeded' in error_msg or 'Temporary password has expired' in error_msg:
            return 'FORCE_CHANGE_PASSWORD', username
        return False, 'Invalid username or password'
    except self.client.exceptions.UserNotFoundException:
        return False, 'User not found'
    except self.client.exceptions.PasswordResetRequiredException:
        return 'PASSWORD_RESET_REQUIRED', username
    except Exception as e:
        return False, f'Authentication error: {str(e)}'
    
    def initiate_forgot_password(self, username):
        try:
            params = {'Username': username}
            if self.client_secret:
                params['SecretHash'] = self.get_secret_hash(username)
            
            self.client.forgot_password(
                ClientId=self.client_id,
                **params
            )
            return True, 'Password reset email sent'
        except Exception as e:
            return False, f'Error sending reset email: {str(e)}'
    
    def confirm_forgot_password(self, username, confirmation_code, new_password):
        try:
            params = {
                'Username': username,
                'ConfirmationCode': confirmation_code,
                'Password': new_password
            }
            if self.client_secret:
                params['SecretHash'] = self.get_secret_hash(username)
            
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                **params
            )
            return True, 'Password reset successful'
        except Exception as e:
            return False, f'Password reset error: {str(e)}'
        
    def reset_password(self, username, new_password, session):
        try:
            challenge_params = {
                'USERNAME': username,
                'NEW_PASSWORD': new_password
            }
            
            if self.client_secret:
                challenge_params['SECRET_HASH'] = self.get_secret_hash(username)
            
            response = self.client.respond_to_auth_challenge(
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
