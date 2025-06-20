import paramiko
import threading
import socket
import os
import sys
import time
import logging
from configparser import ConfigParser

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ssh_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SSHServerConfig:
    def __init__(self, config_file='config.ini'):
        self.config = ConfigParser()
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        self.config['SERVER'] = {
            'host': '127.0.0.1',
            'port': '2222',
            'host_key_file': 'host_key'
        }
        self.config['AUTH'] = {
            'username': 'admin',
            'password': 'admin'
        }
        self.config['DIRECTORIES'] = {
            'base_directory': '/workspace/db-ready',
            'allowed_directories': '/workspace/db-ready,/tmp,/home'
        }
        self.config['TUNNELING'] = {
            'enable_port_forwarding': 'true',
            'allowed_hosts': 'localhost,127.0.0.1,0.0.0.0',
            'allowed_ports': '1024-65535'
        }
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        logger.info(f"Created default config file: {self.config_file}")
    
    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)

class SSHServerInterface(paramiko.ServerInterface):
    def __init__(self, config):
        self.config = config
        
    def check_channel_request(self, kind, chanid):
        if kind in ('session', 'direct-tcpip'):
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_port_forward_request(self, address, port):
        """Consenti port forwarding per tutti gli indirizzi e porte"""
        logger.info(f"Port forward request: {address}:{port}")
        
        # Verifica se il tunneling è abilitato
        if not self.config.get('TUNNELING', 'enable_port_forwarding', 'true').lower() == 'true':
            logger.warning("Port forwarding disabled in config")
            return False
        
        # Verifica host consentiti
        allowed_hosts = self.config.get('TUNNELING', 'allowed_hosts', 'localhost,127.0.0.1').split(',')
        if address not in [h.strip() for h in allowed_hosts]:
            logger.warning(f"Host {address} not in allowed hosts: {allowed_hosts}")
            return False
            
        # Verifica porte consentite  
        allowed_ports = self.config.get('TUNNELING', 'allowed_ports', '1024-65535')
        if '-' in allowed_ports:
            min_port, max_port = map(int, allowed_ports.split('-'))
            if not (min_port <= port <= max_port):
                logger.warning(f"Port {port} not in allowed range: {allowed_ports}")
                return False
        
        logger.info(f"Port forward approved: {address}:{port}")
        return True
    
    def check_auth_password(self, username, password):
        expected_username = self.config.get('AUTH', 'username', 'admin')
        expected_password = self.config.get('AUTH', 'password', 'admin')
        
        if username == expected_username and password == expected_password:
            logger.info(f"Authentication successful for user: {username}")
            return paramiko.AUTH_SUCCESSFUL
        else:
            logger.warning(f"Authentication failed for user: {username}")
            return paramiko.AUTH_FAILED
    
    def get_allowed_auths(self, username):
        return 'password'
    
    def check_channel_shell_request(self, channel):
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

class SSHShell:
    def __init__(self, channel, config):
        self.channel = channel
        self.config = config
        self.current_dir = self.config.get('DIRECTORIES', 'base_directory', '/workspace/db-ready')
        self.allowed_dirs = [d.strip() for d in self.config.get('DIRECTORIES', 'allowed_directories', '/workspace/db-ready').split(',')]
        
    def is_allowed_directory(self, path):
        """Verifica se il percorso è in una directory consentita"""
        abs_path = os.path.abspath(path)
        for allowed in self.allowed_dirs:
            if abs_path.startswith(os.path.abspath(allowed)):
                return True
        return False
    
    def send_prompt(self):
        prompt = f"ssh-server:{self.current_dir}$ "
        self.channel.send(prompt)
    
    def handle_command(self, command):
        command = command.strip()
        if not command:
            return
        
        parts = command.split()
        cmd = parts[0].lower()
        
        try:
            if cmd == 'ls':
                self.cmd_ls(parts[1:])
            elif cmd == 'cd':
                self.cmd_cd(parts[1:])
            elif cmd == 'pwd':
                self.cmd_pwd()
            elif cmd == 'cat':
                self.cmd_cat(parts[1:])
            elif cmd == 'help':
                self.cmd_help()
            elif cmd == 'exit' or cmd == 'quit':
                self.channel.send("Goodbye!\r\n")
                return False
            elif cmd == 'mkdir':
                self.cmd_mkdir(parts[1:])
            elif cmd == 'rmdir':
                self.cmd_rmdir(parts[1:])
            elif cmd == 'touch':
                self.cmd_touch(parts[1:])
            elif cmd == 'rm':
                self.cmd_rm(parts[1:])
            else:
                self.channel.send(f"Command not found: {cmd}. Type 'help' for available commands.\r\n")
        except Exception as e:
            self.channel.send(f"Error: {str(e)}\r\n")
        
        return True
    
    def cmd_ls(self, args):
        try:
            target_dir = self.current_dir
            if args:
                target_dir = os.path.join(self.current_dir, args[0])
            
            if not self.is_allowed_directory(target_dir):
                self.channel.send("Permission denied: Directory not allowed\r\n")
                return
            
            if os.path.exists(target_dir) and os.path.isdir(target_dir):
                items = os.listdir(target_dir)
                items.sort()
                for item in items:
                    item_path = os.path.join(target_dir, item)
                    if os.path.isdir(item_path):
                        self.channel.send(f"{item}/\r\n")
                    else:
                        size = os.path.getsize(item_path)
                        self.channel.send(f"{item} ({size} bytes)\r\n")
            else:
                self.channel.send("Directory not found\r\n")
        except Exception as e:
            self.channel.send(f"Error listing directory: {str(e)}\r\n")
    
    def cmd_cd(self, args):
        if not args:
            target_dir = self.config.get('DIRECTORIES', 'base_directory', '/workspace/db-ready')
        else:
            if args[0].startswith('/'):
                target_dir = args[0]
            else:
                target_dir = os.path.join(self.current_dir, args[0])
        
        target_dir = os.path.abspath(target_dir)
        
        if not self.is_allowed_directory(target_dir):
            self.channel.send("Permission denied: Directory not allowed\r\n")
            return
        
        if os.path.exists(target_dir) and os.path.isdir(target_dir):
            self.current_dir = target_dir
            self.channel.send(f"Changed to: {self.current_dir}\r\n")
        else:
            self.channel.send("Directory not found\r\n")
    
    def cmd_pwd(self):
        self.channel.send(f"{self.current_dir}\r\n")
    
    def cmd_cat(self, args):
        if not args:
            self.channel.send("Usage: cat <filename>\r\n")
            return
        
        file_path = os.path.join(self.current_dir, args[0])
        
        if not self.is_allowed_directory(file_path):
            self.channel.send("Permission denied: File not in allowed directory\r\n")
            return
        
        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    self.channel.send(content + "\r\n")
            else:
                self.channel.send("File not found\r\n")
        except Exception as e:
            self.channel.send(f"Error reading file: {str(e)}\r\n")
    
    def cmd_mkdir(self, args):
        if not args:
            self.channel.send("Usage: mkdir <directory_name>\r\n")
            return
        
        dir_path = os.path.join(self.current_dir, args[0])
        
        if not self.is_allowed_directory(dir_path):
            self.channel.send("Permission denied: Directory not in allowed path\r\n")
            return
        
        try:
            os.makedirs(dir_path, exist_ok=True)
            self.channel.send(f"Directory created: {args[0]}\r\n")
        except Exception as e:
            self.channel.send(f"Error creating directory: {str(e)}\r\n")
    
    def cmd_rmdir(self, args):
        if not args:
            self.channel.send("Usage: rmdir <directory_name>\r\n")
            return
        
        dir_path = os.path.join(self.current_dir, args[0])
        
        if not self.is_allowed_directory(dir_path):
            self.channel.send("Permission denied: Directory not in allowed path\r\n")
            return
        
        try:
            os.rmdir(dir_path)
            self.channel.send(f"Directory removed: {args[0]}\r\n")
        except Exception as e:
            self.channel.send(f"Error removing directory: {str(e)}\r\n")
    
    def cmd_touch(self, args):
        if not args:
            self.channel.send("Usage: touch <filename>\r\n")
            return
        
        file_path = os.path.join(self.current_dir, args[0])
        
        if not self.is_allowed_directory(file_path):
            self.channel.send("Permission denied: File not in allowed directory\r\n")
            return
        
        try:
            with open(file_path, 'a'):
                pass
            self.channel.send(f"File created/touched: {args[0]}\r\n")
        except Exception as e:
            self.channel.send(f"Error creating file: {str(e)}\r\n")
    
    def cmd_rm(self, args):
        if not args:
            self.channel.send("Usage: rm <filename>\r\n")
            return
        
        file_path = os.path.join(self.current_dir, args[0])
        
        if not self.is_allowed_directory(file_path):
            self.channel.send("Permission denied: File not in allowed directory\r\n")
            return
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                self.channel.send(f"File removed: {args[0]}\r\n")
            else:
                self.channel.send("File not found or is not a regular file\r\n")
        except Exception as e:
            self.channel.send(f"Error removing file: {str(e)}\r\n")
    
    def cmd_help(self):
        help_text = """
Available commands:
  ls [directory]    - List directory contents
  cd [directory]    - Change directory
  pwd              - Print working directory  
  cat <filename>   - Display file contents
  mkdir <dirname>  - Create directory
  rmdir <dirname>  - Remove empty directory
  touch <filename> - Create empty file
  rm <filename>    - Remove file
  help             - Show this help
  exit/quit        - Close connection

Current directory: """ + self.current_dir + """
Allowed directories: """ + ", ".join(self.allowed_dirs) + """
\r\n"""
        self.channel.send(help_text)
    
    def run(self):
        self.channel.send("Welcome to SSH Server!\r\n")
        self.channel.send("Type 'help' for available commands.\r\n")
        self.send_prompt()
        
        command_buffer = ""
        
        while True:
            try:
                data = self.channel.recv(1024)
                if not data:
                    break
                
                char = data.decode('utf-8', errors='ignore')
                
                for c in char:
                    if c == '\r' or c == '\n':
                        self.channel.send("\r\n")
                        if command_buffer.strip():
                            if not self.handle_command(command_buffer):
                                break
                        command_buffer = ""
                        self.send_prompt()
                    elif c == '\x08' or c == '\x7f':  # Backspace
                        if command_buffer:
                            command_buffer = command_buffer[:-1]
                            self.channel.send('\x08 \x08')
                    elif c == '\x03':  # Ctrl+C
                        self.channel.send("^C\r\n")
                        command_buffer = ""
                        self.send_prompt()
                    elif ord(c) >= 32:  # Printable characters
                        command_buffer += c
                        self.channel.send(c)
                        
            except Exception as e:
                logger.error(f"Error in shell: {str(e)}")
                break
        
        self.channel.close()

class SSHServer:
    def __init__(self, config_file='config.ini'):
        self.config = SSHServerConfig(config_file)
        self.host_key = None
        self.setup_host_key()
    
    def setup_host_key(self):
        host_key_file = self.config.get('SERVER', 'host_key_file', 'host_key')
        
        if os.path.exists(host_key_file):
            try:
                self.host_key = paramiko.RSAKey(filename=host_key_file)
                logger.info(f"Loaded existing host key from {host_key_file}")
            except Exception as e:
                logger.error(f"Error loading host key: {e}")
                self.generate_host_key(host_key_file)
        else:
            self.generate_host_key(host_key_file)
    
    def generate_host_key(self, filename):
        try:
            key = paramiko.RSAKey.generate(2048)
            key.write_private_key_file(filename)
            self.host_key = key
            logger.info(f"Generated new host key: {filename}")
        except Exception as e:
            logger.error(f"Error generating host key: {e}")
            sys.exit(1)
    
    def handle_tunnel(self, transport, channel):
        """Gestisce i tunnel TCP/IP"""
        try:
            # Per tunnel direct-tcpip
            if hasattr(channel, 'origin_addr'):
                logger.info(f"Handling tunnel from {channel.origin_addr} to {channel.dest_addr}")
            
            # Mantieni il canale aperto per il tunneling
            while not channel.closed:
                if channel.recv_ready():
                    data = channel.recv(1024)
                    if not data:
                        break
                    # Il tunneling viene gestito automaticamente da paramiko
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in tunnel: {str(e)}")
        finally:
            channel.close()

    def handle_client(self, client, addr):
        logger.info(f"New connection from {addr}")
        
        try:
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)
            
            server_interface = SSHServerInterface(self.config)
            
            transport.start_server(server=server_interface)
            
            # Wait for authentication
            event = threading.Event()
            transport.auth_timeout = 60
            
            # Gestisci multiple channel (shell + tunnel)
            channel = transport.accept(20)
            if channel is None:
                logger.warning("No channel received")
                return
            
            # Start shell
            shell = SSHShell(channel, self.config)
            shell.run()
            
        except Exception as e:
            logger.error(f"Error handling client {addr}: {str(e)}")
        finally:
            try:
                transport.close()
            except:
                pass
            client.close()
            logger.info(f"Connection closed for {addr}")
    
    def start(self):
        host = self.config.get('SERVER', 'host', '127.0.0.1')
        port = int(self.config.get('SERVER', 'port', '2222'))
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((host, port))
            server_socket.listen(100)
            
            logger.info(f"SSH Server started on {host}:{port}")
            logger.info(f"Username: {self.config.get('AUTH', 'username', 'admin')}")
            logger.info(f"Password: {self.config.get('AUTH', 'password', 'admin')}")
            logger.info(f"Base directory: {self.config.get('DIRECTORIES', 'base_directory', '/workspace/db-ready')}")
            
            while True:
                client, addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = SSHServer()
    server.start()
