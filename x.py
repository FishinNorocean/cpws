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
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])



def format_output(output):
    try:
        #additional_note_start = output.rfind("|")
        #additional_note = output[additional_note_start+1:].strip()

        lines = output.split("\n")
        if len(lines) < 3: 
            return "Not enough data provided"
        data = lines[2].split("|")
        if len(data) < 6: 
            return "Not enough data provided"

        plaintiff = data[1].strip()
        plaintiff_gender = data[2].strip()
        defendants = data[3].strip()
        defendant_gender = data[4].strip()
        verdict = data[5].strip() if len(data) > 5 else "Data not provided"

        return plaintiff, plaintiff_gender, defendants, defendant_gender, verdict
    except Exception as e:
        return str(e)



def process_data(df,file_name):
    global df_output
    num_rows = min(101, df.shape[0])
    i = 0
    for i in range(0, num_rows):#这里要注意从第几行开始算，如果第一行没有标题的就填-1，有标题填0，不然会落，这里python索引是从0开始算第一行，所以要-1
        
        cell_value = df.iloc[i, 14]
        if type(cell_value) == float:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Empty cell", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None}, index=[0])
            continue
        elif len(cell_value) < 40:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Cell length too short", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None}, index=[0])
            continue
        prompt = str(cell_value) + bsc_prpt
        trial = 0
        for trial in range(5):
            try:
                response, history = model.chat(tokenizer, prompt, history=[])
                good_response = True
            except Exception as Error:
                good_response = False
                Error = "Bad response. sys:" + str(Error)
                break # 结束trial 循环，反正寄了，再试还是寄
            if good_response:
                data = format_output(response)
                if not isinstance(data, str):  # 如果format没毛病
                    for j in range(len(data[2])): # 提取信息到row
                        row = pd.DataFrame({'File':file_name, 'Row':int(i),'Trial':int(trial), '原因': None, '原告': data[0], '原告性别': data[1], '被告': data[2], '被告性别': data[3], '被告是否胜诉': data[4]}, index=[0])
                    break # 结束 trial 循环
        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
        except:
            if good_response:
                Error = "Trials used up. sys:" + data
                Err_report = "FILE {} ROW {} Error: {}".format(file_name, i, Error)
            else:
                Err_report = "FILE {} ROW {} Error: {}".format(file_name, i, Error)
            print(Err_report)
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), '原因': Err_report, '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None}, index=[0])  # 创建一个包含错误原因的DataFrame
            df_output = pd.concat([df_output, row], ignore_index=True)
    df_output.to_excel(os.path.join(PJ_path, 'results/output.xlsx'), index=False)
    df_output.to_csv(os.path.join(PJ_path, 'results/output.csv'), index=False)



df1 = pd.read_excel(os.path.join(PJ_path, 'data/1-100.xlsx'), sheet_name='Sheet1')
df2 = pd.read_excel(os.path.join(PJ_path, 'data/101-200.xlsx'), sheet_name='Sheet1')
df3 = pd.read_excel(os.path.join(PJ_path, 'data/201-300.xlsx'), sheet_name='Sheet1')

t1 = threading.Thread(target=process_data, args=(df1,"1-100.xlsx"))
t2 = threading.Thread(target=process_data, args=(df2,"101-200.xlsx"))
t3 = threading.Thread(target=process_data, args=(df3,"201-300.xlsx"))

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()