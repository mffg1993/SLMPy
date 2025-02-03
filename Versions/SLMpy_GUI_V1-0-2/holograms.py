"""
Hologram Generation - Laguerre-Gaussian and Hermite-Gaussian Beam Holograms

This module provides functions to generate holograms for optical beam simulations,
including Laguerre-Gaussian (LG) and Hermite-Gaussian (HG) beams. It also includes
tools for propagation, coordinate transformations, and wavefront correction using
Zernike polynomials.

Author: Manuel Ferrer (@mferrerg)
"""

import numpy as np
from optics import cart2pol, LG, HG, Zernike, propTF

def Hologram(A, hx, hy, LA):
    """
    Generate a phase hologram for an optical beam.
    
    Parameters:
        A (np.ndarray): Complex amplitude of the beam.
        hx, hy (float): Pixel spacing in x and y directions.
        LA (float): Grating period in the hologram.
    
    Returns:
        np.ndarray: A 2D hologram pattern.
    """
    nn = np.sum(np.abs(A)**2) * hx * hy
    NU = A / np.sqrt(nn)
    Amp = np.abs(NU)
    PHI = np.angle(NU)
    mm = Amp.shape
    x1, y1 = np.meshgrid(hx * np.arange(1, mm[1] + 1), hy * np.arange(1, mm[0] + 1))
    ss = np.linspace(-np.pi, 0, 2000)
    sincc = np.sin(ss) / ss
    sincc[np.isnan(sincc)] = 1
    M = 1 + np.interp(Amp, sincc, ss) / np.pi
    M[np.isnan(M)] = 0
    return np.mod(PHI - np.pi * M + x1 / LA, 2 * np.pi)

def HoloLG(l, p, w0, z=(0, 5), Z=(1, 0, 0, 0), LA=0.005, maxx=1, SLM_Pix=(1024, 780), position=(0, 0)):
    """
    Generate a Laguerre-Gaussian (LG) beam hologram.
    
    Parameters:
        l (int): Azimuthal index.
        p (int): Radial index.
        w0 (float): Beam waist.
        z (tuple): Propagation parameters.
        Z (tuple): Zernike polynomial parameters.
        LA (float): Grating period.
        maxx (float): Half-width of the simulation window.
        SLM_Pix (tuple): Spatial light modulator resolution.
        position (tuple): Beam displacement in x and y.
    
    Returns:
        np.ndarray: Generated LG beam hologram.
    """
    rate = SLM_Pix[1] / SLM_Pix[0]
    maxy = rate * maxx
    X = np.linspace(-maxx, maxx, SLM_Pix[0]) + position[0]
    Y = -np.linspace(-maxy, maxy, SLM_Pix[1]) + position[1]
    dx = np.abs(X[1] - X[2])
    dy = np.abs(Y[1] - Y[2])
    xx, yy = np.meshgrid(X, Y)
    r, phi = cart2pol(xx, yy)
    ZPM = Zernike(r / Z[0], phi, Z[2], Z[3])
    A = LG(r, phi, l, p, w0) * np.exp(1j * 2 * np.pi * Z[1] * ZPM)
    return Hologram(A, dx, dy, LA)

def HoloHG(m, n, w0, z=(0, 5), Z=(1, 0, 0, 0), LA=0.005, maxx=1, SLM_Pix=(1024, 780), position=(0, 0)):
    """
    Generate a Hermite-Gaussian (HG) beam hologram.
    
    Parameters:
        m (int): Order in the horizontal direction.
        n (int): Order in the vertical direction.
        w0 (float): Beam waist.
        z (tuple): Propagation parameters.
        Z (tuple): Zernike polynomial parameters.
        LA (float): Grating period.
        maxx (float): Half-width of the simulation window.
        SLM_Pix (tuple): Spatial light modulator resolution.
        position (tuple): Beam displacement in x and y.
    
    Returns:
        np.ndarray: Generated HG beam hologram.
    """
    rate = SLM_Pix[1] / SLM_Pix[0]
    maxy = rate * maxx
    X = np.linspace(-maxx, maxx, SLM_Pix[0]) + position[0]
    Y = -np.linspace(-maxy, maxy, SLM_Pix[1]) + position[1]
    dx = np.abs(X[1] - X[2])
    dy = np.abs(Y[1] - Y[2])
    xx, yy = np.meshgrid(X, Y)
    r, phi = cart2pol(xx, yy)
    ZPM = Zernike(r / Z[0], phi, Z[2], Z[3])
    A = HG(xx, yy, m, n, w0) * np.exp(1j * 2 * np.pi * Z[1] * ZPM)
    return Hologram(A, dx, dy, LA)
