# Setup and login
import json


class State:
    BEGIN = 0
    PENDING_URLS = 1
    PENDING_ITEMS = 2
    END = 3
    PENDING_URLS_ITEMS = 4

def get_job_template(job_name):
    return {
            "state": State.BEGIN,
            "name": job_name,
            "urls_queued": [],
            "urls_error": [],
            "execution_time": 1
        }

def save_job(file_job, job):
    with open(file_job, 'w') as f:
        json.dump(job, f, ensure_ascii=False, indent=4)
        
def load_job(file_job):
    with open(file_job) as f:
        return json.load(f)