#!/bin/bash

# SSH Server Python - Deployment Script
# This script builds and deploys the SSH server using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Starting SSH Server deployment..."

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs keys

# Check if config file exists
if [ ! -f config.ini ]; then
    print_warning "config.ini not found. Creating default configuration..."
    ./setup.sh
fi

# Check if SSH host key exists
if [ ! -f ssh_host_key ]; then
    print_warning "SSH host key not found. Generating new key..."
    ssh-keygen -t rsa -b 2048 -f ssh_host_key -N ""
    print_success "SSH host key generated."
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start the service
print_status "Building Docker image..."
docker-compose build --no-cache

print_status "Starting SSH server..."
docker-compose up -d

# Wait for service to be ready
print_status "Waiting for service to be ready..."
sleep 10

# Check if service is running
if docker-compose ps | grep -q "Up"; then
    print_success "SSH server is running successfully!"
    print_status "Service details:"
    docker-compose ps
    echo
    print_status "You can now connect to the SSH server on port 2222"
    print_status "Check logs with: docker-compose logs -f"
    print_status "Stop service with: docker-compose down"
else
    print_error "Failed to start SSH server. Check logs:"
    docker-compose logs
    exit 1
fi
