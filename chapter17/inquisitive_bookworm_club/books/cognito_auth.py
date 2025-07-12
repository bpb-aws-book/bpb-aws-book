import boto3
import hmac
import hashlib
import base64
from django.conf import settings
from warrant import Cognito

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
            cognito = Cognito(
                user_pool_id=self.user_pool_id,
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=username
            )
            
            cognito.authenticate(password=password)
            
            if cognito.access_token:
                return True, {'AccessToken': cognito.access_token}
            else:
                return False, 'Authentication failed'
                
        except Exception as e:
            error_msg = str(e)
            if 'PasswordResetRequiredException' in error_msg:
                return 'PASSWORD_RESET_REQUIRED', username
            elif 'UserNotConfirmedException' in error_msg:
                return 'FORCE_CHANGE_PASSWORD', username
            return False, f'Authentication error: {error_msg}'
    
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
