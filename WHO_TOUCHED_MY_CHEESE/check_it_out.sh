#!/bin/bash
#SBATCH -p gpu
#SBATCH -J top
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -o Out.txt
#SBATCH -e Error.txt
#SBATCH --gres=gpu:0
ps aux | grep -v "root"



