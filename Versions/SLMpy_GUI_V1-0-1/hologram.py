import numpy as np
from optics import cart2pol, LG, HG, Zernike

def HoloLG(l, p, w0, LA=0.005, SLM_Pix=(1024, 780), position=(0, 0)):
    maxx = 1
    rate = SLM_Pix[1] / SLM_Pix[0]
    maxy = rate * maxx

    X = np.linspace(-maxx, maxx, SLM_Pix[0]) + position[0]
    Y = np.linspace(-maxy, maxy, SLM_Pix[1]) + position[1]
    dx = np.abs(X[1] - X[2])
    dy = np.abs(Y[1] - Y[2])

    xx, yy = np.meshgrid(X, Y)
    r, phi = cart2pol(xx, yy)
    A = LG(r, phi, l, p, w0)

    return A

def HoloHG(m, n, w0, LA=0.005, SLM_Pix=(1024, 780), position=(0, 0)):
    X = np.linspace(-1, 1, SLM_Pix[0]) + position[0]
    Y = np.linspace(-1, 1, SLM_Pix[1]) + position[1]
    xx, yy = np.meshgrid(X, Y)
    
    A = HG(xx, yy, m, n, w0)
    return A
