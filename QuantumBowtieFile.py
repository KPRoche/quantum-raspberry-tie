#----------------------------------------------------------------------
#     QuantumBowtie
#       by KPRoche (Kevin P. Roche) (c) 2017
#
#     Connect to the IBM Quantum Experience site via the QISKIT api functions
#             in qiskit-api-py and run OPENQASM code on the simulator there
#     Display the results using the 8x8 LED array on a SenseHat
#     Spin off the display functions in a separate thread so they can exhibit
#             smooth color changes while "thinking"
#----------------------------------------------------------------------


# import the necessary modules

import datetime                        # used to create unique experiment names
from threading import Thread           # used to spin off the display functions
from colorsys import hsv_to_rgb        # used to build the color array
from time import process_time          # used for loop timer
from time import sleep                 # used for delays
from sense_hat import SenseHat         # class for controlling the SenseHat
from IBMQuantumExperience import IBMQuantumExperience  # class for accessing the Quantum Experience API

# some variables we are going to need as we start up

maxpattern='00000'
hat = SenseHat()      # instantiate the interface to the SenseHat

# create a connection to the Quantum Experience
# you must replace the string in the next statement with the Personal Access Token for your Quantum Experience account
api = IBMQuantumExperience("a24ffaabe0cb6d8f2d772a05c1f536e8142de1c6c4a96fa8b5f5dd9fea586c8356440da5d7bb50b4354a3355d600029828f44dcf35fe08187403fbb5b9274f0f")api = IBMQuantumExperience("REPLACE_THIS_STRING_WITH_YOUR_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN")

#-----------------------------------------------------------------------
#             functions and variables for the LED display on the SenseHat
#               color rotation code based on the rainbow.py example included
#               with the Sensehat library
#-----------------------------------------------------------------------

hues = [
    0.00, 0.00, 0.06, 0.13, 0.20, 0.27, 0.34, 0.41,
    0.00, 0.06, 0.13, 0.21, 0.28, 0.35, 0.42, 0.49,
    0.07, 0.14, 0.21, 0.28, 0.35, 0.42, 0.50, 0.57,
    0.15, 0.22, 0.29, 0.36, 0.43, 0.50, 0.57, 0.64,
    0.22, 0.29, 0.36, 0.44, 0.51, 0.58, 0.65, 0.72,
    0.30, 0.37, 0.44, 0.51, 0.58, 0.66, 0.73, 0.80,
    0.38, 0.45, 0.52, 0.59, 0.66, 0.73, 0.80, 0.87,
    0.45, 0.52, 0.60, 0.67, 0.74, 0.81, 0.88, 0.95,
    ]
pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]

thinqing=False

# pixel coordinates to draw the bowtie qubits
ibm_qx5 = [[40,41,48,49],[8,9,16,17],[28,29,36,37],[6,7,14,15],[54,55,62,63]]

def scale(v):
    return int(v * 255)

def resetrainbow(show=False):
   global pixels,hues
   pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
   pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
   if (show): hat.set_pixels(pixels)

#-------------------------------------------------------------
#     blinky
#        function to rotate rainbow colors through the "bowtie"
#         on the display
#        interruptible by joystick action or (if identifier provided)
#           DONE status for an experiment at IBM Quantum Experience
#--------------------------------------------------------------

def blinky(time=10,experimentID=''):
   global pixels,hues,experiment
   #resetrainbow()
   count=0
   GoNow=False
   while ((count*.02<time) and (not GoNow)):
      # Rotate the hues
      hues = [(h + 0.01) % 1.0 for h in hues]
      # Convert the hues to RGB values
      pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
      # hsv_to_rgb returns 0..1 floats; convert to ints in the range 0..255
      pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
      for p in range(64):
         if p in sum(ibm_qx5,[]):
            pass
         else:
            pixels[p]=[0,0,0]
      if (experimentID!=''):
         status =api.get_execution(experimentID)
         if (status['status']['id']=='DONE'):
            GoNow=True
      # Update the display
      hat.set_pixels(pixels)
      sleep(0.002)
      count+=1
      for event in hat.stick.get_events():
         if event.action == 'pressed':
            goNow=True

#-------------------------------------------------------
#         showqubits
#            function to display a 5-qubit measurement based on a string
#               of '1's and '0's
#-------------------------------------------------------
def showqubits(pattern='00000'):
   global hat
  
   for p in range(64):          # assign them all to off
           pixels[p]=[0,0,0]

   for q in range(5):
      if pattern[q]=='1':       # if it's a 1 in the string set to blue
         for p in ibm_qx5[q]:
            pixels[p]=[0,0,255]
      else:
         for p in ibm_qx5[q]:   # otherwise set to red
            pixels[p]=[255,0,0]

   hat.set_pixels(pixels)


#-------------------------------------------------------
# create a class "Glow" so we can run blinky in a separate thread
class glow():
   global thinqing,hat, maxpattern
   def __init__(self):
      self._running = True
      
   def stop(self):
      self._running = False
      self._stop = True

   def run(self):
      #thinqing=False
      while self._running:
         if thinqing:
            blinky(.1)
         else:
            showqubits(maxpattern)

#-----------------------------------------------------------------------

# Now we're ready to go

glowing = glow()   #instantiate an instance of the glow class

rainbowTie = Thread(target=glowing.run) # make a thread out of it

exptfile = open('expt.qasm','r') # open the file with the OPENQASM code in it
qasm= exptfile.read()            # read the contents into our experiment string

if (len(qasm)<5):                # if that is too short to be real, exit
    exit
else:                            # otherwise print it to the console for reference
    print("OPENQASM code to send:\n",qasm)
    
backend='simulator'              # select the simulation backend

rainbowTie.start()               #spin off the display thread

while True:
   thinqing = True
   print(api.backend_status(backend))
   xpname='Experiment #{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
   experiment=api.run_experiment(qasm, backend ,10,xpname,0)
   experimentID=experiment['idExecution']
   print('Running experiment',experiment['idExecution'])
   experiment=api.get_result_from_execution(experimentID)
   values = experiment['measure']['values']
   labels = experiment['measure']['labels']
   index_max = max( range (len(values)), key=values.__getitem__)
   maxvalue=values[index_max]
   maxpattern=labels[index_max]
   #print(experiment['status'])
   print("Maximum value:",maxvalue)
   print("Maximum pattern:",maxpattern)
   thinqing = False

   goAgain=False            #once we've run an experiment, wait 10 seconds or until the joystick is tapped
   myTimer=process_time()
   while not goAgain:
      for event in hat.stick.get_events():
         if event.action == 'pressed':
            goAgain=True
            blinky(.001)
            hat.set_pixels(pixels)
      if (process_time()-myTimer>10):
            goAgain=True

