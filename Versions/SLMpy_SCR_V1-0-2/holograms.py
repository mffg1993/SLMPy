import numpy as np
from optics import cart2pol, LG, HG, Zernike, propTF



def Hologram(A, hx, hy, LA):
    """
    Generate a hologram pattern for a beam with specific characteristics.
    
        Parameters:
            - A: Complex amplitude of the beam.
            - hx, hy: Spacing in x and y directions.
            - LA: Grating period in the hologram.
    """
    # Normalize the input beam
    nn = np.sum(np.abs(A)**2) * hx * hy
    NU = A / np.sqrt(nn)

    # Compute amplitude and phase patterns
    Amp = np.abs(NU)
    PHI = np.angle(NU)

    # Generate grating
    mm = Amp.shape
    x1, y1 = np.meshgrid(hx * np.arange(1, mm[1] + 1), hy * np.arange(1, mm[0] + 1))

    # Inverse Sinc function interpolation
    ss = np.linspace(-np.pi, 0, 2000)
    # sincc = np.sin(ss) / ss
    # sincc[np.isnan(sincc)] = 1
    sincc = np.sinc(ss / np.pi)

    # Apply amplitude masking
    M = 1 + np.interp(Amp, sincc, ss) / np.pi
    M[np.isnan(M)] = 0

    # Generate phase hologram
    F = np.mod(PHI - np.pi * M + x1 / LA, 2 * np.pi)

    # Return the full hologram
    return M * F

def HoloLG(l, p, w0, z=(0, 5), Z=(1, 0, 0, 0), LA=0.005, maxx=1, SLM_Pix=(1024, 780), position=(0, 0)):
    """
    Generate a Laguerre-Gaussian beam hologram.
    
    Parameters:
        - l (int): Azimuthal index (orbital angular momentum quantum number).
        - p (int): Radial index.
        - w0 (float): Beam waist (radius at which the beam's intensity drops to 1/e^2).
        - z (tuple): Propagation parameters (z[0]: propagation distance, z[1]: steps).
        - Z (tuple): Zernike polynomial parameters (Z[0]: normalization, Z[1]: strength,
                      Z[2], Z[3]: indices for the Zernike polynomial).
        - LA (float): Grating period (used to control diffraction properties).
        - maxx (float): Size of the simulation window along the x-axis (half-width).
        - SLM_Pix (tuple): Resolution of the spatial light modulator (width, height).
        - position (tuple): Displacement of the beam's center in x and y directions.
    
    Returns:
        - numpy.ndarray: A 2D array representing the generated Laguerre-Gaussian hologram.
    """
    
    # Aspect ratio of the simulation window
    rate = SLM_Pix[1] / SLM_Pix[0]  # Assuming square pixels
    maxy = rate * maxx  # Scaling the Y-axis based on aspect ratio

    # Define the simulation space and include beam displacement
    X = np.linspace(-maxx, maxx, SLM_Pix[0]) + position[0]
    Y = -np.linspace(-maxy, maxy, SLM_Pix[1]) + position[1]

    # Calculate spacing between pixels
    dx = np.abs(X[1] - X[2])
    dy = np.abs(Y[1] - Y[2])

    # Create a meshgrid for Cartesian coordinates
    xx, yy = np.meshgrid(X, Y)

    # Convert Cartesian coordinates to polar coordinates
    r, phi = cart2pol(xx, yy)

    # Apply Zernike polynomial mask for wavefront correction
    ZPM = Zernike(r / Z[0], phi, Z[2], Z[3])

    # Generate the Laguerre-Gaussian beam field with Zernike corrections
    A = LG(r, phi, l, p, w0) * np.exp(1j * 2 * np.pi * Z[1] * ZPM)

    # Propagation logic if a propagation distance is specified
    if z[0] > 0:
        # Define propagation space with uniform step sizes
        ZZ = np.linspace(0, z[0], z[1])
        dz = np.abs(ZZ[0] - ZZ[1])  # Step size

        # Initialize a list to store the propagated field
        F = [A]

        # Iteratively propagate the beam through the specified distance
        for _ in range(z[1]):
            A = propTF(A, 2 * maxx, 1, dz)  # Fresnel propagation
            F.append(A)

    # Generate the hologram from the resulting field
    return Hologram(A, dx, dy, LA)

def HoloHG(m, n, w0, z=(0, 5), Z=(1, 0, 0, 0), LA=0.005, maxx=1, SLM_Pix=(1024, 780), position=(0, 0)):
    """
    Generate a Hermite-Gaussian beam hologram.
    
    Parameters:
        - m (int): Order in the horizontal direction
        - n (int): Order in the vertical direction
        - w0 (float): Beam waist (radius at which the beam's intensity drops to 1/e^2).
        - z (tuple): Propagation parameters (z[0]: propagation distance, z[1]: steps).
        - Z (tuple): Zernike polynomial parameters (Z[0]: normalization, Z[1]: strength,
                      Z[2], Z[3]: indices for the Zernike polynomial).
        - LA (float): Grating period (used to control diffraction properties).
        - maxx (float): Size of the simulation window along the x-axis (half-width).
        - SLM_Pix (tuple): Resolution of the spatial light modulator (width, height).
        - position (tuple): Displacement of the beam's center in x and y directions.
    
    Returns:
        - numpy.ndarray: A 2D array representing the generated Laguerre-Gaussian hologram.
    """
    # Aspect ratio of the simulation window
    rate = SLM_Pix[1] / SLM_Pix[0]  # Assuming square pixels
    maxy = rate * maxx  # Scaling the Y-axis based on aspect ratio

    # Define the simulation space and include beam displacement
    X = np.linspace(-maxx, maxx, SLM_Pix[0]) + position[0]
    Y = -np.linspace(-maxy, maxy, SLM_Pix[1]) + position[1]

    # Calculate spacing between pixels
    dx = np.abs(X[1] - X[2])
    dy = np.abs(Y[1] - Y[2])

    # Create a meshgrid for Cartesian coordinates
    xx, yy = np.meshgrid(X, Y)

    # Convert Cartesian coordinates to polar coordinates
    r, phi = cart2pol(xx, yy)

    # Apply Zernike polynomial mask for wavefront correction
    ZPM = Zernike(r / Z[0], phi, Z[2], Z[3])

    # Generate the Laguerre-Gaussian beam field with Zernike corrections
    A = HG(xx, yy, m, n, w0) * np.exp(1j * 2 * np.pi * Z[1] * ZPM)

    # Propagation logic if a propagation distance is specified
    if z[0] > 0:
        # Define propagation space with uniform step sizes
        ZZ = np.linspace(0, z[0], z[1])
        dz = np.abs(ZZ[0] - ZZ[1])  # Step size

        # Initialize a list to store the propagated field
        F = [A]

        # Iteratively propagate the beam through the specified distance
        for _ in range(z[1]):
            A = propTF(A, 2 * maxx, 1, dz)  # Fresnel propagation
            F.append(A)

    # Generate the hologram from the resulting field
    return Hologram(A, dx, dy, LA)
