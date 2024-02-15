#!/bin/bash
#SBATCH -p gpu
#SBATCH -J nv_cpws
#SBATCH -N 1
#SBATCH -n 18
#SBATCH --gres=gpu:1
#SBATCH -o Out.txt
#SBATCH -e Error.txt
export PATH=/share/apps/cuda-12.1/bin:/share/apps/anaconda3/py385-2020.11/bin:$PATH 

./GPU_check.sh &
echo "1,glm3-6b-8k" > parameters.txt
python main.py
echo "2,glm3-6b-8k" > parameters.txt
python main.py
echo "3,glm3-6b-8k" > parameters.txt
python main.py
echo "1,Qwen-1_8B-chat-int8" > parameters.txt
python main.py
echo "2,Qwen-1_8B-chat-int8" > parameters.txt
python main.py
echo "3,Qwen-1_8B-chat-int8" > parameters.txt
python main.py
echo "1,Qwen-7B-chat-int4" > parameters.txt
python main.py
echo "2,Qwen-7B-chat-int4" > parameters.txt
python main.py
echo "1,Qwen-14B-chat-int4" > parameters.txt
python main.py
echo "2,Qwen-14B-chat-int4" > parameters.txt
python main.py
