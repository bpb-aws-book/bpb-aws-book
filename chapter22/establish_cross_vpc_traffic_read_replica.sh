#!/bin/bash

# Variables - replace with your actual values
SOURCE_REGION="us-east-1"
TARGET_REGION="us-west-2"  # Region where read replica is deployed

# Get SOURCE_VPC_ID from CloudFormation export
SOURCE_VPC_ID=$(aws cloudformation list-exports \
  --query "Exports[?Name=='BPBBookVPCForLearning'].Value" \
  --output text \
  --region $SOURCE_REGION)

# Get PEERING_CONNECTION_ID from CloudFormation export
PEERING_CONNECTION_ID=$(aws cloudformation list-exports \
  --query "Exports[?Name=='ReadReplicaVPCPeeringConnection'].Value" \
  --output text \
  --region $TARGET_REGION)

# Get source RDS security group ID from CloudFormation export
SOURCE_RDS_SG_ID=$(aws cloudformation list-exports \
  --query "Exports[?Name=='BPBBookRDSSecurityGroup'].Value" \
  --output text \
  --region $SOURCE_REGION)

# Accept the peering connection in the source region
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id $PEERING_CONNECTION_ID \
  --region $SOURCE_REGION \
  --output text > /dev/null
echo "Accepted peering connection $PEERING_CONNECTION_ID"

# Get route table IDs for the source VPC
ROUTE_TABLES=$(aws ec2 describe-route-tables \
  --filters "Name=vpc-id,Values=$SOURCE_VPC_ID" \
  --query "RouteTables[].RouteTableId" \
  --output text \
  --region $SOURCE_REGION)

# Add route to destination VPC CIDR for each route table
for RT_ID in $ROUTE_TABLES; do
  aws ec2 create-route \
    --route-table-id $RT_ID \
    --destination-cidr-block 192.168.0.0/16 \
    --vpc-peering-connection-id $PEERING_CONNECTION_ID \
    --region $SOURCE_REGION
  echo "Added route to $RT_ID"
done

# Add outbound rule to source RDS security group for read replica access
aws ec2 authorize-security-group-egress \
  --group-id $SOURCE_RDS_SG_ID \
  --protocol tcp \
  --port 5432 \
  --cidr 192.168.0.0/16 \
  --region $SOURCE_REGION
echo "Added outbound rule to source RDS security group"
