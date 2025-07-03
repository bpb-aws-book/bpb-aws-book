#!/bin/bash
# Script to build the Lambda layer with pg8000 for Python 3.12

# Create directory structure
mkdir -p ./layer/python

# Install pg8000 directly (no Docker)
pip install pg8000 -t ./layer/python

# Check if installation was successful
if [ ! "$(ls -A ./layer/python)" ]; then
  echo "Error: pg8000 installation failed. Layer directory is empty."
  exit 1
fi

# Create zip file for the layer
cd ./layer
zip -r ../pg8000-layer.zip .
cd ..

#if we add a layer manually, we could ignore the rest of the script
# Verify zip file was created and is not empty
if [ ! -s ./pg8000-layer.zip ]; then
  echo "Error: Generated zip file is empty."
  exit 1
fi

# Copy the layer to the src directory
mkdir -p ./src/python
cp -r ./layer/python/* ./src/python/

echo "Layer built successfully at $(pwd)/pg8000-layer.zip"
echo "Layer contents also copied to ./src/python/ for SAM deployment"