import warnings

from tqdm.auto import tqdm
import numpy as np
from scipy.spatial.distance import cdist


def find_far_points(X, n_points, metric="seuclidean", bound="infimum"):
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

    selected = [np.random.randint(len(X))] # randomly select the first point
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
