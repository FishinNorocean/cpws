#!/bin/bash
echo "Initializing..."
cd "$HOME/swk_cpws_1.0/"
echo "Emptying last result."
if [ -f "id.sh" ]; then
    source id.sh
    mv results/ "$HOME/.Trash/results_$last_job_id"
elif [ -d "results" ]; then
    mv results/ "$Home/.Trash/results"
else
    echo "No last run."
fi
mkdir results
mkdir -p acu_results
echo "Done."

job_id=$(sbatch run.sh | awk '{print $4}')
echo "export last_job_id=\"$job_id\"" > id.sh
echo "Monitoring cession starting..."
sleep 4
./monitor.sh

