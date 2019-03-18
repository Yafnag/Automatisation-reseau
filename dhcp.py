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

DNS = ""
dhcp_dict = {
    'default-lease-time ' : 600,
    'max-lease-time ' : 7200,
    'option domain-name-servers ' : DNS }

subnet_list = []
netmask_list = []
routers_list = []
ip_range_list = []
broadcast_address_list = []

subnet_dict = {
    'subnet' : subnet_list,
    'netmask' : netmask_list,
    'routers' : routers_list,
    'range' : ip_range_list,
    'broadcast' : broadcast_address_list}

device_name = ""

vlan_dict = {
    'auto' : 'vlan',
    'iface' : 'vlan',
    'inet' : 'static',
    'vlan-raw-device' : device_name,
    'address' : routers_list,
    'netmask' : netmask_list }

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

def generate_vlan_interface(interface_name):
    vlan_dict['vlan-raw-device'] = interface_name
    vlan_config = ""
    for i in range (len(subnet_dict.get("subnet"))):
        vlan_config += "auto " + vlan_dict['auto'] + str(i+1) + "\n"
        vlan_config += "iface " + vlan_dict['auto'] + str(i+1) + " inet " + vlan_dict['inet'] + "\n"
        vlan_config += "\tvlan-raw-device " + vlan_dict['vlan-raw-device'] + "\n"
        vlan_config += "\taddress " + vlan_dict['address'][i] + "\n"
        vlan_config += "\tnetmask " + vlan_dict['netmask'][i] + "\n\n"
    return vlan_config

def main(argv):
    DNS = input("Renseignez le(s) serveur(s) DNS :")
    dhcp_dict['option domain-name-servers '] = DNS
    print("\n\n---------------------------------------------------------------------------\n\n")
    for subnet in argv:
        generate_dhcp_subnet(subnet)

    dhcp_config = ""

    for conf_str, conf_value in dhcp_dict.items():
        dhcp_config += conf_str + str(conf_value) + ";\n"

    for i in range (len(subnet_dict.get("subnet"))): #on récupère le nombre de subnet à déclarer et on boucle
        dhcp_config += "\nsubnet " +  subnet_dict['subnet'][i] + " netmask " + subnet_dict['netmask'][i] + " {\n"
        dhcp_config += "\toption routers " + subnet_dict['routers'][i] + ";\n"
        dhcp_config += "\trange " + subnet_dict['range'][i] + ";\n"
        dhcp_config += "\toption broadcast-address " + subnet_dict['broadcast'][i] + ";\n}\n"

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

    iface_name = input("Nom de la carte réseau sur laquelle générer les VLANs :")
    print("\n\n---------------------------------------------------------------------------\n\n")
    vlan_config = generate_vlan_interface(iface_name)
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
        description="Pour executer le script il faut commencer par editer le fichier de configuration conf.yaml.\n"+
        "- Renseigner les serveurs DNS qui seront attribués par le serveur DHCP à la ligne option domain-name-servers.\n"+
        "- Renseigner le nom de l'interface réseau sur laquel seront généré les VLANs à la ligne device_name = EXAMPLE\n\n"+
        "python dhcp.py -s subnet1/netmask1CIDR subnet2/netmask2CIDR...\n\n"+
        "Exemple :\n"+
        "python dhcp.py -s 192.168.0.0/25 192.168.0.128/27 192.168.0.160/28 192.168.0.176/28 192.168.0.192/29", formatter_class=RawTextHelpFormatter)
    parser.add_argument('-s','--subnets', nargs='+', default=[])
    args=parser.parse_args()

    order_network = sorted(args.subnets, key=lambda x: int(x.rsplit('/',1)[1]))
    main(order_network)

