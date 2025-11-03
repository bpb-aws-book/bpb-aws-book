#!/usr/bin/env python3
import boto3

def delete_autoscaling_alarms(table_name):
    """Delete CloudWatch alarms created by DynamoDB autoscaling"""
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        # Check current region
        print(f"Checking region: {cloudwatch._client_config.region_name}")
        
        print("Calling describe_alarms...")
        response = cloudwatch.describe_alarms()
        print(f"Response received: {type(response)}")
        
        alarms = response.get('Alarms', [])
        print(f"Total alarms found: {len(alarms)}")
        
        if not alarms:
            print("No alarms found in this region")
            return
        
        # Show all alarm names for debugging
        print("All alarm names:")
        for alarm in alarms[:5]:  # Show first 5
            print(f"  {alarm['AlarmName']}")
        
        table_alarms = [
            alarm['AlarmName'] for alarm in alarms
            if table_name in alarm['AlarmName']
        ]
        
        print(f"Alarms containing '{table_name}': {len(table_alarms)}")
        for alarm_name in table_alarms:
            print(f"  {alarm_name}")
        
        if table_alarms:
            cloudwatch.delete_alarms(AlarmNames=table_alarms)
            print(f"Deleted {len(table_alarms)} alarms for table {table_name}")
        else:
            print(f"No alarms found containing '{table_name}'")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # You can specify region if needed
    # delete_autoscaling_alarms("ChatMessages")
    import sys
    table_name = sys.argv[1] if len(sys.argv) > 1 else "ChatMessages"
    delete_autoscaling_alarms(table_name)
