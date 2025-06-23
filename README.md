# SSH Server with Tunneling Support

Un server SSH Python completo basato su AsyncSSH che supporta port forwarding e SOCKS proxy per creare tunnel sicuri. Perfetto per development, testing e tunneling sicuro di servizi.

## 🚀 Caratteristiche

- **Autenticazione password**: Username e password configurabili
- **Port Forwarding Locale**: `ssh -L localport:remotehost:remoteport`
- **Port Forwarding Remoto**: `ssh -R remoteport:localhost:localport`
- **SOCKS Proxy**: `ssh -D port` per proxy SOCKS5
- **Configurazione flessibile**: Tutte le impostazioni in `config.ini`
- **Logging completo**: Log delle connessioni e operazioni
- **Avvio automatico**: Script di start con controlli e setup automatico
- **Sicurezza**: Generazione automatica delle chiavi host SSH

## 📋 Prerequisiti

- Python 3.7 o superiore
- pip (Python package installer)
- Sistema Linux/Unix (testato su Ubuntu/Debian)

## 🔧 Installazione Rapida

### Metodo 1: Avvio Nativo

1. **Avvio diretto** (consigliato):
   ```bash
   cd /workspace/db-ready/ssh-server-python
   chmod +x start.sh
   ./start.sh
   ```
   Lo script si occuperà automaticamente di:
   - Creare il virtual environment
   - Installare le dipendenze
   - Verificare la configurazione
   - Avviare il server

2. **Setup manuale**:
   ```bash
   cd /workspace/db-ready/ssh-server-python
   chmod +x setup.sh
   ./setup.sh
   ```

### Metodo 2: Docker Deployment 🐳

1. **Deploy automatico** (consigliato):
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Docker Compose manuale**:
   ```bash
   # Build e avvio
   docker-compose up -d
   
   # Controlla stato
   docker-compose ps
   
   # Visualizza log
   docker-compose logs -f
   
   # Ferma il servizio
   docker-compose down
   ```

3. **Monitoraggio Docker**:
   ```bash
   chmod +x monitor.sh
   ./monitor.sh
   ```

#### Comandi Docker Utili

- **Build immagine**: `docker-compose build --no-cache`
- **Avvia servizio**: `docker-compose up -d`
- **Ferma servizio**: `docker-compose down`
- **Visualizza log**: `docker-compose logs -f ssh-server`
- **Riavvia servizio**: `docker-compose restart`
- **Aggiorna e riavvia**: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`

## ⚙️ Configurazione

Il file `config.ini` contiene tutte le impostazioni:

```ini
[server]
host = 0.0.0.0          # Indirizzo di binding (0.0.0.0 per tutte le interfacce)
port = 2222             # Porta SSH (default: 2222)
username = admin        # Username per l'autenticazione
password = admin        # Password per l'autenticazione
host_key_path = ssh_host_key  # Percorso della chiave host SSH

[forwarding]
allow_local_forwarding = true   # Permetti port forwarding locale
allow_remote_forwarding = true  # Permetti port forwarding remoto
allow_socks = true             # Permetti proxy SOCKS

[logging]
log_level = INFO        # Livello di logging (DEBUG, INFO, WARNING, ERROR)
log_file = ssh_server.log  # File di log
```

## Utilizzo

### Avvio del Server

```bash
# Attiva l'ambiente virtuale
source venv/bin/activate

# Avvia il server
python ssh_server.py

# Oppure con un file di configurazione specifico
python ssh_server.py custom_config.ini
```

### Esempi di Tunneling

#### 1. Local Port Forwarding
Espone una porta locale che redirige il traffico verso un host remoto:

```bash
# Redirige la porta locale 1521 verso localhost:1521 attraverso il server SSH
ssh -L 1521:localhost:1521 admin@localhost -p 2222

# Redirige la porta locale 3306 verso un database remoto
ssh -L 3306:database.example.com:3306 admin@localhost -p 2222
```

#### 2. Remote Port Forwarding
Espone una porta sul server SSH che redirige verso il client locale:

```bash
# Espone la porta 8080 sul server SSH che redirige verso localhost:80
ssh -R 8080:localhost:80 admin@localhost -p 2222

# Utile per esporre servizi locali attraverso il server SSH
ssh -R 9090:localhost:9090 admin@localhost -p 2222
```

#### 3. SOCKS Proxy
Crea un proxy SOCKS5 per routing dinamico:

```bash
# Crea un proxy SOCKS5 sulla porta locale 1080
ssh -D 1080 admin@localhost -p 2222

# Usa il proxy per navigare attraverso il server SSH
curl --socks5 localhost:1080 http://example.com
```

#### 4. Tunnel in Background
Per mantenere i tunnel attivi in background:

```bash
# Tunnel in background con autenticazione automatica
ssh -fN -L 1521:localhost:1521 admin@localhost -p 2222

# Parametri:
# -f: va in background
# -N: non eseguire comandi remoti
# -L: local port forwarding
```

## Casi d'Uso Comuni

### 1. Accesso a Database Remoti
```bash
# Tunnel per Oracle Database
ssh -L 1521:oracle-server:1521 admin@localhost -p 2222

# Tunnel per MySQL
ssh -L 3306:mysql-server:3306 admin@localhost -p 2222

# Tunnel per PostgreSQL
ssh -L 5432:postgres-server:5432 admin@localhost -p 2222
```

### 2. Accesso a Servizi Web
```bash
# Tunnel per servizio web interno
ssh -L 8080:internal-web:80 admin@localhost -p 2222

# Accesso a servizio HTTPS
ssh -L 8443:internal-web:443 admin@localhost -p 2222
```

### 3. Proxy per Navigazione
```bash
# Proxy SOCKS per navigazione sicura
ssh -D 1080 admin@localhost -p 2222

# Configura il browser per usare localhost:1080 come proxy SOCKS5
```

## Sicurezza

### Configurazioni Sicure

1. **Cambia credenziali default**:
   ```ini
   [server]
   username = your_username
   password = strong_password_here
   ```

2. **Limita l'accesso per IP**:
   ```ini
   [server]
   host = 127.0.0.1  # Solo connessioni locali
   ```

3. **Disabilita forwarding non necessario**:
   ```ini
   [forwarding]
   allow_local_forwarding = true
   allow_remote_forwarding = false
   allow_socks = false
   ```

### Monitoraggio

- I log sono salvati in `ssh_server.log`
- Tutte le connessioni e tentativi di autenticazione sono registrati
- Monitorare i file di log per attività sospette

```bash
# Monitora i log in tempo reale
tail -f ssh_server.log

# Cerca connessioni fallite
grep "Failed authentication" ssh_server.log

# Visualizza connessioni attive
grep "SSH connection from" ssh_server.log
```

## 🐛 Troubleshooting

### Problemi Comuni

1. **Porta già in uso**:
   ```
   Error: [Errno 98] Address already in use
   ```
   **Soluzione**: 
   ```bash
   # Trova il processo che usa la porta
   netstat -tulpn | grep :2222
   # Oppure cambia la porta nel config.ini
   ```

2. **Permessi file di log**:
   ```
   PermissionError: [Errno 13] Permission denied: 'ssh_server.log'
   ```
   **Soluzione**: 
   ```bash
   chmod 666 ssh_server.log
   # Oppure cambia il percorso del log nel config.ini
   ```

3. **Autenticazione fallita**:
   Verifica username e password nel `config.ini`.

4. **Virtual environment non trovato**:
   ```bash
   # Ricrea il virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Test di Connettività

```bash
# Test connessione SSH base
ssh admin@localhost -p 2222

# Test con verbose output per debugging
ssh -vvv admin@localhost -p 2222

# Test port forwarding locale
ssh -L 9999:localhost:22 admin@localhost -p 2222

# Test proxy SOCKS
ssh -D 1080 admin@localhost -p 2222
curl --socks5 localhost:1080 http://httpbin.org/ip
```

## 📦 Dipendenze Complete

Il file `requirements.txt` include:

```
asyncssh>=2.13.0       # Core SSH functionality
configparser           # Configuration file parsing
pathlib                # Path manipulation
logging                # Logging functionality
sys                    # System-specific parameters
os                     # Operating system interface
asyncio                # Asynchronous I/O
```

Tutte le dipendenze sono automaticamente installate dal script `start.sh`.

## 📁 Struttura File

```
ssh-server-python/
├── config.ini          # Configurazione del server
├── ssh_server.py       # Server SSH principale
├── requirements.txt    # Dipendenze Python
├── setup.sh           # Script di setup automatico
├── start.sh           # Script di avvio migliorato
├── test_client.py     # Client di test
├── README.md          # Questa documentazione
├── venv/              # Virtual environment (creato automaticamente)
├── ssh_host_key       # Chiave host SSH (generata automaticamente)
└── ssh_server.log     # File di log (creato automaticamente)
```

## 🔧 Comandi Utili

```bash
# Avvio del server
./start.sh

# Arresto del server
# Premi Ctrl+C o trova il PID e killalo
ps aux | grep ssh_server.py
kill <PID>

# Restart del server
pkill -f ssh_server.py && ./start.sh

# Verifica stato porta
netstat -tulpn | grep :2222

# Test di connessione rapido
echo "exit" | ssh admin@localhost -p 2222

# Verifica log errori
grep -i error ssh_server.log
```

## 📈 Performance e Limitazioni

- **Connessioni simultanee**: Supporta multiple connessioni concorrenti
- **Throughput**: Dipende dalla rete e dalle risorse di sistema
- **Protocolli supportati**: SSH-2 only (più sicuro)
- **Metodi di autenticazione**: Solo password (per semplicità)

## 🔐 Note di Sicurezza

Il server è progettato per essere sicuro per default:
- ✅ Non permette esecuzione di comandi arbitrari
- ✅ SCP è disabilitato per sicurezza
- ✅ Process factory disabilitato
- ✅ Solo tunneling e port forwarding sono permessi
- ✅ Logging completo di tutte le operazioni
- ✅ Generazione automatica delle chiavi host

### Raccomandazioni di Sicurezza

1. **Cambia sempre le credenziali default**
2. **Usa porte non standard** (evita 22, 2222)
3. **Limita l'accesso per IP** quando possibile
4. **Monitora i log regolarmente**
5. **Aggiorna regolarmente le dipendenze**

## 🤝 Contributi

Per modifiche avanzate:
1. Edita `ssh_server.py` 
2. Personalizza le classi `SSHServerAuth` e `SSHServerSession`
3. Aggiorna `requirements.txt` se aggiungi dipendenze
4. Testa accuratamente le modifiche
5. Aggiorna questa documentazione

## 📝 Changelog

- **v1.3**: Supporto Docker completo con deploy.sh e monitor.sh
- **v1.2**: Script di start migliorato con controlli e colori
- **v1.1**: Dipendenze complete in requirements.txt
- **v1.0**: Versione base con supporto completo SSH tunneling

---

**Autore**: SSH Server Python Team  
**Licenza**: MIT  
**Supporto**: Controllare i log per debugging
