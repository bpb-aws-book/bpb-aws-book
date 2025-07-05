import json
import os
import boto3
import pg8000
import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function that connects to PostgreSQL RDS using credentials from Secrets Manager
    and performs operations on books table.
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
        
        # Determine operation based on HTTP method
        http_method = event.get('httpMethod')
        print(f"Event: {json.dumps(event)}")
        
        # If direct invocation without httpMethod, check for body to determine if it's a POST
        if not http_method and event.get('body'):
            http_method = 'POST'
        
        if http_method == 'POST':
            # Handle POST request to create a new book
            try:
                # Parse request body
                body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
                name = body.get('name')
                description = body.get('description')
                author = body.get('author')
                price = body.get('price')
                
                # Validate required fields
                if not all([name, author, price]):
                    return {
                        'statusCode': 400,
                        'body': json.dumps({
                            'message': 'Name, author, and price are required fields'
                        })
                    }
                
                # Execute SQL query to insert a record
                cursor.execute(
                    "INSERT INTO public.books_book (name, description, author, price, is_rented, created_at, updated_at) VALUES ($1, $2, $3, $4, 'false', current_date, current_date) RETURNING id",
                    (name, description, author, price)
                )
                
                # Get the ID of the inserted record
                record_id = cursor.fetchone()[0]
                
                # Commit the transaction
                conn.commit()
                
                return {
                    'statusCode': 201,
                    'body': json.dumps({
                        'message': 'Book created successfully',
                        'id': record_id
                    })
                }
            except Exception as e:
                conn.rollback()
                print(f"Error creating book: {str(e)}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': f'Error creating book: {str(e)}'
                    })
                }
        else:  # Default to GET
            # Extract ID from the event (API Gateway path parameter)
            book_id = event.get('pathParameters', {}).get('id') if event.get('pathParameters') else event.get('id')
            if not book_id:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'ID is required'
                    })
                }
            
            # Execute SQL query to retrieve a record
            cursor.execute(
                "SELECT id, name, description, author, price, is_rented, created_at, updated_at FROM public.books_book WHERE id = $1",
                (book_id,)
            )
            
            # Get the record
            record = cursor.fetchone()
            
            if not record:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'message': 'Book not found'
                    })
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'id': record[0],
                    'name': record[1],
                    'description': record[2],
                    'author': record[3],
                    'price': float(record[4]),
                    'is_rented': record[5],
                    'created_at': record[6].isoformat() if record[6] else None,
                    'updated_at': record[7].isoformat() if record[7] else None
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
