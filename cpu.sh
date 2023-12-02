#!/bin/bash
#SBATCH -p com
#SBATCH -J cpu_cpws
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -o results/Out.txt
#SBATCH -e results/Error.txt
export PATH=/share/apps/cuda-12.1/bin:/share/apps/anaconda3/py385-2020.11/bin:$PATH 

./GPU_check.sh &
python main.py
source id.sh
touch results/acu_main.log
echo "Jobid: $last_job_id" >> acu_main.log
cat results/log/main.log >> acu_main.log  # 添加要追加的内容，并换行
echo "" >> acu_main.log 

cp -r results "acu_results/results_$last_job_id"

pkill -f GPU_check.sh
