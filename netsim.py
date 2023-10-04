import lxml.etree as ET
import subprocess
import os
import shutil
import sys


ncs_instance = os.environ["NCS_INSTANCE_DIR"]
netsim_dir = f"{ncs_instance}/netsim"
script_dir = "/root/create-netsim"
# [TODO] ned_dir = f"{ncs_instance}/packages/NED"


# Structure:
# Devices Dict {
#    DeviceType:[DeviceName,DeviceNumber (Ex: 2 will create 2 devices with the following name = "xr0" and "xr1"), NED Dir]    
# }

devicesDict = {
    "xr":['xr',2,f"{ncs_instance}/packages/cisco-iosxr-cli-7.41"],
    "vrp":['vrp',2,f"{ncs_instance}/packages/huawei-vrp-cli-6.35"],
    "nokia":['PRAG',2,f"{ncs_instance}/packages/alu-sr-cli-8.28"], ## MAN UC only accepts nokia devices with "AC", "AG", "DI", "CO" in their hostnames.
    "junos":['junos',2,f"{ncs_instance}/packages/juniper-junos-nc-4.6"]
}

#It's possible to add as many devices types as you want, you just need to follow the pattern and add the config template to the script folder.

#Device-groups that will be added to the NSO
devicesGroup = ['PE','CE','MAN','AGGREGATOR','PE-CORP']


def create():
    
    if os.path.exists(netsim_dir) == False:
        #Use the first device in the dict to create the netsim network
        os.chdir(ncs_instance)
        first_Device = list(devicesDict)[0] 
        
        create_network = subprocess.getoutput(f"ncs-netsim create-network {devicesDict[first_Device][2]} {devicesDict[first_Device][1]} {devicesDict[first_Device][0]}")
        devicesDict.pop(first_Device)
        
        print(create_network)

    for device in devicesDict:

        os.chdir(netsim_dir)
        add_to_network = subprocess.getoutput(f"ncs-netsim add-to-network {devicesDict[device][2]} {devicesDict[device][1]} {devicesDict[device][0]}")
        print(add_to_network)
        
    #Check if the authgroup default exists
    authgroup = subprocess.getoutput(f'echo "show running-config devices authgroups" | ncs_cli -C')  
    if 'devices authgroups group default' not in authgroup:
        create_authgroup = subprocess.getoutput(f'echo "config; devices authgroups group default default-map remote-name admin remote-password admin; commit" | ncs_cli -C')
        
def init():
    
    os.chdir(netsim_dir)
    
    start_netsim = subprocess.getoutput(f"ncs-netsim start")
    
    print(start_netsim)
    
    # devicesDict[deviceKey][0] == Device Name
    # devicesDict[deviceKey][1] == Number of Devices
    # devicesDict[deviceKey][2] == NED Dir
       
    for deviceKey in devicesDict:
        
        index = 0
                
        while index < devicesDict[deviceKey][1]:
            
            #Allowing the execution of the scripts (Needed for sync-from)
            script_permission = subprocess.getoutput(f'find {devicesDict[deviceKey][0]}/ -name "*.sh" -exec chmod +x {{}} \;')
            
            init_netsim = subprocess.getoutput(f"ncs-netsim ncs-xml-init {devicesDict[deviceKey][0]}{index} > device{devicesDict[deviceKey][0]}{index}.xml")
            load_netsim = subprocess.getoutput(f"ncs_load -l -m device{devicesDict[deviceKey][0]}{index}.xml")
                     
            sync_device = subprocess.getoutput(f'echo "devices device {devicesDict[deviceKey][0]}{index} sync-from" | ncs_cli -C')
            print(f"Added {devicesDict[deviceKey][0]}{index} device \nsync-from: {sync_device}") 
            
            # Creating the device-groups and adding the devices.
            for group in devicesGroup:
                
                add_device_group = subprocess.getoutput(f'echo "config; devices device-group {group} device-name {devicesDict[deviceKey][0]}{index}; commit" | ncs_cli -Cu admin')
                
                if "Commit complete." in add_device_group:
                
                    print(f"Added {devicesDict[deviceKey][0]}{index} to {group} group.")
                    
                else:
                    
                    print(f"{devicesDict[deviceKey][0]}{index} message: {add_device_group}")
            
            index += 1
        
        index = 0
    
def remove():
    
    os.chdir(netsim_dir)
    
    stop_netsim = subprocess.getoutput(f"ncs-netsim stop")
    
    print(stop_netsim)
    
    # devicesDict[deviceKey][0] == Device Name
    # devicesDict[deviceKey][1] == Number of Devices
    # devicesDict[deviceKey][2] == NED Dir
    
    for deviceKey in devicesDict:
        
        index = 0
        
        while index < devicesDict[deviceKey][1]:
            
            # Removing the devices from the device-groups.
            for group in devicesGroup:
                
                add_device_group = subprocess.getoutput(f'echo "config; no devices device-group {group} device-name {devicesDict[deviceKey][0]}{index}; commit" | ncs_cli -Cu admin')
                
                if "Commit complete." in add_device_group:
                
                    print(f"Removed {devicesDict[deviceKey][0]}{index} from {group} group.")
                    
            remove_netsim_nso = subprocess.getoutput(f'echo "config; no devices device {devicesDict[deviceKey][0]}{index}; commit" | ncs_cli -Cu admin')
            
            index += 1
    
        index = 0
        
    shutil.rmtree(netsim_dir)

def config():
    
    
    for deviceKey in devicesDict:
        
        index = 0
        
        # devicesDict[deviceKey][0] == Device Name
        # devicesDict[deviceKey][1] == Number of Devices
        # devicesDict[deviceKey][2] == NED Dir
        
        while index < devicesDict[deviceKey][1]:
                        
            # Edit the config_{device}.xml templates         
            with open(f'config_{deviceKey}.xml', encoding="utf8") as f:
                tree = ET.parse(f)
                root = tree.getroot()


            for elem in root.getiterator(): # [TODO] Find a way to select only the <name> tag.
                try:
                   elem.text = elem.text.replace(f'{{DEVICE {deviceKey.upper()}}}', f'{devicesDict[deviceKey][0]}{index}')
                except AttributeError:
                    pass
            
            # Bypassing system permissions
            os.chdir(netsim_dir)
                               
            #tree.write('output.xml', encoding="utf8")
            # Adding the xml_declaration and method helped keep the header info at the top of the file.
            tree.write(f'output_{devicesDict[deviceKey][0]}{index}.xml', encoding="utf8")
            
            # Inserts the config into the NSO
            insert_config = subprocess.getoutput(f"ncs_load -u admin -l -m output_{devicesDict[deviceKey][0]}{index}.xml")
            print(insert_config)
            
            # Delete the specific config file
            os.remove(f"output_{devicesDict[deviceKey][0]}{index}.xml")
            
            # Bypassing system permissions
            os.chdir(script_dir)
            
            index += 1
    
        index = 0  

def create_network():
    
    create()
    init()
    config()

if __name__ == '__main__':
    args = sys.argv
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
    globals()[args[1]](*args[2:])
