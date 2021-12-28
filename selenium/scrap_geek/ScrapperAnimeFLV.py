# relevant packages & modules
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
from tqdm import tqdm  # from tqdm.notebook
import os
from IPython.display import clear_output


import pandas as pd
class ItemAnimeFLV:
    
    attributes = []
    
    def set_attributes(self, dict_attributes:dict):
        self.attributes = []
        for key,value in dict_attributes.items():
            setattr(self, key, value)
            self.attributes.append(key)
    
    def get_serie(self, map_attributes_to_columns=dict()):
        if len(self.attributes) == 0:
            print("First add atributes with set_attributes")
            return pd.Series()
        
        if len(map_attributes_to_columns) > 0:
            # not supported
            return pd.Series()
        
        data = dict()
        for attribute in self.attributes:
            data[attribute] = getattr(self, attribute)
        
        return pd.Series(data=data)
            


class ScrapperAnimeFLV:
    
    driver = None
    
    logged_in = False
    restarting = False
    
    cache = dict()
    
    stop = False
    
    def __init__(self, path_driver_chrome, start=True, headless=False, smoth = 800, wait_smoth = 1):
        
        
        self.smoth = smoth
        self.wait_smoth = wait_smoth
        self.stop = False
        
        if start:
            if headless:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                print("chrome option --headless")
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
        
        self.driver.find_element(By.CSS_SELECTOR, "div[class='AFixed']").click()
        self.wait(2)
        self.driver.find_element(By.CSS_SELECTOR, "div[class='Login']").click()
        self.wait(2)
        web_element_username = self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")
        web_element_username.clear()
        web_element_username.send_keys(username)

        web_element_password = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        web_element_password.clear()
        web_element_password.send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait(3)
        self.driver.get("https://www3.animeflv.net/browse")
        self.logged_in = True
        print("Logged in!")
        
    def obtain_urls_items(self, url_begin="https://www3.animeflv.net/browse?page=1", early_stop=-1):
        
        if not self.check_requisites():
            return []
        
        queue = [url_begin]

        urls = []

        while len(queue) > 0:
            
            if early_stop != -1 :
                if len(urls) > early_stop:
                    break
                
            url_page = queue.pop()

            self.driver.get(url_page)
            self.wait(1)
            
            items_cards = self.driver.find_elements(By.XPATH, "//ul[contains(@class,'ListAnimes')]/li/article/a")
            for card in items_cards:
                urls.append(card.get_attribute("href"))

            try:
                element_next = self.driver.find_element(By.XPATH, "//ul[@class='pagination']/li[last()]")
                if element_next.get_attribute("class") != "disabled":
                    url_next = element_next.find_element(By.XPATH, "./a").get_attribute("href")
                    queue.append(url_next)
            except:
                print("Error at parsing next of", url_page)

        return urls


    def scrape_items(self, timers: dict(),
                     url_begin="https://www3.animeflv.net/browse?page=1", 
                     urls=None,
                     header=["title","title_alternative1","title_alternative2","rating","votes","type_serie","cover","state","followers","categories","related","episodes","description","reactions_like","reactions_funny","reactions_love","reactions_surprise","reactions_angry","reactions_sad","reactions_total"], early_stop=-1):
        
        df = pd.DataFrame(columns=header)
        
        if not self.check_requisites():
            return df
        
        try:
            urls_items = urls
            if urls is None:
                urls_items = self.obtain_urls_items(url_begin=url_begin, early_stop=-1)
            
            self.cache["urls"] = urls_items
            self.cache["index_seen"] = -1
            self.cache["urls_error"] = []
            self.cache["df"] = df
            
            
            
            index_df = 0

            timer_load_page = timers.get("timer_load_page", 2)
            timer_load_disqus = timers.get("timer_load_disqus",1)
            timer_load_reactions = timers.get("timer_load_reactions",1)
            
            
            for url in tqdm(urls_items):
                
                # initial
                self.driver.get(url)
                self.wait(timer_load_page)
                def extract_first(elements, mapping=None, default="none"):
                    elements_len = len(elements)
                    if elements_len == 0:
                        return default
                    
                    
                    try:
                        element = elements[0].text
                        if mapping is not None:
                            element = mapping(element)
                        return element
                    except:
                        return default


                def parse_multiple(web_elements, separator="|"):
                    
                    out = ""
                    for i in range(len(web_elements)):
                        out += web_elements[i].text
                        if i < len(web_elements)-1:
                            out += separator        
                    return out
                    
                title = extract_first(self.driver.find_elements(By.CSS_SELECTOR, "h1.Title"),default=url)
                title_alternatives = self.driver.find_elements(By.CSS_SELECTOR, "span.TxtAlt")
                title_alternatives_len = len(title_alternatives)
                title_alternative1 = "none"
                title_alternative2 = "none"

                if title_alternatives_len > 2:
                    title_alternative1 = title_alternatives[-2].text
                    title_alternative2 = title_alternatives[-1].text
                else:
                    index_alternative = 0
                    if title_alternatives_len > index_alternative:
                        title_alternative1 = title_alternatives[index_alternative].text
                        index_alternative += 1            
                    if title_alternatives_len > index_alternative:
                        title_alternative2 = title_alternatives[index_alternative].text
                        index_alternative += 1
                try:
                    rating = extract_first(self.driver.find_elements(By.CSS_SELECTOR, "span#votes_prmd"), mapping=float, default=0)
                    votes = extract_first(self.driver.find_elements(By.CSS_SELECTOR, "span#votes_nmbr"), mapping=int, default=0)
                    type_serie = extract_first(self.driver.find_elements(By.CSS_SELECTOR, "span.Type"))
                    cover = self.driver.find_elements(By.XPATH, "//div[@class='AnimeCover']/div/figure/img")
                    cover = "none" if len(cover) == 0 else cover[0].get_attribute("src")

                    state = extract_first(self.driver.find_elements(By.XPATH, '//p[contains(@class,"AnmStts")]/span'))
                    followers = extract_first(self.driver.find_elements(By.XPATH, '//div[contains(@class,"Title")]/span'), mapping=int, default=0)

                    categories = parse_multiple(self.driver.find_elements(By.XPATH, '//nav[contains(@class,"Nvgnrs")]/a'))

                    description = extract_first(self.driver.find_elements(By.XPATH, '//div[contains(@class,"Description")]/p')).replace("\n", "")
                    related = parse_multiple(self.driver.find_elements(By.XPATH, '//ul[@class="ListAnmRel"]/li'))

                    episodes = float(extract_first(self.driver.find_elements(By.XPATH, '//ul[@id="episodeList"]/li/a/p'), default="Episodio 0").split(" ")[1])

                
                except Exception as error1:
                    print("Error with basic parsing", url, error1)
                    self.cache["urls_error"].append(url)
                    self.cache["index_seen"] += 1
                    continue
                
                holder_error = "Error in iframe"
                switched = False
                try:
                    errors_maximum = 5
                    errors_actual = 0
                    done = False
                    
                    
                    while not done and errors_actual < errors_maximum:
                        
                        try:
                            result = self.driver.execute_script('var element = document.querySelector("#disqus_thread"); if(element){element.scrollIntoView();return 1;}else{return 0}')
                    
                            if result == int(0):
                                state = "404 not found"
                                reactions_like = 0
                                reactions_funny = 0
                                reactions_love = 0
                                reactions_surprise = 0
                                reactions_angry = 0
                                reactions_sad = 0
                            else:
                                self.wait(timer_load_disqus)
                                frame_disqus = self.driver.find_elements(By.XPATH, '//div[@id="disqus_thread"]/iframe')[0]
                                self.driver.switch_to.frame(frame_disqus)
                                switched = True
                                reactions = self.driver.find_elements(By.XPATH, "//div[contains(@class,'reaction-item__enabled')]")
                                reactions[0].click()
                                
                                self.wait(timer_load_reactions)
                                # refresh in case no voted
                                reactions = self.driver.find_elements(By.XPATH, "//div[contains(@class,'reaction-item__enabled')]")
                                

                                def get_reactions_number(web_element_reaction):
                                    s = web_element_reaction.find_element(By.XPATH, ".//div[@class='reaction-item__votes']").text
                                    n = 0
                                    if len(s) > 0:
                                        n = int(s.strip())
                                    
                                    return n

                                reactions_like = get_reactions_number(reactions[0]) - 1
                                reactions_funny = get_reactions_number(reactions[1])
                                reactions_love = get_reactions_number(reactions[2])
                                reactions_surprise = get_reactions_number(reactions[3])
                                reactions_angry = get_reactions_number(reactions[4])
                                reactions_sad = get_reactions_number(reactions[5])
                                
                            done = True
                        except Exception as hold:
                            errors_actual += 1
                            holder_error = hold
                            print("Discuss error", errors_actual, end=". ")
                            if switched:
                                self.driver.switch_to.parent_frame()
                                switched = False
                          
                    if not done:
                        raise Exception()
                          
                    
                except:
                    print("Error with iframe parsing", url, holder_error)
                    self.cache["urls_error"].append(url)
                    self.cache["index_seen"] += 1
                    continue
                """
                print(title, title_alternative1, title_alternative2)
                print(rating,votes,type_serie)
                print(cover, state, followers)
                print(categories)
                print(related, episodes)
                """

                item_dict = {
                    "title": title,
                    "title_alternative1": title_alternative1,
                    "title_alternative2": title_alternative2,
                    "rating": rating,
                    "votes": votes,
                    "type_serie": type_serie,
                    "cover": cover,
                    "state": state,
                    "followers": followers,
                    "categories": categories,
                    "related": related,
                    "episodes": episodes,
                    "description": description,
                    "reactions_like": reactions_like,
                    "reactions_funny": reactions_funny,
                    "reactions_love": reactions_love,
                    "reactions_surprise": reactions_surprise,
                    "reactions_angry": reactions_angry,
                    "reactions_sad": reactions_sad,
                    "reactions_total": reactions_like+reactions_funny+reactions_love+reactions_surprise+reactions_angry+reactions_sad,
                }
                
                item = ItemAnimeFLV()
                item.set_attributes(item_dict)
                # Warning: not parallelism/concurrency or RAM controled
                df.at[index_df, :] = item.get_serie()
                index_df += 1
                self.cache["df"] = df
                self.cache["index_seen"] += 1
                
                if self.stop:
                    return df, False
            print("Finished!")
            return df, True
        except Exception as error:
            print("General Error:", error)
            return df, False


    def close(self):
        print("CLOSING OBJECT...")
        if self.driver:
            self.driver.close()
            
    def __del__(self):
        print("DESTRUCTING OBJECT")
        if not self.restarting:
            self.close()
