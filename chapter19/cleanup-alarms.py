#!/usr/bin/env python3
import boto3

def delete_autoscaling_alarms(table_name):
    """Delete CloudWatch alarms created by DynamoDB autoscaling"""
    cloudwatch = boto3.client('cloudwatch')
    
    # Get all alarms
    response = cloudwatch.describe_alarms()
    
    # Filter alarms related to the table
    table_alarms = [
        alarm['AlarmName'] for alarm in response['Alarms']
        if table_name in alarm['AlarmName'] and 
        ('TargetTracking' in alarm['AlarmName'] or 'DynamoDB' in alarm.get('Namespace', ''))
    ]
    
    if table_alarms:
        cloudwatch.delete_alarms(AlarmNames=table_alarms)
        print(f"Deleted {len(table_alarms)} alarms for table {table_name}")
    else:
        print(f"No autoscaling alarms found for table {table_name}")

if __name__ == "__main__":
    delete_autoscaling_alarms("ChatMessages")
