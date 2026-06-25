import os
import time
import json
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# ==========================================
# CORS — Allow all origins for your frontend
# ==========================================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ==========================================
# CONFIGURATION — Use /tmp for Vercel (read-only except /tmp)
# ==========================================
DB_PATH = "/tmp/vault.db"
GLOBAL_KEYS_VAULT = {}
GLOBAL_HISTORY_LOGS = []
SYSTEM_GLOBAL_MUTEX = True

MASTER_KEY = os.environ.get("MASTER_KEY", "vernex-6a9dc4fdd5923c40b0aba27bf1e39e3f")
API_BASE = "https://ft-osint-api.duckdns.org/api"

TOOLS_CONFIG = {
    "number": f"{API_BASE}/number",
    "vehicle": f"{API_BASE}/vehicle",
    "aadhar": f"{API_BASE}/aadhar",
    "family": f"{API_BASE}/adharfamily",
    "insta": f"{API_BASE}/insta",
    "email": f"{API_BASE}/email",
    "git": f"{API_BASE}/git",
    "tg": f"{API_BASE}/tg",
    "tgidinfo": f"{API_BASE}/tgidinfo",
    "bomber": f"{API_BASE}/bomber"
}

# ==========================================
# SELF-HEALING AGENT ENGINE
# ==========================================
def run_self_healing_agent(context_key=None, inbound_sync=None):
    global GLOBAL_KEYS_VAULT, SYSTEM_GLOBAL_MUTEX
    agent_report = []
    
    if inbound_sync and isinstance(inbound_sync, list):
        for item in inbound_sync:
            k_str = item.get("key")
            if k_str and k_str not in GLOBAL_KEYS_VAULT:
                GLOBAL_KEYS_VAULT[k_str] = item
                agent_report.append(f"Restored key node [{k_str}] from local ledger.")
    
    if not os.path.exists(DB_PATH) and GLOBAL_KEYS_VAULT:
        save_local_disk_db()
        agent_report.append("Rebuilt corrupted disk database file structure.")
        
    for route, endpoint in TOOLS_CONFIG.items():
        if "duckdns.org" not in endpoint:
            fixed = route if route != 'family' else 'adharfamily'
            TOOLS_CONFIG[route] = f"{API_BASE}/{fixed}"
            agent_report.append(f"Corrected broken upstream URI for {route}")

    if context_key and context_key in GLOBAL_KEYS_VAULT:
        target = GLOBAL_KEYS_VAULT[context_key]
        if "status" not in target:
            target["status"] = "on"
            agent_report.append(f"Healed missing state flags for [{context_key}].")
            
    if agent_report:
        print(f"[AGENT DIAGNOSTICS] {'; '.join(agent_report)}")
    return agent_report

# ==========================================
# DATABASE HELPERS
# ==========================================
def load_local_disk_db():
    global GLOBAL_KEYS_VAULT
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as f:
                GLOBAL_KEYS_VAULT = json.load(f)
        except Exception:
            pass

def save_local_disk_db():
    try:
        with open(DB_PATH, "w") as f:
            json.dump(GLOBAL_KEYS_VAULT, f)
    except Exception:
        pass

load_local_disk_db()

# ==========================================
# DATA CLEANING
# ==========================================
def clean_branding_data(data):
    data_str = json.dumps(data)
    data_str = data_str.replace("@ftgamer2", "shayan_explorer").replace("@FTgamer2", "shayan_explorer")
    data_str = data_str.replace("FTgamer2", "shayan_explorer").replace("ftgamer2", "shayan_explorer")
    data_str = data_str.replace("@bornex ultra", "shayan_explorer")
    data_str = data_str.replace("https://t.me/lynx_api", "https://t.me/shayan_explorer_channel")
    data_str = data_str.replace("https://t.me/FTgamer2", "https://t.me/shayan_explorer_channel")
    
    cleaned = json.loads(data_str)
    if isinstance(cleaned, dict):
        cleaned["by"] = "shayan_explorer"
        cleaned["channel"] = "https://t.me/shayan_explorer_channel"
    return cleaned

# ==========================================
# SERVE FRONTEND HTML
# ==========================================
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ==========================================
# ADMIN ROUTES
# ==========================================
@app.route('/api/admin/agent', methods=['GET'])
def get_agent_status():
    load_local_disk_db()
    logs = run_self_healing_agent()
    return jsonify({
        "status": "active",
        "agent_name": "Vernex_Auto_Heal_v1",
        "memory_integrity": "Optimal",
        "keys_monitored": len(GLOBAL_KEYS_VAULT),
        "recent_corrections": logs if logs else ["No system drift detected. Operational."]
    })

@app.route('/api/admin/health', methods=['GET', 'POST'])
def toggle_system_mutex():
    global SYSTEM_GLOBAL_MUTEX
    if request.method == 'POST':
        data = request.json or {}
        if "switch" in data:
            SYSTEM_GLOBAL_MUTEX = bool(data.get("switch"))
    return jsonify({"status": "operational", "kill_switch_active": not SYSTEM_GLOBAL_MUTEX})

@app.route('/api/admin/keys', methods=['GET', 'POST'])
def manage_keys():
    global GLOBAL_KEYS_VAULT
    load_local_disk_db()
    data = request.json or {}
    
    run_self_healing_agent(inbound_sync=data.get("sync_list"))
    
    if request.method == 'POST':
        if "sync_list" in data:
            for item in data.get("sync_list", []):
                k_str = item.get("key")
                if k_str:
                    GLOBAL_KEYS_VAULT[k_str] = item
            save_local_disk_db()
            return jsonify({"success": True, "state": "synced"})

        custom_key = data.get('key')
        if not custom_key:
            return jsonify({"error": "Missing identifier"}), 400
        
        GLOBAL_KEYS_VAULT[custom_key] = {
            "name": data.get('name', 'Subscriber Asset'),
            "key": custom_key,
            "price": float(data.get('price', 0) or 0),
            "daily_limit": int(data.get('daily_limit', 2500)),
            "expire_date": data.get('expire_date', 'lifetime'),
            "status": data.get('status', 'on'),
            "deleted_by_admin": False,
            "allow_number": "true" if str(data.get('allow_number')).lower() == "true" else "false",
            "allow_vehicle": "true" if str(data.get('allow_vehicle')).lower() == "true" else "false",
            "allow_aadhar": "true" if str(data.get('allow_aadhar')).lower() == "true" else "false",
            "allow_family": "true" if str(data.get('allow_family')).lower() == "true" else "false",
            "allow_insta": "true" if str(data.get('allow_insta')).lower() == "true" else "false",
            "allow_email": "true" if str(data.get('allow_email')).lower() == "true" else "false",
            "allow_git": "true" if str(data.get('allow_git')).lower() == "true" else "false",
            "allow_tg": "true" if str(data.get('allow_tg')).lower() == "true" else "false",
            "allow_tgidinfo": "true" if str(data.get('allow_tgidinfo')).lower() == "true" else "false",
            "allow_bomber": "true" if str(data.get('allow_bomber')).lower() == "true" else "false"
        }
        save_local_disk_db()
        return jsonify({"success": True})
    
    return jsonify({"keys": list(GLOBAL_KEYS_VAULT.values())})

@app.route('/api/admin/keys/delete', methods=['POST'])
def delete_key():
    global GLOBAL_KEYS_VAULT
    load_local_disk_db()
    data = request.json or {}
    target_key = data.get('key')
    if target_key in GLOBAL_KEYS_VAULT:
        GLOBAL_KEYS_VAULT[target_key]['deleted_by_admin'] = True
        GLOBAL_KEYS_VAULT[target_key]['status'] = 'deleted'
        save_local_disk_db()
    return jsonify({"success": True})

@app.route('/api/admin/toggle', methods=['POST'])
def toggle_key():
    global GLOBAL_KEYS_VAULT
    load_local_disk_db()
    data = request.json or {}
    key_name = data.get('key')
    if key_name in GLOBAL_KEYS_VAULT:
        current = GLOBAL_KEYS_VAULT[key_name].get('status', 'on')
        GLOBAL_KEYS_VAULT[key_name]['status'] = 'off' if current == 'on' else 'on'
        save_local_disk_db()
    return jsonify({"success": True})

@app.route('/api/admin/history', methods=['GET', 'POST', 'DELETE'])
def handle_history():
    global GLOBAL_HISTORY_LOGS
    if request.method == 'DELETE':
        GLOBAL_HISTORY_LOGS.clear()
        return jsonify({"success": True, "message": "History cleared"})
    return jsonify({"history": GLOBAL_HISTORY_LOGS[:100]})

# ==========================================
# PROXY PIPELINE
# ==========================================
def execute_proxy(tool_name, query_param, tracking_label):
    global GLOBAL_KEYS_VAULT, GLOBAL_HISTORY_LOGS, SYSTEM_GLOBAL_MUTEX
    load_local_disk_db()
    
    client_key = request.args.get('key')
    run_self_healing_agent(context_key=client_key)
    
    if not SYSTEM_GLOBAL_MUTEX:
        return jsonify({"error": "System Maintenance", "message": "All API pipelines paused by Administrator."}), 503
        
    lookup_input = request.args.get(query_param)
    if not lookup_input:
        return jsonify({"error": f"Missing query parameter: [{query_param}]"}), 400
        
    if not client_key or client_key not in GLOBAL_KEYS_VAULT:
        return jsonify({"error": "API key validation failed"}), 403
        
    key_meta = GLOBAL_KEYS_VAULT[client_key]
    
    if key_meta.get("deleted_by_admin") is True or key_meta.get("status") == "deleted":
        return jsonify({"error": "API is deleted by admin"}), 403
        
    if key_meta.get("status") == "off":
        return jsonify({"error": "Key disabled by admin"}), 403
        
    exp_date = key_meta.get("expire_date", "lifetime")
    if exp_date != "lifetime":
        current_date = time.strftime("%Y-%m-%d")
        if current_date > exp_date:
            return jsonify({"error": "This key is expired"}), 403
            
    if key_meta.get(f"allow_{tool_name}", "false") != "true":
        return jsonify({"error": "Access Scope Denied for this route"}), 403
    
    try:
        target_url = f"{TOOLS_CONFIG[tool_name]}?key={MASTER_KEY}&{query_param}={lookup_input}"
        
        if tool_name == "bomber":
            counter_val = request.args.get('counter', '100')
            target_url += f"&counter={counter_val}"
            
        response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        upstream_data = clean_branding_data(response.json() if response.status_code == 200 else {"raw": response.text})
    except Exception as e:
        return jsonify({"error": "Upstream timeout", "details": str(e)}), 502
        
    GLOBAL_HISTORY_LOGS.insert(0, {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "key_used": client_key,
        "client_name": key_meta.get("name"),
        "type": tracking_label,
        "query": lookup_input,
        "status_code": response.status_code
    })
    return jsonify(upstream_data)

# ==========================================
# API ENDPOINTS
# ==========================================
@app.route('/api/number', methods=['GET'])
def lookup_num(): return execute_proxy("number", "num", "NUMBER")

@app.route('/api/vehicle', methods=['GET'])
def lookup_veh(): return execute_proxy("vehicle", "vehicle", "VEHICLE")

@app.route('/api/aadhar', methods=['GET'])
def lookup_adr(): return execute_proxy("aadhar", "num", "AADHAR")

@app.route('/api/adharfamily', methods=['GET'])
def lookup_fam(): return execute_proxy("family", "num", "FAMILY")

@app.route('/api/insta', methods=['GET'])
def lookup_ins(): return execute_proxy("insta", "username", "INSTAGRAM")

@app.route('/api/email', methods=['GET'])
def lookup_email(): return execute_proxy("email", "email", "EMAIL")

@app.route('/api/git', methods=['GET'])
def lookup_git(): return execute_proxy("git", "username", "GITHUB")

@app.route('/api/tg', methods=['GET'])
def lookup_tg_info(): return execute_proxy("tg", "info", "TELEGRAM_INFO")

@app.route('/api/tgidinfo', methods=['GET'])
def lookup_tg_id(): return execute_proxy("tgidinfo", "id", "TELEGRAM_ID")

@app.route('/api/bomber', methods=['GET'])
def run_bomber(): return execute_proxy("bomber", "number", "SMS_BOMBER")

# ==========================================
# VERCEL SERVERLESS HANDLER
# ==========================================
# This is the entry point Vercel calls
def handler(request, *args, **kwargs):
    with app.request_context(request.environ):
        return app(request.environ, request.start_response)
