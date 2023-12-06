#!/bin/bash
echo "Initializing..."
git update-index --assume-unchanged acu_main.log Error.txt gpu_status.log id.sh mission_args.txt Out.txt parameters.txt log/.gitkeep results/.gitkeep ../Models/.gitkeep ../Pre_data/.gitkeep
echo "Done."

job_id=$(sbatch run.sh | awk '{print $4}')
echo "export last_job_id=\"$job_id\"" > id.sh
echo "Monitoring cession starting..."
sleep 4
 ./monitor.sh

