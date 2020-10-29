import ipaddress
import random
import platform
import subprocess
import os
import time

def generateIPDS(IP_CONFIGURATION):
    #IP_CONFIGURATION is expected to be a row of poolNetworkAddress,networkAddress,defaultGateway,interfaceName
                                                #10.0.0.0/10,10.0.0.0/8,10.255.255.254,eth0
    IP_CONFIGURATION = IP_CONFIGURATION.split(",")
    poolNetwork = IP_CONFIGURATION[0]
    networkAddress = IP_CONFIGURATION[1]
    defaultGateway = IP_CONFIGURATION[2]
    networkInterface = IP_CONFIGURATION[3]
    pool_address_objects = list(ipaddress.ip_network(poolNetwork).hosts())
    network_address_object = ipaddress.ip_network(networkAddress)
    network_broadcast_address = network_address_object.broadcast_address.compressed
    network_subnet_mask = network_address_object.netmask.compressed
    return {"poolNetwork":poolNetwork, "networkAddress":networkAddress,
            "defaultGateway":defaultGateway, "networkInterface":networkInterface,
            "pool_address_objects":pool_address_objects, "network_address_object":network_address_object,
            "network_broadcast_address":network_broadcast_address, "network_subnet_mask":network_subnet_mask}

def execute(cmd):
    print(cmd)  
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out = p.communicate()

def changeIP(IPDS, debug):
    debug = False #Works on linux
    Available = IPDS["pool_address_objects"]
    interfaceName = IPDS["networkInterface"]
    defaultGateway = IPDS["defaultGateway"]
    networkAddress = IPDS["networkAddress"]
    networkSubnetMask = IPDS["network_subnet_mask"]
    networkBoardcast = IPDS["network_broadcast_address"]
    usable = random.choice(Available)
    execute("/usr/sbin/ip route del default".split(" "))
    execute("/usr/sbin/ifconfig {} {} netmask {} broadcast {}".format(interfaceName,usable,networkSubnetMask,networkBoardcast).split(" "))
    execute("/usr/sbin/ip route add {} dev {}".format(networkAddress,interfaceName).split(" "))
    execute("/usr/sbin/ip route add default via {} dev {}".format(defaultGateway,interfaceName).split(" "))

    outfile = open("temp.txt","w")
    outfile.write("update delete badguy.redteam.ccdc.core\n")
    outfile.write("update add badguy.redteam.ccdc.core 4 a {}\n".format(usable))
    outfile.write("send\n")
    outfile.close()
    print("Successfully changed IP to {}. . .".format(usable))  
    print("\tNext SourceIP: {}".format(usable))

    while True:
        os.system("nsupdate -v {}/temp.txt\n".format(os.getcwd()))
        time.sleep(1)

IP_RAW = open('ip_configuration.txt', 'r')
IP_DS = generateIPDS(IP_RAW.read().strip("\n"))
changeIP(IP_DS,True)