# quantum-raspberry-tie
Your Raspberry Pi running code on the IBM Q quantum processors via Python 3 -- with results displayed courtesy of the 8x8 LED array on a SenseHat!

This code is specifically designed to run on a Raspberry Pi 3 with the SenseHat installed. The 8x8 array on the SenseHat is used to display the results.
The QuantumBowtie5.py runs a 5-qubit program and displays it in a manner corresponding to the IBM 5-qubit "bowtie" quantum processor.
<br/><img src='ibm_qubit_cpu.jpg' width='200' alt='IBM 5 qubit processor' style='float:left;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src='RaspberryTieOutput.png' width='200' alt='Output displayed on the SenseHat' style='float:right;'><br/> 
(It's called a bowtie because of the arrangement of the 5 qubits, and the particular ways they can interconnect via entanglement. Each of those rectangles touched by a squiggly line in the image on the left holds a qubit.)

The QuantumRaspberry16.py code can run and display an program corresponding to a 16-qubit processor
<br /><img src='ibm_16_qubit_processor-100722935-large.3x2.jpg' width='200' alt='IBM 16 qubit processor' style='float:left;'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src='16-bitRpi-result.JPG' width='200' alt='16 qubit Output displayed on the SenseHat' style='float:right;'><br/> >

Actual calculations are run using the quantum simulator backend for the quantum processor, to avoid overwhelming the physical processor in the IBM Q lab.

# Installation

## Prerequisites
You will need a Raspberry Pi 3 running at least the Jessie release of Raspbian, with a SenseHat hat properly installed.
If your processor did not come with the SenseHat libraries pre-installed, you must install them.
     https://www.raspberrypi.org/documentation/hardware/sense-hat/
     
Your Raspberry Pi must have an active internet connection for the API to function properly
     
You will need to install the **Python Library for the IBM Quantum Experience API**
     https://github.com/QISKit/qiskit-api-py
     
**IMPORTANT:** Do not install the complete QISKit library, only this API library! A complete QISKit install will corrupt a library necessary for the SenseHat library to function. 
Using _pip install IBMQuantumExperience_  (or _pip3 install IBMQuantumExperience_ as appropriate) will install just the API library you need for the Raspberry Pi to work with both IBM Q and the SenseHat.

If your Raspberry Pi has more than one version of Python installed, be sure to install the QISKit API library for the Python 3 interpreter!

You must have an account set up at the IBM Q Experience and obtain your Personal Access Token from the My Account settings. The readme file for the <a href='https://github.com/QISKit/qiskit-api-py'>qiskit-api-py library</a> explains how to get that token.

## Customizing the code for your use
Download the source code for the QuantumBowtie program of your choice and open it with an editor. Search for the string that should be replaced with your Personal Access Token, delete it, and paste in your token string instead. Your code should be ready to run!
Be sure to download the correct OPENQASM file (_expt.qasm_ or _expt16.qasm_) for the probram and put it in the same directory as your source file.

# Versions
There are two versions of the code. 
Both require that the **sense-hat** and **QISKIT/qiskit-api-py** libraries be installed in order to function, and use the **threading**, **time**, and **datetime** modules.

## QuantumBowtie5.py
This program tries to test its connection to the IBM Q website before making requests. It's designed to cope somewhat gracefully with what happens if you are running on batteries and your Raspberry Pi switches wireless access points as you move around, or are in a somewhat glitchy wifi environment.

In the source code, search for the string *REPLACE_THIS_STRING_WITH_YOUR_QUANTUM_EXPERIENCE_PERSONAL_ACCESS_TOKEN* and replace it with your token.

The program first pings the IBM Q Experience website to make sure it has a connection; if not it will exit. 

It then loads the OPENQASM code for the experiment from a separarate text file, _expt.qasm_ which makes it easier to modify your experiment code. If the first ping was successful, in each cycle it pings again before it confirms the backend status and (presuming the backend is not busy) sending the OPENQASM code. If there no good response to the ping, or the backend responds as busy, it waits 10 seconds and tries again, begining again with that initial ping to the website. 

If the ping is good, it then connects to the IBM Quantum Experience API using your token, initializes the LED display, and then sends the OPENQASM code to the processor. While it waits for the response, it cycles the light display through a rainbow shift to indicate that the system is "thinking". Once the result is returned by the processor, the measured values of the qubits are displayed as either red (measured 0) or blue (measured 1).

The system will pause for 10 seconds, then run the code again to display a new result. You may trigger a new run sooner by pressing the SenseHat joystick in any direction. 

In each cycle, the status of the backend is checked and printed to the console, as are experiment ID, then the probability value and measured bit pattern of the most-frequent result wich is used for the display


**QuantumRaspberry16.py** -- This version runs exactly the same way, but is set up to display a 16-qubit result on the SENSEHAT. It uses  the file _expt16.qasm_ to load its OPENQASM source code.

Both versions run the display by spawning a second thread. As long as the variable *thinking* is True, the rainbow cycle is run. If it is False, the value of the string variable *maxpattern* is translated into the red and blue qubit display.

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
