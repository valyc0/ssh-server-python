#!/usr/bin/env python3
"""
SSH Server with Tunneling Support
Supports local/remote port forwarding and SOCKS proxy
"""

import asyncio
import asyncssh
import configparser
import logging
import sys
import os
from pathlib import Path


class SSHServerAuth(asyncssh.SSHServer):
    """SSH Server with password authentication"""
    
    def __init__(self, config):
        self.config = config
        self.username = config.get('server', 'username')
        self.password = config.get('server', 'password')
        
        # Configure forwarding options
        self.allow_local_forwarding = config.getboolean('forwarding', 'allow_local_forwarding', fallback=True)
        self.allow_remote_forwarding = config.getboolean('forwarding', 'allow_remote_forwarding', fallback=True)
        self.allow_socks = config.getboolean('forwarding', 'allow_socks', fallback=True)
        
    def connection_made(self, conn):
        """Called when a new SSH connection is made"""
        peer = conn.get_extra_info('peername')
        logging.info(f'SSH connection from {peer[0]}:{peer[1]}')
        
    def connection_lost(self, exc):
        """Called when an SSH connection is lost"""
        if exc:
            logging.error(f'SSH connection lost: {exc}')
        else:
            logging.info('SSH connection closed')
    
    def password_auth_supported(self):
        """Enable password authentication"""
        return True
        
    def validate_password(self, username, password):
        """Validate username and password"""
        if username == self.username and password == self.password:
            logging.info(f'Successful authentication for user: {username}')
            return True
        else:
            logging.warning(f'Failed authentication attempt for user: {username}')
            return False
            
    def session_requested(self):
        """Allow session requests for shell/exec"""
        return SSHServerSession()
        
    def server_requested(self, listen_host, listen_port):
        """Handle remote port forwarding requests"""
        if self.allow_remote_forwarding:
            logging.info(f"Remote port forwarding requested: {listen_host}:{listen_port}")
            return True
        else:
            logging.warning("Remote port forwarding denied")
            return False
            
    def connection_requested(self, dest_host, dest_port, orig_host, orig_port):
        """Handle local port forwarding requests"""
        if self.allow_local_forwarding:
            logging.info(f"Local port forwarding requested: {dest_host}:{dest_port}")
            return True
        else:
            logging.warning("Local port forwarding denied")
            return False


class SSHServerSession(asyncssh.SSHServerSession):
    """SSH Server Session Handler"""
    
    def __init__(self):
        self._process = None
        
    def connection_made(self, chan):
        """Called when a new SSH session channel is created"""
        self._chan = chan
        
    def shell_requested(self):
        """Handle shell requests - return a simple shell"""
        return True
        
    def exec_requested(self, command):
        """Handle exec requests"""
        logging.info(f'Exec request: {command}')
        return True
        
    def subsystem_requested(self, subsystem):
        """Handle subsystem requests (like SFTP)"""
        logging.info(f'Subsystem request: {subsystem}')
        return False
        
    def data_received(self, data, datatype):
        """Handle data received from client"""
        # Echo back the data for simple shell simulation
        if datatype == asyncssh.EXTENDED_DATA_STDERR:
            self._chan.write_stderr(data)
        else:
            # Simple echo for demonstration
            self._chan.write(f"Echo: {data}")
            
    def eof_received(self):
        """Handle EOF from client"""
        self._chan.exit(0)
        
    def break_received(self, msec):
        """Handle break signal"""
        return True


class TunnelingSSHServer:
    """Main SSH Server class with tunneling support"""
    
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file {self.config_file} not found")
            
        self.config.read(self.config_file)
        
        # Validate required sections
        required_sections = ['server', 'forwarding', 'logging']
        for section in required_sections:
            if not self.config.has_section(section):
                raise ValueError(f"Missing required section: {section}")
                
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('logging', 'log_level', fallback='INFO')
        log_file = self.config.get('logging', 'log_file', fallback='ssh_server.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def generate_host_key(self):
        """Generate SSH host key if it doesn't exist"""
        host_key_path = self.config.get('server', 'host_key_path')
        
        if not os.path.exists(host_key_path):
            logging.info(f"Generating new SSH host key: {host_key_path}")
            key = asyncssh.generate_private_key('ssh-rsa', key_size=2048)
            with open(host_key_path, 'wb') as f:
                f.write(key.export_private_key())
            os.chmod(host_key_path, 0o600)
        else:
            logging.info(f"Using existing SSH host key: {host_key_path}")
            
        return host_key_path
        
    async def start_server(self):
        """Start the SSH server"""
        host = self.config.get('server', 'host')
        port = self.config.getint('server', 'port')
        host_key_path = self.generate_host_key()
        
        # Server options
        server_options = {
            'server_host_keys': [host_key_path],
            'process_factory': None,  # Disable process creation for security
            'allow_scp': False,       # Disable SCP for security
        }
        
        try:
            # Create and start the SSH server
            server = await asyncssh.create_server(
                lambda: SSHServerAuth(self.config),
                host=host,
                port=port,
                **server_options
            )
            
            logging.info(f"SSH Server started on {host}:{port}")
            logging.info(f"Username: {self.config.get('server', 'username')}")
            logging.info(f"Password: {self.config.get('server', 'password')}")
            logging.info("Server supports:")
            logging.info(f"  - Local port forwarding: {self.config.getboolean('forwarding', 'allow_local_forwarding', fallback=True)}")
            logging.info(f"  - Remote port forwarding: {self.config.getboolean('forwarding', 'allow_remote_forwarding', fallback=True)}")
            logging.info(f"  - SOCKS proxy: {self.config.getboolean('forwarding', 'allow_socks', fallback=True)}")
            logging.info("Example tunnel commands:")
            logging.info(f"  Local port forward: ssh -L 1521:localhost:1521 admin@localhost -p {port}")
            logging.info(f"  Remote port forward: ssh -R 8080:localhost:80 admin@localhost -p {port}")
            logging.info(f"  SOCKS proxy: ssh -D 1080 admin@localhost -p {port}")
            
            # Keep the server running
            async with server:
                await server.wait_closed()
                
        except Exception as e:
            logging.error(f"Failed to start SSH server: {e}")
            raise


async def main():
    """Main function"""
    try:
        # Get config file path from command line or use default
        config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'
        
        # Create and start the SSH server
        ssh_server = TunnelingSSHServer(config_file)
        await ssh_server.start_server()
        
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
