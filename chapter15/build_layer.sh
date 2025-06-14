#!/bin/bash
# Script to build the Lambda layer with psycopg2

# Create directory structure
mkdir -p ./layer/python

# Install dependencies into the layer directory
pip install -r ./src/python/requirements.txt -t ./layer/python

# Copy the layer to the src directory
cp -r ./layer/* ./src/

echo "Layer built successfully"
