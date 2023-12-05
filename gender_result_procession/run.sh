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
file_path="mission_args.txt"

if [ ! -f "$file_path" ]; then
    echo "Arg file not exist."
    exit 1
fi

while IFS= read -r line || [ -n "$line" ]; do
    if [ -z "$line" ]; then
        break
    fi
    if [[ $line == \#* ]]; then
        continue
    fi
    # 处理非空非注释行
    echo "$line" > parameters.txt
    python main.py
done < "$file_path"



