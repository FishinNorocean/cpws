# Qwen-14B-chat Model Processer

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# set up
import pandas as pd, logging, time, os, set_up
from func_timeout import func_timeout


# import the model and initialize the dialog
Model_path = os.path.join(set_up.PJ_path, '../Models/Qwen-14B-Chat')
from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    Model_path,
    device_map="auto",
    trust_remote_code=True,
    fp16=True
).eval()
set_up.logger_main.debug('Model_Q14-chat has been loaded.')
set_up.logger_acu.debug('Model_Q14-chat has been loaded.')



def process_data(df,file_name):
    df_output = pd.DataFrame()
    df_Toolong = pd.DataFrame()
    open(os.path.join(set_up.LOG_path, '{}.log'.format(file_name)), 'w').close()
    logger_b = logging.getLogger('logger_{}'.format(file_name))
    logger_b.setLevel(logging.DEBUG)
    handler_b = logging.FileHandler(os.path.join(set_up.LOG_path, '{}.log'.format(file_name)), encoding = 'utf-8')
    handler_b.setLevel(logging.DEBUG)
    handler_b.setFormatter(set_up.public_formatter)
    logger_b.addHandler(handler_b)
    logger_b.debug(f"{file_name} started processing...\n")
    num_rows = min(3000, df.shape[0])
    logger_b.debug(f"Records num: {num_rows}\n")
    for i in range(num_rows):
        row = None
        logger_b.debug(f"Row {str(int(i))} - started processing...\n")
        data = "Not processed"
        cell_value = df.iloc[i, 16]
        logger_b.debug(f"Text: {cell_value}\n")
        if type(cell_value) == float:
            row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1], 'Trial':None, 'Error': "Empty cell"}, index=[0])

        elif len(cell_value) < 40:
            row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1], 'Trial':None, 'Error': "Cell length too short"}, index=[0])

        elif len(cell_value) > 7500:
            TL_row = df.iloc[i,:].to_frame().T
            df_Toolong = pd.concat([df_Toolong, TL_row], ignore_index=True)

        else:
            prompt = set_up.bsc_prpt.format(df.iloc[i, 4], df.iloc[i, 16])
            logger_b.debug(f"Prompt setted.\n")
            for trial in range(5):
                logger_b.debug(f"Trial {trial} - started running...\n")
                try:
                    st_time = time.time()
                    history=[]
                    response, history = func_timeout(set_up.time_8k, model.chat, args=(tokenizer, prompt, history))
                except:
                    response = None
                    data = "Timed out."
                duration = time.time() - st_time
                logger_b.debug(f"Response {trial} in {duration:.3f} seconds: {response} \n")
                if response:
                    data = set_up.format_output(response)

                logger_b.debug(f"Data: {str(data)}\n")

                if not isinstance(data, str) and len(data) == 6:  # 如果format没毛病
                    row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1],'Trial':int(trial), 'Error':None, '离婚': data[0], '未成年不公开': data[1], '判断的原因':data[2]}, index=[0])
                    break # 结束 trial 循环
                else:
                    row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1], 'Trial':int(trial), 'Error': data}, index=[0])

        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
        except:
            Error = "Variable `row` is undefined"
            logger_b.debug(f"Row {i} Error at appending: {Error}")
    logger_b.debug(f"{file_name} finished running.")
    set_up.logger_main.debug(f"{file_name} finished running.")
    set_up.logger_acu.debug(f"{file_name} finished running.")
    return df_output, df_Toolong