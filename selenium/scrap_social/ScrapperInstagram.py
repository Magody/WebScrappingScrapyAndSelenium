# relevant packages & modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import urllib.request
import json
from tqdm import tqdm

class ScrapperInstagram:
    
    driver = None
    
    logged_in = False
    
    def __init__(self, path_driver_chrome = "/home/magody/chromedriver_linux64/chromedriver", headless=False):
        
    
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
    
    def login(self, username, password):
        
        self.driver.get("https://www.instagram.com/")
        self.wait(2)
        web_element_username = self.driver.find_element(By.CSS_SELECTOR, "input[name='username']")
        web_element_password = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        web_element_username.clear()
        web_element_password.clear()
        web_element_username.send_keys(username)
        web_element_password.send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait(5) #wait for "save your login info?""
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]").click()
        self.wait(5) # wait for "turn on notifications"
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]").click()
        self.logged_in = True
        print("Logged in!")
        
    def collect_posts(self, url)->list:
        
        if not self.check_requisites():
            return []
        
        self.driver.get(url)
        self.wait(5)
        
        #scroll
        scrolldown=self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
        match=False

        urls_posts = []

        while not match:
            last_count = scrolldown
            chunk = self.driver.find_elements(By.XPATH, '//a')
            
            for c in chunk:
                try:
                    post = str(c.get_attribute("href"))
                    if '/p/' in post and not post in urls_posts:
                        urls_posts.append(post)
                except Exception as error:
                    pass
            
            self.wait(2)
            scrolldown = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
            if last_count==scrolldown:
                match=True
        
        return urls_posts
    
    def scrape_urls(self,posts):
        
        if not self.check_requisites():
            return [], []
        
        # Adding information about user agent
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)
        
        
        collected_urls_imgs = []
        collected_urls_videos = []

        print("Visiting posts...")
        for i,post in tqdm(enumerate(posts)):
            self.driver.get(post)
            self.wait(2)
            
            try:
                exist_video = self.driver.find_element(By.XPATH, "//video")
                exist_video = True
            except:
                exist_video = False
            
            is_image = True
            carrosel = True
            if exist_video:
                is_image = False
                carrosel = False
            
            while carrosel:
                candidates_imgs = self.driver.find_elements(By.XPATH, '//article[@role="presentation"]//img[@class="FFVAD"]')
                
                if candidates_imgs:
                    for c in candidates_imgs:
                        
                        try:
                            url = str(c.get_attribute("src"))
                            if len(url) == 0:
                                print("Cant get image", post)
                        
                            if url not in collected_urls_imgs:
                                collected_urls_imgs.append(url)
                        except Exception as error:
                            pass
                
                try:
                    element = self.driver.find_element(By.XPATH, "//button[contains(@class,'_6CZji')]")
                    self.driver.execute_script("arguments[0].click();", element)
                    self.wait(0.5)
                except Exception as error:
                    element = None
                    carrosel = False
            
            
            if exist_video:
                q = f"{post}?__a=1"
                self.driver.get(q)
                time.sleep(1)
                
                
                state = 0
                try:
                    data = json.loads(self.driver.find_element(By.XPATH, "//pre").text)
                    
                    if len(data) == 0:
                        print("Cant get video", post)
                    state = 1
                    url = data["graphql"]["shortcode_media"]['video_url']
                    if url not in collected_urls_videos:
                        collected_urls_videos.append(url)
                except Exception as error:
                    if state == 0:
                        print("error", error)
                        
        
        return collected_urls_imgs, collected_urls_videos


    def scrape_profile(self,url,output_dir="temp"):
        
        results = {"collected_imgs": 0, "collected_videos": 0}
        
        if not self.check_requisites():
            return results
        
        posts = self.collect_posts(url)
        posts_len =len(posts)
        print(f"Collected: {posts_len} posts")
        
        
        if len(posts) == 0:
            return results
        
        collected_urls_imgs, collected_urls_videos = self.scrape_urls(posts)
        print(f"Images:{len(collected_urls_imgs)},Videos:{len(collected_urls_videos)}")
        print("Downloading images...")
        collected_imgs = 0
        for i in tqdm(range(len(collected_urls_imgs))):
            url_img = collected_urls_imgs[i]
            try:
                filename = f"{output_dir}/img{i}.jpg"
                urllib.request.urlretrieve(url_img, filename)
                collected_imgs += 1
            except Exception as error:
                print("Cant get", url_img)
                
        print("Downloading videos...")
        collected_videos = 0
        for i in tqdm(range(len(collected_urls_videos))):
            url_video = collected_urls_videos[i]
            try:
                filename = f"{output_dir}/video{i}.mp4"
                urllib.request.urlretrieve(url_video, filename)
                collected_videos += 1
            except Exception as error:
                print("Cant get", url_video)
            
        results["collected_imgs"] = collected_imgs
        results["failed_imgs"] = len(collected_urls_imgs) - collected_imgs
        results["collected_videos"] = collected_videos
        results["failed_videos"] = len(collected_urls_videos) - collected_videos
        return results

    def close(self):
        if self.driver:
            self.driver.close()
            
    def __del__(self):
        print("Closing...")
        self.close()