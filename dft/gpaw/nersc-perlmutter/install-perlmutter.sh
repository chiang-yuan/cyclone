
# NOTE
# 
# Pre-installation:
#   1. Activate virtual environment
#   2. Set the installation path
#   3. Copy this file and siteconfig.py to the installation path
# Installation:
#   1. Run this script
# Post-installation / Run-time:
#   - export MPICH_GPU_SUPPORT_ENABLED=1
#   - Dynamic linking: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$libxc_path/lib

module purge
source /opt/cray/pe/cpe/23.12/restore_lmod_system_defaults.sh

module load python
source activate /pscratch/sd/c/cyrusyc/.conda/mlip-arena

module load PrgEnv-cray
module load craype-x86-milan
module load cudatoolkit/12.2
module load craype-accel-nvidia80
module load cray-fftw

module -t list

# conda/Miniconda3-py311_23.11.0-2
# evp-patch
# python/3.11
# cce/17.0.0
# craype/2.7.30
# cray-dsmml/0.2.2
# libfabric/1.20.1
# craype-network-ofi
# cray-mpich/8.1.28
# cray-libsci/23.12.5
# PrgEnv-cray/8.5.0
# craype-x86-milan
# cudatoolkit/12.2
# craype-accel-nvidia80
# cray-fftw/3.3.10.6

export CRAY_ACCEL_TARGET=nvidia80

workdir=$(pwd) # or install to a specific directory
libxc_path=${workdir}/libxc

cd $workdir

# Install xc
if [ ! -d libxc ]; then
    wget https://gitlab.com/libxc/libxc/-/archive/6.2.2/libxc-6.2.2.tar.bz2
    tar -xvf libxc-6.2.2.tar.bz2
    mv libxc-6.2.2 libxc
    # git clone https://gitlab.com/libxc/libxc.git
fi

cd libxc


if [ ! -d include ]; then
    autoreconf -i
    ./configure --prefix=${libxc_path} CFLAGS="-O3 -fPIC"
    make -j 16
    make check -j 16
    make install
fi

cd $workdir

# https://wiki.fysik.dtu.dk/gpaw/platforms/Cray/nersc_perlmutter.htmli

# export C_INCLUDE_PATH=$C_INCLUDE_PATH:$libxc_path/include
# export LIBRARY_PATH=$LIBRARY_PATH:$libxc_path/lib
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$libxc_path/lib

# pip install ase

if [ ! -d gpaw ]; then
    git clone https://gitlab.com/gpaw/gpaw.git
fi

# cp siteconfig.py gpaw/

cd gpaw
# wget https://raw.githubusercontent.com/NERSC/community-software/main/gpaw/siteconfig.py -O siteconfig.py

sed -i "s|'/your/path/to/libxc/6.2.2'|\'${libxc_path}/\'|g" siteconfig.py

python setup.py build_ext
python setup.py install