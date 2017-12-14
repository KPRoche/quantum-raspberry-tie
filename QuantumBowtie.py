#--------------------------------------------------------------------
#
#            QuantumBowtiePing.py
#             by KPRoche (Kevin Roche)
#             first uploaded December 14, 2017
#
#             Run a simple OPENQASM experiment on the IBM Quantum Experience processor
#               and display the results on the 8x8 LED array on a SenseHat
#
#---------------------------------------------------------------------

import datetime
from threading import Thread
from colorsys import hsv_to_rgb
from time import process_time
from time import sleep
from sense_hat import SenseHat
from IBMQuantumExperience import IBMQuantumExperience
maxpattern='00000'
hat = SenseHat()
api = IBMQuantumExperience("REPLACE_THIS_STRING_WITH_YOUR_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN")
global glowStop
def scale(v):
    return int(v * 255)
# pixel coordinates to draw the bowtie qubits
ibm_qx5 = [[40,41,48,49],[8,9,16,17],[28,29,36,37],[6,7,14,15],[54,55,62,63]]
bowtie = [6,7,8,9,14,15,16,17,28,29,36,37,54,55,40,41,48,49,62,63]
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

def resetrainbow(show=False):
   global pixels,hues
   pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
   pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
   if (show): hat.set_pixels(pixels)

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
         if p in bowtie:
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


glowing = glow()

rainbowTie = Thread(target=glowing.run)


   



def showqubits(pattern='00000'):
   global hat
  
   for p in range(64):
           pixels[p]=[0,0,0]

   for q in range(5):
      if pattern[q]=='1':
         for p in ibm_qx5[q]:
            pixels[p]=[0,0,255]
      else:
         for p in ibm_qx5[q]:
            pixels[p]=[255,0,0]

   hat.set_pixels(pixels)





qasm='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[5];\ncreg c[5];\nh q[0];\nh q[1];\nh q[2];\nh q[3];\nh q[4];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];\nmeasure q[3] -> c[3];\nmeasure q[4] -> c[4];\n'
backend='simulator'

rainbowTie.start()
while True:
   thinqing = True
   print(api.backend_status(backend))
   xpname='Experiment #{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
   experiment=api.run_experiment(qasm, backend ,10,xpname,0)
   experimentID=experiment['idExecution']
   print('Running experiment',experiment['idExecution'])

   #blinky(25,experimentID)
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
#   rainbowTie.stop()
#   showqubits(maxpattern)

   goAgain=False
   myTimer=process_time()
   while not goAgain:
      for event in hat.stick.get_events():
         if event.action == 'pressed':
            goAgain=True
            blinky(.001)
            hat.set_pixels(pixels)
      if (process_time()-myTimer>10):
            goAgain=True

