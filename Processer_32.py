# ChatGLM3-6b-32k Model Processer

# This project is built up by Sang Wenkai(zju), in order to get data from Judgement Document with AI. (Also great gratitude to Zhe Yuan and Dengkun Chen for their warm and helpful guidance.)

# set up
import pandas as pd
import logging
import signal
from main import PJ_path, LOG_path, public_formatter, bsc_prpt, logger_main, df_output, time_32k as time_lim

# import the model and initialize the dialog
Model_path = os.path.join(PJ_path, 'chatglm3-6b-32k')
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
model = AutoModel.from_pretrained(Model_path, trust_remote_code=True).half().cuda()
model = model.eval()

logger_main.debug('Model_32 has been loaded.')

def respond_in_time(tokenizer, model, prompt, time_lim):
    def handler(signum, frame):
        raise TimeoutError("")

    # 设置超时处理程序
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(time_lim)  # 设置超时时间
    try:
        # 这里放置你的代码
        response, history = model.chat(tokenizer, prompt, history=[])
        signal.alarm(0)  # 取消超时
        return response, history
    except TimeoutError as e:
        return None, None


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
    df_Toolong = pd.DataFrame()
    open(os.path.join(LOG_path, '{}.log'.format(file_name)), 'w').close()
    logger_b = logging.getLogger('logger_{}'.format(file_name))
    logger_b.setLevel(logging.DEBUG)
    handler_b = logging.FileHandler(os.path.join(LOG_path, '{}.log'.format(file_name)))
    handler_b.setLevel(logging.DEBUG)
    handler_b.setFormatter(public_formatter)
    logger_b.addHandler(handler_b)
    logger_b.debug(f"{file_name} started processing...\n")
    num_rows = min(1000, df.shape[0])
    logger_b.debug(f"TL records num: {num_rows}\n")
    for i in range(num_rows):
        row = None
        logger_b.debug(f"Row {str(int(i))} - started processing...\n")
        data = "Not processed"
        cell_value = df.iloc[i, 16]
        logger_b.debug(f"Length: {len(cell_value)}; Text: {cell_value}\n")
        if len(cell_value) > 31500:
            row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1], 'Trial':None, 'Error': "Prompt still too long", '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])
            TL_row = df.iloc[i,:].to_frame().T
            df_Toolong = pd.concat([df_Toolong, TL_row], ignore_index=True)

        else:
            prompt = str(cell_value) + bsc_prpt
            logger_b.debug(f"Prompt setted.\n")
            for trial in range(5):
                logger_b.debug(f"Trial {trial} - started running...\n")
                response, history = respond_in_time(tokenizer, model, prompt, time_lim)
                logger_b.debug(f"Response {trial}: {response} \n")
                if response:
                    data = format_output(response)
                else:
                    data = "Timed out."
                logger_b.debug(f"Data: {str(data)}\n")

                if not isinstance(data, str) and len(data) == 6:  # 如果format没毛病
                    row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1],'Trial':int(trial), 'Error':None, '原告': data[0], '原告性别': data[1], '被告': data[2], '被告性别': data[3], '被告是否胜诉': data[4], '判断的原因':data[5]}, index=[0])
                    break # 结束 trial 循环
                else:
                    row = pd.DataFrame({'File':df.iloc[i,0], 'Row':df.iloc[i,1], 'Trial':int(trial), 'Error': data, '原告': None, '原告性别': None, '被告': None, '被告性别': None, '被告是否胜诉': None, '判断的原因':None}, index=[0])

        try:
            df_output = pd.concat([df_output, row], ignore_index=True)
        except:
            Error = "Variable `row` is undefined"
            logger_b.debug(f"Row {i} Error at appending: {Error}")
    return df_output, df_Toolong
    logger_b.debug(f"{file_name} finished running.")