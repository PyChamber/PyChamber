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
    theta_rad = np.deg2rad(theta)
    phi_rad = np.deg2rad(phi)

    x = r * np.sin(phi_rad) * np.cos(theta_rad)
    y = r * np.sin(phi_rad) * np.sin(theta_rad)
    z = r * np.cos(phi_rad)

    return x, y, z
