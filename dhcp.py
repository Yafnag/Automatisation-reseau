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

iface_list = []


#Fonction generate_dhcp_subet :
#Prend en argument une chaine de caractère qui est un réseau et son masque sous la notation CIDR (ex : 192.168.0.0/24)
#Génère automatiquement le réseau, netmask, adresse broadcast, adresse du routeur et le range d’adresse IP
#Remplie les listes correspondant à chaque caractéristique du réseau
def generate_dhcp_subnet(subnet):    
    net = IPv4Network(subnet)
    
    netmask = str(net.netmask)
    network = str(net.network_address)    
    broadcast_addr = str(net.broadcast_address)
    #L'adresse du routeur est calculée avec l'adresse broadcast -1
    routers = str(ipaddress.ip_address(broadcast_addr) - 1)

    #Fin de ip range est calculée avec l'adresse routeur -1 pour exclure le routeur de la plage d'adresse ip
    ip_range_end = str(ipaddress.ip_address(routers) -1)
    ip_range_first = str(ipaddress.ip_address(network) + 1)
    ip_range = ip_range_first + " " + ip_range_end

    #Test si une variable est vide, si oui exit du script sinon remplissage des listes
    if network != "" and netmask != "" and routers != "" and ip_range != " " and broadcast_addr != "" :
        subnet_list.append(network)
        netmask_list.append(netmask)
        routers_list.append(routers)
        ip_range_list.append(ip_range)
        broadcast_address_list.append(broadcast_addr)
    else :
        sys.exit("Erreur lors du remplissage des listes subnet")

#Fonction generate_vlan_interface :
#Génère automatiquement les interfaces virtuelles en se basant sur les listes remplie par la fonction ‘generate_dhcp_subnet’ et sur un dictionnaire.
#Remplie la liste des interfaces virtuelles qui sera utilisé pour le fichier 'isc-dhcp-server'
#Retourne une chaîne de caractères : la configuration vlan à ajouter au fichier ‘interfaces’
def generate_vlan_interface():
    vlan_config = ""
    #Boucle sur la longueur de la liste subnet_list pour créer les différentes interfaces
    for i in range (len(subnet_list)):
        vlan_config += "auto {}{}\niface {}{} inet {}\n\tvlan-raw-device {}\n\taddress {}\n\tnetmask {}\n\n".format(conf['vlan_dict']['auto'],
                                                                                                                  i+1,
                                                                                                                  conf['vlan_dict']['iface'],
                                                                                                                  i+1,
                                                                                                                  conf['vlan_dict']['inet'],
                                                                                                                  conf['vlan_dict']['vlan-raw-device'],
                                                                                                                  routers_list[i],
                                                                                                                  netmask_list[i])
        #Ajoute le nom des différentes interfaces virtuelle dans une liste
        iface_list.append(conf['vlan_dict']['iface'] + str(i+1))
    return vlan_config

#Fonction generate_dhcp_iface_file
#Prend en argument la liste des interfaces remplie pendant l'execution de la fonction "generale_vlan_interface"
#Boucle sur la longueur de cette liste et met en forme le texte pour le fichier de configuration "isc-dhcp-server"
#Retourne une chaîne de caractères : la configuration à écrire dans le fichier
def generate_dhcp_iface_file(interfaces_list):
    interfaces = ""
    #Boucle sur la liste d'interfaces et création du string de configuration "interfaces" pour le fichier isc-dhcp-server
    for iface in interfaces_list:
        interfaces += iface + " "

    file_conf = "INTERFACESv4=\"{}\"".format(interfaces)
    return file_conf

#Fonction main
#Mise en forme de la configuration dhcpd
#Affichage et vérification par l’utilisateur avant modification ou création de fichier
#Backup des fichiers de configuration déjà existants
#Prend en argument la liste de réseau passé en argument au script grâce à "--subnets"
def main(argv):
    for subnet in argv:
        generate_dhcp_subnet(subnet)

    dhcp_config = ""
    #Début de la config dhcpd grâce au dictionnaire "dhcp_dict" de la configuration yaml
    for conf_str, conf_value in conf['dhcp_dict'].items():
        dhcp_config += conf_str + " " + str(conf_value) + ";\n"

    #Boucle sur le nombre de subnet de la liste subnet_list et déclaration des subnets grâces aux valeurs présentes dans les listes
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
        if os.path.isfile(conf['dhcpd_file_name']):
            #Si le fichier dhcpd.conf existe alors backup
            try:
                shutil.copyfile(conf['dhcpd_file_name'], conf['dhcpd_file_name'] + '.bak')
            except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors du backup de dhcpd.conf")

        #Ouverture du fichier dhcpd.conf avec l'attribut "w" afin d'écraser et écrire la nouvelle configuration
        try:
            dhcpd = open(conf['dhcpd_file_name'], "w")
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
        if os.path.isfile(conf['iface_file_name']):
            #Backup du fichier interfaces 
            try:
                shutil.copyfile(conf['iface_file_name'], conf['iface_file_name'] +'.bak')
            except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors du backup du fichier interfaces")

        #Ouverture du fichier interfaces avec l'attribut "a" donc écriture de la configuration vlan en fin de fichier
        try:
            interfaces = open(conf['iface_file_name'], "a")
            interfaces.write("\n\n" + vlan_config)
        except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors de l'écriture du fichier interfaces")
        interfaces.close()
        print("Le fichier interface a été modifié")
    else :
        sys.exit("Relancer le script afin de générer la configuration VLAN qui vous convient")

    isc = generate_dhcp_iface_file(iface_list)
    if os.path.isfile(conf['dhcp_interface_file']):
        #Si le fichier dhcpd.conf existe alors backup
        try:
            shutil.copyfile(conf['dhcp_interface_file'], conf['dhcp_interface_file'] + '.bak')
        except OSError as err:
            print("OS error: {0}".format(err))
            sys.exit("Erreur lors du backup de isc-dhcp-server")

        #Ouverture du fichier isc-dhcp-server avec l'attribut "w" afin d'écraser et écrire la nouvelle configuration
        try:
            dhcpd = open(conf['dhcp_interface_file'], "w")
            dhcpd.write(isc)
        except OSError as err:
                print("OS error: {0}".format(err))
                sys.exit("Erreur lors de l'écriture du fichier isc-dhcp-server")
        dhcpd.close()
        print("Le fichier isc-dhcp-server a été généré\n\n")
            

if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description="Editer le fichier de configuration conf.yaml.\n"+
        "\t- Renseigner les serveurs DNS qui seront attribués par le serveur DHCP à la ligne \"option domain-name-servers\".\n"+
        "\t- Renseigner le nom de l'interface réseau sur laquel seront générés les VLANs à la ligne \"vlan_raw_device\"\n"+
        "\t- Configurer les chemins d'accès aux fichiers de configurations \"isc-dhcp-server\", \"dhcpd.conf\" et \"interfaces\"\n\n"+
        "python dhcp.py -c path/to/conf.yaml -s subnet1/netmask1CIDR subnet2/netmask2CIDR...\n\n"+
        "Exemple :\n"+
        "python dhcp.py -c./ conf.yaml -s 192.168.0.0/25 192.168.0.128/27 192.168.0.160/28 192.168.0.176/28 192.168.0.192/29", formatter_class=RawTextHelpFormatter)
    #Ajout de l'argument --subnets pour déclarer les différents réseau à passer en argument au script
    parser.add_argument('-s','--subnets', nargs='+', default=[])
    #Ajout de l'argument --config pour le chemin vers le fichier de configuration yaml
    parser.add_argument('-c','--config', dest='filename', required=True, help="Chemin vers le fichier de configuration")
    args=parser.parse_args()

    #Load le fichier de configuration yaml
    try:
        conf = yaml.load(open(args.filename))
    except OSError as err:
        print("OS error: {0}".format(err))
        sys.exit("Erreur lors de l'ouverture du fichier de configuration")

    #Tri des réseau par le masque de sous réseau en notation CIDR pour classer par ordre croissant
    order_network = sorted(args.subnets, key=lambda x: int(x.rsplit('/',1)[1]))
    main(order_network)

