import os
import pandas as pd

shards = os.listdir("./temp")
print(len(shards))

df = pd.DataFrame(columns=["title","title_alternative1","title_alternative2","rating","votes","type_serie","cover","state","followers","categories","related","episodes","description","reactions_like","reactions_funny","reactions_love","reactions_surprise","reactions_angry","reactions_sad","reactions_total"])

for shard in shards:
    file_name = f"./temp/{shard}"
    df = pd.concat([df, pd.read_csv(file_name)], axis=0, ignore_index=True)
    
df.to_csv("merged_shards.csv",index=False)