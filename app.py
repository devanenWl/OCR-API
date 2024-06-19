from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
from celery_worker import process_task
import os


app = FastAPI()

# Try to mkdir temp folder
try:
    os.mkdir("./temp")
except FileExistsError:
    pass

@app.post("/submit-pdf/")
async def submit_pdf(file: UploadFile = File(...)):
    # Save the uploaded PDF to a temporary file
    task_id = str(uuid4())
    file_path = f"./temp/{task_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Submit the task to Celery
    task = process_task.delay(file_path)

    return {"message": "PDF processing started, go to the status page to check the status", "task_id": task.id}


@app.get("/check-status/{task_id}")
async def check_status(task_id: str):
    task_result = process_task.AsyncResult(task_id)
    if task_result.ready():
        return {"status": "complete", "result": task_result.get()}
    else:
        return {"status": "processing"}
