# This is a python file written by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# set up
import pandas as pd
import threading
import logging
import os
import re
import datetime
import signal
import time


public_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


# The package os and the following line of code get your working directory so don't worry about your working directory
PJ_path = os.path.dirname(os.path.abspath(__file__))
Model_path = os.path.join(PJ_path, 'chatglm3-6b-32k')
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(Model_path, trust_remote_code=True).half().cuda()
model = model.eval()


# import the model and initialize the dialog


# basic prompt
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])

Timeout = False
def respond_in_time(tokenizer, model, prompt, timeout=1):
    global Timeout
    Timeout = False
    def handler(signum, frame):
        raise TimeoutError("")

    # 设置超时处理程序
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)  # 设置超时时间为30秒

    try:
        # 这里放置你的代码
        response, history = model.chat(tokenizer, prompt, history=[], temperature=1)
        signal.alarm(0)  # 取消超时
        return response, history
    except TimeoutError as e:
        Timeout = True
        return None, str(e)




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

def process_data_32k(df):
    global df_output
    file_name = "32k"
    open(os.path.join(PJ_path, 'results/{}.log'.format(file_name)), 'w').close()
    logger_b = logging.getLogger('logger_{}'.format(file_name))
    logger_b.setLevel(logging.DEBUG)
    handler_b = logging.FileHandler(os.path.join(PJ_path, 'results/{}.log'.format(file_name)))
    handler_b.setLevel(logging.DEBUG)
    handler_b.setFormatter(public_formatter)
    logger_b.addHandler(handler_b)
    logger_b.debug(f"32k started...\n")
    num_rows = min(1000, df.shape[0])
    logger_b.debug(f"TL records num: {num_rows}\n")
    for i in range(num_rows):
        cell_value = df.iloc[i,2]
        logger_b.debug(f"Length: {len(cell_value)}; Text: {cell_value}\n")
        if len(cell_value) > 31500:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':None, 'Error': "Prompt still too long", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
        else:
            prompt = str(cell_value) + bsc_prpt
            logger_b.debug(f"32k prompt setted.\n")
            for trial in range(5):
                try:
                    logger_b.debug(f"Trial {trial} - started running...\n")
                    response, history = respond_in_time(tokenizer, model, prompt)
                    logger_b.debug(f"Response {trial}: {response} \n")
                except:
                    if not Timeout:
                        row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Failed response", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
                    logger_b.debug(f"Response failed. \n")
                    break # 结束trial 循环，反正寄了，再试还是寄
                if Timeout:
                    data = "Timed out."
                else:
                    data = format_output(response)
                logger_b.debug(f"Data: {str(data)}\n")

                if not isinstance(data, str) and len(data) == 6:  # 如果format没毛病
                    row = pd.DataFrame({'File':file_name, 'Row':int(i),'Trial':int(trial), '原因': None, '原告': data[0], '原告性别': data[1], '被告': data[2], '被告性别': data[3], '被告是否胜诉': data[4], '判断的原因':data[5]}, index=[0])
                    break # 结束 trial 循环
                else:
                    row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': data, '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
        except:
            Error = "Row is undefined"
            logger_b.debug(f"Error at appending: {Error}")
    df_output_sorted = df_output.sort_values(by=['File', 'Row'])
    df_output_sorted.to_csv(os.path.join(PJ_path, '32k.csv'), index=False)
    logger_b.debug(f"{file_name} finished running.")



df1 = pd.read_csv(os.path.join(PJ_path, 'results/TL-docus.csv'))

process_data_32k(df1)