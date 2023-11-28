#!/bin/bash
#SBATCH -p gpu
#SBATCH -J nv_glm
#SBATCH -N 1
#SBATCH -n 16
#SBATCH --gres=gpu:1
#SBATCH -o results/Out.txt
#SBATCH -e results/Error.txt
export PATH=/share/apps/cuda-12.1/bin:/share/apps/anaconda3/py385-2020.11/bin:$PATH 
python x.py