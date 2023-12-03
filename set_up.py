# Set up file

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# Key options  VERY IMPORTANT 
data_dir = '../trial_data' 
log_dir = 'log'
results_dir = 'results'
max_threads = 4

# e.g. 'data'. Put all your unprocessed data files in a directory and input the directory 

bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "# basic prompt

time_8k = 30 #Time limit for each trial in 8k model. 
time_32k = 30 #Time limit for each trial in 32k model. 

# set up
import logging, os, subprocess, pickle

# The package os and the following line of code get your working directory so don't worry about your working directory
PJ_path = os.path.dirname(os.path.abspath(__file__))
LOG_path = os.path.join(PJ_path, log_dir)
OUT_path = os.path.join(PJ_path, results_dir)
DATA_path = os.path.join(PJ_path, data_dir)
os.makedirs(LOG_path, exist_ok=True)
os.makedirs(OUT_path, exist_ok=True)

try:
    with open('last_run_info.pkl', 'rb') as file:
        loaded_data = pickle.load(file)
    last_log, last_out, last_data,last_job_id = loaded_data 
    if last_job_id:
        trash_dir = os.path.join(os.environ['HOME'], f'.Trash/results_{last_job_id}')
        subprocess.run(["mv", last_out, trash_dir])
        subprocess.run(["mv", last_log, trash_dir])
    else:
        print("No last run.")
except:
    print("No last run.")

os.makedirs("acu_results", exist_ok=True)
os.makedirs(LOG_path, exist_ok=True)
os.makedirs(OUT_path, exist_ok=True)


result = subprocess.run("squeue | grep ' R ' | awk '{print $1}'", shell=True, capture_output=True, text=True)
if result.returncode == 0:
    JOB_id = result.stdout
    JOB_id = JOB_id[0:4]
else:
    JOB_id = None

data_to_store = (LOG_path, OUT_path, DATA_path, JOB_id)
with open('last_run_info.pkl', 'wb') as file:
    pickle.dump(data_to_store, file)

# Log
public_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

open(os.path.join(LOG_path, 'main.log'), 'w').close()
logger_main = logging.getLogger('logger_main')
logger_main.setLevel(logging.DEBUG)
main_handler = logging.FileHandler(os.path.join(LOG_path, 'main.log'), encoding = 'utf-8')
main_handler.setLevel(logging.DEBUG)
main_handler.setFormatter(public_formatter)
logger_main.addHandler(main_handler)

open(os.path.join(LOG_path, 'files.log'), 'w').close()
logger_files = logging.getLogger('logger_files')
logger_files.setLevel(logging.DEBUG)
handler_files = logging.FileHandler(os.path.join(LOG_path, 'files.log'), encoding = 'utf-8')
handler_files.setLevel(logging.DEBUG)
handler_files.setFormatter(public_formatter)
logger_files.addHandler(handler_files)

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

logger_main.debug("Set up done.")


