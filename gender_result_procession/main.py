# Main file

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

import pandas as pd, threading, logging, os, concurrent.futures, subprocess, time
import set_up

set_up.logger_main.debug("Main started running...")
set_up.logger_acu.debug("Main started running...")
start_time = time.time()
# basic datafrmae
df_output = pd.DataFrame(columns=["File","Row","Trial","Error", "原告", "原告性别", "被告", "被告性别", "被告是否胜诉", "判断的原因"])
df_32k_output = df_output
df_Toolong = pd.DataFrame()
df_SToolong = pd.DataFrame()

# Select the right model
if set_up.Main_model == 'glm3-6b-8k':
    import Processer_8  as main_processer
elif set_up.Main_model == 'Qwen-1_8B-Chat-Int8':
    import Q1_8_c_8  as main_processer
elif set_up.Main_model == 'Qwen-7B-Chat-Int4':
    import Q7_c_4  as main_processer
elif set_up.Main_model == 'Qwen-14B-Chat-Int4':
    import Q14_c_4 as main_processer
else:
    set_up.logger_main.error(f"Model name Error! Invalid name:{set_up.Main_model}")


def process_data(df, file_name, option):
    global df_output, df_32k_output, df_Toolong, df_SToolong
    set_up.logger_main.debug(f"{file_name} started processing...")
    set_up.logger_acu.debug(f"{file_name} started processing...")
    if option:
        if set_up.Add_model == 'glm3-6b-32k':
            import Processer_32  as add_processer
        # elif set_up.Main_model == 'Q1_8-C-8':
            # import Q1_8_c_8  as main_processer
        
        df_th_mid, df_TL_mid = add_processer.process_data(df,file_name)
        df_SToolong = pd.concat([df_SToolong, df_TL_mid], ignore_index=True)
        df_32k_output = pd.concat([df_32k_output, df_th_mid], ignore_index=True)
    else:
        df_th_mid, df_TL_mid = main_processer.process_data(df,file_name)
        df_Toolong = pd.concat([df_Toolong, df_TL_mid], ignore_index=True)
    df_output = pd.concat([df_output, df_th_mid], ignore_index=True)

file_list = os.listdir(set_up.DATA_path)


total_num = 0

# Thread pool runs 8k process with max thread limit.
with concurrent.futures.ThreadPoolExecutor(max_workers=set_up.max_threads) as executor:
    futures = []
    for file in file_list:
        try:
            file_name, extension = file.rsplit('.', 1)
        except:
            set_up.logger_files.info(f"File {file} : directory.")
            continue
        if extension == 'xlsx' or extension == 'xls':
            set_up.logger_files.info(f"File {file} : excel.")
            df = pd.read_excel(os.path.join(set_up.DATA_path, file), sheet_name='Sheet1', header=0)
            num = df.shape[0]
            total_num = total_num + num
        elif extension == 'csv':
            set_up.logger_files.info(f"File {file} : csv.")
            df = pd.read_csv(os.path.join(set_up.DATA_path, file), header=0)
            num = df.shape[0]
            total_num = total_num + num
        else:
            set_up.logger_files.info(f"File {file} : unsupported.")
            continue
        df_index = pd.DataFrame({'File': [file for i in range(num)], 'Row': [i for i in range(num)]})
        df = pd.concat([df_index, df], axis=1)
        future = executor.submit(process_data, df, file_name, False)
        futures.append(future)
    concurrent.futures.wait(futures)

set_up.logger_main.debug(f"All threads done.")
set_up.logger_acu.debug(f"All threads done.")


df_output.to_excel(os.path.join(set_up.OUT_path, 'output_8k.xlsx'), index=False)
df_output.to_csv(os.path.join(set_up.OUT_path, 'output_8k.csv'), index=False)

df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(set_up.OUT_path, 'output_8k_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(set_up.OUT_path, 'output_8k_sorted.csv'), index=False)

if not set_up.Add_model:
    set_up.logger_main.debug(f"No additional request.")
    set_up.logger_acu.debug(f"No additional request.")
    df_Toolong.to_csv(os.path.join(set_up.OUT_path, 'TL-records.csv'), index=False)
elif df_Toolong.empty:
    set_up.logger_main.debug(f"No docu too long.")
    set_up.logger_acu.debug(f"No docu too long.")
else:
    set_up.logger_main.debug(f"Some docu too long.")
    set_up.logger_acu.debug(f"Some docu too long.")
    del main_processer
    df_Toolong.to_csv(os.path.join(set_up.OUT_path, 'TL-records.csv'), index=False)
    set_up.logger_main.debug(f"Additional procession started...")
    set_up.logger_acu.debug(f"Additional procession started...")
    process_data(df_Toolong, "Additional_32k", True)
    set_up.logger_main.debug(f"Additional procession done.")
    set_up.logger_acu.debug(f"Additional procession done.")
    if df_SToolong.empty:
        set_up.logger_main.debug(f"No docu still too long.")
        set_up.logger_acu.debug(f"No docu still too long.")
    else:
        set_up.logger_main.debug(f"Some docu still too long.")
        set_up.logger_acu.debug(f"Some docu still too long.")
        df_SToolong.to_csv(os.path.join(set_up.OUT_path, 'STL-records.csv'), index=False)

df_output_sorted = df_output.sort_values(by=['File', 'Row'])
df_32k_output_sorted = df_32k_output.sort_values(by=['File', 'Row'])
df_output_sorted.to_excel(os.path.join(set_up.OUT_path, 'output_all_sorted.xlsx'), index=False)
df_output_sorted.to_csv(os.path.join(set_up.OUT_path, 'output_all_sorted.csv'), index=False)
df_32k_output_sorted.to_csv(os.path.join(set_up.OUT_path, 'output_32k_sorted.csv'), index=False)

duration = time.time() - start_time
formatted_duration = time.strftime("%H:%M:%S", time.gmtime(duration))
    
if df_output.shape[0] == total_num:
    ACU_path = os.path.join(set_up.PJ_path, f'acu_results/results_{set_up.JOB_id}-{set_up.DATA_path.rsplit("/", 1)[1]}-{str(set_up.Main_model)[:7]}-{str(set_up.Add_model)[:7]}-{set_up.max_threads}_P')
else:
    ACU_path = os.path.join(set_up.PJ_path, f'acu_results/results_{set_up.JOB_id}-{set_up.DATA_path.rsplit("/", 1)[1]}-{str(set_up.Main_model)[:7]}-{str(set_up.Add_model)[:7]}-{set_up.max_threads}_F')


set_up.logger_main.debug(f"Main finished running: {formatted_duration}.")
set_up.logger_acu.debug(f"Main finished running: {formatted_duration}.")



subprocess.run(["cp", "-r", set_up.OUT_path, ACU_path])
subprocess.run(["cp", "-r", set_up.DATA_path, ACU_path])
subprocess.run(["cp", "-r", set_up.LOG_path, ACU_path])
subprocess.run(["cp", os.path.join(set_up.PJ_path, 'Error.txt'), ACU_path])
subprocess.run(["cp", os.path.join(set_up.PJ_path, 'Out.txt'), ACU_path])
subprocess.run(["cp", os.path.join(set_up.PJ_path, 'gpu_status.log'), ACU_path])

set_up.logger_main.debug(f"Results backup done.")
set_up.logger_acu.debug(f"Results backup done.\n")


