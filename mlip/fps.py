import warnings

from tqdm.auto import tqdm
import numpy as np
from scipy.spatial.distance import cdist
from ase import Atoms
from typing import Sequence


def mace_mp_fps(
    traj: Sequence[Atoms],
    nsamples: int | None = None,
    model="medium-mpa-0",
    metric="seuclidean",
):
    """
    Perform farthest point sampling (FPS) on a trajectory of atomic structures using MACE-MP descriptors.
    Parameters:
        traj (Sequence[Atoms]): A sequence of atomic structures (e.g., ASE Atoms objects) representing the trajectory.
        nsamples (int | None, optional): The number of samples to select. If None, defaults to 10% of the trajectory length.
        model (str, optional): The MACE-MP model to use for descriptor calculation. Defaults to MACE-MPA ("medium-mpa-0").
        metric (str, optional): The distance metric to use for computing pairwise distances between descriptors. Defaults to "seuclidean".
    Returns:
        tuple:
            - sampled_traj (list[Atoms]): A list of sampled atomic structures from the trajectory.
            - sampled_descriptors (np.ndarray): A NumPy array of descriptors corresponding to the sampled structures.
    Raises:
        UserWarning: If `nsamples` is not specified, a warning is issued, and the default value is used.
    Notes:
        - This function uses the MACE-MP calculator to compute descriptors for each atomic structure in the trajectory.
        - The farthest point sampling is performed using the `find_farthest_points` function with the "infimum" bound.
        - The progress of descriptor computation is displayed using a progress bar.
    """

    from mace.calculators import mace_mp

    calc = mace_mp(model=model)

    if nsamples is None:
        warnings.warn(
            "Number of samples not specified, using 10% of the trajectory length as default.",
            UserWarning,
        )
        nsamples = int(len(traj) * 0.1)

    assert nsamples > 0, "Number of samples must be greater than 0."
    assert nsamples < len(traj), (
        "Number of samples must be less than the trajectory length."
    )

    descriptors = []

    for atoms in tqdm(traj, desc="MACE-MP descriptors"):
        descriptor = calc.get_descriptors(atoms=atoms)
        descriptors.append(descriptor)

    descriptors = np.array(descriptors)

    sampled_descriptors, indices = find_farthest_points(
        descriptors, nsamples, metric, bound="infimum"
    )

    sampled_traj = []

    for idx in indices:
        sampled_traj.append(traj[idx])

    return sampled_traj, sampled_descriptors


def find_farthest_points(X, n_points, metric="seuclidean", bound="infimum"):
    """
    Find farthest points from a given set of points using Farthest Point Sampling (FPS).

    Parameters:
        X (numpy.ndarray): Descriptor array of shape (nbatch, natoms, dim), where `nbatch` is the
            number of batches, `natoms` is the number of atoms (or points), and `dim` is the
            dimensionality of each point. The array will be reshaped internally to
            (nbatch, natoms * dim).
        n_points (int): The number of farthest points to sample.
        metric (str, optional): The distance metric to use for computing pairwise distances.
            Defaults to "seuclidean". See `scipy.spatial.distance.cdist` for available metrics.
        bound (str, optional): The type of bound to use for selecting the farthest points.
            Options are:
            - "infimum" (default): Selects the point with the minimum distance to the
              already selected points.
            - "supremum": Selects the point with the maximum distance to the already
              selected points. Note that this is not recommended as it may lead to
              suboptimal sampling.

    Returns:
        tuple: A tuple containing:
            - numpy.ndarray: The sampled farthest points, with the same dimensionality as
              the input points.
            - list: Indices of the selected points in the original input array.

    Raises:
        ValueError: If the `bound` parameter is not "infimum" or "supremum".

    Warnings:
        UserWarning: If `bound` is set to "supremum", a warning is issued indicating that
            this option is not recommended.

    Notes:
        - The first point is selected randomly.
        - The function uses `scipy.spatial.distance.cdist` to compute pairwise distances.
    """

    X = X.reshape(X.shape[0], -1)

    selected = [np.random.randint(len(X))]  # randomly select the first point
    available = set(range(len(X))) - set(selected)

    for _ in tqdm(range(1, n_points), desc="Farthest point sampling"):
        if bound == "infimum":
            distances = cdist(X[list(available)], X[selected], metric=metric).min(
                axis=1
            )
        elif bound == "supremum":
            warnings.warn(
                "Using supremum bound for farthest point sampling is not recommended. "
                "It tends to select only a few most distant points. "
                "Consider using infimum bound instead.",
                UserWarning,
            )
            distances = cdist(X[list(available)], X[selected], metric=metric).max(
                axis=1
            )
        else:
            raise ValueError("bound must be 'infimum' or 'supremum'")

        next_point = list(available)[np.argmax(distances)]
        selected.append(next_point)
        available.remove(next_point)

    return X[selected], selected
