#!/bin/bash
# Script to build the Lambda layer with pg8000 for Python 3.12

# Create directory structure
mkdir -p ./layer/python

# Use Docker to build in Amazon Linux 2 environment
docker run --rm -v $(pwd):/var/task amazon/aws-lambda-python:3.12 \
  /bin/bash -c "
    # Install pg8000 into the layer directory
    pip install pg8000 -t /var/task/layer/python
    
    # Fix permissions
    chown -R $(id -u):$(id -g) /var/task/layer
  "

# Create zip file for the layer
cd layer
zip -r ../pg8000-layer.zip .
cd ..

# Copy the layer to the src directory
mkdir -p ./src/python
cp -r ./layer/python/* ./src/python/

echo "Layer built successfully at $(pwd)/pg8000-layer.zip"
echo "Layer contents also copied to ./src/python/ for SAM deployment"
