import json

with open('./temp.json') as f:
    data: dict = json.load(f)
    d = data["graphql"]["shortcode_media"]
    print(d['display_url'])
    print(d['video_url'])
    
    
    
