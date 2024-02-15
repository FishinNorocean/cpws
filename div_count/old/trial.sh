#!/bin/bash
#SBATCH -p gpu
#SBATCH -J trial
#SBATCH -N 1
#SBATCH -n 12
#SBATCH -o Out.txt
#SBATCH -e Error.txt
export PATH=/share/apps/cuda-12.1/bin:/share/apps/anaconda3/py385-2020.11/bin:$PATH 

./GPU_check.sh &
python trial.py
pkill -f GPU_check.sh
