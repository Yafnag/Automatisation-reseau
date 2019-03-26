#!/usr/bin/python

from __future__ import unicode_literals
from ipaddress import IPv4Network
import socket
import struct
import ipaddress
import sys
import os
import shutil
import argparse
from argparse import RawTextHelpFormatter
import yaml


subnet_list = []
netmask_list = []
routers_list = []
ip_range_list = []
broadcast_address_list = []



def generate_dhcp_subnet(subnet):    
    net = IPv4Network(subnet)
    
    netmask = str(IPv4Network(subnet).netmask)
    network = str(IPv4Network(subnet).network_address)    
    broadcast_addr = str(net.broadcast_address)    
    routers = str(ipaddress.ip_address(broadcast_addr) - 1)

    ip_range_end = str(ipaddress.ip_address(routers) -1)
    ip_range_first = str(ipaddress.ip_address(network) + 1)
    ip_range = ip_range_first + " " + ip_range_end

    if network != "" and netmask != "" and routers != "" and ip_range != " " and broadcast_addr != "" :
        subnet_list.append(network)
        netmask_list.append(netmask)
        routers_list.append(routers)
        ip_range_list.append(ip_range)
        broadcast_address_list.append(broadcast_addr)
    else :
        sys.exit("Erreur lors du remplissage des listes subnet")

def generate_vlan_interface():
    vlan_config = ""
    for i in range (len(subnet_list)):
        vlan_config += "auto {}{}\niface {}{} inet {}\n\tvlan-raw-device {}\n\taddress {}\n\tnetmask {}\n\n".format(conf['vlan_dict']['auto'],
                                                                                                                  i+1,
                                                                                                                  conf['vlan_dict']['auto'],
                                                                                                                  i+1,
                                                                                                                  conf['vlan_dict']['inet'],
                                                                                                                  conf['vlan_dict']['vlan-raw-device'],
                                                                                                                  routers_list[i],
                                                                                                                  netmask_list[i])
    return vlan_config

def main(argv):
    for subnet in argv:
        generate_dhcp_subnet(subnet)

    dhcp_config = ""

    for conf_str, conf_value in yaml.load(open('conf.yaml'))['dhcp_dict'].items():
        dhcp_config += conf_str + " " + str(conf_value) + ";\n"

    for i in range (len(subnet_list)): 
        dhcp_config += "\nsubnet {} netmask {}{{\n\toption routers {};\n\trange {};\n\toption broadcast-address {};\n}}\n".format(subnet_list[i],
                                                                                                                               netmask_list[i],
                                                                                                                               routers_list[i],
                                                                                                                               ip_range_list[i],
                                                                                                                               broadcast_address_list[i])

    print(dhcp_config)
    print("\n\n---------------------------------------------------------------------------\n\n")
    confirm_dhcp_conf = input("Cette configuration DHCP vous convient-elle ? (Y/N)")

    if confirm_dhcp_conf == "Y" :
        if os.path.isfile('./dhcpd.conf'):
            try:
                shutil.copyfile('dhcpd.conf', 'dhcpd.conf.bak')
            except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors du backup de dhcpd.conf")

        try:
            dhcpd = open("dhcpd.conf", "w")
            dhcpd.write(dhcp_config)
        except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors de l'écriture du fichier dhcpd.conf")
        dhcpd.close()
        print("Le fichier dhcpd.conf a été généré\n\n")
    else :
        sys.exit("Relancer le script afin de générer la configuration DHCP qui vous convient")

    vlan_config = generate_vlan_interface()
    print(vlan_config)
    print("\n\n---------------------------------------------------------------------------\n\n")

    confirm_vlan_conf = input("La configuration VLAN vous convient-elle ? (Y/N)")

    if confirm_vlan_conf == "Y" :
        if os.path.isfile('./interfaces'):
            try:
                shutil.copyfile('interfaces', 'interfaces.bak')
            except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors du backup du fichier interfaces")

        try:
            interfaces = open("interfaces", "a")
            interfaces.write("\n\n" + vlan_config)
        except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors de l'écriture du fichier interfaces")
        interfaces.close()
        print("Le fichier interface a été modifié")
    else :
        sys.exit("Relancer le script afin de générer la configuration VLAN qui vous convient")
            

if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description="Pour executer le script il faut editer le fichier de configuration conf.yaml.\n"+
        "\t- Renseigner les serveurs DNS qui seront attribués par le serveur DHCP à la ligne \"option domain-name-servers\".\n"+
        "\t- Renseigner le nom de l'interface réseau sur laquel seront générés les VLANs à la ligne \"vlan_raw_device\"\n\n"+
        "python dhcp.py -s subnet1/netmask1CIDR subnet2/netmask2CIDR...\n\n"+
        "Exemple :\n"+
        "python dhcp.py -s 192.168.0.0/25 192.168.0.128/27 192.168.0.160/28 192.168.0.176/28 192.168.0.192/29", formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s','--subnets', nargs='+', default=[])
    args=parser.parse_args()

    try:
        conf = yaml.load(open('conf.yaml'))
    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit("Erreur lors de l'ouverture du fichier de configuration")

    order_network = sorted(args.subnets, key=lambda x: int(x.rsplit('/',1)[1]))
    main(order_network)

