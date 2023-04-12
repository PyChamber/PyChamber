import numpy as np


def cartesian_to_spherical(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert cartesian coordinates to spherical coordinates.

    Args:
        x (np.ndarray): x coordinates
        y (np.ndarray): y coordinates
        z (np.ndarray): z coordinates

    Returns:
        r (np.ndarray): r coordinates
        theta (np.ndarray): theta coordinates
        phi (np.ndarray): phi coordinates
    """
    xy_sq = x**2 + y**2
    r = np.sqrt(xy_sq + z**2)
    theta = np.arctan2(np.sqrt(xy_sq), z)
    phi = np.arctan2(y, x)

    return r, theta, phi


def spherical_to_cartesian(
    r: np.ndarray, theta: np.ndarray, phi: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert spherical coordinates to cartesian coordinates.

    Args:
        r (np.ndarray): r coordinates
        theta (np.ndarray): theta coordinates
        phi (np.ndarray): phi coordinates

    Returns:
        x (np.ndarray): x coordinates
        y (np.ndarray): y coordinates
        z (np.ndarray): z coordinates
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)

    return x, y, z


def clean_complex_to_db(array: np.ndarray) -> np.ndarray:
    """Calculates dB from an array of complex values.

    Does some preprocessing of the input data to ensure no warnings are
    generated. Specifically, it replaces 0 magnitudes with a very small constant
    (1e-20).

    Args:
        array (np.ndarray): Array of complex values

    Returns:
        (np.ndarray): $20 log_{10}(array)$
    """
    mag = np.abs(array)
    clean_array = np.where(mag == 0, 1e-20, mag)
    return 20 * np.log10(clean_array)
