#!/bin/bash
export CUDA_VISIBLE_DEVICES=$((3-SLURM_LOCALID))
$*
