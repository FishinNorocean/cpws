import pandas as pd, logging, time, os
from func_timeout import func_timeout

# import the model and initialize the dialog
Model_path = '/share/home/zju0018053/cpws/Models/Qwen-14B-Chat'
from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained(Model_path, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    Model_path,
    device_map="auto",
    trust_remote_code=True
).eval()
response, history = model.chat(tokenizer, "你好，给我讲个笑话", history=[])
print(response)