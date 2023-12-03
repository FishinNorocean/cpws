#!/bin/bash
#SBATCH -p gpu
#SBATCH -J nv_cpws
#SBATCH -N 1
#SBATCH -n 12
#SBATCH --gres=gpu:1
#SBATCH -o Out.txt
#SBATCH -e Error.txt
export PATH=/share/apps/cuda-12.1/bin:/share/apps/anaconda3/py385-2020.11/bin:$PATH 

./GPU_check.sh &
python main.py
pkill -f GPU_check.sh
