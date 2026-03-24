import os


def handler(event, context):
    token = event.get("authorizationToken", "")
    method_arn = event.get("methodArn", "")
    expected = os.environ.get("AUTH_TOKEN", "")

    if token == expected and expected:
        return _generate_policy("user", "Allow", method_arn)

    return _generate_policy("user", "Deny", method_arn)


def _generate_policy(principal_id, effect, resource):
    # Allow access to all methods/resources under this API
    arn_parts = resource.split(":")
    region = arn_parts[3]
    account_id = arn_parts[4]
    api_gateway_arn = arn_parts[5].split("/")
    api_id = api_gateway_arn[0]
    stage = api_gateway_arn[1]
    wildcard_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/{stage}/*"

    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": wildcard_arn,
                }
            ],
        },
    }
