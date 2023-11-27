## Instrucitons for This Project

We used local chatglm3-6b model to process the Judgement Documents.

## To run:

Just launch your terminal and chage the directory towards this folder.

Then type `sbatch run.sh` to run the project

Enjoy the results at `./results/`.


## Notions:

- The model we applied is stored in `./chatglm3-6b`

- `x.py` stores the source code.

- `run.sh` is the bash script of sbatch which sent the task to the right node.

- `./data/` diretory stores the source data.

- In `./results/` directory, `Error` file stores the exceptions if there were any during the process and `Out` file stores the shell output if there were any. Don't be confused if it's empty as it's the normal case(I did not add any shell output). `output.csv` & `output.xlsx` are two versions of same results we wanna have.
