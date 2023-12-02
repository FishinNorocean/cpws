# Set up file

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# Key options  VERY IMPORTANT 
data_dir = 'data' 
log_dir = 'log'
results_dir = 'results'
max_threads = 4

# e.g. 'data'. Put all your unprocessed data files in a directory and input the directory 

bsc_prpt="请你从这段文本中找到原告, 原告性别（若是企业则回答企业）, 被告, 被告性别（若是企业则回答企业）, 并判断被告是否胜诉（并说明原因），回答格式为markdown表格代码，原告：，原告性别：，被告：，被告性别：，被告是否胜诉：，这么判断胜诉与否的原因： "# basic prompt

time_8k = 0 #Time limit for each trial in 8k model. 0 for no limit.
time_32k = 30 #Time limit for each trial in 32k model. 0 for no limit

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
    last_log, last_out, last_data = loaded_data 
    if os.path.isfile("id.sh"):
        subprocess.run("./id.sh", shell=True)
        last_job_id = os.environ.get("last_job_id")
    if last_job_id:
        trash_dir = os.path.join(os.environ['HOME'], '.Trash/results_' + last_job_id)
        os.rename(last_log, trash_dir)
        os.rename(last_out, trash_dir)
    else:
        print("No last run.")
except:
    print("No last run.")
data_to_store = (LOG_path, OUT_path, DATA_path)
with open('last_run_info.pkl', 'wb') as file:
    pickle.dump(data_to_store, file)

os.makedirs("acu_results", exist_ok=True)
os.makedirs(LOG_path, exist_ok=True)
os.makedirs(OUT_path, exist_ok=True)


result = subprocess.run("squeue | grep ' R ' | awk '{print $1}'", shell=True, capture_output=True, text=True)
if result.returncode == 0:
    JOB_id = result.stdout
else:
    JOB_id = None

# Log
public_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

open(os.path.join(LOG_path, 'main.log'), 'w').close()
logger_main = logging.getLogger('logger_main')
logger_main.setLevel(logging.DEBUG)
main_handler = logging.FileHandler(os.path.join(LOG_path, 'main.log'))
main_handler.setLevel(logging.DEBUG)
main_handler.setFormatter(public_formatter)
logger_main.addHandler(main_handler)

open(os.path.join(LOG_path, 'files.log'), 'w').close()
logger_files = logging.getLogger('logger_files')
logger_files.setLevel(logging.DEBUG)
handler_files = logging.FileHandler(os.path.join(LOG_path, 'files.log'))
handler_files.setLevel(logging.DEBUG)
handler_files.setFormatter(public_formatter)
logger_files.addHandler(handler_filesr)

logger_main.debug("Set up done.")


