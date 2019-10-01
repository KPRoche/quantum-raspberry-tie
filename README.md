# quantum-raspberry-tie
Your Raspberry Pi running code on the IBM Q quantum processors via Python 3 -- with results displayed courtesy of the 8x8 LED array on a SenseHat!
## Second Release: Adaptive to version of Qiskit installed (v2.1 added comms stall exception handling)

### (Update from First Release: New Version uses full qiskit library, detects orientation)

This code is specifically designed to run on a Raspberry Pi 3 with the SenseHat installed. The 8x8 array on the SenseHat is used to display the results.
If the Pi is held with on edge, the accelerometer is used to determine which edge is "up" and orients the qubit display accordingly (default is "up" equals towards the HDMI and USB power in ports).
This version asseses the QASM program being loaded and selects either a 5-qubit or 16-qubit display accordingly. The default is to load and run a 5-qubit random number-generating program.

The 5-qubit display formats output in a manner corresponding to the IBM 5-qubit "bowtie" quantum processor.
<br/><img src='ibm_qubit_cpu.jpg' width='200' alt='IBM 5 qubit processor' style='float:left;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src='RaspberryTieOutput.png' width='200' alt='Output displayed on the SenseHat' style='float:right;'><br/> 
(It's called a bowtie because of the arrangement of the 5 qubits, and the particular ways they can interconnect via entanglement. Each of those rectangles touched by a squiggly line in the image on the left holds a qubit.)

The 16 qubit display corresponds to a 16-qubit processor
<br /><img src='ibm_16_qubit_processor-100722935-large.3x2.jpg' width='200' alt='IBM 16 qubit processor' style='float:left;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src='16-bitRpi-result.JPG' width='200' alt='16 qubit Output displayed on the SenseHat' style='float:right;'><br/>

Actual calculations are run using the quantum simulator backend for the quantum processor, to avoid overwhelming the physical processor in the IBM Q lab.

The programs can trigger a shutdown of the Raspberry Pi by means of pressing and holding the SenseHat Joystick button straight down. This is very useful when running as a headless demo from battery, as it provides a means of safely shutting down the Pi and avoiding SD card damage even without a screen and input device.

# Installation

## Prerequisites
You will need a Raspberry Pi 3 running at least the _Jessie_ release of Raspbian, with a SenseHat* hat properly installed.  
**Note** I found it much easier to get working reliably by doing a fresh install of Raspbian Stretch (or Buster) and going from there.  
If your processor did not come with the SenseHat libraries pre-installed, you must install them.
     https://www.raspberrypi.org/documentation/hardware/sense-hat/
     
Alternatively, you can install the SenseHat EMULATOR libraries instead, and simulate the SenseHat display on the emulator.
     https://sense-emu.readthedocs.io/en/v1.1/install.html
If you use the emulator libraries, you will need to start the emulator before running your code, go into the preferences and set the Inertial Measurement Unit simulation to be **on**
     
Your Raspberry Pi must have an active internet connection for the API to function properly
     
You will need to install the **qiskit library**
     https://github.com/QISKit/
     
**IMPORTANT:** this new version does require the complete QISKit library, not the simpler API library used before! 
Installing Qiskit and the SenseHat libraries on a Raspberry Pi can be quite complicated; I hope to add more information on the correct sequence of steps to do so. I have successfully installed everything on Raspbian _buster_ running berryconda (python 3.6.6), but it took a bit of work and required compiling 

**Release 2 is compatible with both Qiskit v0.9 and Qiskit v0.12 if you have created your stored credentials properly**

If your Raspberry Pi has more than one version of Python installed, be sure to install the QISKit API library for your Python 3 interpreter!

You must have an account set up at the IBM Quantum Experience and obtain your Personal Access Token from the My Account settings. The introductory material for the IBM Quantum Experience explains how to get that token.

## Customizing the code for your use
**Qiskit v0.9.0** You will need to use the IBMQ.save_account() method to store your API token on your Raspberry Pi.

**Qiskit v0.12.0** You will need to use the new methods to store your API token. If you have upgraded from v0.9, follow the instructions to use the IBMQ.update_account() method.

The real difference between these two versions is in the authentication technique in qiskit-ibmq-provider. The new version (0.3.x) uses a _provider_ object for connections to the backend while the previous version used the IBMQ object.

Download the source code for the QuantumRaspberryTie program and the code should be ready to run!
Be sure to download the OPENQASM files as well (_expt.qasm_ & _expt16.qasm_) for the probram and put them in the same directory as your source file.

# Versions
There is now a single version of the code, which can run in one of two modes. 
Both require that the **sense-hat** and **qiskit** libraries be installed in order to function, and use the **threading**, **time**, and **datetime** modules.

## QuantumRaspberryTie.qiskit.py
This program tries to test its connection to the IBM Q website before making requests. It's designed to cope somewhat gracefully with what happens if you are running on batteries and your Raspberry Pi switches wireless access points as you move around, or are in a somewhat glitchy wifi environment. It also can now handle gracefully communications timeouts with the IBM Q backend, or the occasional glitch where the simulator queue status for a job gets stuck in "RUNNING" state.

To start the program, simply call it from its directory (on my system, the default version of python is python 3.6.6; add the version number if that is not true on your system):
+     *python QuantumRaspberryTie*  
          will launch with the default (5-qubit) quantum circuit 
          
+     *python QuantumRaspberryTie 16*  
          will launch with the 16-qubit circuit
+     *python QuantumRaspberryTie* _yourprogram.qasm_  
          will launch and attempt to load the circuit specified in file _yourprogram.qasm_

After loading libraries, the program checks the SenseHat accelerometer to see which way the Pi is oriented. If it is flat on a table, "up" will be towards the power and display connectors on the Pi. If you wish to change the display orientation, simply hold the pi in the orientation you want until an up arrow appears on the display. The program will now use that orientation until the next cycle.

The program then pings the IBM Q Experience website to make sure it has a connection; if not it will exit. 

It then loads the OPENQASM code for the experiment from a separarate text file, _expt.qasm_ (or _expt16.qasm_) which makes it easier to modify your experiment code. If the first ping was successful, in each cycle it pings again before it confirms the backend status and (presuming the backend is not busy) sending the OPENQASM code. If there no good response to the ping, or the backend responds as busy, it waits 10 seconds and tries again, begining again with that initial ping to the website. 

If the ping is good, it then connects to the IBM Quantum Experience API using your token and initializes the LED display (displaying a Q). It compiles the OPENQASM code into a "quantum circuit", echoes the quantum circuit drawing to the terminal. and then sends the quantum circuit to the processor to execute. While it waits for the response, it cycles the light display through a rainbow shift to indicate that the system is "thinking". Once the result is returned by the processor, the measured values of the qubits are displayed as either red (measured 0) or blue (measured 1).

The system will pause for a few seconds, then run the code again (flashing the Q as it starts) to display a new result. You may trigger a new run sooner by pressing the SenseHat joystick in any direction. If you want to change which way on the display is "up" simply hold the Pi in the correct orientation until the Q displays as the cycle starts (the position is measured before sending the job).

In each cycle, the status of the backend is checked and printed to the console, as is the quantum circuit diagram, then the probability value and measured bit pattern of the most-frequent result wich is used for the display

To stop the program and shut down the Pi, press and hold the joystick button on the SenseHat. The color display will stop cycling, it will briefly display **OFF** on the LED array, and then the Pi will shut down. When the green light on the Pi stops flashing, it is safe to disconnect power.

Both versions run the display by spawning a second thread. As long as the variable *thinking* is True, the rainbow cycle is run. If it is False, the value of the string variable *maxpattern* is translated into the red and blue qubit display.

The "blinky" and "showqubits" functions in the code are generalized to work with a global *display* variable. Setting that to equal the list defining the 5-qubit processor (ibm_qx5) will result in the bowtie display, setting it equal to the 16 (ibm_qx16) will result in the 16 bit display.

## The OPENQASM code being run
The program being run on the 5-qubit processor is very simple. 5 qubits are initialized to the ground state, a Hadamard gate is applied to each one to place it into a state of full superposition, then each is measured. The net effect is a 5-bit random number generator. Only 10 shots are run, so one pattern should always randomly end up higher in the results. The code is found in the variable *qasm* in both versions. It looks like this:

     OPENQASM 2.0;
     include "qelib1.inc";
     qreg q[5];
     creg c[5];
     h q[0];
     h q[1];
     h q[2];
     h q[3];
     h q[4];
     measure q[0] -> c[0];
     measure q[1] -> c[1];
     measure q[2] -> c[2];
     measure q[3] -> c[3];
     measure q[4] -> c[4];

The 16-qubit version does exactly the same thing only with 16 quantum registers and 16 classical registers. 

## acknowledgements
The color-shifting technique in the "thinking" display while waiting for the result from the processor is based on the rainbow.py example included with the SenseHat library.

The Ping function is based on that in the Pi-Ping program by Wesley Archer (c) 2017 
             https://github.com/raspberrycoulis/Pi-Ping

I also want to acknowledge Alex Lennon of Dynamic Devices, whose work on a docker template for an IOT project gave me hints on getting the Qiskit install to work on my Raspberry Pi : https://github.com/DynamicDevices/does-rpi3-qiskit
