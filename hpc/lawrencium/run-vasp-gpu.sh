#!/bin/bash
#SBATCH --job-name=vasp-gpu
#SBATCH --account=pc_materials
#SBATCH --partition=es1
#SBATCH --qos=es_normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
# Processors per task (please always specify the total number of processors twice the number of GPUs):
#SBATCH --cpus-per-task=2
#Number of GPUs, this can be in the format of "gpu:[1-4]", or "gpu:V100:[1-4] with the type included
#SBATCH --gres=gpu:1
#SBATCH --time=1:00:00


module load nvhpc/23.11

export LD_LIBRARY_PATH=/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/nvhpc-23.11-gh5cygvdqksy6mxuy2xgoibowwxi3w7t/Linux_x86_64/23.11/compilers/extras/qd/lib:/global/software/rocky-8.x86_64/gcc/linux-rocky8-x86_64/gcc-8.5.0/nvhpc-23.11-gh5cygvdqksy6mxuy2xgoibowwxi3w7t/Linux_x86_64/23.11/cuda/lib64:$LD_LIBRARY_PATH

mpirun --prefix $LD_LIBRARY_PATH -np 8 vasp_std


