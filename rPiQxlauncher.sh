#!/bin/bash
# rPiQxlauncher.sh
# navigate to home directory, then to code directory, then launch
# navigate to the drive root
cd /
# navigate to the directory with the Quantum Raspberry files in it (you must change YOURCODEDIRECTORY appropriately)
cd home/pi/YOURCODEDIRECTORY

# Launch the program
# (Modify the comments in the lines below to select the program you want to launch at boot)
# Notes: These are set up to run in the Python 3 IDLE environment.
# if you prefer to run in a Python 3 terminal, replace 'idle3 -r' with 'python3'
# the trailing code specifies to run as default user pi, so the python environment
# has all the appropriate libraries installed.
# if you have renamed the default account to something other than "pi" update the line appropriately.

sudo su -c "idle3 -r QuantumBowtie5.py expt.qasm &" -s /bin/sh pi
#sudo su -c "idle3 -r QuantumRaspberry16.py expt16.qasm &" -s /bin/sh pi
