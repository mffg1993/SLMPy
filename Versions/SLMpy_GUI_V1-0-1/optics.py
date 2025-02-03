import numpy as np
import math

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return rho, phi


################################################################################
# Zernike Polynomials
################################################################################

# Generate Zernike polynomials for optical phase modulation.
# Parameters:
# - RHO, PHI: Polar coordinates.
# - m, n: Azimuthal and radial indices.

# Coeffcients and powers or the radial Polynomials
def RR(m,n):
    """
    Compute coefficients and powers for the radial polynomial of Zernike functions.
    
    Parameters:
        - m (int): Azimuthal index (absolute value used internally).
        - n (int): Radial index.

    Returns:
        - list: Coefficients and powers for the radial polynomial.
    """
    coeff = []  # List to store coefficients
    pow = []    # List to store corresponding powers

    # Zernike radial polynomials exist only if (n - m) is even
    if (n - m) % 2 == 0:
        for kk in range(0, int((n - m) / 2 + 1)):
            # Compute the coefficient for the current term using factorials
            aa = ((-1) ** kk * math.factorial(int(n - kk))) / (
                math.factorial(int(kk)) *
                math.factorial(int((n + m) / 2 - kk)) *
                math.factorial(int((n - m) / 2 - kk))
            )
            # Compute the corresponding power
            bb = n - 2 * kk
            coeff.append(aa)
            pow.append(bb)
    else:
        # If (n - m) is not even, return zero for coefficients and powers
        coeff.append(0)
        pow.append(0)

    return [coeff, pow]  # Return the coefficients and powers as a list


def Zernike(RHO, PHI, m, n):
    """
    Construct the Zernike polynomial.
    
    Parameters:
        - RHO (2D array): Radial distance (normalized to 1 for the aperture boundary).
        - PHI (2D array): Azimuthal angle (polar coordinate).
        - m (int): Azimuthal index (can be negative for sine terms).
        - n (int): Radial index.
    Returns:
        - numpy.ndarray: Normalized Zernike polynomial values within the aperture.

    """
    ZR = np.zeros(RHO.shape)  # Initialize the Zernike radial polynomial
    rn = RR(np.abs(m), n)     # Compute radial coefficients and powers

    # Evaluate the radial polynomial using the precomputed coefficients
    for ii in range(len(rn[0])):
        ZR = ZR + rn[0][ii] * RHO ** rn[1][ii]

    # Handle the azimuthal dependence (cosine or sine based on the sign of m)
    if m >= 0:
        Z = ZR * np.cos(np.abs(m) * PHI)
    else:
        Z = ZR * np.sin(np.abs(m) * PHI)

    # Mask the polynomial to be valid only inside the unit disk (RHO <= 1)
    M = (RHO <= 1)  # Boolean mask for the aperture
    P = Z * M       # Apply the mask to restrict Zernike values to the aperture

    # Normalize the polynomial to have a range of 0 to 1
    P = (P - np.min(P)) / np.max(P - np.min(P))
    return P


################################################################################
# Numerical Implementation of Special Functions
################################################################################


def NlaguerreL(n, a, X):
    """
    Compute the generalized Laguerre polynomial numerically.
    
    Parameters:
        - n (int): Order of the polynomial.
        - a (float): Parameter for the polynomial.
        - X (array-like): Input values for the polynomial.
    Returns:
        - numpy.ndarray: Values of the generalized Laguerre polynomial.
        
    """
    LL = 0  # Initialize the result
    # Iterate over each term in the polynomial expansion
    for m in range(n + 1):
        # Compute each term using the formula for Laguerre polynomials
        term = (
            ((-1) ** m) * math.factorial(n + a) /
            (math.factorial(n - m) * math.factorial(a + m) * math.factorial(m)) *
            (X ** m)
        )
        LL += term  # Accumulate the result
    return LL



def LG(RHO, PHI, ell, p, w0):
    """
    Generate a Laguerre-Gaussian beam.
    
    Parameters:
        - RHO (2D array): Radial coordinate (distance from the center).
        - PHI (2D array): Azimuthal angle (in radians).
        - ell (int): Azimuthal index (orbital angular momentum quantum number).
        - p (int): Radial index.
        - w0 (float): Beam waist (radius at which the beam's intensity drops to 1/e^2).
    
    Returns:
        - numpy.ndarray: Complex field of the Laguerre-Gaussian beam.
    """
    # Normalization constant for the Laguerre-Gaussian mode
    C = np.sqrt((2 * math.factorial(p)) / (np.pi * math.factorial(p + np.abs(ell)))) * (1 / w0)
    
    # Compute the Laguerre-Gaussian field
    field = (
        C *
        np.exp(-(RHO / w0) ** 2) *  # Radial Gaussian envelope
        (np.sqrt(2) * RHO / w0) ** np.abs(ell) *  # Radial dependence
        np.exp(1j * ell * PHI) *  # Azimuthal phase factor
        NlaguerreL(p, np.abs(ell), 2 * (RHO / w0) ** 2)  # Laguerre polynomial
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
    # Generate a Hermite-Gaussian beam.
    
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

################################################################################
# Propagation and Utility Functions
################################################################################

# Perform Fresnel propagation using the transfer function approach.
# Parameters:
# - u1: Input field amplitude.
# - Lx, Ly: Window size in x and y directions.
# - lambda: Wavelength of light.
# - z: Propagation distance.

# Fresnel propagation using the Transfer function approach
# Based on Computational Fourier Optics by Voelz
# Generalization to non-square windows
#
# PARAMETERS
#
# u1      - Complex Amplitude of the beam at the source plane. It is a square array
# Lx       - Sidelength of the simulation window of the source plane in the X direction
# Ly       - Sidelength of the simulation window of the source plane in the X direction
# lambda  - Wavelength
# z       - Propagation distance
# u2      - Complex Amplitude of the beam at the observation plane

def propTF(u1,Lx,Ly,la,z):
    """
    Perform Fresnel propagation using the transfer function approach. 
    Based on Computational Fourier Optics by Voelz
    Generalization to non-square windows

    Parameters:
        - u1 (2D array): Complex amplitude of the beam at the source plane.
        - Lx, Ly (float): Side lengths of the simulation window in x and y directions.
        - la (float): Wavelength of the light.
        - z (float): Propagation distance.
        
    Returns:
        - numpy.ndarray: Complex amplitude of the beam at the observation plane.
    
    """
    # Determine the shape of the input field
    Yd, Xd = u1.shape
    
    # Calculate sampling intervals
    dx = Lx / Xd
    dy = Ly / Yd

    # Define frequency grids for x and y directions
    fx = np.arange(-1 / (2 * dx), 1 / (2 * dx), 1 / Lx)
    fy = np.arange(-1 / (2 * dy), 1 / (2 * dy), 1 / Ly)
    Fx, Fy = np.meshgrid(fx, fy)  # Create 2D frequency grids

    # Compute the transfer function for Fresnel propagation
    H = np.exp(-1j * np.pi * 0.25 * la * z * (Fx**2 + Fy**2))

    # Perform Fourier transform of the input field
    U1 = np.fft.fftshift(np.fft.fft2(u1))

    # Apply the transfer function in the frequency domain
    U2 = H * U1

    # Transform back to the spatial domain
    u2 = np.fft.ifft2(np.fft.ifftshift(U2))
    return u2