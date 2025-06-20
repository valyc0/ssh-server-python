#!/bin/bash

# Script per avviare il server SSH con configurazione personalizzata

echo "=== SSH Server Configurator ==="
echo

# Chiedi la porta se non è specificata come argomento
if [ -z "$1" ]; then
    read -p "Inserisci la porta del server SSH (default: 2222): " PORT
    PORT=${PORT:-2222}
else
    PORT=$1
fi

# Chiedi la directory base se non specificata come secondo argomento
if [ -z "$2" ]; then
    read -p "Inserisci la directory base (default: /workspace/db-ready): " BASE_DIR
    BASE_DIR=${BASE_DIR:-/workspace/db-ready}
else
    BASE_DIR=$2
fi

# Chiedi username se non specificato come terzo argomento
if [ -z "$3" ]; then
    read -p "Inserisci username (default: admin): " USERNAME
    USERNAME=${USERNAME:-admin}
else
    USERNAME=$3
fi

# Chiedi password se non specificata come quarto argomento
if [ -z "$4" ]; then
    read -p "Inserisci password (default: admin): " PASSWORD
    PASSWORD=${PASSWORD:-admin}
else
    PASSWORD=$4
fi

echo
echo "=== Configurazione SSH Server ==="
echo "Porta: $PORT"
echo "Directory base: $BASE_DIR"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
echo

# Crea il file di configurazione
cat > config.ini << EOF
[SERVER]
host = 127.0.0.1
port = $PORT
host_key_file = host_key

[AUTH]
username = $USERNAME
password = $PASSWORD

[DIRECTORIES]
base_directory = $BASE_DIR
allowed_directories = $BASE_DIR,/tmp,/home

[TUNNELING]
enable_port_forwarding = true
allowed_hosts = localhost,127.0.0.1,0.0.0.0
allowed_ports = 1024-65535
EOF

echo "File config.ini creato con successo!"
echo

# Installa le dipendenze se necessario
if ! python3 -c "import paramiko" 2>/dev/null; then
    echo "Installazione di paramiko..."
    pip3 install paramiko
fi

echo "Avvio del server SSH..."
echo "Per connetterti usa: ssh -p $PORT $USERNAME@127.0.0.1"
echo "Password: $PASSWORD"
echo
echo "Premi Ctrl+C per fermare il server"
echo

# Avvia il server
python3 ssh_server.py
