import numpy as np
import matplotlib.pyplot as plt
import math

#################################################################################################

##############################################################################################
# Hologram
####################################################################lo##########################


# Generation of holograms for almost whatever you want
def Hologram(A,hx,hy,LA):
    # A -> Complex amplitude of the beam
    # hx, hy
  # Normalization of the input beam

  nn=np.sum(np.abs(A)**2)*hx*hy
  NU=A/np.sqrt(nn)

  # Amplitude and phase pattern
  Amp=np.abs(NU)
  PHI=np.angle(NU)

  # Grating
  mm=Amp.shape
  x1,y1=np.meshgrid(hx*np.arange(1,mm[1]+1),hy*np.arange(1,mm[0]+1))

  # Inverse Sinc fucntion
  ss=np.linspace(-np.pi,0,2000)
  sincc=np.sin(ss)/ss
  sincc[np.isnan(sincc)]=1

  # Amplitude masking
  M=1+np.interp(Amp,sincc,ss)/np.pi
  M[np.isnan(M)]=0


  # Phase Hologram
  F=np.mod(PHI-np.pi*M+x1/LA,2*np.pi)

  # Full Hologram
  return M*F



## Generation of a Laguerre-Gaussian Hologram
def HoloLG(l,p,w0,z=(0,5),Z=(1,0,0,0),LA=0.09,maxx=1,SLM_Pix=(1024,780),position=(0,0)):
    rate=SLM_Pix[1]/SLM_Pix[0] # Assuming squared pixels
    maxy=rate*maxx; #Scaling of the Y axis

    # Space definition + displacements
    X=np.linspace(-maxx,maxx,SLM_Pix[0])+position[0];
    Y=-np.linspace(-maxy,maxy,SLM_Pix[1])+position[1];

    # Relevant stuff
    dx=np.abs(X[1]-X[2]);
    dy=np.abs(Y[1]-Y[2]);
    xx,yy=np.meshgrid(X,Y);
    r, phi= cart2pol(xx,yy)

    # Zernike Polynomial mask - Zorro no te lo lleves!
    ZPM=Zernike(r/Z[0],phi,Z[2],Z[3])

    # LG beam including the Zernike Polynomial stuff
    A=LG(r,phi,l,p,w0)*np.exp(1j*2*np.pi*Z[1]*ZPM)

    # Propagating the shit out of me :)
    if z[0]>0:
        # Propagation space
        ZZ=np.linspace(0,z[0],z[1])

        # Propagation steps
        dz=np.abs(ZZ[0]-ZZ[1])

        # Saving the field at every plane
        F=[A]

        for ii in range(0,z[1]):
            A=propTF(A,2*maxx,1,dz) # Field at plane z->z_0
            F.append(A)

    # Generation of the Hologram
    return(Hologram(A,dx,dy,LA))




##############################################################################################
# Zernike Polynomials
##############################################################################################


# Coeffcients and powers or the radial Polynomials
def RR(m,n):
  coeff=[]
  pow=[]
  if (n-m)%2==0:
    for kk in range(0,int(((n-m)/2+1))):
      aa=((-1)**kk*math.factorial(int(n-kk)))/(math.factorial(int(kk))*math.factorial(int((n+m)/2-kk))*math.factorial(int((n-m)/2-kk)))
      bb=n-2*kk
      coeff.append(aa)
      pow.append(bb)
  else:
    coeff.append(0)
    pow.append(0)
  return([coeff,pow])

# Construction of the polynomial
def Zernike(RHO,PHI,m,n):
  ZR=np.zeros(RHO.shape);
  rn=RR(np.abs(m),n)

  for ii in range(len(rn[0])):
    ZR=ZR+rn[0][ii]*RHO**rn[1][ii]

  if m>=0:
    Z=ZR*np.cos(np.abs(m)*PHI)
  else:
    Z=ZR*np.sin(np.abs(m)*PHI)
  M=(RHO<=1)
  P=Z*M
  P=(P-np.min(P))/np.max(P-np.min(P))
  return(P)


##############################################################################################
# Numerical implementation of the Special functions
##############################################################################################


# Numerical Implementation of the Laguerre Polynomials
def NlaguerreL(n,a,X):
  LL=0
  for m in range(n+1):
    LL=LL+((-1)**m)*(math.factorial(n+a))/(math.factorial(n-m)*math.factorial(a+m)*math.factorial(m))*(X**m);
  return(LL)

# Laguerre-Gaussian Beam where ell and p are the azimuthal and radial indexes, respectively
def LG(RHO,PHI,ell,p,w0):
    C=np.sqrt((2*math.factorial(p))/(np.pi*math.factorial(p+np.abs(ell))))*(1/w0)
    return(C*np.exp(-(RHO/w0)**2)*((np.sqrt(2)*RHO/w0)**np.abs(ell))*np.exp(1j*ell*PHI)*NlaguerreL(p,np.abs(ell),2*(RHO/w0)**2))

#Numerical definition of the Hermite Polynomials
def NHermite(n,X):
    Hn1=np.ones(X.shape);
    H=2*X;
    if n<0:
        print('The index must be 0 or positive')
    elif n==0:
        H=Hn1;
    elif n==1:
        H=H;
    else:
        for nn in range(2,n+1):
            Hn=2*X*H-2*(nn-1)*Hn1;
            Hn1=H;
            H=Hn;
    return(H)

# Hermite Gaussian beam where m and ell are the orders in the x and y direction, respectively
def HG(X,Y,m,n,w0):
    h=np.abs(X[0,0]-X[0,1])
    a=NHermite(m,np.sqrt(2)*X/w0)*NHermite(n,np.sqrt(2)*Y/w0)*np.exp(-(X**2+Y**2)/w0**2)
    N=np.sum(h*h*np.abs(a)**2)
    a=a/np.sqrt(N)
    return(a)

##############################################################################################
# Propagating my dreams a tiny step at the time
##############################################################################################

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
  Yd,Xd=u1.shape
  dx=Lx/Xd
  dy=Ly/Yd
  fx=np.arange(-1/(2*dx),1/(2*dx),1/Lx)
  fy=np.arange(-1/(2*dy),1/(2*dy),1/Ly)
  Fx, Fy = np.meshgrid(fx, fy)
  #print(Fx.shape)
  #print(u1.shape)

  H=np.exp(-1j*np.pi*0.25*la*z*(Fx**2+Fy**2))


  U2=H*np.fft.fftshift(np.fft.fft2(u1))

  u2=np.fft.ifft2(np.fft.ifftshift(U2))
  return u2



##############################################################################################
# Manuel's toolbox for lazy people
##############################################################################################

# Cartesian to Polar coordinates
def cart2pol(x, y):
  rho = np.sqrt(x**2 + y**2)
  phi = np.arctan2(y, x)
  return(rho, phi)


# Chopping as in Mathematica
def Chop(A):
    return(np.real(A)*(np.abs(np.real(A)>1e-8))+np.imag(A)*(np.abs(np.imag(A)>1e-8)))


##############################################################################################
# SLM code 
##############################################################################################
##############################################################################################
# SLM code 
##############################################################################################
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import threading

class ArrayDisplay(QMainWindow):
    def __init__(self, array):
        super().__init__()

        self.setWindowTitle('Display Array on Second Screen')

        # Create a central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create a figure and a subplot without margins
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.set_axis_off()
        self.image = self.ax.imshow(array, cmap='gray', aspect='auto')

        # Convert the matplotlib figure to a PyQt canvas
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        # Set full screen on the second monitor and make it borderless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        # Move to the second screen if available
        screen_count = QApplication.screens()
        if len(screen_count) > 1:
            screen = QApplication.screens()[1]
            self.setGeometry(screen.geometry())

    def update_array(self, new_array):
        self.image.set_data(new_array)
        self.canvas.draw()

def console_input_thread(display):
    try:
        while True:
            command = input("Enter 'quit' to exit: ")
            if command == 'quit':
                QApplication.quit()
                break
    except KeyboardInterrupt:
        QApplication.quit()
        print("Application exited")

def main():
    app = QApplication(sys.argv)
    B=QApplication.screens()[1]
    initial_array = HoloLG(1,0,0.5,LA=0.01,maxx=3,SLM_Pix=(1920,1080),position=(-0.7,0))
    display = ArrayDisplay(initial_array)

    # Start the console input thread
    input_thread = threading.Thread(target=console_input_thread, args=(display,))
    input_thread.daemon = True
    input_thread.start()

    # Run the PyQt application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


########## 