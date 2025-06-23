#!/bin/bash

# SSH Server Python - Usage Examples
# This script shows practical examples of how to use the SSH server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${CYAN}=======================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}=======================================${NC}"
}

print_example() {
    echo -e "${BLUE}[EXAMPLE]${NC} $1"
    echo -e "${YELLOW}Command:${NC} $2"
    echo
}

print_note() {
    echo -e "${GREEN}[NOTE]${NC} $1"
    echo
}

# Main function
main() {
    print_header "SSH Server Python - Usage Examples"
    echo
    
    print_example "Local Port Forwarding (Forward local port 8080 to remote service)" \
        "ssh -L 8080:target-server:80 admin@localhost -p 2222"
    
    print_note "This forwards connections to localhost:8080 to target-server:80 through the SSH tunnel"
    
    print_example "Remote Port Forwarding (Expose local service on remote port)" \
        "ssh -R 9090:localhost:3000 admin@localhost -p 2222"
    
    print_note "This makes a local service on port 3000 available on the remote server's port 9090"
    
    print_example "SOCKS Proxy (Use SSH as a SOCKS5 proxy)" \
        "ssh -D 1080 admin@localhost -p 2222"
    
    print_note "This creates a SOCKS5 proxy on localhost:1080. Configure your browser to use this proxy."
    
    print_example "Combined Tunneling (Multiple forwards in one connection)" \
        "ssh -L 8080:web-server:80 -L 3306:db-server:3306 -D 1080 admin@localhost -p 2222"
    
    print_note "This creates multiple tunnels: web server, database, and SOCKS proxy all in one connection"
    
    print_example "Background Connection (Keep tunnel running in background)" \
        "ssh -f -N -L 8080:target-server:80 admin@localhost -p 2222"
    
    print_note "The -f flag runs SSH in background, -N means no command execution (tunnel only)"
    
    print_example "Test Connection (Quick connectivity test)" \
        "ssh admin@localhost -p 2222 'echo \"Connection successful!\"'"
    
    print_note "Note: Command execution is disabled for security, this will fail but test connectivity"
    
    echo -e "${CYAN}Advanced Usage:${NC}"
    echo
    
    print_example "Use with autossh for persistent tunnels" \
        "autossh -M 20000 -f -N -L 8080:target:80 admin@localhost -p 2222"
    
    print_example "SSH config file entry" \
        "Add to ~/.ssh/config:"
    
    echo "Host myserver"
    echo "    HostName localhost"
    echo "    Port 2222"
    echo "    User admin"
    echo "    LocalForward 8080 target-server:80"
    echo "    RemoteForward 9090 localhost:3000"
    echo "    DynamicForward 1080"
    echo
    
    print_note "Then simply use: ssh myserver"
    
    print_header "Testing Your Setup"
    echo
    
    echo -e "${YELLOW}1. Test basic connectivity:${NC}"
    echo "   nc -zv localhost 2222"
    echo
    
    echo -e "${YELLOW}2. Test SSH authentication:${NC}"
    echo "   echo 'exit' | ssh admin@localhost -p 2222"
    echo
    
    echo -e "${YELLOW}3. Test port forwarding:${NC}"
    echo "   ssh -L 8080:google.com:80 admin@localhost -p 2222 &"
    echo "   curl -H 'Host: google.com' http://localhost:8080"
    echo
    
    print_header "Troubleshooting"
    echo
    
    echo -e "${RED}Common Issues:${NC}"
    echo "• Connection refused: Check if server is running (./monitor.sh)"
    echo "• Permission denied: Verify username/password in config.ini"
    echo "• Port already in use: Change the port or kill existing process"
    echo "• Tunnel not working: Check firewall and target service availability"
    echo
    
    echo -e "${GREEN}Need help?${NC} Check the logs:"
    echo "• Docker: docker-compose logs -f"
    echo "• Native: tail -f ssh_server.log"
    echo
}

# Run examples
main
