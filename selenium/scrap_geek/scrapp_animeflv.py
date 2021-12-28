from ScrapperAnimeFLV import ScrapperAnimeFLV
from Jobs import State, get_job_template, save_job, load_job
import json
import pandas as pd
import signal
import sys
import os


args = sys.argv
args_len = len(args)
if args_len == 1:
    print("Send arguments!!")
    sys.exit()
    
job_name = args[1]

headless = False
if args_len > 2:
    if args[2] == "headless":
        headless = True
print("HEADLESS MODE", headless)
        
        
global scrapper


### JOB
  


# clear_output()

global job, file_job


folder_job = os.path.join("jobs",job_name)
file_job = os.path.join(folder_job,"info.json")

if os.path.isdir(folder_job):
    job = load_job(file_job)
else:
    os.mkdir(folder_job)
    job = get_job_template(job_name)
    save_job(file_job, job)
    

def close_job(is_completed, df):
    global scrapper
    global file_job, job 
    print("Stopping scraper...", is_completed, type(df))
    scrapper.stop = True
    
    print("Saving job...")
    
    pending = []
    if not is_completed:
        index_seen = scrapper.cache.get("index_seen",-1)
        pending = scrapper.cache.get("urls",[])
        if len(pending) > 0:
            pending = pending[index_seen+1:]
          
        df = scrapper.cache.get("df", None)
        
    job['urls_queued'] = pending
    
    job['urls_error'] = scrapper.cache.get("urls_error", [])
    save_job(file_job, job)
    
    if df is not None:
        df.to_csv(f"temp/db_{job['name']}_items{job['execution_time']}.csv", index=False)
    
    print(f"Closing with: {len(scrapper.cache.get('urls',[])) -len(job['urls_queued'])} completed, {len(job['urls_queued'])} pending urls and {len(job['urls_error'])} error urls")
    

def signal_handler(sig, frame):
    close_job(False, None)
    
    try:
        sys.exit()
    except:
        print("Problems with sys.exit!")
        sys.exit()
        
signal.signal(signal.SIGINT, signal_handler)

df = pd.DataFrame()

print(f"Begin work, don't open or touch files in {folder_job}")

timers = {
    "timer_load_page": 2,
    "timer_load_disqus": 2,
    "timer_load_reactions": 1
}

state = job["state"]

if state != State.END:
    
    f = open(".env.json", "r")
    env = json.load(f)
    f.close()
    scrapper = ScrapperAnimeFLV(headless=headless, path_driver_chrome = "/home/magody/chromedriver_linux64/chromedriver")
    scrapper.driver.get("https://www3.animeflv.net/")
    scrapper.wait(5)
    # clear_output()
    ### LOGIN
    scrapper.login(env["username_animeflv"], env["password_animeflv"])
    del env["password_animeflv"]


if state == State.BEGIN:
    print("Begining")
    df = scrapper.scrape_items(timers, url_begin="https://www3.animeflv.net/browse?page=1")
    close_job(True, df)
elif state == State.PENDING_ITEMS:
    scrapper.stop = False
    urls_items = job["urls_queued"]
    urls_items.extend(job["urls_error"])  # try again the errors
    job["urls_error"] = []
    job["execution_time"] += 1
    print(f"Pending work...{len(urls_items)} urls in queue")
    df, completed = scrapper.scrape_items(timers, urls=urls_items)
    print("scrape_items ended")
    if completed and len(scrapper.cache["urls_error"]) == 0: 
        job["state"] = State.END
    close_job(completed, df)
elif state == State.END:
    print("Work already completed!")
else:
    print("Can't handle this state")
    
    
    



