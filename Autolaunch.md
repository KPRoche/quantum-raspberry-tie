# Setting up a Quantum Raspberry program to autolaunch

These programs were designed to be run headless on a Raspberry Pi with SenseHat connected only to a battery. 
It took several attempts to find a technique that offered consistently satisfactory results, 
including the ability to optionally connect to the Pi and see the messages being returned by IBM Q or modify the program.

You will need to do a series of things in advance for this to be reliable:
1. Setup VNC Server for cloud connections
1. Configure the Pi to autoconnect to a wireless hotspot (perhaps your phone) in your demo space
1. Edit a shell script file to launch the program you want to run
1. Set that script file to executable
1. Add that file to /etc/profile so it will run on boot
## 1. Setup VNC Server for cloud connections
My Raspberry Pi came with VNC Server already installed. While my worksite has a secure wireless intranet, I found it simplest to set my Raspberry Pi to connect to public wifi and use a cloud-based VNC connection for remote connections. This avoids having to attempt to harden the security on your Pi to corporate standards. It does **not** mean you shouldn't use best practices setting up your Pi for its own security.
* You need to enable VNC on the *interfaces* tab of the Raspberry Pi configuration tool and reboot.
* You will need to create an account and team at RealVNC.com . This is not difficult, just follow the instructions. 
* You will also need to download and install VNC Viewer on a mobile device, tablet, or laptop and set it up to sign into your account. You DO NOT need to install VNCServer on the device that you will be using to remote-control the Pi, just the viewer.
* After rebooting, click on the VNC icon in the Taskbar on the Raspbian desktop
  * **If you are setting up more than one Pi** be sure to give each one a unique name before you activate the VNC Server. Their tools automatically create entries on your "team" and giving them unique names makes your life much simpler.
  * Follow the prompts to set up connect via the cloud. This allows you to connect on public networks. 
  * You will be setting a cloud password for the Pi on RealVNC. Be smart about your password
  * Once it is set, start VNCViewer on your remote device and make sure you can see and connect to your Pi
## 2. Configure the Pi to autoconnect to a WiFi hotspost
  * I found it most useful to configure my Pi to autoconnect to my mobile phone running a personal hotspot. That way if I boot in a location with a new wifi network, it will start by connecting to the Internet via the phone hotspot. 
  * Once it has internet access, you can use VNCViewer to remotely configure it to whatever the local wifi network is called.
  * If you are running a demo in an area with spotty/no wifi and your phone has reception, you can also just keep using your phone hotspot. These programs are not running high bandwidth connections to IBM Q.
  ## 3. Edit a shell script file to launch the program you wish to run.
  * There is a sample shell file  **rPiQXlauncher.sh** in this repository which looks like this:
      ```python
      #!/bin/bash
      # rPiQxlauncher.sh
      # navigate to home directory, then to code directory, then launch
      # navigate to the drive root
      cd /
      # navigate to the directory with the Quantum Raspberry files in it (update YOURCODEDIRECTORY appropriately)
      cd home/pi/YOURCODEDIRECTORY

      # Launch the program
      # (Modify the comments in the lines below to select the program you want to launch at boot)
      # Notes: These are set up to run in the Python 3 IDLE environment.
      # if you prefer to run in a Python 3 terminal, replace 'idle3-r' with 'python3'
      # the trailing code specifies to run as default user pi, so the python environment
      # has all the appropriate libraries installed.
      # if you have renamed the default account to something other than "pi" update the line appropriately.

      sudo su -c "idle3 -r QuantumBowtie5.py expt.qasm &" -s /bin/sh pi
      #sudo su -c "idle3 -r QuantumRaspberry16.py expt16.qasm &" -s /bin/sh pi
      ```
  * Change the text *YOURCODEDIRECTORY* to complete the path to where you have placed the Quantum Raspberry files
  * Comment/uncomment the last two lines to launch either the 5 qubit or the 16 qubit demonstrator
  * Note that the command launching the Quantum Raspberry program is set up to run as user **pi**. If you have changed the name of the default user from pi to something else, change this to match. It is necessary to make sure the Python environment can locate the QISKIT libraries to run properly
  * The script as written launches the program in the Python 3 IDLE enviroment using the *idle3 -r* command. I find this convenient because if necessary you can connect via VNC, stop the executing code, then easily load/edit a Python file and relaunch it. If you prefer to simply run in a Python 3 terminal, replace *idle3 -r* with *python3* in the script file. If you do not remove the -r option the script will throw an error.

  ## 4. Set the shell file to be executable
  * Open a terminal and navigate to the directory where you have placed the shell script file.
  * enter the command
      ```raspbian
      sudo chmod +x rPiQXlauncher.sh
      ```
  * to make the shell script executable. Leave the terminal window open
  * test that it runs with the command (in the same window)
      ```raspbian
      . rPiQXlauncher.sh
      ```
    to confirm if the Quantum Raspberry program launches correctly.
    
 ## 5. Add the script file to /etc/profile so it will run on boot
   * Open a terminal window and enter the command 
       ```raspbian
       sudo nano /etc/profile
       ```
       and scroll to the end of the file using the cursor keys
   * At the end, add the line 
       ```raspbian
       . /home/pi/YOURCODEDIRECTORY/rPiQXlauncher.sh
       ```
       (Obviously, YOURCODEDIRECTORY must be replaced to complete the path to your shell script)
   * Hit Ctrl-X, Y, and Enter to save and exit the nano editor
   * Reboot the Pi
       ```raspbian
       sudo reboot
       ```
       
  ## And now your demonstration program should autolaunch in a window on the Pi desktop once it finishes booting!

