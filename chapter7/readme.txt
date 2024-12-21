Review more advanced scalings scenario with the DB AMI. Reuses application code from Chapter 6.

Step 1: Use the first two CFN Templates from Chapter 6 to create VPC and DB and EC2 with DB connection. Then create AMI.
Step 2: Run third template to create running EC2 instance.  Then create AMI.
Step 3: Create ASG with ELB with that AMI.
Step 4: Scale it with the stress script.
