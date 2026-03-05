import json
import os
import boto3
import pg8000
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function that connects to PostgreSQL RDS using credentials from Secrets Manager
    and retrieves books based on search criteria.

    Get all books: no parameters
    Get books by name: ?name=Clean Code
    Get rented books: ?is_rented=true
    Combined: ?name=Code&is_rented=false
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
        
        # Extract query parameters from the event
        query_params = event.get('queryStringParameters', {})
        name = query_params.get('name')
        is_rented = query_params.get('is_rented')
        
        # Build the SQL query dynamically based on provided parameters
        query = "SELECT id, name, description, author, price, is_rented, created_at, updated_at FROM books_book WHERE 1=1"
        params = []
        
        if name:
            query += " AND name ILIKE $" + str(len(params) + 1)
            params.append(f"%{name}%")
        
        if is_rented is not None:
            query += " AND is_rented = $" + str(len(params) + 1)
            params.append(is_rented.lower() == 'true')
        
        # Execute the query
        cursor.execute(query, tuple(params))
        
        # Fetch all results
        rows = cursor.fetchall()
        
        # Convert results to list of dictionaries
        books = []
        for row in rows:
            books.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'author': row[3],
                'price': float(row[4]),
                'is_rented': row[5],
                'created_at': row[6].isoformat() if row[6] else None,
                'updated_at': row[7].isoformat() if row[7] else None
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Books retrieved successfully',
                'count': len(books),
                'books': books
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
