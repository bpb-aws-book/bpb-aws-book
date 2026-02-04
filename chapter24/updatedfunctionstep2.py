import pandas as pd
import boto3

def lambda_handler(event, context):

    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket='ch2ch2-chapter24bucket-l4n4oqwlonql', Key='sampledatafile.csv')
    df = pd.read_csv(obj['Body'])

    author = df[df['book'] == 'Code Complete']['author'].values[0]
    print(author)
    return {'statusCode': 200, 'body': author}
