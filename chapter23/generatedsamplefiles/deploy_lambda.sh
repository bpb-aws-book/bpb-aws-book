#!/bin/bash

# Deployment script for Books Query Lambda Function on Amazon Linux 2023

set -e

REGION="us-east-1"

show_menu() {
    echo "=================================="
    echo "Books Query Lambda Deployment"
    echo "=================================="
    echo "1. Install Docker (requires sudo)"
    echo "2. Install SAM CLI (requires sudo)"
    echo "3. Build SAM application"
    echo "4. Deploy SAM application"
    echo "5. Remove SAM stack"
    echo "6. Full installation and deployment (1-4)"
    echo "7. Exit"
    echo "=================================="
}

install_docker() {
    echo "Installing Docker..."
    sudo yum update -y
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -a -G docker ec2-user
    echo "Docker installed. You may need to log out and back in for group changes to take effect."
    echo "Or run: newgrp docker"
}

install_sam_cli() {
    echo "Installing SAM CLI..."
    cd ~
    wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip
    unzip -o aws-sam-cli-linux-x86_64.zip -d sam-installation
    sudo ./sam-installation/install --update
    rm -rf sam-installation aws-sam-cli-linux-x86_64.zip
    echo "SAM CLI installed successfully."
}

build_sam() {
    echo "Building SAM application with container..."
    sam build --use-container --region $REGION
    echo "Build completed successfully."
}

deploy_sam() {
    echo "Deploying SAM application in guided mode..."
    sam deploy --guided --region $REGION --capabilities CAPABILITY_IAM
}

remove_stack() {
    read -p "Enter stack name to remove (default: books-query-lambda-stack): " stack_name
    stack_name=${stack_name:-books-query-lambda-stack}
    
    echo "Removing stack: $stack_name"
    aws cloudformation delete-stack --stack-name $stack_name --region $REGION
    echo "Waiting for stack deletion to complete..."
    aws cloudformation wait stack-delete-complete --stack-name $stack_name --region $REGION
    echo "Stack removed successfully."
}

full_deployment() {
    install_docker
    newgrp docker << END
    cd $(pwd)
    install_sam_cli
    build_sam
    deploy_sam
END
}

while true; do
    show_menu
    read -p "Select an option (1-7): " choice
    
    case $choice in
        1)
            install_docker
            ;;
        2)
            install_sam_cli
            ;;
        3)
            build_sam
            ;;
        4)
            deploy_sam
            ;;
        5)
            remove_stack
            ;;
        6)
            full_deployment
            ;;
        7)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please select 1-7."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
