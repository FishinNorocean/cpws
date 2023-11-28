#!/bin/bash
#SBATCH -p gpu
#SBATCH -J nv_glm
#SBATCH -N 1
#SBATCH -n 16
#SBATCH --gres=gpu:1
#SBATCH -o results/Out.txt
#SBATCH -e results/Error.txt
export PATH=/share/apps/cuda-12.1/bin:/share/apps/anaconda3/py385-2020.11/bin:$PATH 

echo "Initializing"
directory="./results"  
if [ ! -d "$directory" ]; then
    echo "./results directory isn't here. Setting it up..."
    mkdir -p "$directory" 
    echo "Done"
else
    echo "./results directory already exists"
fi
python x.py