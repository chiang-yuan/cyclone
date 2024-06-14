
# NOTE
# 
# Pre-installation:
#   1. Activate virtual environment
#   2. Set the installation path
#   3. Copy this file and siteconfig.py to the installation path
# Installation:
#   1. Run this script
# Post-installation:
#   - Dynamic linking: export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$libxc_path/lib

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
    ./configure --prefix=${libxc_path} CFLAGS="-fPIC"
    make -j 32
    make check -j 32
    make install
fi



cd $workdir

# https://wiki.fysik.dtu.dk/gpaw/platforms/Cray/nersc_perlmutter.htmli

# export C_INCLUDE_PATH=$C_INCLUDE_PATH:$libxc_path/include
# export LIBRARY_PATH=$LIBRARY_PATH:$libxc_path/lib
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$libxc_path/lib

module load cray-fftw

pip install ase

if [ ! -d gpaw ]; then
    git clone https://gitlab.com/gpaw/gpaw.git
fi

cp siteconfig.py gpaw/

cd gpaw
# wget https://raw.githubusercontent.com/NERSC/community-software/main/gpaw/siteconfig.py -O siteconfig.py

sed -i "s|'/your/path/to/libxc/6.2.2'|\'${libxc_path}\'|g" siteconfig.py

python setup.py build_ext
python setup.py install