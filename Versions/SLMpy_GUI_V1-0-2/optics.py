"""
Optical Beam Simulation - Special Functions for Beam Propagation and Hologram Generation

This module provides numerical implementations of special functions used in optical simulations,
including Zernike polynomials, Laguerre-Gaussian (LG) and Hermite-Gaussian (HG) beams, as well as
Fresnel propagation using the transfer function approach. It is designed to facilitate the
generation of holograms and wavefront corrections in optical research and applications.

Author: Manuel Ferrer (@mferrerg)
"""

import numpy as np
import math

def cart2pol(x, y):
    """
    Convert Cartesian coordinates (x, y) to polar coordinates (rho, phi).
    
    Parameters:
        x (float or np.ndarray): X-coordinate(s).
        y (float or np.ndarray): Y-coordinate(s).
    
    Returns:
        tuple: (rho, phi) where rho is the radial distance and phi is the azimuthal angle.
    """
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return rho, phi

def RR(m, n):
    """
    Compute coefficients and powers for the radial polynomial of Zernike functions.
    
    Parameters:
        m (int): Azimuthal index.
        n (int): Radial index.
    
    Returns:
        list: Coefficients and powers for the radial polynomial.
    """
    coeff = []
    pow = []
    if (n - m) % 2 == 0:
        for kk in range(0, int((n - m) / 2 + 1)):
            aa = ((-1) ** kk * math.factorial(int(n - kk))) / (
                math.factorial(int(kk)) *
                math.factorial(int((n + m) / 2 - kk)) *
                math.factorial(int((n - m) / 2 - kk))
            )
            bb = n - 2 * kk
            coeff.append(aa)
            pow.append(bb)
    else:
        coeff.append(0)
        pow.append(0)
    return [coeff, pow]

def Zernike(RHO, PHI, m, n):
    """
    Compute the Zernike polynomial.
    
    Parameters:
        RHO (np.ndarray): Radial coordinate.
        PHI (np.ndarray): Azimuthal coordinate.
        m (int): Azimuthal index.
        n (int): Radial index.
    
    Returns:
        np.ndarray: Normalized Zernike polynomial values.
    """
    ZR = np.zeros(RHO.shape)
    rn = RR(np.abs(m), n)
    for ii in range(len(rn[0])):
        ZR += rn[0][ii] * RHO ** rn[1][ii]
    if m >= 0:
        Z = ZR * np.cos(np.abs(m) * PHI)
    else:
        Z = ZR * np.sin(np.abs(m) * PHI)
    M = (RHO <= 1)
    P = Z * M
    P = (P - np.min(P)) / np.max(P - np.min(P))
    return P

def NlaguerreL(n, a, X):
    """
    Compute the generalized Laguerre polynomial numerically.
    
    Parameters:
        n (int): Order of the polynomial.
        a (float): Parameter.
        X (np.ndarray): Input values.
    
    Returns:
        np.ndarray: Laguerre polynomial values.
    """
    LL = 0
    for m in range(n + 1):
        term = (
            ((-1) ** m) * math.factorial(n + a) /
            (math.factorial(n - m) * math.factorial(a + m) * math.factorial(m)) *
            (X ** m)
        )
        LL += term
    return LL

def LG(RHO, PHI, ell, p, w0):
    """
    Generate a Laguerre-Gaussian beam.
    
    Parameters:
        RHO (np.ndarray): Radial coordinate.
        PHI (np.ndarray): Azimuthal coordinate.
        ell (int): Azimuthal index.
        p (int): Radial index.
        w0 (float): Beam waist.
    
    Returns:
        np.ndarray: Complex field of the Laguerre-Gaussian beam.
    """
    C = np.sqrt((2 * math.factorial(p)) / (np.pi * math.factorial(p + np.abs(ell)))) * (1 / w0)
    field = (
        C *
        np.exp(-(RHO / w0) ** 2) *
        (np.sqrt(2) * RHO / w0) ** np.abs(ell) *
        np.exp(1j * ell * PHI) *
        NlaguerreL(p, np.abs(ell), 2 * (RHO / w0) ** 2)
    )
    return field




def NHermite(n, X):
    """
    Compute the numerical Hermite polynomial using recurrence relations.
    
    Parameters:
        - n (int): Order of the Hermite polynomial.
        - X (array-like): Input values for the polynomial.
    
    Returns:
        - numpy.ndarray: Values of the Hermite polynomial.

    """
    # Initialize the first two Hermite polynomials
    Hn1 = np.ones(X.shape)  # H_0(x) = 1
    H = 2 * X  # H_1(x) = 2x

    if n < 0:
        raise ValueError("The index must be 0 or positive.")
    elif n == 0:
        return Hn1  # Return H_0(x)
    elif n == 1:
        return H  # Return H_1(x)
    else:
        # Use recurrence relation to compute higher-order polynomials
        for nn in range(2, n + 1):
            Hn = 2 * X * H - 2 * (nn - 1) * Hn1  # Recurrence relation: H_n(x) = 2xH_{n-1}(x) - 2(n-1)H_{n-2}(x)
            Hn1 = H  # Update H_{n-2} to H_{n-1}
            H = Hn  # Update H_{n-1} to H_n
    return H

def HG(X, Y, m, n, w0):
    """
     Generate a Hermite-Gaussian beam.
    
    Parameters:
        - X, Y (2D arrays): Cartesian coordinates.
        - m, n (int): Orders of the Hermite polynomial along x and y, respectively.
        - w0 (float): Beam waist (radius at which the beam's intensity drops to 1/e^2).
    
    Returns:
        - numpy.ndarray: Complex field of the Hermite-Gaussian beam.
    """
    # Compute the spacing between grid points
    h = np.abs(X[0, 0] - X[0, 1])

    # Calculate the Hermite-Gaussian field
    field = (
        NHermite(m, np.sqrt(2) * X / w0) *  # Hermite polynomial in X
        NHermite(n, np.sqrt(2) * Y / w0) *  # Hermite polynomial in Y
        np.exp(-(X ** 2 + Y ** 2) / w0 ** 2)  # Gaussian envelope
    )
    
    # Normalize the field to ensure unit power
    normalization = np.sum(h * h * np.abs(field) ** 2)
    field = field / np.sqrt(normalization)
    return field




def propTF(u1, Lx, Ly, la, z):
    """
    Perform Fresnel propagation using the transfer function approach.
    
    Parameters:
        u1 (np.ndarray): Complex amplitude of the beam.
        Lx, Ly (float): Window size in x and y directions.
        la (float): Wavelength.
        z (float): Propagation distance.
    
    Returns:
        np.ndarray: Complex amplitude of the beam at the observation plane.
    """
    Yd, Xd = u1.shape
    dx = Lx / Xd
    dy = Ly / Yd
    fx = np.arange(-1 / (2 * dx), 1 / (2 * dx), 1 / Lx)
    fy = np.arange(-1 / (2 * dy), 1 / (2 * dy), 1 / Ly)
    Fx, Fy = np.meshgrid(fx, fy)
    H = np.exp(-1j * np.pi * 0.25 * la * z * (Fx**2 + Fy**2))
    U1 = np.fft.fftshift(np.fft.fft2(u1))
    U2 = H * U1
    u2 = np.fft.ifft2(np.fft.ifftshift(U2))
    return u2
