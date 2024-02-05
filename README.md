## netsim.py

Script will be used after an instalation of Cisco NSO (Network Service Orchestrator) to create dummy devices that will be used to validate the installed packages.

### Configure the devices you want to create and the folder containing your script within netsim.py

<p style="color:red"> Change the 'script_dir' variable to the path where the script is located. </p>

<h3 style="color:#00BFFF"> def create </h3>

Creates the netsim devices based on the dict passed before, ex:

<span style="color:#FE642E">
Devices Dict = { <br>
&nbsp&nbsp&nbsp DeviceType : [ <br> 
&nbsp&nbsp&nbsp DeviceName,<br>
&nbsp&nbsp&nbsp DeviceNumber (Ex: 2 will create 2 devices with the following name = "xr0" and "xr1"),<br>
&nbsp&nbsp&nbsp NED Dir <br>
&nbsp&nbsp&nbsp ]<br>    
}
</span>

It also creates the authgroup that the netsim devices will be inserted into.

Command: python3 netsim.py create

<h3 style="color:#00BFFF"> def init </h3>

Creates the necessary configuration files and insertS the devices into NSO.

Command: python3 netsim.py init

<h3 style="color:#00BFFF"> def remove </h3>

Removes the netsim devices from the NSO and delete the network created.

Command: python3 netsim.py remove

<h3 style="color:#FF4000"> def config</h3>

Change template name variable for the device created and load the configuration into NSO.

Command: python3 netsim.py config

<h3 style="color:#FF4000"> def create_network </h3>

Call all the necessary functions to create a NETSIM network (create, init, config).

Command: python3 netsim.py create_network
