from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os


def connect():
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["ocr"]
    pdf_collection = db["pdf"]
    result_collection = db["result"]
    account_collection = db["account"]
    google_api_collection = db["google_api"]
    return pdf_collection, result_collection, account_collection, google_api_collection
