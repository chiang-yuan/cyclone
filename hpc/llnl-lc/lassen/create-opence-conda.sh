#!/bin/bash

# install to anaconda subdirectory within current working directory
installdir=/usr/workspace/$USER/.local/$SYS_TYPE/conda
 
# install conda
bash /usr/global/tools/opence/blueos_3_ppc64le_ib_p9/opence-1.7.2/Miniconda3-py39_4.12.0-Linux-ppc64le.sh -b -f -p $installdir
 
# activate conda environment
source $installdir/bin/activate