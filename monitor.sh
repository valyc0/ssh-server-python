#!/bin/bash

# SSH Server Python - Monitoring Script
# This script monitors the SSH server health and provides useful information

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

# Function to check if container is running
check_container() {
    if docker-compose ps | grep -q "Up"; then
        print_success "SSH server container is running"
        return 0
    else
        print_error "SSH server container is not running"
        return 1
    fi
}

# Function to check SSH port connectivity
check_ssh_port() {
    if nc -z localhost 2222 2>/dev/null; then
        print_success "SSH port 2222 is accessible"
        return 0
    else
        print_error "SSH port 2222 is not accessible"
        return 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Recent logs:"
    docker-compose logs --tail=20
}

# Function to show container stats
show_stats() {
    print_status "Container statistics:"
    docker stats ssh-tunnel-server --no-stream 2>/dev/null || print_warning "Container not found"
}

# Function to test SSH connection
test_ssh_connection() {
    print_status "Testing SSH connection..."
    python test_client.py 2>/dev/null && print_success "SSH connection test passed" || print_error "SSH connection test failed"
}

# Main monitoring function
main() {
    echo "======================================="
    echo "SSH Server Python - Health Monitor"
    echo "======================================="
    echo
    
    check_container
    container_running=$?
    
    if [ $container_running -eq 0 ]; then
        check_ssh_port
        test_ssh_connection
        echo
        show_stats
        echo
        show_logs
    else
        print_status "Attempting to show last logs..."
        show_logs
    fi
    
    echo
    print_status "Monitoring complete."
}

# Run monitoring
main
