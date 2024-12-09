#!/bin/bash
METADATATOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
EC2PUBLICIPV4=$(curl http://169.254.169.254/latest/meta-data/public-ipv4 -H "X-aws-ec2-metadata-token: $METADATATOKEN")
cd /home/ec2-user/inquisitive_bookworm_club/inquisitive_bookworm_club_project
sudo sed -i "/ALLOWED_HOSTS/c\ALLOWED_HOSTS = ['EC2PUBLICIPV4','localhost']" settings.py
sudo sed -i 's/EC2PUBLICIPV4/'${EC2PUBLICIPV4}'/g' settings.py
sudo systemctl restart gunicorn