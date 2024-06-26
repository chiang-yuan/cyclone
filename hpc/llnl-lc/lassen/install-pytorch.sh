#!/bin/bash

# create an opence environment in conda (Python-3.9)
conda create -y -n opence-1.7.2-cuda-11.4 python=3.9
 
# activate the opence environment
conda activate opence-1.7.2-cuda-11.4
 
# register LLNL SSL certificates
conda config --env --set ssl_verify /etc/pki/tls/cert.pem
 
# register LC's local conda channel for Open-CE
condachannel=/usr/global/tools/opence/${SYS_TYPE}/opence-1.7.2/condabuild-py3.9-cuda11.4
conda config --env --prepend channels file://$condachannel
 
# install some packages
conda install -y pytorch=1.12.1=cuda11.4_py39_1