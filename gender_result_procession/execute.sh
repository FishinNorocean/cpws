#!/bin/bash
echo "Initializing..."
cd "$HOME/swk_cpws_1.0/gender_result_procession"

touch acu_main.log
mkdir -p acu_results
echo "Done."

job_id=$(sbatch run.sh | awk '{print $4}')
echo "export last_job_id=\"$job_id\"" > id.sh
echo "Monitoring cession starting..."
sleep 4
 ./monitor.sh

