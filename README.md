# dhcp.py - Script d'automatisation

Le but de ce script est de générer de manière automatique une configuration DHCP pour dhcpd qui est un programme de serveur DHCP, et générer les différentes interfaces virtuelles dans le fichier "interfaces" de Linux.

## Arguments du scripts

`dhcp.py -h` <br/>
L'arguement "--help" est utilisé afin de consulter l'aide concernant l'utilisation du script.<br/><br/>

`dhcp.py -c ./conf.yaml` <br/>
L'argument --config est utilisé pour déclarer le fichier de configuration yaml, le chemin vers le fichier de configuration doit être indiqué.<br/><br/>

`dhcp.py -s 192.168.0.0/24` <br/>
L'argument --subnets est utilisé pour déclarer les différents subnets à déclarer dans la configuration dhcp.<br/><br/>

## Fichier de configuration

Tout dabord, éditer le fichier de configuration conf.yaml.<br/>
	- Renseigner les serveurs DNS qui seront attribués par le serveur DHCP à la ligne `option domain-name-servers`. Par défaut ce sont les DNS google qui sont utilisés (8.8.8.8, 8.8.4.4).<br/>
	- Renseigner le nom de l'interface réseau sur laquel seront généré les interfaces virtuelles à la ligne `vlan-raw-device`.<br/>
	- Configurer les chemins d'accès aux fichiers de configurations "isc-dhcp-server", "dhcpd.conf" et "interfaces"<br/><br/>
	
## Utilisation du script

Une fois la configuration sauvegardée, éxecutez le script de la manière suivante :<br/>
`python dhcp.py -c path/to/conf.yaml -s subnet1/netmask1CIDR subnet2/netmask2CIDR...`<br/><br/>

## Exemple :

Générer une configuration DHCP pour les réseaux :<br/>
	- 192.168.0.0/25<br/>
	- 192.168.0.128/27<br/>
	- 192.168.0.160/28<br/>
	- 192.168.0.176/28<br/>
	- 192.168.0.192/29<br/><br/>
	
Executez le script de la manière suivante :<br/><br/>

`python dhcp.py -c ./conf.yaml -s 192.168.0.0/25 192.168.0.128/27 192.168.0.160/28 192.168.0.176/28 192.168.0.192/29`<br/><br/>

Automatiquement le script va génrer la configuration DHCP et demander confirmation avant de l'exporter<br/><br/>
```shell
Cette configuration DHCP vous convient-elle ? (Y/N)
```
<br/>

Idem pour la configuration du fichier interfaces <br/><br/>
```shell
La configuration VLAN vous convient-elle ? (Y/N)
```

## Licence
License:BSD-3-Clause