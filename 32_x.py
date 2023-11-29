# This is a python file written by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# set up
import pandas as pd
import threading
import os
import re

# The package os and the following line of code get your working directory so don't worry about your working directory
PJ_path = os.path.dirname(os.path.abspath(__file__))
Model_path = os.path.join(PJ_path, 'chatglm3-6b-32k')
# import the model and initialize the dialog
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(Model_path, trust_remote_code=True).half().cuda()
model = model.eval()


# basic prompt
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])



def format_output(output):
    try:
        position = output.find("|")
        zs = output.find("张三")
        if position != -1:
            First_appearance = output[:position].count("\n")
        else:
            return "No table responded"

        lines = output.split("\n")
        true_appearance = First_appearance + 2
        if len(lines) < 3: 
            return "Not enough data provided"
        data = lines[true_appearance].split("|")
        if len(data) < 6: 
            return "Not enough data provided"
        if zs != -1:
            return "Zhangsan condition"
        plaintiff = data[1].strip()
        plaintiff_gender = data[2].strip()
        defendants = data[3].strip()
        defendant_gender = data[4].strip()
        verdict = data[5].strip() if len(data) > 6 else "Data not responded"
        reason = data[6].strip() if len(data) > 7 else "Data not responded"

        return plaintiff, plaintiff_gender, defendants, defendant_gender, verdict, reason
    except Exception as e:
        return str(e)



def process_data(df,file_name):
    global df_output
    num_rows = min(101, df.shape[0])
    for i in range(0, num_rows):#这里要注意从第几行开始算，如果第一行没有标题的就填-1，有标题填0，不然会落，这里python索引是从0开始算第一行，所以要-1
        data = "original data"
        cell_value = df.iloc[i, 14]
        print(cell_value)
        if type(cell_value) == float:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Empty cell", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])

        elif len(cell_value) < 40:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Cell length too short", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])

        elif len(cell_value) > 32000:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Prompt too long", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])

        else:
            prompt = str(cell_value) + bsc_prpt
            print("prompt set up done")
            for trial in range(5):
                try:
                    response, history = model.chat(tokenizer, prompt, history=[])
                    print(response)
                except Exception as Error:
                    row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Bad response", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
                    break # 结束trial 循环，反正寄了，再试还是寄
                print("line 77 done")
                data = format_output(response)
                print(data)
                if not isinstance(data, str) and len(data) == 6:  # 如果format没毛病
                    row = pd.DataFrame({'File':file_name, 'Row':int(i),'Trial':int(trial), '原因': None, '原告': data[0], '原告性别': data[1], '被告': data[2], '被告性别': data[3], '被告是否胜诉': data[4], '判断的原因':data[5]}, index=[0])
                    break # 结束 trial 循环

        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
            print(row)
        except:
            Error = "Row is undefined"
            Err_report = "FILE {} ROW {} Error: {}".format(file_name, i, Error)
            print(Err_report)
    df_output.to_excel(os.path.join(PJ_path, 'results/output.xlsx'), index=False)
    df_output.to_csv(os.path.join(PJ_path, 'results/output.csv'), index=False)
    df_output_sorted = df_output.sort_values(by=['File', 'Row'])
    df_output_sorted.to_excel(os.path.join(PJ_path, 'results/output_sorted.xlsx'), index=False)
    df_output_sorted.to_csv(os.path.join(PJ_path, 'results/output_sorted.csv'), index=False)


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
