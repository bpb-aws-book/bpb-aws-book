#!/usr/bin/env python3
import boto3
import time
import threading
from datetime import datetime

def execute_load_test():
    """Generate sustained write load for 3+ minutes to trigger autoscaling"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ChatMessages')
    
    def write_worker(duration_seconds=200):
        start_time = time.time()
        counter = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                table.put_item(
                    Item={
                        'SessionId': f'sustained-{threading.current_thread().ident}',
                        'Timestamp': int(time.time() * 1000) + counter,
                        'Sender': 'load-test',
                        'Message': f'Sustained load message {counter}',
                        'MessageType': 'sustained-test'
                    }
                )
                counter += 1
                time.sleep(0.8)  # Write every 0.8 seconds to stay just above 1 WCU
            except Exception as e:
                print(f"{datetime.now()}: Write error: {e}")
                time.sleep(1)  # Wait before retrying
    
    print(f"{datetime.now()}: Starting sustained load test for 3+ minutes...")
    
    # Start 2 threads to generate consistent load above 80% of 1 WCU
    threads = []
    for i in range(2):
        t = threading.Thread(target=write_worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"{datetime.now()}: Sustained load test completed. Check CloudWatch for scaling activity.")

if __name__ == "__main__":
    execute_load_test()
