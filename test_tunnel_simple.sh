#!/bin/bash

echo "=== Test Tunnel SSH Pratico ==="
echo

# Avvia un server web di test
echo "1. Avvio server web di test sulla porta 8000..."
cd /workspace/db-ready
python3 -m http.server 8000 &
HTTP_PID=$!
echo "   Server HTTP avviato (PID: $HTTP_PID)"

sleep 2

echo
echo "2. Creo tunnel SSH: porta locale 8080 → porta remota 8000"
echo "   Comando: ssh -N -L 8080:127.0.0.1:8000 -p 2222 admin@127.0.0.1"
echo "   Password: admin"
echo

# Test del tunnel (in background)
expect << 'EOF' &
spawn ssh -N -L 8080:127.0.0.1:8000 -p 2222 admin@127.0.0.1
expect "password:"
send "admin\r"
expect eof
EOF

TUNNEL_PID=$!
echo "   Tunnel SSH avviato (PID: $TUNNEL_PID)"

sleep 3

echo
echo "3. Test del tunnel..."
if curl -s http://127.0.0.1:8080 | grep -q "Directory listing"; then
    echo "   ✅ TUNNEL FUNZIONA! Connessione tramite tunnel riuscita"
    echo "   📡 http://127.0.0.1:8080 (tunnel) → http://127.0.0.1:8000 (server)"
else
    echo "   ❌ Tunnel non funziona o server non raggiungibile"
fi

echo
echo "4. Pulisco i processi di test..."
kill $HTTP_PID $TUNNEL_PID 2>/dev/null

echo "   Test completato!"
