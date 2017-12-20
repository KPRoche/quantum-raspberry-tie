# quantum-raspberry-tie
Your Raspberry Pi running code on the IBM Q quantum processors via Python 3 -- with results displayed courtesy of the 8x8 LED array on a SenseHat!

This code is specifically designed to run on a Raspberry Pi 3 with the SenseHat installed. The 8x8 array on the SenseHat is used to display the results corresponding to the IBM 5-qubit "bowtie" quantum processor.
<br/><img src='ibm_qubit_cpu.jpg' width='200' alt='IBM 5 qubit processor'>&nbsp;&nbsp;
<img src='RaspberryTieOutput.png' width='200' alt='Output displayed on the SenseHat'><br/> 
(It's called a bowtie because of the arrangement of the 5 qubits, and the particular ways they can interconnect via entanglement. Each of those rectangles touched by a squiggly line in the image holds a qubit.)

Actual calculations are run using the quantum simulator backend for the quantum processor, to avoid overwhelming the physical processor in the IBM Q lab.

# Installation

You will need a Raspberry Pi 3 running at least the Jessie release of Raspbian, with a SenseHat hat properly installed.
If your processor did not come with the SenseHat libraries pre-installed, you must install them.
     https://www.raspberrypi.org/documentation/hardware/sense-hat/
     
Your Raspberry Pi must have an active internet connection for the API to function properly
     
You will need to install the **Python Library for the IBM Quantum Experience API**
     https://github.com/QISKit/qiskit-api-py
     
If your Raspberry Pi has more than one version of Python installed, be sure to install this library for the Python 3 interpreter!

You must have an account set up at the IBM Quantum Experience and obtain your Personal Access Token from the My Account settings. The readme file for the <a href='https://github.com/QISKit/qiskit-api-py'>qiskit-api-py library</a> explains how to get that token.

Download the source code for the QuantumBowtie program of your choice and open it with an editor. Search for the string that should be replaced with your Personal Access Token, delete it, and paste in your token string instead. Your code should be ready to run!

# Versions
There are two versions of the code. 
Both require that the **sense-hat** and **QISKIT/qiskit-api-py** libraries be installed in order to function, and use the **threading**, **time**, and **datetime** modules.

## QuantumBowtie.py 
In the source code, search for the string *REPLACE_THIS_STRING_WITH_YOUR_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN* and replace it with your token.

This version connects to the IBM Q.E. API using your token, initializes the LED display, and then sends the OPENQASM code to the processor. While it waits for the response, it cycles the light display through a rainbow shift to indicate that the system is "thinking". Once the result is returned by the processor, the measured values of the qubits are displayed as either red (measured 0) or blue (measured 1).

The system will pause for 10 seconds, then run the code again to display a new result. You may trigger a new run sooner by pressing the SenseHat joystick in any direction.

In each cycle, the status of the backend is checked and printed to the console, as are experiment ID, then the probability value and measured bit pattern of the most-frequent result wich is used for the display

## QuantumBowtiePing.py
In the source code, search for the string *REPLACE_THIS_STRING_WITH_YOUR_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN* and replace it with your token.

This version is a little "smarter" and tries to test its connection to the website before making requests. It's designed to cope more gracefully with what happens if you are running on batteries and your Raspberry Pi switches wireless access points as you move around, or are in a somewhat glitchy wifi environment.

It pings the IBM Quantum Experience site before initializing the API to make sure the site is responding. If the site does not respond at first, the program will exit.

If it successfully connects, in each cycle it pings again before it confirms the backend status and (presuming the backend is not busy) sending the OPENQASM code. If there no good response to the ping, or the backend responds as busy, it waits 10 seconds and tries again, begining again with that initial ping to the website. Other than that, it is doing exactly the same thing as the simpler version.

Both versions run the display by spawning a second thread. As long as the variable *thinQing* is True, the rainbow cycle is run. If it is False, the value of the string variable *maxpattern* is translated into the red and blue qubit display.

## The OPENQASM code being run
The program being run on the processor is very simple. 5 qubits are initialized to the ground state, a Hadamard gate is applied to each one to place it into a state of full superposition, then each is measured. The net effect is a 5-bit random number generator. Only 10 shots are run, so one pattern should always randomly end up higher in the results. The code is found in the variable *qasm* in both versions. It looks like this:

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
     
## Other notes
The call to api.run_experiment() generates a datetime-based name for each experiment. This is to make sure the backend runs the code rather than looking up results for that experiment name. (At one point, an early version of the code with a static experiment name in the call kept returning exactly the same result every time, because once it had run once, the API kept returning the values from the first time the code was run.)

## acknowledgements
The color-shifting technique in the "thinking" display while waiting for the result from the processor is based on the rainbow.py example included with the SenseHat library.

The Ping function is based on that in the Pi-Ping program by Wesley Archer (c) 2017 
             https://github.com/raspberrycoulis/Pi-Ping
