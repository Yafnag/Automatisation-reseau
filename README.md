# dhcp.py - Script d'automatisation

Le but de ce script est de générer de manière automatique une configuration DHCP pour dhcpd qui est un programme de serveur DHCP, et générer les différentes interfaces virtuel qui se configurent dans le fichier "interfaces" de Linux.

## Utilisation
`dhcp.py -h` <br/>
Le script est dotté d'un arguement "-h" afin de consulter l'aide concernant l'utilisation de ce dernier. <br/><br/>

Pour executer le script il faut commencer par editer le fichier de configuration conf.yaml.<br/>
	- Renseigner les serveurs DNS qui seront attribués par le serveur DHCP à la ligne `option domain-name-servers`. Par défaut ce sont les DNS google qui sont utilisés (8.8.8.8, 8.8.4.4).<br/>
	- Renseigner le nom de l'interface réseau sur laquel seront généré les VLANs à la ligne `vlan-raw-device`.<br/><br/>
	
Une fois le fichier de configuration modifié et sauvegarder il suffit d'éxecuter le script de la manière suivante :<br/>
`python dhcp.py -s subnet1/netmask1CIDR subnet2/netmask2CIDR...`<br/><br/>

## Exemple :

Afin de générer une configuration DHCP pour les réseaux :<br/>
	- 192.168.0.0/25<br/>
	- 192.168.0.128/27<br/>
	- 192.168.0.160/28<br/>
	- 192.168.0.176/28<br/>
	- 192.168.0.192/29<br/><br/>
	
Il faut donc appeler notre script de la manière suivante :<br/><br/>

`python dhcp.py -s 192.168.0.0/25 192.168.0.128/27 192.168.0.160/28 192.168.0.176/28 192.168.0.192/29`<br/><br/>

Automatiquement le script va génrer la configuration DHCP et demander confirmation avant de l'exporter<br/><br/>
```shell
Cette configuration DHCP vous convient-elle ? (Y/N)
```
<br/>

Idem pour la configuration du fichier interfaces <br/><br/>
```shell
La configuration VLAN vous convient-elle ? (Y/N)
```