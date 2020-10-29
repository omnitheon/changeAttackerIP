import ipaddress
import random
import platform
import subprocess
import os

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

def changeIP(IPDS, debug):
    debug = False #Works on linux
    Available = IPDS["pool_address_objects"]
    interfaceName = IPDS["networkInterface"]
    defaultGateway = IPDS["defaultGateway"]
    networkAddress = IPDS["networkAddress"]
    networkSubnetMask = IPDS["network_subnet_mask"]
    networkBoardcast = IPDS["network_broadcast_address"]
    print("{} available IPs".format(len(Available))) if debug==True else ''
    usable = random.choice(Available)
    print("Checking if {} is in use. . .".format(usable))  if debug==True else ''
    if platform.system() == "Windows":
        cmd = "ping -w 1 -n 1 {}".format(usable)
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()
    else:
        cmd = "/usr/bin/ping -i 0.3 -c 1 {}".format(usable).split(" ")
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()
    
    stdOUT = out[0].decode("utf-8")
    while (platform.system() == "Windows" and "Reply from {}".format(usable) in stdOUT) or (platform.system() == "Linux" and "64 bytes from {}".format(usable) in stdOUT):
        print("Previously selected IP was in use...trying again.")   if debug==True else ''
        usable = random.choice(Available)
        print("Checking if {} is in use. . .".format(usable))  if debug==True else ''
        if platform.system() == "Windows":
            cmd = "ping -w 1 -n 1 {}".format(usable)
            p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out = p.communicate()
        else:
            cmd = "/usr/bin/ping -i 0.3 -c 1 {}".format(usable).split(" ")
            p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out = p.communicate()
        stdOUT = out[0].decode("utf-8")
    else:
        cmd = "/usr/sbin/ip route del default".split(" ")
        print(cmd)  if debug==True else ''
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()
        cmd = "/usr/sbin/ifconfig {} {} netmask {} broadcast {}".format(interfaceName,usable,networkSubnetMask,networkBoardcast).split(" ")
        print(cmd)  if debug==True else ''
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()
        cmd = "/usr/sbin/ip route add {} dev {}".format(networkAddress,interfaceName).split(" ")
        print(cmd)  if debug==True else ''
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()
        cmd = "/usr/sbin/ip route add default via {} dev {}".format(defaultGateway,interfaceName).split(" ")
        print(cmd)  if debug==True else ''
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()

        outfile = open("temp.txt","w")
        outfile.write("update delete badguy.redteam.ccdc.core\n")
        outfile.write("update add badguy.redteam.ccdc.core 86400 a {}\n".format(usable))
        outfile.write("send\n".format(usable))
        outfile.close()
        cmd = 'nsupdate -v {}/temp.txt'.format(os.getcwd())

        print(cmd)  if debug==True else ''
        p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out = p.communicate()

        print("[{}] Successfully changed IP to {}. . .".format(currT(),usable))  if debug==True else ''
        print("\tNext SourceIP: {}".format(usable))

IP_RAW = open('ip_configuration.txt', 'r')
IP_DS = generateIPDS(IP_RAW.read().strip("\n"))
changeIP(IP_DS,True)