# This is a python file written by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# set up
import pandas as pd
import threading
import logging
import os
import signal
# The package os and the following line of code get your working directory so don't worry about your working directory
PJ_path = os.path.dirname(os.path.abspath(__file__))
Model_path = os.path.join(PJ_path, 'chatglm3-6b')

# Log
public_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

open(os.path.join(PJ_path, 'results/{}.log'.format("main")), 'w').close()
logger_main = logging.getLogger('logger_main')
logger_main.setLevel(logging.DEBUG)
main_handler = logging.FileHandler(os.path.join(PJ_path, 'results/main.log'))
main_handler.setLevel(logging.DEBUG)
main_handler.setFormatter(public_formatter)
logger_main.addHandler(main_handler)

logger_main.debug("Script started running")

# import the model and initialize the dialog

from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(Model_path, trust_remote_code=True, device='cuda')
model = model.eval()

logger_main.debug('Model has been loaded.')

# basic prompt
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])
df_Toolong = pd.DataFrame(columns=["File","Row","cellvalue"])
sth_TL = False
Timeout = False


def respond_in_time(tokenizer, model, prompt, timeout=30):
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


def process_data(df,file_name):
    global df_output 
    global sth_TL
    global df_Toolong
    open(os.path.join(PJ_path, 'results/{}.log'.format(file_name)), 'w').close()
    logger_b = logging.getLogger('logger_{}'.format(file_name))
    logger_b.setLevel(logging.DEBUG)
    handler_b = logging.FileHandler(os.path.join(PJ_path, 'results/{}.log'.format(file_name)))
    handler_b.setLevel(logging.DEBUG)
    handler_b.setFormatter(public_formatter)
    logger_b.addHandler(handler_b)

    logger_b.debug(f"{file_name} started processing...\n")

    num_rows = min(101, df.shape[0])
    for i in range(num_rows):#这里要注意从第几行开始算，如果第一行没有标题的就填-1，有标题填0，不然会落，这里python索引是从0开始算第一行，所以要-1
        row = None
        logger_b.debug(f"Row {str(int(i))} - started processing...\n")
        data = "Not processed"
        cell_value = df.iloc[i, 14]
        logger_b.debug(f"Cell value: {cell_value} \n")
        if type(cell_value) == float:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':None, 'Error': "Empty cell", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])

        elif len(cell_value) < 40:
            row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':None, 'Error': "Cell length too short", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])

        elif len(cell_value) > 7500:
            TL_row = pd.DataFrame({'File':file_name, 'Row':int(i), 'cellvalue':cell_value}, index=[0])
            df_Toolong = pd.concat([df_Toolong, TL_row], ignore_index=True)
            sth_TL = True


        else:
            prompt = str(cell_value) + bsc_prpt
            logger_b.debug(f"Prompt setted.\n")
            for trial in range(5):
                logger_b.debug(f"Trial {trial} - started running...\n")
                try:
                    response, history = model.chat(tokenizer, prompt, history=[])
                    logger_b.debug(f"Response {trial}: {response} \n")
                except Exception as Error:
                    row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': "Failed response", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
                    logger_b.debug(f"Response failed. \n")
                    break # 结束trial 循环，反正寄了，再试还是寄
                data = format_output(response)
                logger_b.debug(f"Data: {str(data)}\n")

                if not isinstance(data, str) and len(data) == 6:  # 如果format没毛病
                    row = pd.DataFrame({'File':file_name, 'Row':int(i),'Trial':int(trial), 'Error': None, '原告': data[0], '原告性别': data[1], '被告': data[2], '被告性别': data[3], '被告是否胜诉': data[4], '判断的原因':data[5]}, index=[0])
                    break # 结束 trial 循环
                else:
                    row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': data, '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])


        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
        except:
            Error = "Variable `row` is undefined"
            logger_b.debug(f"Row {i} Error at appending: {Error}")
    logger_b.debug(f"{file_name} finished running.")


def process_data_32k(df):
    global df_output
    global df_32k_output
    file_name = "32k"
    open(os.path.join(PJ_path, 'results/{}.log'.format(file_name)), 'w').close()
    logger_b = logging.getLogger('logger_{}'.format(file_name))
    logger_b.setLevel(logging.DEBUG)
    handler_b = logging.FileHandler(os.path.join(PJ_path, 'results/{}.log'.format(file_name)))
    handler_b.setLevel(logging.DEBUG)
    handler_b.setFormatter(public_formatter)
    logger_b.addHandler(handler_b)
    logger_b.debug(f"32k started...\n")
    Model_path = os.path.join(PJ_path, 'chatglm3-6b-32k')
    from transformers import AutoTokenizer, AutoModel
    tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(Model_path, trust_remote_code=True).half().cuda()
    model = model.eval()
    logger_b.debug(f"32k model loaded.\n")
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
                    row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1],'Trial':int(trial), 'Error':None , '原告': data[0], '原告性别': data[1], '被告': data[2], '被告性别': data[3], '被告是否胜诉': data[4], '判断的原因':data[5]}, index=[0])
                    break # 结束 trial 循环
                else:
                    row = pd.DataFrame({'File':file_name, 'Row':int(i), 'Trial':int(trial), 'Error': data, '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
            df_32k_output = pd.concat([df_32k_output, row], ignore_index=True)
        except:
            Error = "Row is undefined"
            logger_b.debug(f"Error at appending: {Error}")
    logger_b.debug(f"{file_name} finished running.")

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
logger_main.debug(f"All threads done.")

df_output.to_excel(os.path.join(PJ_path, 'results/output_8k.xlsx'), index=False)
df_output.to_csv(os.path.join(PJ_path, 'results/output_8k.csv'), index=False)
df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(PJ_path, 'results/output_8k_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(PJ_path, 'results/output_8k_sorted.csv'), index=False)
df_Toolong.to_csv(os.path.join(PJ_path, 'results/TL-records.csv'), index=False)

logger_main.debug(f"Something too long: {str(sth_TL)}")

if sth_TL:
    df_32k_output = pd.DataFrame(columns=["File","Row", "Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])
    tokenizer = None
    model = None
    logger_main.debug(f"32k_procession started...")
    process_data_32k(df_Toolong)
    logger_main.debug(f"32k_procession done.")

df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_32k_output_sorted = df_32k_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(PJ_path, 'results/output_all_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(PJ_path, 'results/output_all_sorted.csv'), index=False)
df_32k_output_sorted.to_csv(os.path.join(PJ_path, 'results/output_32k_sorted.csv'), index=False)

logger_main.debug(f"Script finished running.")
