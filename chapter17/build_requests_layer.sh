#!/bin/bash

# Create requests Lambda layer
echo "Creating requests Lambda layer..."

# Create directory structure
mkdir -p layers/requests/python

# Install requests library
pip install requests -t layers/requests/python/

# Create zip file for the layer
cd layers/requests
zip -r requests-layer.zip python/
cd ../..

echo "Requests layer created successfully!"
echo "Layer zip file: layers/requests/requests-layer.zip"