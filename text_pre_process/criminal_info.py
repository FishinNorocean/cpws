import pandas as pd
import re

# 读取Excel文件
df = pd.read_csv('sample_data/crime.csv')
try:
    df_Null = df[df['案号'].isnull()]
except:
    pass
df = df[~ df['案号'].isnull()]
df_xg = df[df['案号'].str.contains("刑更")]
df = df[~ df['案号'].str.contains("刑更")]
df_n_first_trial = df[~ df['审理程序'].str.contains('一审')]
df = df[df['审理程序'].str.contains('一审')]
df_unpublished = df[df['全文'].str.contains('未成年|其他情形|调解|国家秘密')]
df = df[~ df['全文'].str.contains('未成年|其他情形|调解|国家秘密')]

for index, row in df.iterrows():
    source_text = row['全文']
    title, remain = source_text.split('号', 1)
    title = title + "号"
    prosecution, remain = remain.split('。', 1)
    print(prosecution)
    




# df.to_csv('output.csv', index = False)


