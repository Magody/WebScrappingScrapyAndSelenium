import os
url = "https://twitter.com/saorikiyomix/status/1470455870970499074"
output = "/home/magody/programming/python/web_scrapping/selenium/scrap_instagram/temp/"
output += "vid1.mp4"
os.system(f"youtube-dl {url} -o {output} -q")