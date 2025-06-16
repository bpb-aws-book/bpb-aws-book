import json
import os
import boto3
import pg8000
import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function that connects to PostgreSQL RDS using credentials from Secrets Manager
    and adds a record to a table.
    """
    # Get environment variables
    secret_arn = os.environ['SECRET_ARN']
    db_name = os.environ['DB_NAME']
    db_host = os.environ['DB_HOST']
    db_port = os.environ['DB_PORT']
    
    # Get database credentials from Secrets Manager
    credentials = get_secret(secret_arn)
    
    try:
        # Connect to PostgreSQL using pg8000
        conn = pg8000.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=credentials['username'],
            password=credentials['password']
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Extract data from the event
        data = event.get('data', {})
        name = data.get('name', 'Default Name')
        description = data.get('description', 'Default Description')
        author = data.get('author', 'Default Author')
        price = data.get('price', 0)
        current_date = datetime.datetime.now().date()
        
        # Execute SQL query to insert a record
        cursor.execute(
            "INSERT INTO books_book (name, description, author, price, is_rented, created_at, updated_at) VALUES ($1, $2, $3, $4, 'false', current_date, current_date) RETURNING id",
            (name, description, author, price)
        )
        
        # Get the ID of the inserted record
        record_id = cursor.fetchone()[0]
        
        # Commit the transaction
        conn.commit()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Record added successfully',
                'id': record_id
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }
    
    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_secret(secret_arn):
    """
    Retrieve and decrypt the secret from AWS Secrets Manager
    """
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
    except ClientError as e:
        raise e
    
    # Decrypts secret using the associated KMS key
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)
