# SSH Server in Python

Un server SSH implementato in Python con autenticazione e navigazione delle directory configurabile.

## Caratteristiche

- ✅ **Porta configurabile** tramite file `config.ini`
- ✅ **Autenticazione** con username/password (default: admin/admin)
- ✅ **Directory base configurabile** con restrizioni di sicurezza
- ✅ **Comandi shell** supportati: ls, cd, pwd, cat, mkdir, rmdir, touch, rm, help, exit
- ✅ **Logging** completo delle attività
- ✅ **Generazione automatica** delle chiavi host SSH
- ✅ **Supporto completo per SSH Tunneling** (Local, Remote, Dynamic Port Forwarding)

## Installazione

1. Clona il repository:
```bash
git clone https://github.com/valyc0/ssh-server-python.git
cd ssh-server-python
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Avvia il server:
```bash
python ssh_server.py
```

## Connessione

Connettiti al server SSH:
```bash
ssh admin@127.0.0.1 -p 2222
```

Password: `admin`

## Tunneling SSH

Il server supporta tutti i tipi di tunnel SSH:

### Local Port Forwarding
```bash
ssh -L 8080:127.0.0.1:80 -p 2222 admin@127.0.0.1
```

### Remote Port Forwarding
```bash
ssh -R 9090:127.0.0.1:8080 -p 2222 admin@127.0.0.1
```

### Dynamic Port Forwarding (SOCKS Proxy)
```bash
ssh -D 1080 -p 2222 admin@127.0.0.1
```

## Licenza

MIT License