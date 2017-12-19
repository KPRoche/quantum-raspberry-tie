import requests
import sys
import datetime
import socket
from threading import Thread
from colorsys import hsv_to_rgb
from time import process_time
from time import sleep
from sense_hat import SenseHat
from IBMQuantumExperience import IBMQuantumExperience

# some variables we are going to need as we start up
# you must replace the string in the next statement with the Personal Access Token for your Quantum Experience account
myAPItoken="INSERT_YOUR_IBM_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN_HERE"
maxpattern='00000'
hat = SenseHat() # creating hat early so we can use it in functions
thinQing=False    # used to tell the display thread when to show the result

#----------------------------------------------------------------------------
# set up a ping function so we can confirm the API can connect before we attempt it
#           ping uses the requests library
#           based on pi-ping by Wesley Archer (raspberrycoulis)
#           https://github.com/raspberrycoulis/Pi-Ping
#----------------------------------------------------------------------------
def ping(website='https://quantumexperience.ng.bluemix.net',repeats=1,wait=0.5,verbose=False):
  msg = 'ping response'
  for n in range(repeats):
    response = requests.get(website)
    if int(response.status_code) == 200: # OK
        pass
    elif int(response.status_code) == 500: # Internal server error
        msg ='Internal server error'
    elif int(response.status_code) == 503: # Service unavailable
        msg = 'Service unavailable'
    elif int(response.status_code) == 502: # Bad gateway
        msg = 'Bad gateway'
    elif int(response.status_code) == 520: # Cloudflare: Unknown error
        msg = 'Cloudflare: Unknown error'
    elif int(response.status_code) == 522: # Cloudflare: Connection timed out
        msg = 'Cloudflare: Connection timed out'
    elif int(response.status_code) == 523: # Cloudflare: Origin is unreachable
        msg = 'Cloudflare: Origin is unreachable'
    elif int(response.status_code) == 524: # Cloudflare: A Timeout occurred
        msg = 'Cloudflare: A Timeout occurred'
    if verbose: print(response.status_code,msg)
    if repeats>1: time.sleep(wait)
    
  return int(response.status_code)
# end DEF ----------------------------------------------------------------

# ------------------------------------------------------------------------
#  try to start our API connection to IBM QE
#       Here we attempt to ping the IBM Quantum Experience website. If no response, we exit
#       If we get a 200 response, the site is live and we initialize our connection to it
#-------------------------------------------------------------------------------
def startAPI():
    global api
    print ('Pinging IBM Quantum Experience before start')
    p=ping('https://quantumexperience.ng.bluemix.net',1,0.5,True)

    if p==200:
        api = IBMQuantumExperience(myAPItoken)
    else:
        exit()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------    
#   These variables and functions are for lighting up the "bowtie" display
#           SenseHat
#   the color shift effect is based on the rainbow example in the sensehat library
#-------------------------------------------------------------------------------
# pixel coordinates to draw the bowtie qubits
ibm_qx5 = [[40,41,48,49],[8,9,16,17],[28,29,36,37],[6,7,14,15],[54,55,62,63]]


# setting up the 8x8=64 pixel variables

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

# scale lets us do a simple color rotation of hues and convert it to RGB in pixels

def scale(v):
    return int(v * 255)

def resetrainbow(show=False):
   global pixels,hues
   pixels = [hsv_to_rgb(h, 1.0, 1.0) for h in hues]
   pixels = [(scale(r), scale(g), scale(b)) for r, g, b in pixels]
   if (show): hat.set_pixels(pixels)

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

#------------------------------------------------
#  now that the light pattern functions are defined,
#    build a class so we can launch display control as a thread
#------------------------------------------------
class glow():
   global thinQing,hat, maxpattern
   def __init__(self):
      self._running = True
      
   def stop(self):
      self._running = False
      self._stop = True

   def run(self):
      #thinQing=False
      while self._running:
         if thinQing:
            blinky(.1)
         else:
            showqubits(maxpattern)

glowing = glow()

#-------------------------------------------------
#  OK, let's get this shindig started
#-------------------------------------------------

rainbowTie = Thread(target=glowing.run)
startAPI()

qasm='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[5];\ncreg c[5];\nh q[0];\nh q[1];\nh q[2];\nh q[3];\nh q[4];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\nmeasure q[2] -> c[2];\nmeasure q[3] -> c[3];\nmeasure q[4] -> c[4];\n'
backend='simulator'

rainbowTie.start()
while True:
   thinQing = True
   p=ping()
   if p==200:
       backend_status = api.backend_status(backend)
       print(backend_status)
       if not backend_status['busy']:
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
           print("Maximum value:",maxvalue, "Maximum pattern:",maxpattern)
           thinQing = False  # this cues the display thread to show the qubits in maxpattern
       else:
            print(backend,'busy; waiting to try again')
   else:
        print(p,'response to ping; waiting to try again')

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
