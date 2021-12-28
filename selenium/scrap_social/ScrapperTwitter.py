# relevant packages & modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import urllib.request
import json
from tqdm.notebook import tqdm
import os
from IPython.display import clear_output

class ScrapperTwitter:
    
    driver = None
    
    logged_in = False
    restarting = False
    
    def __init__(self, path_driver_chrome, start=True, headless=False, smoth = 800, wait_smoth = 1):
        
        
        self.smoth = smoth
        self.wait_smoth = wait_smoth
        
        if start:
            if headless:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                self.driver = webdriver.Chrome(executable_path=path_driver_chrome, options=chrome_options)
            else:
                self.driver = webdriver.Chrome(executable_path=path_driver_chrome)
        
            self.wait(3)
        
    def wait(self, t):
        time.sleep(t)
        
    def check_requisites(self):
        
        if not self.logged_in:
            print("Please login first")
            return False        
        return True
    
    def login(self, username, password, control_unusual=False, user="DannyDa80813926"):
        
        self.driver.get("https://twitter.com/i/flow/login")
        self.wait(5)
        web_element_username = self.driver.find_element(By.CSS_SELECTOR, "input[autocomplete='username']")
        web_element_username.clear()
        web_element_username.send_keys(username)
        self.driver.find_element(By.XPATH, '//div[@role="button" and div/span/span/text() = "Next"]').click()
        self.wait(3)
        
        if control_unusual:
            web_element_unusual = self.driver.find_element(By.CSS_SELECTOR, "input[name='text']")
            web_element_unusual.clear()
            web_element_unusual.send_keys(user)
            self.driver.find_elements(By.XPATH, '//div[@role="button" and div/span/span/text() = "Next"]')[-1].click()
            self.wait(3)
        
        web_element_password = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        web_element_password.clear()
        web_element_password.send_keys(password)
        self.wait(2)
        self.driver.find_elements(By.XPATH, '//div[@role="button" and div/span/span/text() = "Log in"]')[-1].click()
        self.wait(3)
        self.logged_in = True
        print("Logged in!")
        
    def scrape_urls(self, url, early_stop=-1):
        
        if not self.check_requisites():
            return [], []
        
        # Adding information about user agent
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        
        self.driver.get(url)
        self.wait(3)

        #scroll
        scrolldown=self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
        match=False

        collected_urls_imgs = []
        collected_urls_videos = []

        next_height = 0
        continues = 0
        while not match:
            
            if early_stop != -1:
                if len(collected_urls_imgs) > early_stop:
                    break
                
            last_count = scrolldown
            chunk_imgs = self.driver.find_elements(By.XPATH, '//div[contains(@aria-label,"Timeline:")]/div/div//img[@alt="Image"]')
            chunk_videos = self.driver.find_elements(By.XPATH, '//div[contains(@aria-label,"Timeline:")]/div/div[count(.//video) > 0]//a[contains(@href,"status")]')
            
            collected = 0
            for c in chunk_imgs:
                try:
                    link = str(c.get_attribute("src"))
                    if not link in collected_urls_imgs and not link.endswith("svg"):
                        if link.endswith("small"):
                            collected_urls_imgs.append(link)
                            collected += 1
                except Exception as error:
                    pass
                
            for c in chunk_videos:
                try:
                    link = str(c.get_attribute("href"))
                    if not link in collected_urls_videos:
                        collected_urls_videos.append(link)
                        collected += 1
                except Exception as error:
                    pass
            
            if collected == 0:
                continues += 1
                if continues > 4:
                    print("Nothing new found, if this repeat, change the configuration")
            else:
                continues = 0
            next_height += self.smoth
            scrolldown = self.driver.execute_script(f"window.scrollTo(0, Math.min(document.body.scrollHeight, {next_height}));var scrolldown=Math.min(document.body.scrollHeight, {next_height});return scrolldown;")
            self.wait(self.wait_smoth)
            
            if last_count==scrolldown:
                match=True
                
        
        return collected_urls_imgs, collected_urls_videos


    def scrape_profile(self,url,output_dir="temp", early_stop=-1):
        
        results = {"collected_imgs": 0, "collected_videos": 0}
        
        if not self.check_requisites():
            return results
        
        collected_urls_imgs, collected_urls_videos = self.scrape_urls(url,early_stop)
        
        clear_output()
        
        errors = []
        
        print(f"Images:{len(collected_urls_imgs)},Videos:{len(collected_urls_videos)}")
        print("Downloading images...")
        collected_imgs = 0
        for i in tqdm(range(len(collected_urls_imgs))):
            url_img = collected_urls_imgs[i].replace("small", "large")
            try:
                filename = f"{output_dir}/img{i}.jpg"
                urllib.request.urlretrieve(url_img, filename)
                collected_imgs += 1
            except Exception as error:
                errors.append(url_img)
                
        print("Downloading videos...")
        collected_videos = 0
        for i in tqdm(range(len(collected_urls_videos))):
            url_video = collected_urls_videos[i]
            output_filename = f"{output_dir}/video{i}.mp4"
            try:
                os.system(f"youtube-dl {url_video} -o {output_filename} -q >/dev/null 2>&1")
                collected_videos += 1
            except Exception as error:
                errors.append(url_video)
            
        results["collected_imgs"] = collected_imgs
        results["failed_imgs"] = len(collected_urls_imgs) - collected_imgs
        results["collected_videos"] = collected_videos
        results["failed_videos"] = len(collected_urls_videos) - collected_videos
        results["errors"] = errors
        return results

    def close(self):
        if self.driver:
            self.driver.close()
            
    def __del__(self):
        if not self.restarting:
            print("Closing...")
            self.close()