import pandas as pd
import boto3

def lambda_handler(event, context):

s3 = boto3.client('s3')
obj = s3.get_object(Bucket='your-bucket-name', Key='sampledatafile.csv')
df = pd.read_csv(obj['Body'])

author = df[df['book'] == 'Code Complete']['author'].values[0]
print(author)
