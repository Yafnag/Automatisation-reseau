#!/usr/bin/python

from __future__ import unicode_literals
import socket
import struct
import ipaddress
import sys

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
    'subnet ' : subnet_list,
    ' netmask ' : netmask_list,
    'option routers ' : routers_list,
    'range ' : ip_range_list,
    'option broadcast-address ' : broadcast_address_list}

def generate_dhcp_subnet(subnet):    
    network, net_bits = subnet.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    net = ipaddress.IPv4Network(network + '/' + netmask, False)
    broadcast_addr = str(net.broadcast_address)

    subnet_list.append(network)
    netmask_list.append(netmask)
    broadcast_address_list.append(broadcast_addr)
    
    split_router_addr = broadcast_addr.split('.')
    split_router_addr[3] = str(int(split_router_addr[3]) - 1)
    routers = ".".join(split_router_addr)

    routers_list.append(routers)

    split_ip_end = routers.split('.')
    split_ip_end[3] = str(int(split_ip_end[3]) - 1)
    ip_range_end = ".".join(split_ip_end)

    split_first_ip = network.split('.')
    split_first_ip[3] = str(int(split_first_ip[3]) + 1)
    ip_range_first = ".".join(split_first_ip)

    ip_range = ip_range_first + " " + ip_range_end

    ip_range_list.append(ip_range)


def main(argv):
    for subnet in argv:
        generate_dhcp_subnet(subnet)

    dhcp_config = ""

    for conf_str, conf_value in dhcp_dict.items():
        dhcp_config += conf_str + str(conf_value) + ";\n"

    for i in range (len(subnet_dict.get("subnet "))):
        for subnet_str, subnet_value in subnet_dict.items():
            if subnet_str == "subnet ":
                dhcp_config += subnet_str + subnet_value[i]
            elif subnet_str == " netmask ":
                dhcp_config += subnet_str + subnet_value[i] + " {\n"
            elif subnet_str == "option broadcast-address ": #broadcast-addr doit être en dernier dans le dictionnaire, on ferme la déclaration subnet après cette valeur
                dhcp_config += "\t" + subnet_str + subnet_value[i] + ";\n}\n\n"
            else :
                dhcp_config += "\t" + subnet_str + subnet_value[i] + ";\n"
    print(dhcp_config)
                
            

if __name__ == "__main__":
    main(sys.argv[1:])

