import argparse
import ast
from pathlib import Path

import numpy as np
import torch
from torch_dftd.torch_dftd3_calculator import TorchDFTD3Calculator
from tqdm.auto import tqdm

from ase import units
from ase.calculators.mixing import SumCalculator
from ase.io import read
from ase.md.npt import NPT
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary
from mace.calculators import MACECalculator

default_disp_kwrags = dict(
    xc="pbe",
    cutoff=40 * units.Bohr,
)


def parse_3x3_array(s):
    try:
        # Use ast.literal_eval to safely evaluate the literal expression
        array_2d = ast.literal_eval(s)

        # Convert the array to NumPy array and check its shape
        array_2d = np.array(array_2d)
        if array_2d.shape != (3, 3):
            raise ValueError("Invalid array shape. Must be a 3x3 array.")

        return array_2d
    except (ValueError, SyntaxError) as e:
        raise argparse.ArgumentTypeError(str(e))


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
    traceless: float = 1.0,
    dispersion: str | None = None,
    dispersion_kwargs: dict = default_disp_kwrags,
    restart: bool = True,
    interval: int = 500,
    device: str | None = None,
    dtype: str = "float64",
):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")

    print(f"Using device: {device}")

    mace_calc = MACECalculator(
        model_paths=[
            "/pscratch/sd/c/cyrusyc/mace-universal/pretrained/2023-12-12-mace-128-L1_epoch-199.model"
        ],
        device=device,
        default_dtype=dtype,
    )

    if dispersion is not None:
        import re

        print(f"Using dispersion: {dispersion}")

        match = re.search(r"(\d+)", device)
        if match:
            device = f"cuda:{int(match.group())+1}"
            print(f"Using device: {device}")

        disp_calc = TorchDFTD3Calculator(
            device=device,
            **dispersion_kwargs,
        )
        calc = SumCalculator([mace_calc, disp_calc])
    else:
        calc = mace_calc

    fxyz = fout.with_suffix(".extxyz")
    fout.with_suffix(".traj")

    last_step = 0
    if restart and fxyz.exists():
        traj = read(fxyz, index=":")
        last_step = len(traj)
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
    npt.set_fraction_traceless(traceless)

    print(f"Running {npt} for {nsteps} steps from {last_step} to {last_step+nsteps}")
    print(f"Structure: {atoms}")
    print(f"Calculator: {atoms.calc}")
    print(f"Writing to {fxyz}")

    with tqdm(total=nsteps) as pbar:

        def write_xyz(dyn=npt, outpath=fxyz):
            dyn.atoms.write(outpath, format="extxyz", append=True)

        def log(dyn=npt):
            if dyn.nsteps % interval == 0:
                print(
                    dyn.nsteps + last_step,
                    dyn.atoms.get_temperature(),
                    dyn.atoms.get_potential_energy(),
                )
                dyn.atoms.wrap()

            pbar.update()

        # npt.attach(traj.write)
        npt.attach(write_xyz)
        npt.attach(log, interval=interval)
        npt.run(nsteps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fin", type=Path)
    parser.add_argument("fout", type=Path)
    parser.add_argument("--timestep", type=float, default=2 * units.fs)
    parser.add_argument("--nsteps", type=int, default=1000)
    parser.add_argument("--temperature", type=float, default=1250)
    parser.add_argument("--pressure", type=float, default=0)
    parser.add_argument("--ttime", type=float, default=100 * units.fs)
    parser.add_argument(
        "--pfactor", type=float, default=(300 * units.fs) ** 70 * units.GPa
    )
    parser.add_argument("--mask", type=parse_3x3_array, default=None)
    parser.add_argument("--traceless", type=float, default=1.0)
    parser.add_argument("--dispersion", default=None)
    parser.add_argument("--interval", type=int, default=500)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--restart", action="store_true")

    args = parser.parse_args()

    main(**vars(args))
