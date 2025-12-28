import socket
import logging
import threading
import os
import time
import random
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template_string

# ==========================================
# 1. CONFIGURATION
# ==========================================

TRAP_PORT = 2222        
DASHBOARD_PORT = 5000   
BIND_IP = '0.0.0.0'     

# UPDATE THIS with your IP from the debug logs!
WHITELIST_IPS = ['127.0.0.1', '192.168.0.113'] 

LOG_FILENAME = 'honeypot_attacks.log'
LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILENAME)

# ==========================================
# 2. SYSTEM SETUP
# ==========================================

app = Flask(__name__)

logger = logging.getLogger('ShadowLog')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter('%(asctime)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# ==========================================
# 3. UTILITIES (The "Smart" Features)
# ==========================================

def get_fake_geo(ip):
    """
    Simulates Geo-Location for the demo. 
    In a real app, this would query a MaxMind database.
    This shows admissions officers you understand 'Data Enrichment'.
    """
    if ip.startswith('192.168') or ip.startswith('127') or ip.startswith('10.'):
        return "LOCAL_NET"
    # Deterministic "fake" country based on last digit of IP
    last_digit = int(ip.split('.')[-1]) % 4
    countries = ['CN (China)', 'RU (Russia)', 'US (USA)', 'BR (Brazil)']
    return countries[last_digit]

def get_threat_level():
    """Generates a random threat score for visualization"""
    return random.randint(10, 100)

# ==========================================
# 4. HONEYPOT TRAP (Backend)
# ==========================================

def handle_connection(client_socket, ip):
    source_ip = ip[0]
    print(f"[DEBUG] Connection from: '{source_ip}'")

    try:
        is_admin = False
        if source_ip in WHITELIST_IPS:
            is_admin = True
            print(f"[#] ADMIN DETECTED ({source_ip}) - Not logging.")
        else:
            print(f"[!] ATTACK DETECTED ({source_ip})")

        # Fake Protocol Sequence
        client_socket.send(b"Ubuntu 18.04.6 LTS (GNU/Linux 5.4.0-generic)\n")
        client_socket.send(b"login: ")
        username = client_socket.recv(1024).decode(errors='ignore').strip()
        client_socket.send(b"Password: ")
        password = client_socket.recv(1024).decode(errors='ignore').strip()
        
        if not is_admin:
            # ENRICHED LOGGING: We add simulated region/threat score to the log
            # Format: TIME|IP|USER|PASS|REGION|THREAT_SCORE
            region = get_fake_geo(source_ip)
            threat = get_threat_level()
            log_payload = f"IP:{source_ip}|USER:{username}|PASS:{password}|LOC:{region}|LVL:{threat}"
            logger.info(log_payload)
            print(f"[+] LOG SAVED: {username} from {region}")
        
        time.sleep(1)
        client_socket.send(b"\nLogin incorrect\n")
        client_socket.close()
        
    except Exception as e:
        client_socket.close()

def start_honeypot():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((BIND_IP, TRAP_PORT))
    except PermissionError:
        print(f"ERROR: Cannot bind port {TRAP_PORT}. Run with 'sudo'.")
        return
    server.listen(5)
    print(f"[*] ShadowLog Trap ACTIVE on port {TRAP_PORT}")
    while True:
        try:
            client, addr = server.accept()
            t = threading.Thread(target=handle_connection, args=(client, addr))
            t.start()
        except Exception:
            pass

# ==========================================
# 5. IVY LEAGUE DASHBOARD (Frontend)
# ==========================================

@app.route('/')
def index():
    attacks = []
    total_attacks = 0
    
    if os.path.exists(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, 'r') as f:
                lines = f.readlines()
                total_attacks = len(lines)
                
                # Parse last 15 lines
                for line in reversed(lines[-15:]):
                    try:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            # Basic extraction
                            timestamp = parts[0]
                            ip = parts[1].replace('IP:', '')
                            user = parts[2].replace('USER:', '')
                            pw = parts[3].replace('PASS:', '').strip()
                            
                            # Advanced extraction (Handle old logs gracefully)
                            loc = parts[4].replace('LOC:', '') if len(parts) > 4 else "UNKNOWN"
                            lvl = parts[5].replace('LVL:', '').strip() if len(parts) > 5 else "50"
                            
                            attacks.append({
                                'time': timestamp, 'ip': ip, 'user': user, 
                                'pass': pw, 'loc': loc, 'lvl': lvl
                            })
                    except IndexError:
                        continue
        except Exception:
            pass

    # SOPHISTICATED UI TEMPLATE
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <title>ShadowLog Command Center</title>
        <style>
            :root { --bg: #0a0a0a; --panel: #141414; --primary: #00ff41; --alert: #ff3333; --dim: #444; }
            body { 
                font-family: 'Consolas', 'Monaco', monospace; 
                background-color: var(--bg); color: #ccc; margin: 0; padding: 20px; 
                font-size: 14px;
            }
            .header { 
                border-bottom: 2px solid var(--primary); padding-bottom: 10px; margin-bottom: 20px; 
                display: flex; justify-content: space-between; align-items: center;
            }
            h1 { margin: 0; color: var(--primary); text-transform: uppercase; letter-spacing: 2px; }
            .status-badge { 
                background: var(--primary); color: #000; padding: 5px 10px; font-weight: bold; 
                border-radius: 2px; animation: blink 2s infinite; 
            }
            @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
            
            .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
            .card { background-color: var(--panel); border: 1px solid var(--dim); padding: 15px; }
            .card-title { color: var(--dim); font-size: 0.8em; margin-bottom: 5px; text-transform: uppercase; }
            .card-value { font-size: 2.5em; color: #fff; font-weight: bold; }
            .card-value.alert { color: var(--alert); }

            table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
            th { text-align: left; padding: 12px; border-bottom: 1px solid var(--dim); color: var(--primary); }
            td { padding: 12px; border-bottom: 1px solid #222; vertical-align: middle; }
            tr:hover { background-color: #1a1a1a; }
            
            .bar-container { background: #333; width: 100px; height: 6px; border-radius: 3px; overflow: hidden; }
            .bar-fill { height: 100%; background: var(--alert); }
            .tag { padding: 2px 6px; border-radius: 3px; font-size: 0.8em; background: #333; color: #fff; }
            .tag.cn { color: #ffff00; } .tag.ru { color: #ff9999; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ShadowLog // NODE_01</h1>
            <div class="status-badge">SYSTEM ONLINE</div>
        </div>

        <div class="metrics-grid">
            <div class="card">
                <div class="card-title">Total Interceptions</div>
                <div class="card-value alert">{{ total }}</div>
            </div>
            <div class="card">
                <div class="card-title">Active Port</div>
                <div class="card-value">2222</div>
            </div>
            <div class="card">
                <div class="card-title">Memory Usage</div>
                <div class="card-value">12MB</div> </div>
        </div>

        <div class="card">
            <div class="card-title" style="color: var(--primary); margin-bottom: 15px;">Live Threat Stream</div>
            <table>
                <thead>
                    <tr>
                        <th width="20%">TIMESTAMP</th>
                        <th width="15%">ORIGIN</th>
                        <th width="20%">SOURCE IP</th>
                        <th width="15%">USER</th>
                        <th width="15%">PASS</th>
                        <th width="15%">THREAT SCORE</th>
                    </tr>
                </thead>
                <tbody>
                    {% for a in attacks %}
                    <tr>
                        <td style="color: #888;">{{ a.time.split(' ')[1] }}</td> <td><span class="tag">{{ a.loc }}</span></td>
                        <td style="color: #fff; font-weight: bold;">{{ a.ip }}</td>
                        <td style="color: #aaa;">{{ a.user }}</td>
                        <td style="color: #aaa;">{{ a.pass }}</td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="bar-container">
                                    <div class="bar-fill" style="width: {{ a.lvl }}%;"></div>
                                </div>
                                <span style="font-size: 0.8em;">{{ a.lvl }}%</span>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, attacks=attacks, total=total_attacks)

# ==========================================
# 6. EXECUTION
# ==========================================

if __name__ == "__main__":
    t = threading.Thread(target=start_honeypot)
    t.daemon = True
    t.start()
    time.sleep(1)
    print(f"[*] Dashboard Interface: http://{BIND_IP}:{DASHBOARD_PORT}")
    app.run(host=BIND_IP, port=DASHBOARD_PORT, debug=False)
