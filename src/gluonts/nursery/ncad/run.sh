#!/bin/bash
#SBATCH --job-name=NCAD
#SBATCH --time=4-00:00:00 # hh:mm:ss
#SBATCH --gres="gpu:1"
#SBATCH --cpus-per-task=2
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=10G
#SBATCH --partition=gpu
#SBATCH --comment="Train some model on SMD"
#SBATCH --exclude=gpu06,gpu05


source activate ./envs

srun python3 examples/article/run_all_experiments.py \
--ncad_dir='.' \
--data_dir='./ncad_datasets' \
--hparams_dir='./examples/article/hparams' \
--out_dir='./ncad_output' \
--download_data=False \
--number_of_trials=1 \
--run_swat=False \
--run_yahoo=False