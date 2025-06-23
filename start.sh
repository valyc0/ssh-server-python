#!/bin/bash

# SSH Server Python - Start Script
# Questo script avvia il server SSH con supporto per tunneling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/venv"
CONFIG_FILE="${PROJECT_DIR}/config.ini"
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt"
LOG_FILE="${PROJECT_DIR}/ssh_server.log"

echo -e "${BLUE}=== SSH Server Python - Avvio ===${NC}"

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Errore: Python3 non trovato. Installare Python3 per continuare.${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment non trovato. Creazione in corso...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "${BLUE}Attivazione virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Install/update dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${BLUE}Installazione/aggiornamento dipendenze...${NC}"
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
else
    echo -e "${RED}Errore: File requirements.txt non trovato!${NC}"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Errore: File di configurazione $CONFIG_FILE non trovato!${NC}"
    exit 1
fi

# Show current configuration
echo -e "${GREEN}=== Configurazione Corrente ===${NC}"
echo -e "${BLUE}Host:${NC} $(grep '^host' $CONFIG_FILE | cut -d'=' -f2 | xargs)"
echo -e "${BLUE}Porta:${NC} $(grep '^port' $CONFIG_FILE | cut -d'=' -f2 | xargs)"
echo -e "${BLUE}Username:${NC} $(grep '^username' $CONFIG_FILE | cut -d'=' -f2 | xargs)"
echo -e "${BLUE}Password:${NC} $(grep '^password' $CONFIG_FILE | cut -d'=' -f2 | xargs)"
echo -e "${BLUE}Log File:${NC} $LOG_FILE"

# Check if another instance is running
PORT=$(grep '^port' $CONFIG_FILE | cut -d'=' -f2 | xargs)
if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo -e "${YELLOW}Avviso: La porta $PORT sembra già in uso. Continuare? (y/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Operazione annullata.${NC}"
        exit 0
    fi
fi

echo -e "${GREEN}=== Avvio Server SSH ===${NC}"
echo -e "${BLUE}Premere Ctrl+C per fermare il server${NC}"
echo -e "${BLUE}Log in tempo reale: tail -f $LOG_FILE${NC}"
echo ""

# Start the SSH server
python3 ssh_server.py "$CONFIG_FILE"
