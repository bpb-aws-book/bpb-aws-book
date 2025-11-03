#!/usr/bin/env python3
import boto3
import json
import time
from datetime import datetime
import uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChatMessages')

def add_message(session_id, sender, message, message_type='text'):
    """Add a message to the chat table"""
    timestamp = int(time.time() * 1000)  # milliseconds
    
    item = {
        'SessionId': session_id,
        'Timestamp': timestamp,
        'Sender': sender,  # 'user' or 'ai'
        'Message': message,
        'MessageType': message_type,
        'CreatedAt': datetime.utcnow().isoformat()
    }
    
    response = table.put_item(Item=item)
    print(f"Added message: {sender} - {message[:50]}...")
    return response

def populate_sample_data():
    """Populate table with sample chat conversations"""
    
    # Sample conversation 1
    session1 = str(uuid.uuid4())
    
    geographychat = [
        ('user', 'Which are the two largest continents in the world?'),
        ('ai', 'The two largest continents in the world are Asia with approximately 44.6 million square kilometers and Africa with approximately 30.3 million square kilometers'),
        ('user', 'Which of the two has larger population?'),
        ('ai', 'Asia has the larger population. Asia has approximately 4.7 billion people (about 60 percnt of the world\'s population while Africa has approximately 1.4 billion people about 18 percent of the world\'s population)')    ]
    
    for sender, message in geographychat:
        add_message(session1, sender, message)
        time.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Sample conversation 2
    session2 = str(uuid.uuid4())
    
    messages2 = [
        ('user', 'I need help with CloudFormation templates'),
        ('ai', 'I can help you with CloudFormation! What type of resources are you looking to create?'),
        ('user', 'I want to create a DynamoDB table with proper configuration'),
        ('ai', 'Here\'s what you\'ll need: define AttributeDefinitions, KeySchema, and consider BillingMode. Would you like me to show you an example?')
    ]
    
    for sender, message in messages2:
        add_message(session2, sender, message)
        time.sleep(0.1)

def query_messages(session_id):
    """Query all messages for a specific session"""
    response = table.query(
        KeyConditionExpression='SessionId = :session_id',
        ExpressionAttributeValues={':session_id': session_id}
    )
    
    print(f"\nMessages for session {session_id}:")
    for item in response['Items']:
        print(f"{item['Sender']}: {item['Message']}")
    
    return response['Items']

def scan_recent_messages(limit=10):
    """Scan for recent messages across all sessions"""
    response = table.scan(
        Limit=limit,
        ProjectionExpression='SessionId, Sender, Message, CreatedAt'
    )
    
    print(f"\nRecent {limit} messages:")
    for item in response['Items']:
        print(f"[{item['SessionId'][:8]}] {item['Sender']}: {item['Message'][:100]}")
    
    return response['Items']

if __name__ == "__main__":
    try:
        print("Populating ChatMessages table with sample data...")
        populate_sample_data()
        
        print("\nData population completed!")
        print("Scanning recent messages...")
        scan_recent_messages()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the DynamoDB table 'ChatMessages' exists and you have proper AWS credentials configured.")
