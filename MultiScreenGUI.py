import sys
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QComboBox, QHBoxLayout, QDockWidget, QFormLayout, QDoubleSpinBox, QSpinBox
)
from PyQt5.QtCore import Qt
from functools import partial


## ############################################################################################
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
def HoloLG(l,p,w0,z=(0,5),Z=(1,0,0,0),LA=0.005,maxx=1,SLM_Pix=(1024,780),position=(0,0)):
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


## Generation of a Hermite-Gaussian Hologram
def HoloHG(l,p,w0,z=(0,5),Z=(1,0,0,0),LA=0.005,maxx=1,SLM_Pix=(1024,780),position=(0,0)):
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
    A=HG(xx,yy,l,p,w0)*np.exp(1j*2*np.pi*Z[1]*ZPM)

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




class ArrayDisplay(QMainWindow):
    """
    A window to display content on a specific screen.
    """
    def __init__(self, array, screen_index):
        super().__init__()
        self.setWindowTitle(f'Display Array on Screen {screen_index}')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create a figure and remove axes
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.set_axis_off()
        self.image = self.ax.imshow(array, cmap='gray', aspect='auto')

        # Add matplotlib canvas to PyQt layout
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        # Display fullscreen on the specified screen
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        # Move to the appropriate screen
        screens = QApplication.screens()
        if screen_index < len(screens):
            self.setGeometry(screens[screen_index].geometry())
        else:
            print(f"Screen {screen_index} is not available. Defaulting to primary screen.")

    def update_array(self, new_array):
        """
        Update the displayed array.
        """
        self.image.set_data(new_array)
        self.canvas.draw()


class MultiScreenController(QMainWindow):
    """
    Main GUI for controlling multiple screens.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Screen Display Controller")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.displays = {}
        self.screens = QApplication.screens()
        self.parameters = {
            i: {
                "type": None,
                "gradient": {"direction": "Horizontal", "scale": 1.0},
                "noise": {"mean": 0.5, "std": 0.1},
                "holo_lg": {"l": 0, "p": 0, "w0": 0.2,"LA":0.4,"X":0,"Y":0},
                "holo_hg": {"nn": 0, "m": 0, "w0": 0.2,"LA":0.4,"X":0,"Y":0},
            }
            for i in range(len(self.screens))
        }
        self.config_docks = {}  # Store docks for each screen

        self.init_ui()

    def init_ui(self):
        """
        Initialize the main GUI layout.
        """
        layout = QVBoxLayout(self.central_widget)

        # Add instructions
        instructions = QLabel("Select content for each screen and configure options.")
        layout.addWidget(instructions)

        # Grid for screen content selection
        self.screen_controls = []
        grid_layout = QVBoxLayout()

        for idx, screen in enumerate(self.screens):
            screen_layout = QHBoxLayout()
            label = QLabel(f"Screen {idx}:")
            combobox = QComboBox()
            combobox.addItems(["None", "Random Noise", "Gradient","Laguerre-Gaussian Hologram","Hermite-Gaussian Hologram", "Zeros"])
            combobox.currentIndexChanged.connect(partial(self.update_content, idx, combobox))
            screen_layout.addWidget(label)
            screen_layout.addWidget(combobox)
            self.screen_controls.append(combobox)
            grid_layout.addLayout(screen_layout)

        layout.addLayout(grid_layout)

        # Buttons for Display and Quit
        button_layout = QHBoxLayout()

        #display_button = QPushButton("Display")
        #display_button.clicked.connect(self.display_on_screens)
        #button_layout.addWidget(display_button)

        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.quit_application)
        button_layout.addWidget(quit_button)

        layout.addLayout(button_layout)

        # Initialize docks for each screen
        self.init_config_docks()

    def init_config_docks(self):
        """
        Initialize the configuration dock widgets for all screens.
        """
        for idx in range(len(self.screens)):
            dock = QDockWidget(f"Screen {idx} Configuration", self)
            dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            dock_widget = QWidget()
            dock_layout = QFormLayout(dock_widget)

            # Gradient parameters
            gradient_direction_label = QLabel("Direction:")
            gradient_direction_combo = QComboBox()
            gradient_direction_combo.addItems(["Horizontal", "Vertical"])
            gradient_direction_label.hide()
            gradient_direction_combo.hide()

            gradient_scale_label = QLabel("Scale:")
            gradient_scale_spinbox = QDoubleSpinBox()
            gradient_scale_spinbox.setRange(0.1, 10.0)
            gradient_scale_spinbox.setValue(1.0)
            gradient_scale_spinbox.setSingleStep(0.1)
            gradient_scale_label.hide()
            gradient_scale_spinbox.hide()

            # Random noise parameters
            noise_mean_label = QLabel("Mean:")
            noise_mean_spinbox = QDoubleSpinBox()
            noise_mean_spinbox.setRange(0.0, 1.0)
            noise_mean_spinbox.setValue(0.5)
            noise_mean_spinbox.setSingleStep(0.1)
            noise_mean_label.hide()
            noise_mean_spinbox.hide()

            noise_std_label = QLabel("Std Dev:")
            noise_std_spinbox = QDoubleSpinBox()
            noise_std_spinbox.setRange(0.0, 1.0)
            noise_std_spinbox.setValue(0.1)
            noise_std_spinbox.setSingleStep(0.1)
            noise_std_label.hide()
            noise_std_spinbox.hide()
            
            # Parameters for LG Hologram
            l_label = QLabel("l:")
            l_spinbox = QSpinBox()
            l_spinbox.setRange(-10, 10)
            l_spinbox.setValue(0)
            l_label.hide()
            l_spinbox.hide()

            p_label = QLabel("p:")
            p_spinbox = QSpinBox()
            p_spinbox.setRange(0, 10)
            p_spinbox.setValue(0)
            p_label.hide()
            p_spinbox.hide()

            w0lg_label = QLabel("w0:")
            w0lg_spinbox = QDoubleSpinBox()
            w0lg_spinbox.setRange(0.1, 10.0)
            w0lg_spinbox.setSingleStep(0.05)
            w0lg_spinbox.setValue(0.2)
            w0lg_label.hide()
            w0lg_spinbox.hide()   
            
            LAlg_label = QLabel("LA:")
            LAlg_spinbox = QDoubleSpinBox()
            LAlg_spinbox.setRange(0.1, 1)
            LAlg_spinbox.setSingleStep(0.05)
            LAlg_spinbox.setValue(0.4)
            LAlg_label.hide()
            LAlg_spinbox.hide()
            
            Xlg_label = QLabel("X:")
            Xlg_spinbox = QDoubleSpinBox()
            Xlg_spinbox.setRange(-6, 6)
            Xlg_spinbox.setSingleStep(0.05)
            Xlg_spinbox.setValue(0)
            Xlg_label.hide()
            Xlg_spinbox.hide()  
            
            Ylg_label = QLabel("Y:")
            Ylg_spinbox = QDoubleSpinBox()
            Ylg_spinbox.setRange(-6, 6)
            Ylg_spinbox.setSingleStep(0.05)
            Ylg_spinbox.setValue(0)
            Ylg_label.hide()
            Ylg_spinbox.hide()  
            
            
            # Parameters for HG Hologram
            m_label = QLabel("m:")
            m_spinbox = QSpinBox()
            m_spinbox.setRange(-10, 10)
            m_spinbox.setValue(1)
            m_label.hide()
            m_spinbox.hide()

            n_label = QLabel("p:")
            n_spinbox = QSpinBox()
            n_spinbox.setRange(-10, 10)
            n_spinbox.setValue(0)
            n_label.hide()
            n_spinbox.hide()

            w0hg_label = QLabel("w0:")
            w0hg_spinbox = QDoubleSpinBox()
            w0hg_spinbox.setRange(0.1, 10.0)
            w0hg_spinbox.setValue(0.2)
            w0hg_label.hide()
            w0hg_spinbox.hide()
            
            
            LAhg_label = QLabel("LA:")
            LAhg_spinbox = QDoubleSpinBox()
            LAhg_spinbox.setRange(0.1, 1)
            LAhg_spinbox.setSingleStep(0.05)
            LAhg_spinbox.setValue(0.4)
            LAhg_label.hide()
            LAhg_spinbox.hide()
            
            Xhg_label = QLabel("X:")
            Xhg_spinbox = QDoubleSpinBox()
            Xhg_spinbox.setRange(-6, 6)
            Xhg_spinbox.setSingleStep(0.05)
            Xhg_spinbox.setValue(0)
            Xhg_label.hide()
            Xhg_spinbox.hide()  
            
            Yhg_label = QLabel("Y:")
            Yhg_spinbox = QDoubleSpinBox()
            Yhg_spinbox.setRange(-6, 6)
            Yhg_spinbox.setSingleStep(0.05)
            Yhg_spinbox.setValue(0)
            Yhg_label.hide()
            Yhg_spinbox.hide()  
            

            apply_button = QPushButton("Apply")
            apply_button.clicked.connect(partial(self.apply_parameters, idx))

            dock_layout.addRow(gradient_direction_label, gradient_direction_combo)
            dock_layout.addRow(gradient_scale_label, gradient_scale_spinbox)
            
            dock_layout.addRow(noise_mean_label, noise_mean_spinbox)
            dock_layout.addRow(noise_std_label, noise_std_spinbox)
            
            dock_layout.addRow(l_label, l_spinbox)
            dock_layout.addRow(p_label, p_spinbox)
            dock_layout.addRow(w0lg_label, w0lg_spinbox)
            dock_layout.addRow(LAlg_label, LAlg_spinbox)
            dock_layout.addRow(Xlg_label, Xlg_spinbox)
            dock_layout.addRow(Ylg_label, Ylg_spinbox)
            
            dock_layout.addRow(m_label, m_spinbox)
            dock_layout.addRow(n_label, n_spinbox)
            dock_layout.addRow(w0hg_label, w0hg_spinbox)
            dock_layout.addRow(LAhg_label, LAhg_spinbox)
            dock_layout.addRow(Xhg_label, Xhg_spinbox)
            dock_layout.addRow(Yhg_label, Yhg_spinbox)

            dock_layout.addWidget(apply_button)

            dock.setWidget(dock_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.hide()  # Initially hidden
            self.config_docks[idx] = {
                "dock": dock,
                "gradient_direction_label": gradient_direction_label,
                "gradient_direction_combo": gradient_direction_combo,
                "gradient_scale_label": gradient_scale_label,
                "gradient_scale_spinbox": gradient_scale_spinbox,
                "noise_mean_label": noise_mean_label,
                "noise_mean_spinbox": noise_mean_spinbox,
                "noise_std_label": noise_std_label,
                "noise_std_spinbox": noise_std_spinbox,
                
                "l_label": l_label,
                "l_spinbox": l_spinbox,
                "p_label": p_label,
                "p_spinbox": p_spinbox,
                "w0lg_label": w0lg_label,
                "w0lg_spinbox": w0lg_spinbox,
                "LAlg_label": LAlg_label,
                "LAlg_spinbox": LAlg_spinbox,
                "Xlg_label": Xlg_label,
                "Xlg_spinbox": Xlg_spinbox,       
                "Ylg_label": Ylg_label,
                "Ylg_spinbox": Ylg_spinbox,                   
                
                "m_label": m_label,
                "m_spinbox": m_spinbox,
                "n_label": n_label,
                "n_spinbox": n_spinbox,
                "w0hg_label": w0hg_label,
                "w0hg_spinbox": w0hg_spinbox,
                "LAhg_label": LAhg_label,
                "LAhg_spinbox": LAhg_spinbox,
                "Xhg_label": Xhg_label,
                "Xhg_spinbox": Xhg_spinbox,       
                "Yhg_label": Yhg_label,
                "Yhg_spinbox": Yhg_spinbox,    
            }

    def update_content(self, screen_index, combobox):
        """
        Update the content of the specified screen based on dropdown selection.
        """
        content_type = combobox.currentText()
        self.parameters[screen_index]["type"] = content_type

        config = self.config_docks[screen_index]
        dock = config["dock"]

        # Show or hide relevant labels and fields based on content type
        if content_type == "Gradient":
            config["gradient_direction_label"].show()
            config["gradient_direction_combo"].show()
            config["gradient_scale_label"].show()
            config["gradient_scale_spinbox"].show()
            
            config["noise_mean_label"].hide()
            config["noise_mean_spinbox"].hide()
            config["noise_std_label"].hide()
            config["noise_std_spinbox"].hide()
            
            config["l_label"].hide()
            config["l_spinbox"].hide()
            config["p_label"].hide()
            config["p_spinbox"].hide()
            config["w0lg_label"].hide()
            config["w0lg_spinbox"].hide()
            config["LAlg_label"].hide()
            config["LAlg_spinbox"].hide()
            config["Xlg_label"].hide()
            config["Xlg_spinbox"].hide()
            config["Ylg_label"].hide()
            config["Ylg_spinbox"].hide()
            
            config["m_label"].hide()
            config["m_spinbox"].hide()
            config["n_label"].hide()
            config["n_spinbox"].hide()
            config["w0hg_label"].hide()
            config["w0hg_spinbox"].hide()
            config["LAhg_label"].hide()
            config["LAhg_spinbox"].hide()
            config["Xhg_label"].hide()
            config["Xhg_spinbox"].hide()
            config["Yhg_label"].hide()
            config["Yhg_spinbox"].hide()
            dock.show()
            
        elif content_type == "Random Noise":
            config["gradient_direction_label"].hide()
            config["gradient_direction_combo"].hide()
            config["gradient_scale_label"].hide()
            config["gradient_scale_spinbox"].hide()
            
            config["noise_mean_label"].show()
            config["noise_mean_spinbox"].show()
            config["noise_std_label"].show()
            config["noise_std_spinbox"].show()
            
            config["l_label"].hide()
            config["l_spinbox"].hide()
            config["p_label"].hide()
            config["p_spinbox"].hide()
            config["w0lg_label"].hide()
            config["w0lg_spinbox"].hide()
            config["LAlg_label"].hide()
            config["LAlg_spinbox"].hide()
            config["Xlg_label"].hide()
            config["Xlg_spinbox"].hide()
            config["Ylg_label"].hide()
            config["Ylg_spinbox"].hide()
            
            config["m_label"].hide()
            config["m_spinbox"].hide()
            config["n_label"].hide()
            config["n_spinbox"].hide()
            config["w0hg_label"].hide()
            config["w0hg_spinbox"].hide()
            config["LAhg_label"].hide()
            config["LAhg_spinbox"].hide()
            config["Xhg_label"].hide()
            config["Xhg_spinbox"].hide()
            config["Yhg_label"].hide()
            config["Yhg_spinbox"].hide()
            dock.show()
            
        elif content_type == "Laguerre-Gaussian Hologram":
            config["gradient_direction_label"].hide()
            config["gradient_direction_combo"].hide()
            config["gradient_scale_label"].hide()
            config["gradient_scale_spinbox"].hide()
            
            config["noise_mean_label"].hide()
            config["noise_mean_spinbox"].hide()
            config["noise_std_label"].hide()
            config["noise_std_spinbox"].hide()
            
            config["l_label"].show()
            config["l_spinbox"].show()
            config["p_label"].show()
            config["p_spinbox"].show()
            config["w0lg_label"].show()
            config["w0lg_spinbox"].show()
            config["LAlg_label"].show()
            config["LAlg_spinbox"].show()
            config["Xlg_label"].show()
            config["Xlg_spinbox"].show()
            config["Ylg_label"].show()
            config["Ylg_spinbox"].show()
            
            config["m_label"].hide()
            config["m_spinbox"].hide()
            config["n_label"].hide()
            config["n_spinbox"].hide()
            config["w0hg_label"].hide()
            config["w0hg_spinbox"].hide()
            config["LAhg_label"].hide()
            config["LAhg_spinbox"].hide()
            config["Xhg_label"].hide()
            config["Xhg_spinbox"].hide()
            config["Yhg_label"].hide()
            config["Yhg_spinbox"].hide()
            dock.show()
            
        elif content_type == "Hermite-Gaussian Hologram":
            config["gradient_direction_label"].hide()
            config["gradient_direction_combo"].hide()
            config["gradient_scale_label"].hide()
            config["gradient_scale_spinbox"].hide()
            
            config["noise_mean_label"].hide()
            config["noise_mean_spinbox"].hide()
            config["noise_std_label"].hide()
            config["noise_std_spinbox"].hide()
            
            config["m_label"].show()
            config["m_spinbox"].show()
            config["n_label"].show()
            config["n_spinbox"].show()
            config["w0hg_label"].show()
            config["w0hg_spinbox"].show()
            config["LAhg_label"].show()
            config["LAhg_spinbox"].show()
            config["Xhg_label"].show()
            config["Xhg_spinbox"].show()
            config["Yhg_label"].show()
            config["Yhg_spinbox"].show()
            
            config["l_label"].hide()
            config["l_spinbox"].hide()
            config["p_label"].hide()
            config["p_spinbox"].hide()
            config["w0lg_label"].hide()
            config["w0lg_spinbox"].hide()
            config["LAlg_label"].hide()
            config["LAlg_spinbox"].hide()
            config["Xlg_label"].hide()
            config["Xlg_spinbox"].hide()
            config["Ylg_label"].hide()
            config["Ylg_spinbox"].hide()
            dock.show()
        else:
            dock.hide()

        self.update_display(screen_index)

    def apply_parameters(self, screen_index):
        """
        Apply parameters from the configuration dock for a specific screen.
        """
        config = self.config_docks[screen_index]
        content_type = self.parameters[screen_index]["type"]

        if content_type == "Gradient":
            self.parameters[screen_index]["gradient"] = {
                "direction": config["gradient_direction_combo"].currentText(),
                "scale": config["gradient_scale_spinbox"].value(),
            }
        elif content_type == "Random Noise":
            self.parameters[screen_index]["noise"] = {
                "mean": config["noise_mean_spinbox"].value(),
                "std": config["noise_std_spinbox"].value(),
            }
        elif content_type == "Laguerre-Gaussian Hologram":
            self.parameters[screen_index]["holo_lg"] = {
                "l": config["l_spinbox"].value(),
                "p": config["p_spinbox"].value(),
                "w0": config["w0lg_spinbox"].value(),
                "LA": config["LAlg_spinbox"].value(),
                "X": config["Xlg_spinbox"].value(),
                "Y": config["Ylg_spinbox"].value(),
            }
        elif content_type == "Hermite-Gaussian Hologram":
            self.parameters[screen_index]["holo_hg"] = {
                "nn": config["n_spinbox"].value(),
                "m": config["m_spinbox"].value(),
                "w0": config["w0hg_spinbox"].value(),
                "LA": config["LAhg_spinbox"].value(),
                "X": config["Xhg_spinbox"].value(),
                "Y": config["Yhg_spinbox"].value(),
            }
        self.update_display(screen_index)

    def generate_gradient(self, params, resolution=(1080, 1920)):
        """
        Generate a gradient based on the provided parameters.
        """
        scale = params["scale"]
        if params["direction"] == "Horizontal":
            return np.linspace(0, scale, resolution[1])[None, :] * np.ones((resolution[0], 1))
        else:
            return np.linspace(0, scale, resolution[0])[:, None] * np.ones((1, resolution[1]))

    def generate_random_noise(self, params, resolution=(1080, 1920)):
        """
        Generate random noise based on the provided parameters.
        """
        mean = params["mean"]
        std = params["std"]
        return np.random.normal(mean, std, resolution)
    
    def generate_holo_lg(self, params, resolution=(1080, 1920)):
        """
        Generate a Laguerre-Gaussian hologram based on the provided parameters.
        """
        l = params["l"]
        p = params["p"]
        w0 = params["w0"]
        La=params["LA"]
        pos=(-params["X"],params["Y"])
        return HoloLG(l, p, w0,LA=La/100, SLM_Pix=resolution,position=pos)

    def generate_holo_hg(self, params, resolution=(1080, 1920)):
        """
        Generate a Laguerre-Gaussian hologram based on the provided parameters.
        """
        n = params["nn"]
        m = params["m"]
        w0 = params["w0"]
        La=params["LA"]
        pos=(-params["X"],params["Y"])
        return HoloHG(n, m, w0, LA=La/100, SLM_Pix=resolution,position=pos)

    def update_display(self, screen_index):
        """
        Update the display for the specified screen based on the current parameters.
        """
        content_type = self.parameters[screen_index]["type"]
        step1 = self.screens[screen_index]
        resolution=(step1.geometry().height(),step1.geometry().width())
        resolution2=(step1.geometry().width(),step1.geometry().height())
        array = None

        if content_type == "Gradient":
            array = self.generate_gradient(self.parameters[screen_index]["gradient"], resolution)
        elif content_type == "Laguerre-Gaussian Hologram":
            array = self.generate_holo_lg(self.parameters[screen_index]["holo_lg"], resolution2)
        elif content_type == "Hermite-Gaussian Hologram":
            array = self.generate_holo_hg(self.parameters[screen_index]["holo_hg"], resolution2)
        elif content_type == "Random Noise":
            array = self.generate_random_noise(self.parameters[screen_index]["noise"], resolution)
        elif content_type == "Zeros":
            array = np.zeros(resolution)

        if array is not None:
            self.show_screen(screen_index, array)

    def show_screen(self, screen_index, array):
        """
        Show or update the screen with the given content.
        """
        if screen_index in self.displays:
            self.displays[screen_index].update_array(array)
        else:
            display = ArrayDisplay(array, screen_index=screen_index)
            self.displays[screen_index] = display

    def display_on_screens(self):
        """
        Display content on all screens based on user selections.
        """
        for idx, combobox in enumerate(self.screen_controls):
            self.update_content(idx, combobox)

    def quit_application(self):
        """
        Close all open windows and quit the application.
        """
        for display in self.displays.values():
            display.close()
        self.close()
        QApplication.quit()


def main():
    """
    Main function to run the application.
    """
    app = QApplication.instance()  # Use existing QApplication instance if running in Spyder
    if app is None:
        app = QApplication(sys.argv)
    controller = MultiScreenController()
    controller.show()
    app.exec_()  # Do not use sys.exit(app.exec_())

if __name__ == "__main__":
    main()
