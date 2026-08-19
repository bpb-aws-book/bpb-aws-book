#!/bin/bash -xe

# Fetch IMDSv2 token and public IP
METADATATOKEN=$(curl -sf -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
EC2PUBLICIPV4=$(curl -sf "http://169.254.169.254/latest/meta-data/public-ipv4" -H "X-aws-ec2-metadata-token: $METADATATOKEN")

# Validate we got an IP address
if [[ ! "$EC2PUBLICIPV4" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "ERROR: Failed to retrieve a valid public IP. Got: $EC2PUBLICIPV4"
    exit 1
fi

echo "Updating ALLOWED_HOSTS with public IP: $EC2PUBLICIPV4"

# Update Django settings with the new public IP
cd /home/ec2-user/inquisitive_bookworm_club/inquisitive_bookworm_club_project
sed -i "/ALLOWED_HOSTS/c\ALLOWED_HOSTS = ['${EC2PUBLICIPV4}','localhost']" settings.py

# Restart Gunicorn to apply changes
systemctl restart gunicorn
