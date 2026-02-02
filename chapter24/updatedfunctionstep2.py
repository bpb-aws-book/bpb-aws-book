import boto3
import pandas as pd

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket='bucket-name', Key='SampleDataFile.csv')
    df = pd.read_csv(obj['Body'])

    author = df[df['book'] == 'Code Complete']['author'].values[0]
    print(author)

    return {
        'statusCode': 200,
        'body': 'hello world'
    }
