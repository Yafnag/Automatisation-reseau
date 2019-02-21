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

def generate_vlan_interface(interface_name):
    vlan_dict['vlan-raw-device'] = interface_name
    vlan_config = ""
    for i in range (len(subnet_dict.get("subnet"))):
        vlan_config += "auto " + vlan_dict['auto'] + str(i) + "\n"
        vlan_config += "iface " + vlan_dict['auto'] + str(i) + " inet " + vlan_dict['inet'] + "\n"
        vlan_config += "\tvlan-raw-device " + vlan_dict['vlan-raw-device'] + "\n"
        vlan_config += "\taddress " + vlan_dict['address'][i] + "\n"
        vlan_config += "\tnetmask " + vlan_dict['netmask'][i] + "\n"
    return vlan_config

def main(argv):
    for subnet in argv:
        generate_dhcp_subnet(subnet)

    dhcp_config = ""

    for conf_str, conf_value in dhcp_dict.items():
        dhcp_config += conf_str + str(conf_value) + ";\n"

    for i in range (len(subnet_dict.get("subnet"))): #on récupère le nombre de subnet à déclarer et on boucle
        dhcp_config += "subnet " +  subnet_dict['subnet'][i] + " netmask " + subnet_dict['netmask'][i] + " {\n"
        dhcp_config += "\toption routers " + subnet_dict['routers'][i] + ";\n"
        dhcp_config += "\trange " + subnet_dict['range'][i] + ";\n"
        dhcp_config += "\toption broadcast-address " + subnet_dict['broadcast'][i] + ";\n}\n\n"

    vlan_config = generate_vlan_interface("enp0s3")
    print(dhcp_config)
    print(vlan_config)
                
            

if __name__ == "__main__":
    main(sys.argv[1:])

