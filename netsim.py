import lxml.etree as ET
from decouple import config

import subprocess
import os
import shutil
import sys


ncs_instance = os.environ["NCS_INSTANCE_DIR"]
netsim_dir = f"{ncs_instance}/netsim"

# [TODO] ned_dir = f"{ncs_instance}/packages/NED"


# Structure:
# Devices Dict {
#    DeviceType:[DeviceName,DeviceNumber (Ex: 2 will create 2 devices with the following name = "xr0" and "xr1"), NED Dir]    
# }

devicesDict = {
    "xr":['xr',2,f"{ncs_instance}/packages/cisco-iosxr-cli-7.41"],
    "vrp":['vrp',2,f"{ncs_instance}/packages/huawei-vrp-cli-6.35"],
    "nokia":['nokia',2,f"{ncs_instance}/packages/alu-sr-cli-8.28"],
    "junos":['junos',2,f"{ncs_instance}/packages/juniper-junos-nc-4.6"]
}

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
    
    #Check if the authgroup has already been created, otherwise, creates the authgroup.
    authgroup_password = config('AUTHGROUP_PASSWORD')
    authgroup_check = subprocess.getoutput(f'echo "show running-config devices authgroup" | ncs_cli -C')
        
    if 'authgroup default' not in authgroup_check:
        
        authgroup_create = subprocess.getoutput(f'echo "config; devices authgroup group default default-map remote-name admin remote-password {authgroup_password}; commit" | ncs_cli -C')
        
def init():
    
    os.chdir(netsim_dir)
    
    start_netsim = subprocess.getoutput(f"ncs-netsim start")
    
    print(start_netsim)
    
    for deviceKey in devicesDict:
        
        index = 0
        
        while index < devicesDict[deviceKey][1]:
            
            init_netsim = subprocess.getoutput(f"ncs-netsim ncs-xml-init {deviceKey}{index} > device{deviceKey}{index}.xml")
            print(init_netsim)
            load_netsim = subprocess.getoutput(f"ncs_load -l -m device {deviceKey}{index}.xml")
            print(load_netsim)

            index += 1
        
        index = 0
        
def remove():
    
    os.chdir(netsim_dir)
    
    stop_netsim = subprocess.getoutput(f"ncs-netsim stop")
    
    print(stop_netsim)
    
    for deviceKey in devicesDict:
        
        index = 0
        
        for deviceNumber in devicesDict[deviceKey][1]:
        
            remove_netsim_nso = subprocess.getoutput(f'echo "config; no devices device {deviceKey}{deviceNumber}; commit" | ncs_cli -Cu admin')
            print(remove_netsim_nso)
            
            index += 1

        index = 0
        
    shutil.rmtree(netsim_dir)


if __name__ == '__main__':
    args = sys.argv
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
    globals()[args[1]](*args[2:])
    

""" def create_netsim():
    
    subprocess.run("ncs-netsim")
    
    #Checar se o diretório do NETSIM existe
    #Criar o network || Adicionar device ao network
    
    #Inicializar o NETSIM
    ##ncs-netsim start DEVICE
    ##ncs-netsim ncs-xml-init DEVICE >> init.xml
    ##ncs_load -l -m init.xml
    
    #Inserir configuração
    ##ncs_load -l -m config_DEVICEType.xml
    ##echo "devices device DEVICE sync-from" | ncs_cli -Cu admin
    
    #Inserir devices nos grupos
    ##echo "config; devices device-group GROUP device-name DEVICE; commit" | ncs_cli -Cu admin
    
    
    
#adding the encoding when the file is opened and written is needed to avoid a charmap error
with open('config_nokia.xml', encoding="utf8") as f:
tree = ET.parse(f)
root = tree.getroot()


for elem in root.getiterator():
    try:
    elem.text = elem.text.replace('{DEVICE NAME}', 'Device1_nokia')
    except AttributeError:
    pass

#tree.write('output.xml', encoding="utf8")
# Adding the xml_declaration and method helped keep the header info at the top of the file.
tree.write('output.xml', xml_declaration=True, method='xml', encoding="utf8") """