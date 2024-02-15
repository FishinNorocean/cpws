import pandas as pd


# 读取Excel文件
df = pd.read_csv('sample_data/18_04_all.csv')
print(df.columns)

# 只取出F列为“刑事案件”的数据且删掉空行
df = df[df['案件类型'] == '刑事案件']
df = df.dropna(subset=['全文'])

# 这里的目的是为了去掉特定的部分
# df['全文'] = df['全文'].str.replace('依照.*裁定如下：', '', regex=True)
# df['全文'] = df['全文'].str.replace('依照.*判决如下：', '', regex=True)
# df['全文'] = df['全文'].str.replace('来源：马 克 数 据 网', '', regex=True)
# df['全文'] = df['全文'].str.replace('更多数据：www.macrodatas.cn', '', regex=True)
# df['全文'] = df['全文'].str.replace('更多数据：搜索“马克数据网”来源：www.macrodatas.cn', '', regex=True)
# df['全文'] = df['全文'].str.replace('关注公众号“马 克 数 据 网”', '', regex=True)
# df['全文'] = df['全文'].str.replace('微信公众号“马克 数据网”', '', regex=True)
# df['全文'] = df['全文'].str.replace('百度搜索“马 克 数 据 网”', '', regex=True)
# df['全文'] = df['全文'].str.replace('来自马克数据网', '', regex=True)
# df['全文'] = df['全文'].str.replace('关注公众号“马克数据网”', '', regex=True)
# df['全文'] = df['全文'].str.replace('搜索“马 克 数 据 网”', '', regex=True)
# df['全文'] = df['全文'].str.replace('[\s\S]{3}马\s*克\s*数\s*据\s*网\s*[\s\S]{3}', '', regex=True)
# df['全文'] = df['全文'].str.replace('马\s*克\s*数\s*据\s*网', '', regex=True)
# df['全文'] = df['全文'].str.replace('www.macrodatas.cn', '', regex=True)
# df['全文'] = df['全文'].str.replace('微信公众号', '', regex=True)
# df['全文'] = df['全文'].str.replace('来自', '', regex=True)
# df['全文'] = df['全文'].str.replace('百度', '', regex=True)
# df['全文'] = df['全文'].str.replace('搜索', '', regex=True)
# df['全文'] = df['全文'].str.replace('来源', '', regex=True)


df.to_csv('sample_data/crime.csv', index = False)


