
# ThiBot | Bot Discord
## Prérequis
-  Python 3
-  Proxmoxer
-  py-cord
-  Token Discord
-  pytube
- JSON
- re
- datetime
- asyncio
- mariadb
- configparser
- os
- math
- requests

## Description 
Ce bot Discord est conçu pour fonctionner avec Proxmoxer, une bibliothèque Python pour interagir avec l'API Proxmox VE. Il offre de nombreuses fonctionnalités, telles que l'affichage des informations d'un utilisateur, du serveur et du bot, la lecture de musique, la gestion de machines virtuelles, la création de conteneurs, l'affichage des anniversaires et bien plus encore. Il dispose également d'une commande d'aide pour répertorier toutes les commandes disponibles.

Pour utiliser ce bot, vous devrez configurer les informations d'identification de votre serveur Proxmox VE et les ajouter au fichier de configuration du bot. Vous pouvez ensuite inviter le bot sur votre serveur Discord et commencer à l'utiliser en tapant les commandes dans le chat.

N'hésitez pas à explorer les commandes et à ajouter des fonctionnalités supplémentaires pour personnaliser ce bot selon vos besoins.
## Installation
1.  Clonez ce projet
2.  Installez les bibliothèques nécessaires à l'aide de la commande suivante :
`pip install -r requirements.txt` 

3.  Créez un fichier `.env` à la racine du projet et ajoutez votre Token Discord :
`DISCORD_TOKEN=your_token_here` 

4.  Lancez le bot avec la commande suivante : 
`python bot.py`

### Config.ini : 
Le fichier `config.ini` est un fichier de configuration utilisé pour stocker les informations de connexion et de configuration du bot Discord ainsi que du cluster Proxmox. Il contient des sections pour chaque système, avec des clés et des valeurs pour les informations spécifiques.

La section `[PROXMOX]` contient les informations de connexion pour le cluster Proxmox, y compris l'adresse IP et le port du serveur, le nom de l'utilisateur et le nom du nœud Proxmox. Il contient également un jeton d'authentification pour le bot Proxmox, qui est utilisé pour autoriser les requêtes API.

La section `[DISCORD]` contient les informations de connexion du bot Discord, y compris son jeton d'authentification et la version du bot.

La section `[MARIADB]` contient les informations de connexion de la base de données MariaDB utilisée pour stocker les données du bot, y compris l'adresse IP et le nom d'utilisateur, le mot de passe et le nom de la base de données.

Le fichier `config.ini` est utilisé pour stocker les informations de connexion et de configuration de manière centralisée afin que les informations ne soient pas codées en dur dans le code source du bot. Cela permet de modifier les informations de configuration plus facilement sans avoir à modifier directement le code du bot.


## Commandes
Voici les différentes commandes disponibles :

-   👑 /userinfo : Affiche les informations d'un utilisateur.
-   📆 /serverinfo : Affiche les informations du serveur.
-   🌐 /botinfo : Affiche les informations du bot.
-   💬 /aide : Affiche les commandes disponibles.
-   🔊 /date : Affiche la date et l'heure.
-   📈 /level : Affiche le niveau d'un utilisateur.
-   📈 /leaderboard : Affiche le classement des utilisateurs.
-   ▶️ /play : Joue une musique.
-   ⏸️ /stop : Arrête la musique.
-   ⏭️ /skip : Passe à la musique suivante.
-   💻 /vminfo : Affiche les informations d'un VM.
-   💻 /startvm : Démarrer une VM.
-   💻 /stopvm : Arrêter une VM.
-   💻 /listvm : Affiche la liste des VM.
-   💻 /createct : Créer un CT.
-   🎂 /birthday : Affiche les anniversaires du jour.
-   🎂 /setbirthday : Définir son anniversaire.
-   🧑‍💻 /set_welcomechannel : Définir le salon de bienvenue et le role.
-   🧑‍💻 /set_vocalchannel : Définir le salon vocal de création de channel

## Contributeurs
BECHARD Thibault

N'hésitez pas à contribuer à ce projet en ajoutant de nouvelles fonctionnalités ou en améliorant les commandes existantes. Merci de votre soutien ! 🎉
