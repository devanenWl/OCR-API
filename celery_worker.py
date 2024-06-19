from celery import Celery
import os
from helper import split_pdf_into_images
from coze_api import image_processing, report_ms_token, chat
from mongodb import connect
from concurrent.futures import ThreadPoolExecutor
from run import headers_global
import time
import random
import traceback

# Get environment variables
REDIS_HOST = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('celery_worker', broker=REDIS_HOST, backend=REDIS_HOST)
pdf_collection, result_collection, account_collection = connect()

def find_account(account_collection):
    account = account_collection.find_one({"use": {"$lt": 50}, "lock": 0})
    if not account:
        return None, None
    # account = account_collection.find_one({"use": {"$lt": 50}})
    # Modify the cookie to be locked and increment the use count
    # If last_used is 0, set it to the current time, if last_used > 86400, set it to the current time, reset use count
    if int(time.time()) - account["last_used"] > 86400:
        timestamp = int(time.time())
        account_collection.update_one({"_id": account["_id"]}, {"$set": {"last_used": timestamp, "use": 1, "lock": 1}})
    else:
        account_collection.update_one({"_id": account["_id"]}, {"$set": {"lock": 1}, "$inc": {"use": 1}})
    return account["cookie"], account["_id"]


def release_account(account_id, account_collection):
    account_collection.update_one({"_id": account_id}, {"$set": {"lock": 0}})
    return


def lock_account(account_id, account_collection):
    account_collection.update_one({"_id": account_id}, {"$set": {"use": 50}})
    return


def recover_use(account_id, account_collection):
    account_collection.update_one({"_id": account_id}, {"$inc": {"use": -1}})
    return


def process_image_task(image, pdf_id, image_index):
    while True:
        pdf_collection, result_collection, account_collection = connect()
        headers = headers_global
        cookie, account_id = find_account(account_collection)
        headers["Cookie"] = cookie
        if not cookie:
            print("No account available")
            time.sleep(5)
            continue
        new_msToken, headers, cookie = report_ms_token(cookie, headers)
        time.sleep(5)
        try:
            try:
                image_data = image_processing(cookie, image, headers)
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                account_collection.delete_one({"_id": account_id})
                continue
            if "Error" in image_data:
                print("Error in image data")
                # Delete the account from the database
                account_collection.delete_one({"_id": account_id})
                time.sleep(random.randint(10, 30))
                continue
            data_return = chat(cookie, image_data, headers)
            if "Error" in data_return:
                print("Error in data return")
                release_account(account_id, account_collection)
                recover_use(account_id, account_collection)
                time.sleep(random.randint(10, 30))
                continue
            if 'Wait' in data_return:
                print("Wait few seconds")
                time.sleep(random.randint(10, 30))
                release_account(account_id, account_collection)
                recover_use(account_id, account_collection)
                continue
            if 'Quota' in data_return or 'Banned' in data_return:
                print("Quota exceeded")
                release_account(account_id, account_collection)
                lock_account(account_id, account_collection)
                time.sleep(random.randint(10, 30))
                continue
            release_account(account_id, account_collection)
            struct_result = {"pdf": pdf_id, "image": [], "text": data_return, "page": image_index}
            result_collection.insert_one(struct_result)
            break
        except Exception as e:
            release_account(account_id, account_collection)
            print(e)
            print(traceback.format_exc())
            continue


@celery_app.task
def process_task(pdf_path):
    pdf_collection, result_collection, account_collection = connect()
    images = split_pdf_into_images(pdf_path)
    struct_pdf = {"images": [], "pdf": pdf_path, "total_pages": len(images)}
    pdf_id = pdf_collection.insert_one(struct_pdf).inserted_id

    tasks = []
    # Limit the number of concurrent tasks to 5
    with ThreadPoolExecutor(max_workers=5) as executor:
        for index, image in enumerate(images):
            tasks.append(executor.submit(process_image_task, image, pdf_id, index))
            time.sleep(15)
        for task in tasks:
            task.result() # Wait for all tasks to finish


    # Find all result with pdf id, sort by page
    results = result_collection.find({"pdf": pdf_id}).sort("page", 1)
    return_data = """\\begin{document}
    """
    for result in results:
        try:
            return_data += result["text"].split('\\begin{document}')[1].split('\\end{document}')[0]
        except Exception as e:
            print(e)
            continue
    return_data += """\\end{document}
    """
    return return_data
