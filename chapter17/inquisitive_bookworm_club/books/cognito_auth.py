import boto3
from django.conf import settings

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID

    def authenticate(self, username, password):
        try:
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            return True, response.get('AuthenticationResult', {})
        except Exception as e:
            return False, str(e)