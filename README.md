## Instrucitons for This Project

We used local chatglm3-6b model in order to get data from Judgement Documents.
The project is built up by Sang Wenkai(zju), under warm and helpful guidance of Zhe Yuan(ZJU) and Dengkun Chen(ZJU).

## Initialization
- Make sure that `chatglm3-6b` model project and `chatglm3-6b-32k` model project are in the same directory as `set_up.py` and correctly named.
- Install the following dependings if you haven't:

```shell
pip install protobuf 'transformers>=4.30.2' cpm_kernels 'torch>=2.0' gradio mdtex2html sentencepiece accelerate func_timeout
```

(We strongly recommend you use the ZJU source for your pip if your working environment can't reach the internet outside zju. If you'd like to, run the following commands in your shell.)
```shell
pip install -i https://mirrors.zju.edu.cn/pypi/web/simple pip -U
pip config set global.index-url https://mirrors.zju.edu.cn/pypi/web/simple
```

## To run:

Just launch your terminal and change the directory towards this folder.

Edit the key variables in `set_up.py`, especially change the data directory.
 - `data_dir` is the directory where data you want to process has been stored. 
 - `log_dir` is where logging files will be stored, you can check the log out to find out what happenned during the procession. 
 - `results_dir` is where the processed data will be stored.
 - `max_threads` is the limit max number of simultanesously running threads.

Then type `./excute.sh` in terminal to run the project

Afterwards, you can type `./monitor.sh` in terminal to monitor the process. You can also check the final status of last process, even after its end. 

Also, you can type `./cancel.sh` in terminal to cancel the current running process.


## Notions:

- `set_up.py` for basic configurations.

- `main.py` is the main process file.
    - If you can directly handle a node with powerful gpus -- necessarily, more than RTX-4090 -- just run `python main.py`.
    - During each procession, we read the import basic variables from `set_up.py` to `main.py` where predata files are converted to `pandas.DataFrames` and starts the procession with many simultaneous threads, while limiting the running threads under `max_threads`.
    - We first try to process the data with 8k model, for docus longer than 8k, we store them and later process them altogether in 32k model.
    - Then we store the processed data into results directory.

- `Processer_8` is the processer of 8k model.

- `Processer_32` is the processer of 32k model.

- In logging directory -- `./log` as set default -- stores all the logging files.
    - `main.log` stores the main messages,
    - `files.log` stores the messages while reading files
    - `Filename.log` stores the messages of threads processing the corresponding data file.

- In output directory -- `./results` as set default -- stores all the processed data files.

- `./acu_results` directory (I'm sorry it can't be configured) stores the previous results, after each run, i store the all data, output, log into it with jod_id tagged. also the character at the end of the directory tells whether some data are dropped: "F" for failed and "P" for passed.

- `acu_main.log` acumulatively records the content of `main.log` after each run.

- `Error.txt` & `Out.txt` stores the errors and outs of terminal while running respectively. It's a result of `sbatch` session.

