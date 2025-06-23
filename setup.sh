#!/bin/bash

# SSH Server Python Setup Script
echo "Setting up SSH Server with Tunneling Support..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To start the SSH server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the server: python ssh_server.py"
echo ""
echo "To test tunneling:"
echo "  Local port forward: ssh -L 1521:localhost:1521 admin@localhost -p 2222"
echo "  Remote port forward: ssh -R 8080:localhost:80 admin@localhost -p 2222"
echo "  SOCKS proxy: ssh -D 1080 admin@localhost -p 2222"
echo ""
echo "Default credentials: admin / admin"
echo "Port: 2222"
