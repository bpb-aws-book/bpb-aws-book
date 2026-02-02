import boto3
def lambda_handler(event, context):
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        print(bucket['Name'])
    return {
        'statusCode': 200,
        'body': 'hello world'
    }
