#!/bin/bash
# Script to build the Lambda layer with psycopg2 for Python 3.12

# Create directory structure
mkdir -p ./layer/python

# Use Docker to build in Amazon Linux 2 environment
docker run --rm -v $(pwd):/var/task amazon/aws-lambda-python:3.12 \
  /bin/bash -c "
    # Install build dependencies
    yum install -y postgresql-devel gcc python3-devel
    
    # Install psycopg2-binary into the layer directory
    pip install psycopg2-binary -t /var/task/layer/python
    
    # Fix permissions
    chown -R $(id -u):$(id -g) /var/task/layer
  "

# Create zip file for the layer
cd layer
zip -r ../psycopg2-layer.zip .
cd ..

# Copy the layer to the src directory
mkdir -p ./src/python
cp -r ./layer/python/* ./src/python/

echo "Layer built successfully at $(pwd)/psycopg2-layer.zip"
echo "Layer contents also copied to ./src/python/ for SAM deployment"
