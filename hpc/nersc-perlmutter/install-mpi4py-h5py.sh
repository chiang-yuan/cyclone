!#/bin/bash

module load python
module load cray-hdf5-parallel

module swap PrgEnv-${PE_ENV,,} PrgEnv-gnu
module load gcc/11.2.0 # match with the python

# mpi4py

MPICC="cc -shared" pip install --force-reinstall --no-cache-dir --no-binary=mpi4py mpi4py

# h5py

conda install -c defaults --override-channels numpy "cython<3"

HDF5_MPI=ON CC=cc pip install -v --force-reinstall --no-cache-dir --no-binary=h5py --no-build-isolation --no-deps h5py