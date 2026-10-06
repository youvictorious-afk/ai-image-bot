from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import os, json, io, requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

app = FastAPI()

# Render pe tu ye 2 env variable dalega
FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

def get_drive_service():
    # JSON ko env se lega
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise Exception("GOOGLE_CREDENTIALS_JSON env nahi mila")
    
    info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

def upload_to_drive(image_bytes, filename):
    service = get_drive_service()
    media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype='image/png')
    file_metadata = {'name': filename, 'parents': [FOLDER_ID]}
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>Vanshi Auto Drive System</h2>
    <input id="p" placeholder="ex: modern wooden sofa" style="width:300px;padding:10px">
    <button onclick="gen()" style="padding:10px">Generate & Save to Drive</button>
    <p id="status"></p>
    <script>
    function gen(){
        let prompt = document.getElementById('p').value;
        document.getElementById('status').innerText = "Ban raha hai, Drive pe ja raha hai...";
        fetch('/generate?prompt='+prompt).then(r=>r.json()).then(d=>{
            document.getElementById('status').innerText = "Ho gaya! File ID: " + d.file_id;
        })
    }
    </script>
    """

@app.get("/generate")
def generate(prompt: str = Query(...)):
    # FREE wala model - bina API key ke chalega
    # Baad me tu isko Stability AI / OpenAI se replace kar sakta hai
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"
    image_bytes = requests.get(url).content
    
    safe_name = "".join(c for c in prompt[:30] if c.isalnum() or c==' ') + ".png"
    file_id = upload_to_drive(image_bytes, safe_name)
    return {"status": "saved", "file_id": file_id, "filename": safe_name}
