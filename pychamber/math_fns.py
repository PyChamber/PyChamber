import numpy as np


def cartesian_to_spherical(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xy_sq = x**2 + y**2
    r = np.sqrt(xy_sq + z**2)
    theta = np.arctan2(np.sqrt(xy_sq), z)
    phi = np.arctan2(y, x)

    return r, theta, phi


def spherical_to_cartesian(
    r: np.ndarray, theta: np.ndarray, phi: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    return x, y, z


def clean_complex_to_db(array: np.ndarray) -> np.ndarray:
    mag = np.abs(array)
    clean_array = np.where(mag == 0, 1e-20, mag)
    return 20 * np.log10(clean_array)
