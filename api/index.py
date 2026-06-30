import os
import datetime
import requests
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="SHAYAN_EXPLORER Hub Engine")

# Bulletproof path tracking for Vercel Serverless Architecture
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# --- REST OF YOUR CODE STAYS EXACTLY THE SAME ---
ADMIN_CREDENTIALS = {"username": "vernex", "password": "vernex@16"}
UPSTREAM_BASE_KEY = "vx-osint"
UPSTREAM_URL = "https://ft-osint-api.duckdns.org/api"

API_KEYS_DB = {
    "RAHUL-SECRET-KEY": {
        "name": "Rahul",
        "email": "rahul@example.com",
        "type": "Lifetime",
        "price": "599",
        "expiry": "2026-12-31T23:59",
        "limit": 5000,
        "used": 0,
        "rate_limit": 1000,
        "allowed_tools": ["number", "paytm", "upi", "ip", "challan"],
        "key_note": "Premium License Enabled",
        "admin_notes": "Verified client"
    }
}

LOGS_DB = []

VALID_ENDPOINTS = [
    "adv", "paytm", "imei", "calltracer", "upi", "ifsc", 
    "number", "pincode", "ip", "challan", "ff", "bgmi", 
    "snap", "email", "vehicle", "git", "insta", "tg", "tgidinfo", "numleak"
]

def check_auth_session(request: Request):
    session = request.cookies.get("shayan_admin_session")
    if session != "active_secure_shayan_auth_token":
        raise HTTPException(status_code=401)
    return True

@app.get("/", response_class=HTMLResponse)
async def login_interface(request: Request):
    if request.cookies.get("shayan_admin_session") == "active_secure_shayan_auth_token":
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request, "page": "login", "error": None})

@app.post("/auth/login")
async def process_login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="shayan_admin_session", value="active_secure_shayan_auth_token", httponly=True, path="/")
        return response
    return templates.TemplateResponse("dashboard.html", {"request": {}, "page": "login", "error": "Invalid username or password credentials provided."})

@app.get("/auth/logout")
async def process_logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("shayan_admin_session", path="/")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def admin_panel(request: Request):
    try:
        check_auth_session(request)
    except HTTPException:
        return RedirectResponse(url="/", status_code=303)
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "page": "panel",
        "keys": API_KEYS_DB,
        "logs": reversed(LOGS_DB[-50:]),
        "endpoints": VALID_ENDPOINTS
    })

@app.post("/keys/create")
async def action_create_key(
    request: Request,
    key_type: str = Form(...),
    custom_key: str = Form(...),
    key_name: str = Form(...),
    customer_email: str = Form(""),
    price: str = Form("0"),
    expiry_date: str = Form(...),
    rate_limit: int = Form(1000),
    req_limit: int = Form(...),
    key_note: str = Form(""),
    admin_notes: str = Form(""),
    tools: list = Form([])
):
    try:
        check_auth_session(request)
    except HTTPException:
        return RedirectResponse(url="/", status_code=303)

    API_KEYS_DB[custom_key] = {
        "name": key_name,
        "email": customer_email,
        "type": key_type,
        "price": price,
        "expiry": expiry_date,
        "limit": req_limit,
        "used": 0,
        "rate_limit": rate_limit,
        "allowed_tools": tools,
        "key_note": key_note,
        "admin_notes": admin_notes
    }
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/keys/revoke/{key_id}")
async def action_delete_key(key_id: str, request: Request):
    try:
        check_auth_session(request)
    except HTTPException:
        return RedirectResponse(url="/", status_code=303)
        
    if key_id in API_KEYS_DB:
        del API_KEYS_DB[key_id]
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/api/{endpoint}")
async def gateway_proxy_handler(endpoint: str, request: Request):
    if endpoint not in VALID_ENDPOINTS:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Endpoint profile not found"})
    
    query_params = dict(request.query_params)
    user_provided_key = query_params.get("key")
    
    if not user_provided_key or user_provided_key not in API_KEYS_DB:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Access Denied: Invalid authentication API key."})
    
    target_key_metadata = API_KEYS_DB[user_provided_key]
    
    current_time_iso = datetime.datetime.now().isoformat()
    if target_key_metadata["expiry"] and current_time_iso > target_key_metadata["expiry"]:
        return JSONResponse(status_code=403, content={"status": "error", "message": "Access Forbidden: Provided key has reached its expiration threshold."})
        
    if target_key_metadata["used"] >= target_key_metadata["limit"]:
        return JSONResponse(status_code=429, content={"status": "error", "message": "Access Throttled: Request allocation balance exhausted."})
    
    if target_key_metadata["allowed_tools"] and endpoint not in target_key_metadata["allowed_tools"]:
        return JSONResponse(status_code=403, content={"status": "error", "message": f"Access Exception: Your token scope does not include access to [{endpoint}]"})

    input_argument_keys = [k for k in query_params.keys() if k != 'key']
    payload_value = query_params.get(input_argument_keys[0], "N/A") if input_argument_keys else "N/A"
    payload_header = input_argument_keys[0].upper() if input_argument_keys else "QUERY"

    audit_string = f"{target_key_metadata['name']} [{user_provided_key}] searched for {payload_header}: {payload_value}"
    LOGS_DB.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": endpoint.upper(),
        "details": audit_string
    })
    
    target_key_metadata["used"] += 1
    
    downstream_parameters = {"key": UPSTREAM_BASE_KEY}
    if input_argument_keys:
        downstream_parameters[input_argument_keys[0]] = payload_value

    try:
        network_call = requests.get(f"{UPSTREAM_URL}/{endpoint}", params=downstream_parameters, timeout=12)
        upstream_payload = network_call.json()
        
        if isinstance(upstream_payload, dict):
            legacy_tags = ["developer", "channel", "owner", "credits", "api_developer"]
            for target_tag in list(upstream_payload.keys()):
                if any(x in target_tag.lower() or x in str(upstream_payload[target_tag]).lower() for x in legacy_tags):
                    del upstream_payload[target_tag]
            
            upstream_payload["api_developer"] = "SHAYAN_EXPLORER"
            if target_key_metadata.get("key_note"):
                upstream_payload["note"] = target_key_metadata["key_note"]
            upstream_payload["status"] = "success"
            
        return upstream_payload
    except Exception:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal processing connection interface fault."})
