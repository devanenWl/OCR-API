from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
from celery_worker import process_task
import os
from mongodb import connect

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
    task = process_task.delay(file_path, task_id)

    return {"message": "PDF processing started, go to the status page to check the status", "task_id": task.id}


@app.get("/check-status/{task_id}")
async def check_status(task_id: str):
    task_result = process_task.AsyncResult(task_id)
    if task_result.state == "PENDING" or not task_result.ready():
        pdf_collection, result_collection, account_collection = connect()
        result = result_collection.find({"task_id": task_id}).sort("page", 1)
        result = list(result)
        if len(result) > 0:
            return_data = """\\begin{document}
            """
            for res in result:
                try:
                    return_data += res["text"].split('\\begin{document}')[1].split('\\end{document}')[0]
                except Exception as e:
                    try:
                        try:
                            return_data += res["text"].split('```latex')[1].split('```')[0]
                        except:
                            return_data += res["text"].split('```')[1].split('```')[0]
                    except Exception as e:
                        continue
            return_data += """\\end{document}
            """
            return {"status": "processing", "result": return_data}
        return {"status": "processing", "result": "Processing in progress"}
    else:
        return {"status": "complete", "result": task_result.get()}