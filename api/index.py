import os
import sys
import time
import json
import requests
from flask import Flask, request, jsonify

# Add parent to path for imports if needed
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

# ==========================================
# CORS
# ==========================================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ==========================================
# CONFIG
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
# SELF-HEALING AGENT
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
# DB HELPERS
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
# CLEAN BRANDING
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
# FRONTEND HTML (Embedded)
# ==========================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vernex Control Hub</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
body{background:#020205;font-family:'JetBrains Mono',monospace;color:#cbd5e1;}
.glass{background:rgba(7,7,15,.85);border:1px solid rgba(255,255,255,.05);backdrop-filter:blur(20px);}
.neon-cyan{border-color:rgba(6,182,212,.3)!important;box-shadow:0 0 20px rgba(6,182,212,.1);}
.neon-emerald{border-color:rgba(16,185,129,.3)!important;box-shadow:0 0 20px rgba(16,185,129,.1);}
.neon-purple{border-color:rgba(139,92,246,.3)!important;box-shadow:0 0 20px rgba(139,92,246,.1);}
.btn-cyber{background:rgba(6,182,212,.1);border:1px solid rgba(6,182,212,.3);color:#22d3ee;}
.btn-cyber:hover{background:rgba(6,182,212,.2);}
input,select{background:rgba(2,6,23,.9);border:1px solid #1e293b;color:#22d3ee;}
input:focus{outline:none;border-color:#06b6d4;box-shadow:0 0 10px rgba(6,182,212,.2);}
.status-on{color:#10b981;border-color:rgba(16,185,129,.4);background:rgba(16,185,129,.1);}
.status-off{color:#f59e0b;border-color:rgba(245,158,11,.4);background:rgba(245,158,11,.1);}
.status-del{color:#ef4444;border-color:rgba(239,68,68,.4);background:rgba(239,68,68,.1);animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:#020205}::-webkit-scrollbar-thumb{background:#06b6d4;border-radius:2px}
</style>
</head>
<body class="min-h-screen p-4 md:p-8">

<div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="glass neon-cyan rounded-xl p-4 mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
            <h1 class="text-xl font-black text-white tracking-wider"><i class="fas fa-shield-halved text-cyan-400 mr-2"></i>VERNEX OS</h1>
            <p class="text-xs text-slate-500 mt-1" id="datetime">Loading...</p>
        </div>
        <div class="flex gap-3 text-xs">
            <div class="glass rounded-lg px-3 py-2 text-center">
                <div class="text-slate-500 text-[10px]">Keys</div>
                <div class="text-cyan-400 font-bold text-lg" id="statKeys">0</div>
            </div>
            <div class="glass rounded-lg px-3 py-2 text-center">
                <div class="text-slate-500 text-[10px]">Revenue</div>
                <div class="text-emerald-400 font-bold text-lg">₹<span id="statRev">0</span></div>
            </div>
            <div class="glass rounded-lg px-3 py-2 text-center">
                <div class="text-slate-500 text-[10px]">Queries</div>
                <div class="text-purple-400 font-bold text-lg" id="statVol">0</div>
            </div>
        </div>
    </div>

    <!-- Navigation -->
    <div class="flex gap-2 mb-6 overflow-x-auto pb-2">
        <button onclick="showTab('dashboard')" id="tab-dashboard" class="btn-cyber px-4 py-2 rounded-lg text-xs font-bold transition">Dashboard</button>
        <button onclick="showTab('create')" id="tab-create" class="px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-cyan-400 transition">Create Key</button>
        <button onclick="showTab('logs')" id="tab-logs" class="px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-cyan-400 transition">Logs</button>
    </div>

    <!-- Dashboard Tab -->
    <div id="view-dashboard" class="space-y-4">
        <div class="flex flex-col sm:flex-row gap-3 mb-4">
            <input type="text" id="searchInput" oninput="renderKeys()" placeholder="Search keys..." class="flex-1 px-3 py-2 rounded-lg text-xs">
            <div class="flex gap-2">
                <button onclick="filterStatus='all';renderKeys()" class="tag-btn px-3 py-2 rounded-lg text-[10px] font-bold bg-cyan-950/50 text-cyan-400 border border-cyan-900/50">All</button>
                <button onclick="filterStatus='on';renderKeys()" class="tag-btn px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Active</button>
                <button onclick="filterStatus='off';renderKeys()" class="tag-btn px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Paused</button>
                <button onclick="exportCSV()" class="px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-600"><i class="fas fa-download mr-1"></i>CSV</button>
            </div>
        </div>
        <div class="glass rounded-xl overflow-hidden">
            <div class="overflow-x-auto">
                <table class="w-full text-xs">
                    <thead>
                        <tr class="border-b border-slate-800 text-slate-500 text-[10px] uppercase">
                            <th class="p-3 text-left">Client</th>
                            <th class="p-3 text-left">Key</th>
                            <th class="p-3 text-left">Price</th>
                            <th class="p-3 text-left">Expiry</th>
                            <th class="p-3 text-center">Perms</th>
                            <th class="p-3 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="keysTable" class="divide-y divide-slate-900/50"></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Create Key Tab -->
    <div id="view-create" class="hidden max-w-2xl">
        <div<div class="glass rounded-xl p-6 space-y-4">
            <h3 class="text-cyan-400 font-bold text-sm mb-4"><i class="fas fa-key mr-2"></i>Generate New API Key</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="text-slate-500 text-[10px] uppercase block mb-1">Name</label>
                    <input type="text" id="fName" placeholder="Enterprise Client" class="w-full px-3 py-2 rounded-lg text-xs">
                </div>
                <div>
                    <label class="text-slate-500 text-[10px] uppercase block mb-1">Key ID</label>
                    <div class="flex gap-2">
                        <input type="text" id="fKey" placeholder="custom_key_id" class="flex-1 px-3 py-2 rounded-lg text-xs">
                        <button onclick="genRandom()" class="btn-cyber px-3 py-2 rounded-lg text-xs"><i class="fas fa-dice"></i></button>
                    </div>
                </div>
            </div>
            <div class="grid grid-cols-3 gap-4">
                <div>
                    <label class="text-slate-500 text-[10px] uppercase block mb-1">Price (₹)</label>
                    <input type="number" id="fPrice" value="599" class="w-full px-3 py-2 rounded-lg text-xs">
                </div>
                <div>
                    <label class="text-slate-500 text-[10px] uppercase block mb-1">Daily Limit</label>
                    <input type="number" id="fLimit" value="2500" class="w-full px-3 py-2 rounded-lg text-xs">
                </div>
                <div>
                    <label class="text-slate-500 text-[10px] uppercase block mb-1">Expiry</label>
                    <input type="text" id="fExpiry" value="lifetime" class="w-full px-3 py-2 rounded-lg text-xs">
                </div>
            </div>
            <div>
                <label class="text-cyan-400 text-[10px] uppercase font-bold block mb-2">Permissions</label>
                <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px]">
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pNum" checked class="accent-cyan-500"> Number</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pVeh" checked class="accent-cyan-500"> Vehicle</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pAad" checked class="accent-cyan-500"> Aadhaar</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pFam" checked class="accent-cyan-500"> Family</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pIns" checked class="accent-cyan-500"> Instagram</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pEml" class="accent-cyan-500"> Email</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pGit" class="accent-cyan-500"> GitHub</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pTg" class="accent-cyan-500"> Telegram</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pTgi" class="accent-cyan-500"> TG ID</label>
                    <label class="flex items-center gap-2 cursor-pointer"><input type="checkbox" id="pBmb" class="accent-cyan-500"> Bomber</label>
                </div>
            </div>
            <button onclick="createKey()" class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold py-3 rounded-lg text-xs uppercase tracking-wider hover:opacity-90 transition">
                <i class="fas fa-rocket mr-2"></i>Deploy Key
            </button>
        </div>
    </div>

    <!-- Logs Tab -->
    <div id="view-logs" class="hidden">
        <div class="glass rounded-xl p-4">
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-cyan-400 font-bold text-xs"><i class="fas fa-terminal mr-2"></i>Live Logs</h3>
                <button onclick="clearLogs()" class="text-rose-400 text-[10px] font-bold hover:text-rose-300"><i class="fas fa-trash mr-1"></i>Clear</button>
            </div>
            <div id="logsBox" class="bg-black/50 rounded-lg p-3 h-96 overflow-y-auto text-[11px] font-mono space-y-1"></div>
        </div>
    </div>
</div>

<script>
const API = window.location.origin;
let keys = [], filterStatus = 'all';

async function loadData() {
    try {
        const r = await fetch(API + '/api/admin/keys');
        const d = await r.json();
        keys = d.keys || [];
        localStorage.setItem('vk', JSON.stringify(keys));
        updateStats();
        renderKeys();
    } catch(e) {
        keys = JSON.parse(localStorage.getItem('vk') || '[]');
        renderKeys();
    }
    
    try {
        const r = await fetch(API + '/api/admin/history');
        const d = await r.json();
        document.getElementById('statVol').innerText = d.history.length;
        renderLogs(d.history);
    } catch(e) {}
}

function updateStats() {
    document.getElementById('statKeys').innerText = keys.length;
    const rev = keys.reduce((a,k) => a + (k.status === 'on' ? parseFloat(k.price||0) : 0), 0);
    document.getElementById('statRev').innerText = rev.toLocaleString();
}

function renderKeys() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    let filtered = keys.filter(k => (k.name+k.key).toLowerCase().includes(q));
    if(filterStatus !== 'all') filtered = filtered.filter(k => k.status === filterStatus);
    
    const tbody = document.getElementById('keysTable');
    tbody.innerHTML = filtered.map(k => {
        let stClass = 'status-on', stText = 'ACTIVE';
        if(k.status === 'off') { stClass = 'status-off'; stText = 'PAUSED'; }
        if(k.status === 'deleted') { stClass = 'status-del'; stText = 'DELETED'; }
        
        const perms = [];
        if(k.allow_number === 'true') perms.push('<span class="text-[9px] text-cyan-400 bg-cyan-950/30 px-1 rounded">NUM</span>');
        if(k.allow_vehicle === 'true') perms.push('<span class="text-[9px] text-emerald-400 bg-emerald-950/30 px-1 rounded">VEH</span>');
        if(k.allow_aadhar === 'true') perms.push('<span class="text-[9px] text-purple-400 bg-purple-950/30 px-1 rounded">AAD</span>');
        if(k.allow_family === 'true') perms.push('<span class="text-[9px] text-amber-400 bg-amber-950/30 px-1 rounded">FAM</span>');
        if(k.allow_insta === 'true') perms.push('<span class="text-[9px] text-pink-400 bg-pink-950/30 px-1 rounded">INS</span>');
        
        return `<tr class="border-b border-slate-900/30 hover:bg-slate-900/20">
            <td class="p-3 font-bold text-slate-200 text-[11px]">${k.name}</td>
            <td class="p-3"><code class="text-cyan-400 text-[10px] bg-black/30 px-2 py-1 rounded">${k.key}</code></td>
            <td class="p-3 text-emerald-400 font-bold text-[11px]">₹${k.price}</td>
            <td class="p-3 text-[11px]">${k.expire_date === 'lifetime' ? '<span class="text-emerald-400">∞ Lifetime</span>' : k.expire_date}</td>
            <td class="p-3 text-center">${perms.join('')}</td>
            <td class="p-3 text-center space-x-1">
                <button onclick="toggleKey('${k.key}')" class="${stClass} px-2 py-1 rounded text-[9px] font-bold border">${stText}</button>
                <button onclick="deleteKey('${k.key}')" class="text-rose-400 border border-rose-900/50 px-2 py-1 rounded text-[9px] font-bold hover:bg-rose-950/30">DEL</button>
            </td>
        </tr>`;
    }).join('');
}

function renderLogs(logs) {
    const box = document.getElementById('logsBox');
    box.innerHTML = logs.map(l => {
        let col = 'text-emerald-400';
        if(l.status_code >= 400) col = 'text-rose-400';
        return `<div class="text-slate-400"><span class="text-slate-600">[${l.timestamp}]</span> <span class="text-purple-400">${l.type}</span> ${l.client_name} → <span class="${col}">${l.status_code}</span></div>`;
    }).join('');
}

async function createKey() {
    const obj = {
        name: document.getElementById('fName').value,
        key: document.getElementById('fKey').value,
        price: document.getElementById('fPrice').value,
        daily_limit: document.getElementById('fLimit').value,
        expire_date: document.getElementById('fExpiry').value,
        allow_number: document.getElementById('pNum').checked,
        allow_vehicle: document.getElementById('pVeh').checked,
        allow_aadhar: document.getElementById('pAad').checked,
        allow_family: document.getElementById('pFam').checked,
        allow_insta: document.getElementById('pIns').checked,
        allow_email: document.getElementById('pEml').checked,
        allow_git: document.getElementById('pGit').checked,
        allow_tg: document.getElementById('pTg').checked,
        allow_tgidinfo: document.getElementById('pTgi').checked,
        allow_bomber: document.getElementById('pBmb').checked
    };
    await fetch(API + '/api/admin/keys', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(obj)
    });
    loadData();
    showTab('dashboard');
}

async function toggleKey(k) {
    await fetch(API + '/api/admin/toggle', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({key: k})
    });
    loadData();
}

async function deleteKey(k) {
    if(!confirm('Delete key '+k+'?')) return;
    await fetch(API + '/api/admin/keys/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({key: k})
    });
    loadData();
}

async function clearLogs() {
    await fetch(API + '/api/admin/history', {method: 'DELETE'});
    loadData();
}

function genRandom() {
    document.getElementById('fKey').value = 'vernex_' + Math.random().toString(36).slice(2,10);
}

function exportCSV() {
    let csv = 'Name,Key,Price,Expiry,Status\n';
    keys.forEach(k => csv += `"${k.name}","${k.key}",${k.price},"${k.expire_date}","${k.status}"\n`);
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], {type: 'text/csv'}));
    a.download = 'vernex_keys.csv';
    a.click();
}

function showTab(t) {
    ['dashboard','create','logs'].forEach(x => {
        document.getElementById('view-'+x).classList.add('hidden');
        document.getElementById('tab-'+x).classList.remove('btn-cyber','text-cyan-400');
        document.getElementById('tab-'+x).classList.add('text-slate-400');
    });
    document.getElementById('view-'+t).classList.remove('hidden');
    document.getElementById('tab-'+t).classList.add('btn-cyber','text-cyan-400');
    document.getElementById('tab-'+t).classList.remove('text-slate-400');
}

function updateTime() {
    document.getElementById('datetime').innerText = new Date().toLocaleString();
}

setInterval(updateTime, 1000);
setInterval(loadData, 5000);
updateTime();
loadData();
</script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML_PAGE

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
        "recent_corrections": logs if logs else ["No system drift detected."]
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
            
        response = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
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
