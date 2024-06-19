from multiprocessing import Process
import subprocess
import os
from dotenv import load_dotenv

headers_global = {}
headers_global["Content-Type"] = "application/json"
headers_global["Origin"] = "https://www.coze.com"
headers_global["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
headers_global["Referer"] = "https://www.coze.com/store/bot"

def load_env():
    try:
        load_dotenv()
    except Exception as e:
        print(e)
    REDIS_HOST = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

def start_api(path='.'):
    subprocess.call(['uvicorn', 'app:app', '--port', '8000'], cwd=path)

def start_frontend(path='.'):
    PORT = os.getenv('PORT', '8501')
    subprocess.call(['streamlit', 'run', 'Home.py', '--server.port', PORT], cwd=path)

def start_celery_worker(path='.'):
    subprocess.call(['celery', '-A', 'celery_worker', 'worker', '--loglevel=info'], cwd=path)

if __name__ == '__main__':
    path = os.path.realpath(os.path.dirname(__file__))
    load_env()
    api = Process(target=start_api, kwargs={'path': path})
    frontend = Process(target=start_frontend, kwargs={'path': path})
    celery_worker = Process(target=start_celery_worker, kwargs={'path': path})
    api.start()
    frontend.start()
    celery_worker.start()
    api.join()
    frontend.join()
    celery_worker.join()