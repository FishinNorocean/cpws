# Main file

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

import pandas as pd, threading, logging, os, concurrent.futures
from set_up import bsc_prpt, time_8k, time_32k, PJ_path, LOG_path, OUT_path, DATA_path, logger_main, JOB_id, max_threads

logger_main.debug("Main started running...")

# basic prompt
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])
df_32k_output = df_output
df_Toolong = pd.DataFrame()
df_SToolong = pd.DataFrame()

time_8k = 30 #Time limit for each trial in 8k model. 
time_32k = 30 #Time limit for each trial in 32k model. 

import Processer_8

def process_data(df, file_name, option):
    global df_output, df_32k_output, df_Toolong, df_SToolong
    logger_main.debug(f"{file_name} started processing...")
    if option:
        import Processer_32
        df_th_mid, df_TL_mid = Processer_32.process_data(df,file_name)
        df_SToolong = pd.concat([df_SToolong, df_TL_mid], ignore_index=True)
        df_32k_output = pd.concat([df_32k_output, df_th_mid], ignore_index=True)
    else:
        df_th_mid, df_TL_mid = Processer_8.process_data(df,file_name)
        df_Toolong = pd.concat([df_Toolong, df_TL_mid], ignore_index=True)
    df_output = pd.concat([df_output, df_th_mid], ignore_index=True)

file_list = os.listdir(DATA_path)


total_num = 0

# Thread pool runs 8k process with max thread limit.
with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = []
    for file in file_list:
        file_name, extension = file.rsplit('.', 1)
        if extension == 'xlsx' or extension == 'xls':
            df = pd.read_excel(os.path.join(DATA_path, file), sheet_name='Sheet1', header=0)
            num = df.shape[0]
            total_num = total_num + num
        elif extension == 'csv':
            df = pd.read_csv(os.path.join(DATA_path, file), header=0)
            num = df.shape[0]
            total_num = total_num + num
        else:
            logger_main.error(f"File {file} : unsupported.")
        df_index = pd.DataFrame({'File': [file for i in range(num)], 'Row': [i for i in range(num)]})
        df = pd.concat([df_index, df], axis=1)
        future = executor.submit(process_data, df, file_name, False)
        futures.append(future)
    for future in concurrent.futures.as_completed(futures):
        pass
logger_main.debug(f"All threads done.")

df_output.to_excel(os.path.join(OUT_path, 'output_8k.xlsx'), index=False)
df_output.to_csv(os.path.join(OUT_path, 'output_8k.csv'), index=False)

df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(OUT_path, 'output_8k_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(OUT_path, 'output_8k_sorted.csv'), index=False)

if df_Toolong.empty:
    logger_main.debug(f"No docu too long.")
else:
    logger_main.debug(f"Some docu too long.")
    df_Toolong.to_csv(os.path.join(OUT_path, 'TL-records.csv'), index=False)
    logger_main.debug(f"Additional procession started...")
    process_data(df_Toolong, "Additional_32k", True)
    logger_main.debug(f"Additional procession done.")

df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_32k_output_sorted = df_32k_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(OUT_path, 'output_all_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(OUT_path, 'output_all_sorted.csv'), index=False)
df_32k_output_sorted.to_csv(os.path.join(OUT_path, 'output_32k_sorted.csv'), index=False)

if df_SToolong.empty:
    logger_main.debug(f"No docu still too long.")
else:
    logger_main.debug(f"Some docu still too long.")
    df_Toolong.to_csv(os.path.join(OUT_path, 'STL-records.csv'), index=False)

if df_output.shape[0] == total_num:
    ACU_path = os.path.join(PJ_path, f'acu_results/Job_{JOB_id}_P')
else:
    ACU_path = os.path.join(PJ_path, f'acu_results/Job_{JOB_id}_F')


logger_main.debug(f"Main finished running.")

with open("acu_main.log", "a") as acu_log_file:
    acu_log_file.write(f"Jobid: {JOB_id}\n")
    with open(os.path.join(LOG_path, 'main.log'), "r") as main_log:
        log_file.write(main_log.read() + "\n")

subprocess.run(["cp", "-r", "OUT_path", os.path.join(ACU_path, 'out')])
subprocess.run(["cp", "-r", "DATA_path", os.path.join(ACU_path, 'data')])
subprocess.run(["cp", "-r", "LOG_path", os.path.join(ACU_path, 'log')])

logger_main.debug(f"Results backup done.")

