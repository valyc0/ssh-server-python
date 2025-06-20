#!/bin/bash

echo "=== SSH Server con Tunneling - Test Script ==="
echo

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}1. Avvio server SSH...${NC}"
cd /workspace/db-ready/ssh-server

# Ferma server esistente se in esecuzione
pkill -f ssh_server.py 2>/dev/null

# Avvia il server in background
python3 ssh_server.py &
SERVER_PID=$!
echo "Server SSH avviato con PID: $SERVER_PID"

sleep 3

echo -e "${YELLOW}2. Verifica che il server sia in ascolto...${NC}"
if ss -tulpn | grep -q ":2222"; then
    echo -e "${GREEN}✓ Server in ascolto sulla porta 2222${NC}"
else
    echo -e "${RED}✗ Server non in ascolto${NC}"
    exit 1
fi

echo -e "${YELLOW}3. Test connessione SSH base...${NC}"
if timeout 10 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p 2222 admin@127.0.0.1 "echo 'SSH connection working'" 2>/dev/null; then
    echo -e "${GREEN}✓ Connessione SSH funziona${NC}"
else
    echo -e "${RED}✗ Connessione SSH fallita${NC}"
fi

echo
echo -e "${YELLOW}4. Esempi di comando per tunnel:${NC}"
echo
echo "📡 LOCAL PORT FORWARDING (porta locale → server remoto tramite SSH):"
echo "   ssh -L 8080:127.0.0.1:80 -p 2222 admin@127.0.0.1"
echo "   (Collega porta locale 8080 a porta 80 del server)"
echo
echo "📡 REMOTE PORT FORWARDING (porta remota → server locale tramite SSH):"
echo "   ssh -R 9090:127.0.0.1:8080 -p 2222 admin@127.0.0.1"
echo "   (Espone porta locale 8080 sulla porta remota 9090)"
echo
echo "📡 DYNAMIC PORT FORWARDING (proxy SOCKS):"
echo "   ssh -D 1080 -p 2222 admin@127.0.0.1"
echo "   (Crea proxy SOCKS sulla porta 1080)"
echo
echo "📡 TUNNEL CON SHELL:"
echo "   ssh -L 8080:127.0.0.1:80 -p 2222 admin@127.0.0.1"
echo "   (Apre anche una shell interattiva)"
echo
echo "📡 TUNNEL SENZA SHELL:"
echo "   ssh -N -L 8080:127.0.0.1:80 -p 2222 admin@127.0.0.1"
echo "   (Solo tunnel, nessuna shell)"

echo
echo -e "${YELLOW}5. Test pratico di tunnel...${NC}"
echo "Avvio un server web locale per testare il tunnel..."

# Avvia un server HTTP semplice per il test
cd /workspace/db-ready
python3 -m http.server 8000 &
HTTP_PID=$!
echo "Server HTTP avviato sulla porta 8000 (PID: $HTTP_PID)"

sleep 2

echo "Test del tunnel: ssh -N -L 8080:127.0.0.1:8000 -p 2222 admin@127.0.0.1"
echo "Password: admin"
echo
echo "Una volta connesso il tunnel, potrai accedere a:"
echo "  http://127.0.0.1:8080  (tunnel) → http://127.0.0.1:8000 (server locale)"

echo
echo -e "${GREEN}Server SSH con tunneling pronto!${NC}"
echo
echo "Per fermare tutto:"
echo "  kill $SERVER_PID $HTTP_PID"

# Pulisci alla fine se interrotto
trap "kill $SERVER_PID $HTTP_PID 2>/dev/null; exit" INT TERM

# Mantieni lo script in esecuzione
echo "Premi Ctrl+C per fermare i server..."
wait
