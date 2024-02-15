import pandas as pd, logging, time, os
from func_timeout import func_timeout
from qw_vllm_wrapper import vLLMWrapper

# import the model and initialize the dialog
Model_path = '/share/home/zju0018053/cpws/Models/Qwen-14B-Chat'
from transformers import AutoModelForCausalLM, AutoTokenizer
# tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)
model = vLLMWrapper(Model_path, dtype = "float16", tensor_parallel_size=1)

# model = AutoModelForCausalLM.from_pretrained(
#     Model_path,
#     device_map="auto",
#     trust_remote_code=True
# ).eval()
#response, history = model.chat(tokenizer, "你好，给我讲个笑话", history=[])
#print(response)

response, history = model.chat(query="你好", history=None)
print(response)
response, history = model.chat(query="给我讲一个年轻人奋斗创业最终取得成功的故事。", history=history)
print(response)