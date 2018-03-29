#!/bin/bash
# rPiQxlauncher.sh
# navigate to home directory, then to code directory, then launch

cd /
cd home/pi/YOURCODEDIRECTORY

sudo su -c "idle3 -r QuantumBowtie5.py expt.qasm &" -s /bin/sh pi
#sudo su -c "idle3 -r QuantumRaspberry16.py expt16.qasm &" -s /bin/sh pi