# This is a python file written by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# set up
import pandas as pd
import threading
import os
import re

# the package os and the following line of code get your working directory so don't worry about your working directory
PJ_path = os.path.dirname(os.path.abspath(__file__))
Model_path = os.path.join(PJ_path, 'chatglm3-6b')
# import the model and initialize the dialog
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(Model_path, trust_remote_code=True, device='cuda')
model = model.eval()

# basic prompt
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因："

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","content", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉"])





def process_data(df,file_name):
    global df_output
    num_rows = min(101, df.shape[0])
    i = 26
    #for i in range(0, num_rows):#这里要注意从第几行开始算，如果第一行没有标题的就填-1，有标题填0，不然会落，这里python索引是从0开始算第一行，所以要-1
    cell_value = df.iloc[i, 14]
    prompt = str(cell_value) + bsc_prpt
    print(prompt)
    print(len(prompt))
    trial = 0
    file = open(os.path.join(PJ_path, "debug.results/File_{}_Row_{}".format(file_name, str(int(i)))), "a", encoding = "utf-8")
    file.truncate(0)
    file.write(prompt)
    file.write("\n")
    while trial < 5:
        trial = trial + 1
        try:
            response, history = model.chat(tokenizer, prompt, history=[])
            good_response = True
            file.write(response)
            file.write("\n")
        except Exception as Error:
            good_response = False
            Error = "Bad response. sys:" + str(Error)
            file.write(Error)
            file.wirte("\n")
                



df1 = pd.read_excel(os.path.join(PJ_path, 'data/101-200.xlsx'), sheet_name='Sheet1')


t1 = threading.Thread(target=process_data, args=(df1,"101-200.xlsx"))


t1.start()

t1.join()