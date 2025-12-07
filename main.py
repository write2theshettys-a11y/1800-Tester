
import asyncio
import uuid
from fastapi import FastAPI, UploadFile, File, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.responses import StreamingResponse
from datetime import datetime
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
        else:
            response = client.lookups.v1.phone_numbers(number).fetch(type=["carrier"])

            if response.carrier:
                job["results"][number] = "Active"
            else:
                job["results"][number] = "Inactive"

    except:
        job["results"][number] = "Inactive"

    # After updating this number, check if the job is complete (all numbers in terminal states)
    terminal = {"active", "inactive", "twilio disabled"}
    statuses = [str(s).lower().strip() for s in job["results"].values()]
    if all(s in terminal for s in statuses):
        if not job.get("completed_at"):
            job["completed_at"] = datetime.now().astimezone().isoformat()

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
    return JSONResponse({"results": job["results"], "completed_at": job.get("completed_at")})


@app.get("/download_results/{job_id}")
async def download_results(job_id: str):
    job = job_store.get(job_id)
    if not job:
        return JSONResponse({"error":"Job not found"}, status_code=404)

    # Generate PDF in-memory using ReportLab
    try:
        import io
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Results", styles['Title']))
        elements.append(Spacer(1, 12))

        data = [["Number", "Status"]]
        for n, s in job["results"].items():
            data.append([n, s])

        table = Table(data, colWidths=[250, 200])

        # Build table style with header and per-row status coloring
        ts = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#222222')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BOX', (0,0), (-1,-1), 0.25, colors.HexColor('#d9d9d9')),
            ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#e6e6e6')),
        ])

        # Apply status colors per row (rows start at 1)
        for idx, (_, status) in enumerate(job["results"].items(), start=1):
            st = str(status).lower().strip()
            if 'active' in st:
                bg = colors.HexColor('#e6ffed')
                fg = colors.HexColor('#05582f')
            elif 'inactive' in st:
                bg = colors.HexColor('#ffecec')
                fg = colors.HexColor('#8b1e1e')
            else:
                # in-progress / pending / ringing / testing
                bg = colors.HexColor('#fff7e6')
                fg = colors.HexColor('#8a4b00')

            ts.add('BACKGROUND', (1, idx), (1, idx), bg)
            ts.add('TEXTCOLOR', (1, idx), (1, idx), fg)
            ts.add('ALIGN', (1, idx), (1, idx), 'CENTER')

        table.setStyle(ts)

        elements.append(table)
        doc.build(elements)

        buffer.seek(0)
        return StreamingResponse(buffer, media_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename=results_{job_id}.pdf'
        })

    except Exception as e:
        return JSONResponse({"error": f"PDF generation failed: {str(e)}"}, status_code=500)


@app.get("/download_results_csv/{job_id}")
async def download_results_csv(job_id: str):
    job = job_store.get(job_id)
    if not job:
        return JSONResponse({"error":"Job not found"}, status_code=404)

    try:
        import io, csv

        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Write metadata header with completion timestamp
        writer.writerow(["Test Completed At", job.get("completed_at", "")])
        writer.writerow([])
        # Column headers
        writer.writerow(["Number", "Status"])

        for n, s in job["results"].items():
            writer.writerow([n, s])

        csv_bytes = buffer.getvalue().encode('utf-8')
        return StreamingResponse(io.BytesIO(csv_bytes), media_type='text/csv', headers={
            'Content-Disposition': f'attachment; filename=results_{job_id}.csv'
        })

    except Exception as e:
        return JSONResponse({"error": f"CSV generation failed: {str(e)}"}, status_code=500)

@app.get("/download_sample")
async def download_sample():
    sample_path = "sample_numbers.csv"
    if not os.path.exists(sample_path):
        df = pd.DataFrame({"number":["+18005551234","+18001234567","+18005559876"]})
        df.to_csv(sample_path, index=False)
    return FileResponse(sample_path)
