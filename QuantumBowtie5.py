#----------------------------------------------------------------------
#     QuantumBowtiePing
#       by KPRoche (Kevin P. Roche) 
#     (c) 2017, 2018  by IBM Corporation
#     Connect to the IBM Quantum Experience site via the QISKIT api functions
#             in qiskit-api-py and run OPENQASM code on the simulator there
#     Display the results using the 8x8 LED array on a SenseHat
#     Spin off the display functions in a separate thread so they can exhibit
#             smooth color changes while "thinking"
#     Use a ping function to try to make sure the website is available before
#             sending requests and thus avoid more hangs that way
#     Move the QASM code into an outside file
#----------------------------------------------------------------------


# import the necessary modules
import sys                             # used to check for passed filename
import os                              # used to find script directory
import requests                        # used for ping
import datetime                        # used to create unique experiment names
from threading import Thread           # used to spin off the display functions
from colorsys import hsv_to_rgb        # used to build the color array
from time import process_time          # used for loop timer
from time import sleep                 # used for delays
from sense_hat import SenseHat         # class for controlling the SenseHat
from IBMQuantumExperience import IBMQuantumExperience  # class for accessing the Quantum Experience API


# some variables we are going to need as we start up

# you must replace the string in the next statement with the Personal Access Token for your Quantum Experience account
myAPItoken="REPLACE_THIS_STRING_WITH_YOUR_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN"

maxpattern='00000'

hat = SenseHat() # instantiating hat right away so we can use it in functions
thinQing=False    # used to tell the display thread when to show the result


#----------------------------------------------------------
# find our experiment file... alternate can be specified on command line
#       use a couple tricks to make sure it is there
#       if not fall back on our default file


scriptfolder = os.path.dirname(os.path.realpath(__file__))
print(sys.argv)
if (len(sys.argv) > 1) and type(sys.argv[1]) is str:
  qasmfilename=sys.argv[1]
else:
  qasmfilename='expt.qasm'
if ('/' not in qasmfilename):
  qasmfilename=scriptfolder+"/"+qasmfilename
if (not os.path.isfile(qasmfilename)):
    qasmfilename=scriptfolder+"/"+'expt.qasm'
    
print("OPENQASM file: ",qasmfilename)
if (not os.path.isfile(qasmfilename)):
    print("QASM file not found... exiting.")
    exit()

#----------------------------------------------------------------------------
# set up a ping function so we can confirm the API can connect before we attempt it
#           ping uses the requests library
#           based on pi-ping by Wesley Archer (raspberrycoulis) (c) 2017
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
#         on the SenseHat
#   the color shift effect is based on the rainbow example included with the SenseHat library
#-------------------------------------------------------------------------------

# pixel coordinates to draw the bowtie qubits
ibm_qx5 = [[40,41,48,49],[8,9,16,17],[28,29,36,37],[6,7,14,15],[54,55,62,63]]


# setting up the 8x8=64 pixel variables for color shifts

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
   for p in range(64):          #first set all pixels off
           pixels[p]=[0,0,0]
   for q in range(5):
      if pattern[q]=='1':         # if the digit is "1" assign blue
         for p in ibm_qx5[q]:
            pixels[p]=[0,0,255]
      else:                       # otherwise assign it red
         for p in ibm_qx5[q]:
            pixels[p]=[255,0,0]

   hat.set_pixels(pixels)         # turn them all on


#--------------------------------------------------
#    blinky lets us use the rainbow rotation code to fill the bowtie pattern
#       it can be interrupted by tapping the joystick or if
#       an experiment ID is provided and the 
#       status returns "DONE"
#
#------------------------------------------------------

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
#    build a class glow so we can launch display control as a thread
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


# Instantiate an instance of our glow class

glowing = glow()

#-------------------------------------------------
#  OK, let's get this shindig started
#-------------------------------------------------

rainbowTie = Thread(target=glowing.run)     # create the display thread
startAPI()                                  # try to connect and instantiate the API 

exptfile = open(qasmfilename,'r') # open the file with the OPENQASM code in it
qasm= exptfile.read()            # read the contents into our experiment string

if (len(qasm)<5):                # if that is too short to be real, exit
    exit
else:                            # otherwise print it to the console for reference
    print("OPENQASM code to send:\n",qasm)
    

backend='simulator'             # specify the simulator as the backend

rainbowTie.start()                          # start the display thread

while True:
   thinQing = True
   p=ping()
   if p==200:
       backend_status = api.backend_status(backend)  # check the availability
       print(backend_status)
       if not backend_status['busy']:
           xpname='Experiment #{:%Y%m%d%H%M%S}'.format(datetime.datetime.now())
           qasms=[{'qasm':qasm}]
           jobs=api.run_job(qasms, backend ,8192,1)  # send the QASM code

           experiment_info=jobs['qasms'][0]
           experimentID=experiment_info['executionId']                     # pull out the experiment ID

           print(experiment_info['status'],experiment_info['executionId'])

           experiment=api.get_result_from_execution(experimentID)     # get the result
           while not experiment:
             experiment=api.get_result_from_execution(experimentID)     # get the result
             if not experiment:
               print(experiment)
             
           if 'measure' in experiment:
             values = experiment['measure']['values']
             labels = experiment['measure']['labels']
             index_max = max( range (len(values)), key=values.__getitem__)
             maxvalue=values[index_max]
             maxpattern=labels[index_max]
             print("Maximum value:",maxvalue, "Maximum pattern:",maxpattern)
             thinQing = False  # this cues the display thread to show the qubits in maxpattern
           else:
             print ('No measure data; waiting to try again')
       else:
            print(backend,'busy; waiting to try again')
   else:
        print(p,'response to ping; waiting to try again')

   goAgain=False                    # wait to do it again
   myTimer=process_time()
   while not goAgain:
      for event in hat.stick.get_events():   
         if event.action == 'pressed':      #somebody tapped the joystick -- go now
            goAgain=True
            blinky(.001)
            hat.set_pixels(pixels)
      if (process_time()-myTimer>10):       # 10 seconds elapsed -- go now
            goAgain=True

