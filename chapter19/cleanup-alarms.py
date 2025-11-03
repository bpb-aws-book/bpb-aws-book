#!/usr/bin/env python3
import boto3

def delete_autoscaling_alarms(table_name):
    """Delete CloudWatch alarms created by DynamoDB autoscaling"""
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        # Get all alarms
        response = cloudwatch.describe_alarms()
        
        # Get alarms list safely
        alarms = response.get('Alarms', [])
        
        if not alarms:
            print(f"No alarms found in the account")
            return
        
        # Filter alarms related to the table
        table_alarms = [
            alarm['AlarmName'] for alarm in alarms
            if table_name in alarm['AlarmName'] and 
            ('TargetTracking' in alarm['AlarmName'] or 'DynamoDB' in alarm.get('Namespace', ''))
        ]
        
        if table_alarms:
            cloudwatch.delete_alarms(AlarmNames=table_alarms)
            print(f"Deleted {len(table_alarms)} alarms for table {table_name}")
        else:
            print(f"No autoscaling alarms found for table {table_name}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        delete_autoscaling_alarms("ChatMessages")
    except Exception as e:
        print(f"Script error: {e}")
