#!/bin/bash

module purge
module load nvhpc/23.11
# module load gcc/13.2.0 openmpi/4.1.6
# module load intel-oneapi-compilers/2023.1.0  intel-oneapi-mpi/2021.10.0
# module load intel-oneapi-mkl

module -t list

#
# FFTW
#

# bash build-fftw.sh

fftw_version=3.3.10
src_folder=fftw-${fftw_version}


if [ -d "$src_folder" ]; then
    echo "Skipping extraction: '$src_folder' already exists."
else
    wget https://www.fftw.org/${src_folder}.tar.gz
    tar -xvzf ${src_folder}.tar.gz
fi

cd ${src_folder}

fftw_dir="~/.local/fftw/${fftw_version}"

mkdir -p ${fftw_dir}

make distclean
./configure --prefix=${fftw_dir} --enable-openmp --enable-mpi
make -j16
make install

cd -

#
# VASP
#

vasp_version=6.5.0
src_folder=vasp.${vasp_version}

if [ -d "$src_folder" ]; then
    echo "Skipping extraction: '$src_folder' already exists."
else
    tar -xvzf vasp.${vasp_version}.tgz
fi

cd ${src_folder}
cp arch/makefile.include.nvhpc_omp_acc ./makefile.include

export FFTW_ROOT="${fftw_dir}"

# sed -i "s|/path/to/your/mkl/installation|$MKLROOT|g" makefile.include
sed -i "s|cuda11.8|cuda12.3|g" makefile.include
sed -i "s|/path/to/your/fftw/installation|$FFTW_ROOT|g" makefile.include

make clean
make DEPS=1 -j16 all

cp bin/* ~/.local/bin
