import argparse
from pathlib import Path

import numpy as np
import torch
from torch_dftd.torch_dftd3_calculator import TorchDFTD3Calculator
from tqdm.auto import tqdm

from ase import units
from ase.calculators.mixing import SumCalculator
from ase.io import read, write
from ase.io.trajectory import Trajectory
from ase.md.npt import NPT
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from mace.calculators import MACECalculator


def main(
    fin: Path,
    fout: Path,
    timestep: float = 2 * units.fs,
    nsteps: int = 1000,
    temperature: float = 300,
    pressure: float = 0 * units.GPa,
    ttime: float = 25 * units.fs,
    pfactor: float = (75 * units.fs) ** 1 * units.GPa,
    mask: np.ndarray | list[int] | None = None,
    dispersion: str | None = "bj",
    restart: bool = True,
    interval: int = 100,
):
    mace_calc = MACECalculator(
        model_paths=[
            "/pscratch/sd/c/cyrusyc/mace-universal/pretrained/2023-12-12-mace-128-L1_epoch-199.model"
        ],
        device="cuda" if torch.cuda.is_available() else "cpu",
        default_dtype="float64",
    )

    if dispersion is not None:
        disp_calc = TorchDFTD3Calculator(
            device="cuda" if torch.cuda.is_available() else "cpu", damping=dispersion
        )
        calc = SumCalculator([mace_calc, disp_calc])
    else:
        calc = mace_calc

    fxyz = fout.with_suffix(".extxyz")
    ftraj = fout.with_suffix(".traj")

    if restart and fxyz.exists():
        traj = read(fxyz, index=":")
        nsteps -= len(traj)
        atoms = traj[-1]
    else:
        atoms = read(fin)

    atoms.calc = calc

    MaxwellBoltzmannDistribution(atoms, temperature_K=temperature)
    Stationary(atoms)

    npt = NPT(
        atoms,
        timestep=timestep,
        temperature_K=temperature,
        externalstress=pressure,
        ttime=ttime,
        pfactor=pfactor,
        mask=mask,
    )

    traj = Trajectory(ftraj, "w", atoms)

    with tqdm(total=nsteps) as pbar:

        def log(atoms=atoms, dyn=npt):
            if dyn.nsteps % interval == 0:
                print(dyn.nsteps, atoms.get_temperature(), atoms.get_potential_energy())
                for a in traj[-interval:]:
                    write(fxyz, a, format="extxyz", append=True)
            pbar.update()

        npt.attach(traj.write)
        npt.attach(log, interval=interval)
        npt.run(nsteps)

    for a in traj[-interval:]:
        write(fxyz, a, format="extxyz", append=True)

    traj.close()
    # write(fxyz, read(ftraj, index=":"), format="extxyz")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fin", type=Path)
    parser.add_argument("fout", type=Path)
    parser.add_argument("--timestep", type=float, default=2 * units.fs)
    parser.add_argument("--nsteps", type=int, default=1000)
    parser.add_argument("--temperature", type=float, default=300)
    parser.add_argument("--pressure", type=float, default=0)
    parser.add_argument("--ttime", type=float, default=25 * units.fs)
    parser.add_argument(
        "--pfactor", type=float, default=(75 * units.fs) ** 1 * units.GPa
    )
    parser.add_argument("--mask", type=int, nargs="+", default=None)
    parser.add_argument("--dispersion", type=str, default="bj")
    parser.add_argument("--restart", action="store_true")
    args = parser.parse_args()

    main(**vars(args))
