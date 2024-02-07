#!/bin/bash
#SBATCH -A m3828_g
#SBATCH -J jobname
#SBATCH -q preempt
#SBATCH -C gpu
#SBATCH -G 2
#SBATCH -N 1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=4
#SBATCH --gpu-bind=none
#SBATCH --time=02:00:00
#SBATCH --time-min=01:58:00
#SBATCH --error=%x-<infile>-%j.err
#SBATCH --output=%x-<infile>-%j.out
#SBATCH --comment=7-00:00:00
#SBATCH --signal=B:USR1@60
#SBATCH --requeue
#SBATCH --exclusive
#SBATCH --open-mode=append

module load python
source activate /pscratch/sd/c/cyrusyc/.conda/mace

srun -n 1 --exclusive python npt_mace_d3.py <infile> <outfile> \
    --nsteps=50000 \
    --dispersion=bj \
    --device=cuda:0 \
    --restart &

ckpt_command=

. ~/setup.sh
requeue_job func_trap USR1

wait
