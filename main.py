# Main file

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# Key options  VERY IMPORTANT 
data_dir = 'data' 
# e.g. 'data'. Put all your unprocessed data files in a directory and input the directory name here.

# set up
import pandas as pd, threading, logging, os

# The package os and the following line of code get your working directory so don't worry about your working directory
PJ_path = os.path.dirname(os.path.abspath(__file__))
LOG_path = os.path.join(PJ_path, 'results/log')
OUT_path = os.path.join(PJ_path, 'results')
DATA_path = os.path.join(PJ_path, data_dir)
os.makedirs(LOG_path)
os.makedirs(LOG_path)

# Log
public_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

logger_main = logging.getLogger('logger_main')
logger_main.setLevel(logging.DEBUG)
main_handler = logging.FileHandler(os.path.join(LOG_path, 'main.log'))
main_handler.setLevel(logging.DEBUG)
main_handler.setFormatter(public_formatter)
logger_main.addHandler(main_handler)

logger_main.debug("Script started running")

# basic prompt
bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "

# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])
df_32k_output = df_output
df_Toolong = pd.DataFrame()
df_SToolong = pd.DataFrame()

time_8k = 0 #Time limit for each trial in 8k model. 0 for no limit.
time_32k = 30 #Time limit for each trial in 32k model. 0 for no limit

import Processer_8, Processer_32

def process_data(df, file_name, option):
    global df_output, df_Toolong, df_SToolong
    logger_main.debug(f"{file_name} started processing...\n")
    if option:
        df_th_mid, df_TL_mid = Processer_32.process_data(df,file_name)
        df_SToolong = pd.concat([df_SToolong, df_TL_mid], ignore_index=True)
        df_32k_output = pd.concat([df_32k_output, df_th_mid], ignore_index=True)
    else:
        df_th_mid, df_TL_mid = Processer_8.process_data(df,file_name)
        df_Toolong = pd.concat([df_Toolong, df_TL_mid], ignore_index=True)
    df_output = pd.concat([df_output, df_th_mid], ignore_index=True)

file_list = os.listdir(DATA_path)

# launch the 8k procession first:
threads = []
for file in file_list:
    file_name, extension = file.rsplit(".", 1)
    if extension == 'xlsx' or extension == 'xls':
        df = pd.read_excel(os.path.join(DATA_path, file), sheet_name='Sheet1', header=0)
    elif extension == 'csv':
        df = pd.read_csv(os.path.join(DATA_path, file), header=0)
    else:
        logger_main.error(f"File {file} : unsupported.")
    len = df.shape[0]
    df_index = pd.DataFrame({'File': [file for i in range(len)], 'Row': [i for i in range(len)]})
    df = pd.concat([df_index, df], axis=1)
    thread = threading.Thread(target=process_data, args=(df, file_name, False))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
logger_main.debug(f"All threads done.")

df_output.to_excel(os.path.join(OUT_path, 'output_8k.xlsx'), index=False)
df_output.to_csv(os.path.join(OUT_path, 'output_8k.csv'), index=False)

df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(OUT_path, 'output_8k_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(OUT_path, 'output_8k_sorted.csv'), index=False)

if df_Toolong:
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

if df_SToolong:
    logger_main.debug(f"No docu still too long.")
else:
    logger_main.debug(f"Some docu still too long.")
    df_Toolong.to_csv(os.path.join(OUT_path, 'STL-records.csv'), index=False)

logger_main.debug(f"Script finished running.")
