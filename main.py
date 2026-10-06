from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import os, json, io, requests

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = FastAPI()

def get_drive_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise Exception("GOOGLE_CREDENTIALS_JSON env Render pe missing hai")
    info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

@app.get("/", response_class=HTMLResponse)
def home():
    folder_set = "YES" if os.getenv("DRIVE_FOLDER_ID") else "NO - MISSING"
    json_set = "YES" if os.getenv("GOOGLE_CREDENTIALS_JSON") else "NO - MISSING"
    return f"""
    <h2>Vanshi Auto Drive System - FIXED</h2>
    <p>Folder ID: <b>{folder_set}</b> | JSON: <b>{json_set}</b></p>
    <input id="p" placeholder="car" style="width:300px;padding:10px" value="car">
    <button onclick="gen()" style="padding:10px">Generate & Save to Drive</button>
    <p id="status" style="font-weight:bold;color:blue"></p>
    <script>
    async function gen(){{
        let prompt = document.getElementById('p').value;
        document.getElementById('status').innerText = "Ban raha hai... 40 sec wait karo";
        try {{
            let res = await fetch('/generate?prompt='+encodeURIComponent(prompt));
            let data = await res.json();
            if(data.error) throw data.error;
            document.getElementById('status').innerText = "HO GAYA! File ID: " + data.file_id;
        }} catch(e){{
            document.getElementById('status').innerText = "ERROR: " + JSON.stringify(e).substring(0,500);
        }}
    }}
    </script>
    """

@app.get("/generate")
def generate(prompt: str = Query(...)):
    try:
        folder_id = os.getenv("DRIVE_FOLDER_ID")
        if not folder_id:
            return {"error": "DRIVE_FOLDER_ID env missing hai"}

        service = get_drive_service()
        
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
        r = requests.get(url, timeout=60)
        
        safe_name = "".join
