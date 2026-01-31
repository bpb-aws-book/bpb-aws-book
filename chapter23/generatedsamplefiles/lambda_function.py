import json
import os
import boto3
import pg8000.native
import ssl

def lambda_handler(event, context):
    secret_arn = os.environ['SECRET_ARN']
    db_host = os.environ['DB_HOST']
    
    secrets_client = boto3.client('secretsmanager')
    secret = json.loads(secrets_client.get_secret_value(SecretId=secret_arn)['SecretString'])
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    conn = pg8000.native.Connection(
        user=secret['username'],
        password=secret['password'],
        host=db_host,
        port=5432,
        database='bpbbook',
        ssl_context=ssl_context
    )
    
    rows = conn.run("SELECT name, description, author, price, is_rented, created_at, updated_at FROM books_book")
    
    books = []
    for row in rows:
        books.append({
            'name': row[0].strip() if isinstance(row[0], str) else row[0],
            'description': row[1].strip() if isinstance(row[1], str) else row[1],
            'author': row[2].strip() if isinstance(row[2], str) else row[2],
            'price': str(row[3]),
            'is_rented': row[4],
            'created_at': row[5].isoformat() if row[5] else None,
            'updated_at': row[6].isoformat() if row[6] else None
        })
    
    conn.close()
    
    return {
        'statusCode': 200,
        'body': json.dumps({'books': books})
    }
