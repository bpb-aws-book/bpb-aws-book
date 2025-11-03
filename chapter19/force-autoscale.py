#!/usr/bin/env python3
import boto3
import threading
import time

def write_load_test():
    """Generate high write load to trigger autoscaling"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ChatMessages')
    
    def write_worker():
        for i in range(100):
            try:
                table.put_item(
                    Item={
                        'SessionId': f'load-test-{threading.current_thread().ident}',
                        'Timestamp': int(time.time() * 1000) + i,
                        'Sender': 'load-test',
                        'Message': f'Load test message {i}',
                        'MessageType': 'test'
                    }
                )
            except Exception as e:
                print(f"Write error: {e}")
    
    # Start multiple threads to exceed 80% WCU utilization
    threads = []
    for _ in range(5):
        t = threading.Thread(target=write_worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("Load test completed. Check CloudWatch metrics for autoscaling.")

if __name__ == "__main__":
    write_load_test()
