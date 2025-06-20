#!/bin/bash

# Script per avviare il server SSH
echo "Avvio del server SSH Python..."

# Controlla se paramiko è installato
if ! python3 -c "import paramiko" 2>/dev/null; then
    echo "Installazione di paramiko..."
    pip3 install paramiko cryptography
fi

# Avvia il server
python3 ssh_server.py
