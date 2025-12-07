
import asyncio
import uuid
from fastapi import FastAPI, UploadFile, File, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import pandas as pd
from io import StringIO
import os

from twilio.rest import Client

from dotenv import load_dotenv
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

print("SID:", os.getenv("TWILIO_ACCOUNT_SID"))
print("TOKEN:", os.getenv("TWILIO_AUTH_TOKEN"))

client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

job_store = {}

async def check_number_twilio(job_id: str, number: str):
    job = job_store.get(job_id)
    if not job: return

    job["results"][number] = "Ringing"

    try:
        await asyncio.sleep(1)

        if client is None:
            job["results"][number] = "Twilio Disabled"
            return

        response = client.lookups.v1.phone_numbers(number).fetch(type=["carrier"])

        if response.carrier:
            job["results"][number] = "Active"
        else:
            job["results"][number] = "Inactive"

    except:
        job["results"][number] = "Inactive"

@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        content = await file.read()
        csv_text = content.decode("utf-8")
        df = pd.read_csv(StringIO(csv_text))
        numbers = df.iloc[:,0].astype(str).tolist()

        job_id = str(uuid.uuid4())

        job_store[job_id] = {"numbers": numbers, "results": {n:"Testing..." for n in numbers}}

        for num in numbers:
            background_tasks.add_task(check_number_twilio, job_id, num)

        return templates.TemplateResponse("results.html", {"request": request, "job_id": job_id, "results": job_store[job_id]["results"]})

    except Exception as e:
        return {"error": f"Error reading CSV file: {str(e)}"}

@app.get("/api/results/{job_id}")
async def api_results(job_id: str):
    job = job_store.get(job_id)
    if not job:
        return JSONResponse({"error":"Job not found"}, status_code=404)
    return JSONResponse(job["results"])

@app.get("/download_sample")
async def download_sample():
    sample_path = "sample_numbers.csv"
    if not os.path.exists(sample_path):
        df = pd.DataFrame({"number":["+18005551234","+18001234567","+18005559876"]})
        df.to_csv(sample_path, index=False)
    return FileResponse(sample_path)
