#!/bin/bash
echo "Initializing..."
echo "Emptying last result."
if [ -f "id.sh" ]; then
    source id.sh
    mkdir -p "$HOME/.Trash/results_$last_job_id"
    mv results/ "$HOME/.Trash/results_$last_job_id"
else
    echo "No last run."
    rm -rf results
fi

mkdir results
mkdir -p acu_results
echo "Done."

job_id=$(sbatch run.sh | awk '{print $4}')
echo "export last_job_id=\"$job_id\"" > id.sh
echo "Monitoring cession starting..."
sleep 4
./monitor.sh

