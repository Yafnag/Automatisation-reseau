# dhcp.py - Script d'automatisation

Le but de ce script est de générer de manière automatique une configuration DHCP pour dhcpd qui est un programme de serveur DHCP, et générer les différentes interfaces virtuel qui se configurent dans le fichier "interfaces" de Linux.

## Utilisation
`dhcp.py -h`
Le script est dotté d'un arguement "-h" afin de consulter l'aide concernant l'utilisation de ce dernier.

Pour executer le script il faut commencer par editer le fichier de configuration conf.yaml.
	- Renseigner les serveurs DNS qui seront attribués par le serveur DHCP à la ligne `option domain-name-servers`.
	- Renseigner le nom de l'interface réseau sur laquel seront généré les VLANs à la ligne `device_name = "EXAMPLE"`.
	
Une fois le fichier de configuration modifié et sauvegarder il suffit d'éxecuter le script de la manière suivante :
`python dhcp.py -s subnet1/netmask1CIDR subnet2/netmask2CIDR...`

## Exemple :

Afin de générer une configuration DHCP pour les réseaux :
	- 192.168.0.0/25
	- 192.168.0.128/27
	- 192.168.0.160/28
	- 192.168.0.176/28
	- 192.168.0.192/29
	
Il faut donc appeler notre script de la manière suivante :

`python dhcp.py -s 192.168.0.0/25 192.168.0.128/27 192.168.0.160/28 192.168.0.176/28 192.168.0.192/29`

Automatiquement le script va génrer la configuration DHCP et demander confirmation avant de l'exporter

`Cette configuration DHCP vous convient-elle ? (Y/N)`

Idem pour la configuration du fichier interfaces 

`La configuration VLAN vous convient-elle ? (Y/N)`