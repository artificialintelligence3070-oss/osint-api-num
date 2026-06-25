import os
import sys
import time
import json
import requests
from flask import Flask, request, jsonify, Response

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
# EMBEDDED HTML FRONTEND
# ==========================================
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vernex OS - API Key Manager</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
body{background:#020205;font-family:'JetBrains Mono',monospace;color:#cbd5e1;}
.glass{background:rgba(7,7,15,.9);border:1px solid rgba(255,255,255,.05);backdrop-filter:blur(20px);}
.neon-cyan{border:1px solid rgba(6,182,212,.3)!important;box-shadow:0 0 20px rgba(6,182,212,.1);}
.neon-emerald{border:1px solid rgba(16,185,129,.3)!important;box-shadow:0 0 20px rgba(16,185,129,.1);}
.neon-purple{border:1px solid rgba(139,92,246,.3)!important;box-shadow:0 0 20px rgba(139,92,246,.1);}
.btn-cyber{background:rgba(6,182,212,.15);border:1px solid rgba(6,182,212,.4);color:#22d3ee;}
.btn-cyber:hover{background:rgba(6,182,212,.25);}
input,select,textarea{background:rgba(2,6,23,.9);border:1px solid #1e293b;color:#22d3ee;padding:.5rem;border-radius:.5rem;}
input:focus,select:focus,textarea:focus{outline:none;border-color:#06b6d4;box-shadow:0 0 10px rgba(6,182,212,.2);}
.status-on{color:#10b981;border:1px solid rgba(16,185,129,.4);background:rgba(16,185,129,.1);}
.status-off{color:#f59e0b;border:1px solid rgba(245,158,11,.4);background:rgba(245,158,11,.1);}
.status-del{color:#ef4444;border:1px solid rgba(239,68,68,.4);background:rgba(239,68,68,.1);}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
.pulse{animation:pulse 1.5s infinite;}
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:#020205}::-webkit-scrollbar-thumb{background:#06b6d4;border-radius:2px}
</style>
</head>
<body class="min-h-screen p-4 md:p-6">

<div class="max-w-7xl mx-auto">
    <!-- Header -->
    <div class="glass neon-cyan rounded-xl p-4 mb-4 flex flex-col md:flex-row justify-between items-center gap-3">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <i class="fas fa-shield-halved text-white"></i>
            </div>
            <div>
                <h1 class="text-lg font-black text-white tracking-wider">VERNEX OS</h1>
                <p class="text-[10px] text-cyan-400 font-bold">PROFESSIONAL EDITION</p>
            </div>
        </div>
        <div class="flex gap-3 text-xs">
            <div class="glass rounded-lg px-3 py-2 text-center min-w-[80px]">
                <div class="text-slate-500 text-[9px] uppercase">Keys</div>
                <div class="text-cyan-400 font-bold text-xl" id="statKeys">0</div>
            </div>
            <div class="glass rounded-lg px-3 py-2 text-center min-w-[80px]">
                <div class="text-slate-500 text-[9px] uppercase">Revenue</div>
                <div class="text-emerald-400 font-bold text-xl">&#x20B9;<span id="statRev">0</span></div>
            </div>
            <div class="glass rounded-lg px-3 py-2 text-center min-w-[80px]">
                <div class="text-slate-500 text-[9px] uppercase">Queries</div>
                <div class="text-purple-400 font-bold text-xl" id="statVol">0</div>
            </div>
        </div>
    </div>

    <!-- Nav -->
    <div class="flex gap-2 mb-4 overflow-x-auto pb-1">
        <button onclick="showTab('dash')" id="tab-dash" class="btn-cyber px-4 py-2 rounded-lg text-xs font-bold transition">Dashboard</button>
        <button onclick="showTab('create')" id="tab-create" class="px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-cyan-400 transition">Create Key</button>
        <button onclick="showTab('logs')" id="tab-logs" class="px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-cyan-400 transition">Logs</button>
        <button onclick="showTab('agent')" id="tab-agent" class="px-4 py-2 rounded-lg text-xs font-bold text-slate-400 hover:text-cyan-400 transition">Agent</button>
    </div>

    <!-- Dashboard -->
    <div id="view-dash" class="space-y-4">
        <div class="flex flex-col sm:flex-row gap-3 mb-3">
            <div class="relative flex-1">
                <i class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-600 text-xs"></i>
                <input type="text" id="searchInput" oninput="renderKeys()" placeholder="Search keys..." class="w-full pl-9 pr-3 py-2 text-xs">
            </div>
            <div class="flex gap-2 flex-wrap">
                <button onclick="setFilter('all')" id="f-all" class="filter-btn px-3 py-2 rounded-lg text-[10px] font-bold btn-cyber">All</button>
                <button onclick="setFilter('on')" id="f-on" class="filter-btn px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Active</button>
                <button onclick="setFilter('off')" id="f-off" class="filter-btn px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Paused</button>
                <button onclick="setFilter('expired')" id="f-expired" class="filter-btn px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Expired</button>
                <button onclick="exportCSV()" class="px-3 py-2 rounded-lg text-[10px] font-bold bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-600"><i class="fas fa-download mr-1"></i>CSV</button>
                <button onclick="purgeExpired()" class="px-3 py-2 rounded-lg text-[10px] font-bold bg-rose-950/30 text-rose-400 border border-rose-900/50 hover:bg-rose-950/50"><i class="fas fa-trash mr-1"></i>Purge</button>
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
            <div id="mobileCards" class="md:hidden space-y-3 p-3"></div>
        </div>
    </div>

    <!-- Create Key -->
    <div id="view-create" class="hidden max-w-2xl mx-auto">
        <div class="glass rounded-xl p-6 space-y-4">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                <h3 class="text-cyan-400 font-bold text-sm"><i class="fas fa-key mr-2"></i>Generate New API Key</h3>
                <button onclick="genRandom()" class="btn-cyber px-3 py-1.5 rounded-lg text-[10px] font-bold"><i class="fas fa-dice mr-1"></i>Random</button>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="text-slate-500 text-[10px] uppercase font-bold block mb-1">Subscriber Name</label>
                    <input type="text" id="fName" placeholder="Enterprise Client" class="w-full text-xs">
                </div>
                <div>
                    <label class="text-slate-500 text-[10px] uppercase font-bold block mb-1">Key Identifier</label>
                    <input type="text" id="fKey" placeholder="custom_key_id" class="w-full text-xs">
                </div>
            </div>
            
            <div class="grid grid-cols-3 gap-4">
                <div>
                    <label class="text-slate-500 text-[10px] uppercase font-bold block mb-1">Price (&#x20B9;)</label>
                    <input type="number" id="fPrice" value="599" class="w-full text-xs">
                </div>
                <div>
                    <label class="text-slate-500 text-[10px] uppercase font-bold block mb-1">Daily Limit</label>
                    <input type="number" id="fLimit" value="2500" class="w-full text-xs">
                </div>
                <div>
                    <label class="text-slate-500 text-[10px] uppercase font-bold block mb-1">Expiry Date</label>
                    <div class="flex gap-2">
                        <input type="text" id="fExpiry" value="lifetime" class="flex-1 text-xs">
                        <button onclick="document.getElementById('fExpiry').value='lifetime'" class="btn-cyber px-2 py-1 rounded text-[10px]"><i class="fas fa-infinity"></i></button>
                    </div>
                </div>
            </div>

            <div>
                <div class="flex justify-between items-center mb-2">
                    <label class="text-cyan-400 text-[10px] uppercase font-bold">Permissions Matrix</label>
                    <button onclick="toggleAllPerms(true)" class="text-[10px] text-cyan-400 hover:text-cyan-300 font-bold">Select All</button>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 text-[11px]">
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pNum" checked class="accent-cyan-500 w-4 h-4"> Number</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pVeh" checked class="accent-cyan-500 w-4 h-4"> Vehicle</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pAad" checked class="accent-cyan-500 w-4 h-4"> Aadhaar</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pFam" checked class="accent-cyan-500 w-4 h-4"> Family</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pIns" checked class="accent-cyan-500 w-4 h-4"> Instagram</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pEml" class="accent-cyan-500 w-4 h-4"> Email</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pGit" class="accent-cyan-500 w-4 h-4"> GitHub</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pTg" class="accent-cyan-500 w-4 h-4"> Telegram</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pTgi" class="accent-cyan-500 w-4 h-4"> TG ID Info</label>
                    <label class="flex items-center gap-2 cursor-pointer p-2 rounded hover:bg-slate-900/50 transition"><input type="checkbox" id="pBmb" class="accent-cyan-500 w-4 h-4"> SMS Bomber</label>
                </div>
            </div>

            <div class="glass rounded-lg p-4 border border-cyan-900/30">
                <h4 class="text-[10px] text-slate-500 uppercase font-bold mb-2">Key Preview</h4>
                <div class="grid grid-cols-2 gap-2 text-[11px] font-mono">
                    <div class="flex justify-between"><span class="text-slate-500">Name:</span><span class="text-cyan-400" id="preName">--</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">Key:</span><span class="text-cyan-400" id="preKey">--</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">Price:</span><span class="text-emerald-400" id="prePrice">&#x20B9;599</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">Limit:</span><span class="text-purple-400" id="preLimit">2,500</span></div>
                </div>
            </div>

            <button onclick="createKey()" class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold py-3 rounded-lg text-xs uppercase tracking-wider hover:opacity-90 transition shadow-[0_0_20px_rgba(6,182,212,.3)]">
                <i class="fas fa-rocket mr-2"></i>Deploy Key to Cluster
            </button>
        </div>
    </div>

    <!-- Logs -->
    <div id="view-logs" class="hidden">
        <div class="glass rounded-xl p-4">
            <div class="flex justify-between items-center mb-3 border-b border-slate-800 pb-2">
                <h3 class="text-cyan-400 font-bold text-xs"><i class="fas fa-terminal mr-2"></i>Live Telemetry Logs</h3>
                <div class="flex gap-2">
                    <button onclick="setLogFilter('all')" class="px-2 py-1 rounded text-[9px] font-bold btn-cyber">All</button>
                    <button onclick="setLogFilter('success')" class="px-2 py-1 rounded text-[9px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Success</button>
                    <button onclick="setLogFilter('error')" class="px-2 py-1 rounded text-[9px] font-bold bg-slate-900 text-slate-400 border border-slate-800">Errors</button>
                    <button onclick="clearLogs()" class="px-3 py-1 rounded text-[10px] font-bold bg-rose-950/30 text-rose-400 border border-rose-900/50 hover:bg-rose-950/50"><i class="fas fa-trash"></i></button>
                </div>
            </div>
            <div class="grid grid-cols-3 gap-2 mb-3">
                <div class="glass rounded-lg p-2 text-center border border-emerald-900/30">
                    <div class="text-[9px] text-slate-500">Success</div>
                    <div class="text-emerald-400 font-bold text-lg" id="logOk">0</div>
                </div>
                <div class="glass rounded-lg p-2 text-center border border-amber-900/30">
                    <div class="text-[9px] text-slate-500">Warnings</div>
                    <div class="text-amber-400 font-bold text-lg" id="logWarn">0</div>
                </div>
                <div class="glass rounded-lg p-2 text-center border border-rose-900/30">
                    <div class="text-[9px] text-slate-500">Errors</div>
                    <div class="text-rose-400 font-bold text-lg" id="logErr">0</div>
                </div>
            </div>
            <div id="logsBox" class="bg-black/50 rounded-lg p-3 h-[60vh] overflow-y-auto text-[11px] font-mono space-y-1"></div>
        </div>
    </div>

    <!-- Agent Status -->
    <div id="view-agent" class="hidden">
        <div class="glass neon-cyan rounded-xl p-6">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-3 h-3 rounded-full bg-emerald-400 pulse"></div>
                <h3 class="text-cyan-400 font-bold text-sm">Self-Healing Agent Status</h3>
            </div>
            <div id="agentInfo" class="space-y-2 text-xs font-mono">
                <div class="flex justify-between border-b border-slate-800 pb-2"><span class="text-slate-500">Agent Name:</span><span class="text-cyan-400">Vernex_Auto_Heal_v1</span></div>
                <div class="flex justify-between border-b border-slate-800 pb-2"><span class="text-slate-500">Status:</span><span class="text-emerald-400">ACTIVE</span></div>
                <div class="flex justify-between border-b border-slate-800 pb-2"><span class="text-slate-500">Keys Monitored:</span><span class="text-cyan-400" id="agentKeys">0</span></div>
                <div class="flex justify-between border-b border-slate-800 pb-2"><span class="text-slate-500">Memory Integrity:</span><span class="text-emerald-400">Optimal</span></div>
            </div>
            <div class="mt-4">
                <h4 class="text-[10px] text-slate-500 uppercase font-bold mb-2">Recent Corrections</h4>
                <div id="agentLogs" class="bg-black/50 rounded-lg p-3 h-40 overflow-y-auto text-[11px] font-mono space-y-1"></div>
            </div>
        </div>
    </div>
</div>

<script>
const API = '';
let keys = [], logs = [], currentFilter = 'all', logFilter = 'all';

async function loadAll() {
    try {
        const r = await fetch('/api/admin/keys');
        const d = await r.json();
        keys = d.keys || [];
        localStorage.setItem('vk', JSON.stringify(keys));
    } catch(e) {
        keys = JSON.parse(localStorage.getItem('vk') || '[]');
    }
    updateStats();
    renderKeys();
    
    try {
        const r = await fetch('/api/admin/history');
        const d = await r.json();
        logs = d.history || [];
        renderLogs();
    } catch(e) {}
}

function updateStats() {
    document.getElementById('statKeys').innerText = keys.length;
    const rev = keys.reduce((a,k) => a + (k.status === 'on' ? parseFloat(k.price||0) : 0), 0);
    document.getElementById('statRev').innerText = rev.toLocaleString();
    document.getElementById('statVol').innerText = logs.length;
    document.getElementById('agentKeys').innerText = keys.length;
}

function renderKeys() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    let filtered = keys.filter(k => (k.name+k.key).toLowerCase().includes(q));
    
    if(currentFilter === 'expired') {
        const today = new Date().toISOString().split('T')[0];
        filtered = filtered.filter(k => k.expire_date !== 'lifetime' && k.expire_date < today);
    } else if(currentFilter !== 'all') {
        filtered = filtered.filter(k => k.status === currentFilter);
    }
    
    const tbody = document.getElementById('keysTable');
    const mobile = document.getElementById('mobileCards');
    tbody.innerHTML = '';
    mobile.innerHTML = '';
    
    filtered.forEach(k => {
        let stClass = 'status-on', stText = 'ACTIVE';
        if(k.status === 'off') { stClass = 'status-off'; stText = 'PAUSED'; }
        if(k.status === 'deleted') { stClass = 'status-del pulse'; stText = 'DELETED'; }
        
        const perms = [];
        if(k.allow_number === 'true') perms.push('<span class="text-[8px] bg-cyan-950/50 text-cyan-400 px-1.5 py-0.5 rounded">NUM</span>');
        if(k.allow_vehicle === 'true') perms.push('<span class="text-[8px] bg-emerald-950/50 text-emerald-400 px-1.5 py-0.5 rounded">VEH</span>');
        if(k.allow_aadhar === 'true') perms.push('<span class="text-[8px] bg-purple-950/50 text-purple-400 px-1.5 py-0.5 rounded">AAD</span>');
        if(k.allow_family === 'true') perms.push('<span class="text-[8px] bg-amber-950/50 text-amber-400 px-1.5 py-0.5 rounded">FAM</span>');
        if(k.allow_insta === 'true') perms.push('<span class="text-[8px] bg-pink-950/50 text-pink-400 px-1.5 py-0.5 rounded">INS</span>');
        if(k.allow_email === 'true') perms.push('<span class="text-[8px] bg-blue-950/50 text-blue-400 px-1.5 py-0.5 rounded">EML</span>');
        if(k.allow_git === 'true') perms.push('<span class="text-[8px] bg-slate-950/50 text-slate-400 px-1.5 py-0.5 rounded">GIT</span>');
        if(k.allow_tg === 'true') perms.push('<span class="text-[8px] bg-sky-950/50 text-sky-400 px-1.5 py-0.5 rounded">TG</span>');
        if(k.allow_tgidinfo === 'true') perms.push('<span class="text-[8px] bg-indigo-950/50 text-indigo-400 px-1.5 py-0.5 rounded">TGI</span>');
        if(k.allow_bomber === 'true') perms.push('<span class="text-[8px] bg-rose-950/50 text-rose-400 px-1.5 py-0.5 rounded">BMB</span>');
        
        const copyBtns = `
            <div class="flex flex-wrap gap-1 mt-1">
                ${k.allow_number === 'true' ? `<button onclick="copyEP('${k.key}','number','num')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[NUM]</button>` : ''}
                ${k.allow_vehicle === 'true' ? `<button onclick="copyEP('${k.key}','vehicle','vehicle')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[VEH]</button>` : ''}
                ${k.allow_aadhar === 'true' ? `<button onclick="copyEP('${k.key}','aadhar','num')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[AAD]</button>` : ''}
                ${k.allow_family === 'true' ? `<button onclick="copyEP('${k.key}','adharfamily','num')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[FAM]</button>` : ''}
                ${k.allow_insta === 'true' ? `<button onclick="copyEP('${k.key}','insta','username')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[INS]</button>` : ''}
                ${k.allow_email === 'true' ? `<button onclick="copyEP('${k.key}','email','email')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[EML]</button>` : ''}
                ${k.allow_git === 'true' ? `<button onclick="copyEP('${k.key}','git','username')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[GIT]</button>` : ''}
                ${k.allow_tg === 'true' ? `<button onclick="copyEP('${k.key}','tg','info')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[TG]</button>` : ''}
                ${k.allow_tgidinfo === 'true' ? `<button onclick="copyEP('${k.key}','tgidinfo','id')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[TGI]</button>` : ''}
                ${k.allow_bomber === 'true' ? `<button onclick="copyEP('${k.key}','bomber','number')" class="text-[9px] text-slate-500 hover:text-cyan-400 transition">[BMB]</button>` : ''}
            </div>`;
        
        tbody.innerHTML += `
            <tr class="border-b border-slate-900/30 hover:bg-slate-900/20 transition">
                <td class="p-3 font-bold text-slate-200 text-[11px]">${k.name}</td>
                <td class="p-3">
                    <code class="text-cyan-400 text-[10px] bg-black/30 px-2 py-1 rounded block">${k.key}</code>
                    ${copyBtns}
                </td>
                <td class="p-3 text-emerald-400 font-bold text-[11px]">&#x20B9;${k.price}</td>
                <td class="p-3 text-[11px]">${k.expire_date === 'lifetime' ? '<span class="text-emerald-400 font-bold">&#x267E; Lifetime</span>' : '<span class="text-amber-400">' + k.expire_date + '</span>'}</td>
                <td class="p-3 text-center"><div class="flex flex-wrap gap-1 justify-center">${perms.join('')}</div></td>
                <td class="p-3 text-center">
                    <button onclick="toggleKey('${k.key}')" class="${stClass} px-2 py-1 rounded text-[9px] font-bold">${stText}</button>
                    <button onclick="deleteKey('${k.key}')" class="text-rose-400 border border-rose-900/50 px-2 py-1 rounded text-[9px] font-bold hover:bg-rose-950/30 ml-1">DEL</button>
                </td>
            </tr>`;
            
        mobile.innerHTML += `
            <div class="glass rounded-lg p-3 border border-slate-800">
                <div class="flex justify-between items-center mb-2">
                    <span class="font-bold text-slate-200 text-sm">${k.name}</span>
                    <span class="text-emerald-400 font-bold text-sm">&#x20B9;${k.price}</span>
                </div>
                <code class="text-cyan-400 text-xs bg-black/30 p-2 rounded block text-center mb-2">${k.key}</code>
                <div class="flex flex-wrap gap-1 mb-2">${perms.join('')}</div>
                <div class="flex justify-between items-center">
                    <span class="text-[10px] ${k.expire_date === 'lifetime' ? 'text-emerald-400' : 'text-amber-400'}">${k.expire_date === 'lifetime' ? '&#x267E; Lifetime' : k.expire_date}</span>
                    <div>
                        <button onclick="toggleKey('${k.key}')" class="${stClass} px-2 py-1 rounded text-[9px] font-bold">${stText}</button>
                        <button onclick="deleteKey('${k.key}')" class="text-rose-400 border border-rose-900/50 px-2 py-1 rounded text-[9px] font-bold ml-1">DEL</button>
                    </div>
                </div>
            </div>`;
    });
}

function renderLogs() {
    let filtered = logs;
    if(logFilter === 'success') filtered = logs.filter(l => l.status_code >= 200 && l.status_code < 300);
    if(logFilter === 'error') filtered = logs.filter(l => l.status_code >= 400);
    
    let ok = 0, warn = 0, err = 0;
    logs.forEach(l => {
        if(l.status_code >= 200 && l.status_code < 300) ok++;
        else if(l.status_code >= 400) err++;
        else warn++;
    });
    document.getElementById('logOk').innerText = ok;
    document.getElementById('logWarn').innerText = warn;
    document.getElementById('logErr').innerText = err;
    
    const box = document.getElementById('logsBox');
    box.innerHTML = filtered.map(l => {
        let col = 'text-emerald-400';
        if(l.status_code >= 400) col = 'text-rose-400';
        else if(l.status_code >= 300) col = 'text-amber-400';
        return `<div class="text-slate-400 border-l-2 ${l.status_code >= 400 ? 'border-rose-500' : 'border-emerald-500'} pl-2"><span class="text-slate-600">[${l.timestamp}]</span> <span class="text-purple-400">${l.type}</span> ${l.client_name} <span class="text-slate-500">&#10132;</span> <span class="${col}">${l.status_code}</span></div>`;
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
    await fetch('/api/admin/keys', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(obj)
    });
    loadAll();
    showTab('dash');
}

async function toggleKey(k) {
    await fetch('/api/admin/toggle', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({key: k})
    });
    loadAll();
}

async function deleteKey(k) {
    if(!confirm('Delete key: ' + k + '?')) return;
    await fetch('/api/admin/keys/delete', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({key: k})
    });
    loadAll();
}

async function clearLogs() {
    await fetch('/api/admin/history', {method: 'DELETE'});
    loadAll();
}

async function purgeExpired() {
    const today = new Date().toISOString().split('T')[0];
    const targets = keys.filter(k => k.expire_date !== 'lifetime' && k.expire_date < today);
    if(!targets.length) return alert('No expired keys found');
    if(!confirm('Delete ' + targets.length + ' expired keys?')) return;
    for(const k of targets) {
        await fetch('/api/admin/keys/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key: k.key})
        });
    }
    loadAll();
}

function copyEP(key, ep, param) {
    const url = window.location.origin + '/api/' + ep + '?key=' + key + '&' + param + '=';
    navigator.clipboard.writeText(url);
    showToast('Copied: ' + ep.toUpperCase());
}

function exportCSV() {
    let csv = 'Name,Key,Price,Expiry,Status\\n';
    keys.forEach(k => csv += `"${k.name}","${k.key}",${k.price},"${k.expire_date}","${k.status}"\\n`);
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], {type: 'text/csv'}));
    a.download = 'vernex_keys.csv';
    a.click();
}

function genRandom() {
    document.getElementById('fKey').value = 'vernex_' + Math.random().toString(36).slice(2,10);
    updatePreview();
}

function toggleAllPerms(checked) {
    ['pNum','pVeh','pAad','pFam','pIns','pEml','pGit','pTg','pTgi','pBmb'].forEach(id => {
        document.getElementById(id).checked = checked;
    });
}

function setFilter(f) {
    currentFilter = f;
    document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('btn-cyber');
        b.classList.add('bg-slate-900','text-slate-400','border','border-slate-800');
    });
    const btn = document.getElementById('f-' + f);
    btn.classList.remove('bg-slate-900','text-slate-400','border','border-slate-800');
    btn.classList.add('btn-cyber');
    renderKeys();
}

function setLogFilter(f) {
    logFilter = f;
    renderLogs();
}

function showTab(t) {
    ['dash','create','logs','agent'].forEach(x => {
        document.getElementById('view-' + x).classList.add('hidden');
        document.getElementById('tab-' + x).classList.remove('btn-cyber','text-cyan-400');
        document.getElementById('tab-' + x).classList.add('text-slate-400');
    });
    document.getElementById('view-' + t).classList.remove('hidden');
    document.getElementById('tab-' + t).classList.add('btn-cyber','text-cyan-400');
    document.getElementById('tab-' + t).classList.remove('text-slate-400');
    if(t === 'agent') loadAgent();
}

function showToast(msg) {
    const div = document.createElement('div');
    div.className = 'fixed top-4 right-4 bg-cyan-950/90 border border-cyan-500/30 text-cyan-400 px-4 py-2 rounded-lg text-xs font-bold z-50';
    div.innerText = msg;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 2000);
}

async function loadAgent() {
    try {
        const r = await fetch('/api/admin/agent');
        const d = await r.json();
        document.getElementById('agentKeys').innerText = d.keys_monitored;
        const box = document.getElementById('agentLogs');
        box.innerHTML = d.recent_corrections.map(c => 
            `<div class="text-cyan-400/80"><span class="text-emerald-500">&#10132;</span> ${c}</div>`
        ).join('');
    } catch(e) {}
}

function updatePreview() {
    document.getElementById('preName').innerText = document.getElementById('fName').value || '--';
    document.getElementById('preKey').innerText = document.getElementById('fKey').value || '--';
    document.getElementById('prePrice').innerText = '&#x20B9;' + (document.getElementById('fPrice').value || '0');
    document.getElementById('preLimit').innerText = parseInt(document.getElementById('fLimit').value || 0).toLocaleString();
}

['fName','fKey','fPrice','fLimit'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', updatePreview);
});

setInterval(loadAll, 5000);
loadAll();
</script>
</body>
</html>"""

@app.route('/')
def index():
    return Response(HTML_CONTENT, mimetype='text/html')

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
