# Importation des modules
# Module discord
import discord
# Module proxmoxer
from proxmoxer import ProxmoxAPI
# Module re
import re
# Module datetime
import datetime
# Module random pour les réponses aléatoires
import random
# Module youtube_dl pour la lecture de musique
import youtube_dl
# Module asyncio pour la synchronisation des tâches
import asyncio
import json

# Configuration des informations proxmox
# Adresse IP du serveur Proxmox
proxmox_host = '176.145.10.88:8006'
# Username et mot de passe de l'utilisateur Proxmox
username = 'projet@pve'
# Mot de passe de l'utilisateur Proxmox
password = 'projet'
# Nom du noeud Proxmox
proxmox_node = 'SRV-HADES'
# Nom du token d'authentification Proxmox
token_name = 'bot_discord'
# Valeur du token d'authentification Proxmox
token_value='5332b6cd-8b9e-4c46-9bb2-be56530f11e3'

# Configuration du bot discord
# Token du bot discord
bot_token = 'MTA2MDkyMzM3NjE2NTcyMDEyNA.GJohmF.lOhzjpGH6vTtsH5nXRxHE38_1-n9VWr43Rsxpw'
# Nom du rôle admin
admin_role = 'Administrateur'
# Version du bot
version = "0.1.6"



# Load the configuration from a JSON file
with open("config.json", "r") as f:
    config = json.load(f)

# Connexion au serveur Proxmox en utilisant un jeton d'authentification
# Vérification du certificat SSL désactivée
proxmox = ProxmoxAPI(proxmox_host, user=username, token_name=token_name, token_value=token_value, verify_ssl=False)

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")
    guild = bot.guilds[0]
    members_count = len(guild.members)
    activity = discord.Activity(name=f'{members_count} members', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)

# Fonction qui récupère le prochain vmid disponible pour la commande createCT
def nextvmid():
    netmax = 0
    othermax = 0
    # pour chaque vm dans la liste des vm
    for vm in proxmox.cluster.resources.get(type='vm'):
        # récupération du vmid
        vmid = vm['vmid']
        # si le vmid est supérieur à 3300
        if vmid > 3300:
            # si le vmid est supérieur à netmax
            if vmid > netmax:
                # Netmax prend la valeur du vmid
                netmax = vmid
        # sinon si le vmid est inférieur à 3300
        else:
            # si le vmid est supérieur à othermax
            if vmid > othermax:
                # othermax prend la valeur du vmid
                othermax = vmid
    # si othermax est inférieur à 3300-1
    if othermax < 3300-1:
        # retourne 3300
        return othermax+1
    # sinon
    else:
        # retourne netmax+1
        return netmax+1
    
# Fonction qui génère des reponses automatiques
@bot.event
async def on_message(message):
    # On vérifie que le bot ne réponde pas à lui même
    if message.author == bot.user:
        return
    # le bot répond a salut et bonjour avec une réponse aléatoire
    if message.content.lower() in ["bonjour", "salut"]:
        responses = [f"Salut {message.author.name} !", f"Bonjour {message.author.name} !", f"Salutations {message.author.name} !"]
        await message.channel.send(random.choice(responses))
    # le bot répond a salut avec une réponse
    if "merci" in message.content.lower():
        await message.channel.send("De rien!")
    # le bot répond a salut avec une réponse
    if "arabe" in message.content.lower():
        probability = 0.3 # 50% chance of sending
        if random.random() < probability:
            responses = ["Oui, ils sont gentils", "Arrêtez de vous moquer des Arabes !", "Ce n'est pas très gentil ça !"]
            await message.channel.send(random.choice(responses))
    # le bot répond a salut avec une réponse
    if "bombe" in message.content.lower():
        await message.channel.send("La spécialité de Narcos")
    # le bot répond a salut avec une réponse
    if "xeinmod" in message.content.lower():
        await message.channel.send("Il est mon ennemie juré")
    if message.content.lower() in ["ratio", "Ratio","RATIO"]:
        ratio_emoji = discord.utils.get(message.guild.emojis, name="ratio")
        await message.channel.send(ratio_emoji)
    # le répond a quoi avec une réponse feur    
    if "quoi" in message.content.lower():
        await message.channel.send("feur")

# Commande général discord
@bot.command(name='userinfo', description='Affiche les informations d\'un utilisateur')
# pycord will figure out the types for you
async def userinfo(ctx, member: discord.Member = None):
  
  # Si aucun membre n'est spécifié, on prend l'auteur du message
    if member is None:
        # Récupération de l'auteur du message
        member = ctx.author
    
    # Définir des réponses plus lisibles pour le statut
    status_dict = {
        discord.Status.online: "En ligne",
        discord.Status.idle: "Inactif",
        discord.Status.dnd: "Ne pas déranger",
        discord.Status.offline: "Hors ligne"
    }
    
    # Récupération des informations du serveur
    guild = ctx.guild
    # Récupération de l'information de statut plus lisible
    status = status_dict.get(member.status, member.status)
    # Récupération des dates d'inscription au serveur
    joined_at = member.joined_at.strftime("%d/%m/%Y %H:%M:%S")
    # Récupération des rôles
    roles = [role.mention for role in member.roles]
    # Récupération de la date de création du compte
    created_at = member.created_at.strftime("%d/%m/%Y %H:%M:%S")
    # Vérification si l'utilisateur a boosté le serveur
    is_boosted = "Oui" if member.premium_since else "Non"
    
    # Affichage des informations de l'utilisateur
    embed = discord.Embed(title=f"Informations sur {member}", description=f"Voici les informations disponibles sur {member}.", color=0x3232ff)
    # Id de l'utilisateur
    embed.add_field(name="🆔 ID de l'utilisateur", value=member.id, inline=False)
    # Nom de l'utilisateur
    embed.add_field(name="✅ Statut", value=status, inline=False)
    # Rôles de l'utilisateur
    embed.add_field(name="🔖 Rôles", value=", ".join(roles), inline=False) 
    # Date de création du compte
    embed.add_field(name="📅 Date de création du compte", value=created_at, inline=False)
    # Date d'inscription sur le serveur
    embed.add_field(name=f"📅 Date d'inscription sur le serveur {guild.name}", value=joined_at, inline=False)
    # Si l'utilisateur a boosté le serveur
    embed.add_field(name="💻 Booster du serveur", value=is_boosted, inline=False)
    # Si l'utilisateur joue à un jeu
    if member.activity:
        # Récupération du nom du jeu et du type de jeu
        activity_name = member.activity.name
        activity_type = member.activity.type
        # Ajout du jeu à l'embed
        embed.add_field(name="🎮 Dernière activité", value=f"{activity_type.name} : {activity_name}", inline=False)
    # Si l'utilisateur ne joue pas à un jeu
    else:
        # Ajout d'un message par défaut
        embed.add_field(name="🎮 Dernière activité", value="Aucune activité en cours", inline=False)
    # Ajout de l'avatar de l'utilisateur
    embed.set_thumbnail(url=member.avatar.url)
    # Envoi de l'embed
    await ctx.respond(embed=embed)
    
# Fonction qui affiche les informations du serveur
@bot.command(name="serverinfo", description="Affiche les informations du serveur.")
async def serverinfo(ctx):
    # Récupération des informations du serveur
    guild = ctx.guild
    # Récupération la liste des membres
    online = len([m for m in guild.members if m.status == discord.Status.online])
    # Récupération des informations sur les salons textuels et vocaux
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    # Création de l'embed
    embed = discord.Embed(title=f"Informations sur {guild.name}", description=f"Voici les informations disponibles sur {guild.name}.", color=0x3232ff)
    # Ajout des informations
    # Propriétaire du serveur
    embed.add_field(name="👑 Propriétaire", value=guild.owner, inline=False)
    # Nombre de membres
    embed.add_field(name="🌐 Nombre total de membres", value=guild.member_count, inline=False)
    # Date de création du serveur
    embed.add_field(name="📆 Création", value=guild.created_at)
    # Nombre de membres en ligne
    embed.add_field(name="🟢 Membres en ligne", value=online, inline=False)
    # Nombre de salons textuels et vocaux
    embed.add_field(name="💬 Nombre de salons textuels", value=text_channels, inline=False)
    embed.add_field(name="🔊 Nombre de salons vocaux", value=voice_channels, inline=False)
    # Ajout de l'icône du serveur
    embed.set_thumbnail(url=ctx.guild.icon.url)
    # Envoi de l'embed
    await ctx.respond(embed=embed)

# Fonction qui affiche les informations du bot 
@bot.command(name="botinfo", description="Affiche les informations du bot.")
async def botinfo(ctx):
    # Informations sur le bot
    embed = discord.Embed(title="Informations de ThiBot", color=0x3232ff, description="Un bot pour gérer les noeuds Proxmox de l'infrastructure de Thibault")
    # Ajout du nom du bot
    embed.add_field(name="👑 Nom", value=bot.user.name)
    # Ajout de l'ID du bot
    embed.add_field(name="✅ ID", value=bot.user.id)
    # Ajout de la version du bot
    embed.add_field(name="📆 Version du bot", value=version, inline=False)
    # Ajout du nom du créateur
    embed.add_field(name="💼 Créateur", value="Thibault", inline=False)
    # Ajout de la version de discord.py
    embed.add_field(name="🌐 Version de discord.py", value=discord.__version__, inline=False)
    # Ajout de l'avatar du bot
    await ctx.respond(embed=embed)
    
# Menu d'aide
@bot.command(name="aide", description="Affiche les commandes disponibles.")
async def aide(ctx):
    # Création du menu
    help_embed = discord.Embed(title="👨‍💻 Aide pour les commandes et fonctions du BOT ThiBot", color=0x3232ff)
    # Ajout des commandes
    help_embed.add_field(name="createct {password}", value="Permet de créer un conteneur LXC sur Proxmox avec votre nom.", inline=False)
    help_embed.add_field(name="listvm", value="Permet de lister les machines virtuelles sur Proxmox", inline=False)
    help_embed.add_field(name="vm {id}", value="Permet de démarrer une VM", inline=False)
    help_embed.add_field(name="date {id}", value="Permet d'afficher la date du jour", inline=False)
    help_embed.add_field(name="stopvm {id}", value="Permet de fermer une VM", inline=False)
    help_embed.add_field(name="ct {id}", value="Permet de démarrer un CT", inline=False)
    help_embed.add_field(name="stopct {id}", value="Permet de fermer un CT", inline=False)
    help_embed.add_field(name="vminfo {id}", value="Permet d'afficher les informations d'une VM", inline=False)
    help_embed.add_field(name="play {url}", value="Permet de jouer de la musique", inline=False)
    help_embed.add_field(name="leave", value="Permet de faire quitter le bot du salon vocal", inline=False)
    help_embed.add_field(name="next", value="Permet de passer à la musique suivante", inline=False)
    help_embed.add_field(name="pause", value="Permet de mettre en pause la musique", inline=False)
    help_embed.add_field(name="resume", value="Permet de reprendre la musique", inline=False)

    # Envoi du menu
    await ctx.respond(embed=help_embed)
    
# Fonction qui affiche la date et l'heure
@bot.command(name="date", description="Affiche la date et l'heure.")
async def date(ctx):
    # Affichage de la date et de l'heure
    now = datetime.datetime.now()
    await ctx.respond(f"Nous sommes le {now.day}/{now.month}/{now.year} et il est {now.hour}:{now.minute}")

# Fonction qui permet de ping le bot   
@bot.command(name="ping", description="Affiche le ping du bot.")
async def ping(ctx):
    # Affichage du ping
    await ctx.respond(f"Je suis sur {len(bot.guilds)} serveurs et mon ping est de {round(bot.latency * 1000)}ms")
    

@bot.command(name="custom_embed", description="Crée un embed personnalisé.")
async def custom_embed(ctx, name: str, description: str):
    embed = discord.Embed(title=name, description=description, color=0x3232ff)
    embed.set_footer(text="ThiBot", icon_url="https://images-ext-2.discordapp.net/external/fLkC9Af3Wm2PqMHffcw48pdoswl2boTQmmDrmKD19HI/%3Fsize%3D1024/https/cdn.discordapp.com/icons/717011432947974218/a7853be6f55749f86dabef85add88ca5.png")
    await ctx.respond(embed=embed)

# Commande proxmox

# Fonction qui crée un CT
@bot.command(guild_ids=[717011432947974218], name="createct", description="Crée un conteneur LXC sur Proxmox avec votre nom.")
# Vérification que l'utilisateur a bien rentré un mot de passe
async def createct(ctx, password, os):
    
    # Récupération du prochain vmid disponible
    vmidCT = nextvmid()
    
    # Création du nom du CT
    vmname = ctx.author.name
    # Suppression des caractères spéciaux
    vmname = re.sub(r'[^\w\s]', '', vmname)
    # Suppression des espaces
    vmname = vmname.replace(" ","")
    # Ajout du préfixe
    vmname = f'CT-{vmname}'
    # si l'os est debian
    if os == "debian":
        # on récupère le template debian 10
        os = "local:vztmpl/debian-10-standard_10.7-1_amd64.tar.gz"
    # si l'os est ubuntu
    if os == "ubuntu":
        # on récupère le template ubuntu 22.10
        os = "local:vztmpl/ubuntu-22.10-standard_22.10-1_amd64.tar.zst"
    # si l'os est vide
    if os == None:
        # on affiche un message d'erreur
        await ctx.respond("Vous devez choisir un OS")
        return
    # si l'os n'est pas debian ou ubuntu
    if os != "debian" or os != "ubuntu":
        #
        await ctx.respond("Vous devez choisir un OS valide")
        return
    
    # Création du CT
    node = proxmox.nodes(proxmox_node)
    node.lxc.create(vmid=vmidCT,
    ostemplate=os, # Template Debian 10
    hostname=vmname, # Nom du CT
    storage='local-lvm', # Stockage local
    memory=1024, # 1Go de RAM
    swap=1024, # 1Go de swap
    cores=1, # 1 coeur processeur
    password=password, # Mot de passe root
    net0='name=eth0,bridge=vmbr0,ip=dhcp') # Interface réseau DHCP
    
    # Retour de la commmande discord
    await ctx.respond(f'Vous venez de créer votre {vmname} portant le numéro {vmidCT}, le mot de passe est {password}')

# Fonction qui permet d'afficher les informations d'une VM
@bot.command(guild_ids=[717011432947974218], name="vminfo", description="Affiche les informations d'une VM.")
async def vminfo(ctx, vmid:int):
    # récupération de la liste des vms
    vms = proxmox.cluster.resources.get(type='vm')
    # pour toute vm dans la liste
    for vm in vms:
        # si l'id de la vm est égale à l'id passé en paramètre
        if vm['vmid'] == vmid:
            # si la vm est un container
            if vm['type'] == 'lxc':
                # récupération des informations du lxc
                config = proxmox.nodes(vm['node']).lxc(vm['vmid']).config.get()
                # création de l'embed
                # ID du lxc
                embed = discord.Embed(title="✅ CT ID: {}".format(vm['vmid']), description="Name: {}".format(config['hostname']), color=0x3232ff)
                # Icone proxmox
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
                # status du lxc
                if vm['status'] == 'running':
                    embed.add_field(name="💻 Status", value="🟢 En marche", inline=False)
                elif vm['status'] == 'stopped':
                    embed.add_field(name="💻 Status", value="🔴 Arrêté", inline=False)
                # noeud du lxc
                embed.add_field(name="🖥️ Noeud", value=vm['node'], inline=False)
                # mémoire du lxc
                embed.add_field(name="🧠 Mémoire RAM", value=str(config['memory']) + "MB", inline=True)
                # coeurs du lxc
                embed.add_field(name="💻 Nombres de coeurs CPU", value=str(config['cores']), inline=True)
                # uptime du lxc
                embed.add_field(name="⏱️ Uptime", value=f"{vm['uptime']}s", inline=False)
                # ajout du système d'exploitation
                # si os type est défini
                if 'ostype' in config:
                    # si os type est debian
                    if config['ostype'] == 'debian':
                        # ajout de l'os type à l'embed
                        embed.add_field(name="💻 Système d'exploitation", value="Debian", inline=False)
                    # si os type est ubuntu
                    if config['ostype'] == 'ubuntu':
                        # ajout de l'os type à l'embed
                        embed.add_field(name="💻 Système d'exploitation", value="Ubuntu", inline=False)
                    # si os type est centos
                    if config['ostype'] == 'centos':
                        # ajout de l'os type à l'embed
                        embed.add_field(name="💻 Système d'exploitation", value="CentOS", inline=False)
                    # si os type est fedora
                    if config['ostype'] == 'fedora':
                        # ajout de l'os type à l'embed
                        embed.add_field(name="💻 Système d'exploitation", value="Fedora", inline=False)
                # ajout de l'adresse IP à l'embed
                embed.add_field(name="💻 Réseau", value=str(config['net0']), inline=False)
                # taille du disque du lxc
                # si disque ide0 est configuré
                if 'ide0' in config:
                    embed.add_field(name="💾 Disque Ide", value=str(config['ide0']) + "B", inline=False)
                # si disque scsi0 est configuré
                elif 'scsi0' in config:
                    embed.add_field(name="💾 Disque Scsi", value=str(config['scsi0']) + "B", inline=False)
                # si aucun disque n'est configuré
                else:
                    embed.add_field(name="💾 Disque", value="Aucun disque configuré", inline=False)
                # envoie de l'embed
                await ctx.respond(embed=embed)
                # fin de la fonction
                return
            # si la vm est une machine virtuelle
            else:
                # récupération des informations de la vm
                config = proxmox.nodes(vm['node']).qemu(vm['vmid']).config.get()
                # création de l'embed
                # ID de la vm
                embed = discord.Embed(title="✅ VM ID: {}".format(vm['vmid']), description="Name: {}".format(config['name']), color=0x3232ff)
                # Icone proxmox
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
                # status de la vm
                if vm['status'] == "running":
                    embed.add_field (name="💻 Status", value="🟢 En marche", inline=False)
                elif vm['status'] == "stopped":
                    embed.add_field (name="💻 Status", value="🔴 Arrêtée", inline=False)
                # noeud de la vm
                embed.add_field (name="🖥️ Noeud", value=vm['node'], inline=False)
                # mémoire de la vm
                embed.add_field (name="🧠 Mémoire RAM", value=str(config['memory']) + "MB", inline=True)
                # coeurs de la vm
                embed.add_field (name="💻 Nb coeurs CPU", value=str(config['cores']), inline=True)
                # uptime de la vm
                embed.add_field(name="⏱️ Uptime", value=f"{vm['uptime']}s", inline=False)
                # ajout du système d'exploitation
                # si os type est défini
                if 'ostype' in config:
                    ostype = str(config['ostype'])
                    if ostype == "l26":
                        ostype = "Linux 2.6/3.x/4.x (64-bit)"
                    if ostype == "l24":
                        ostype = "Linux 2.4 (32-bit)"
                    if ostype == "w2k":
                        ostype = "Windows 2000"
                    if ostype == "w2k3":
                        ostype = "Windows 2003"
                    if ostype == "w2k8":
                        ostype = "Windows 2008"
                    if ostype == "wvista":
                        ostype = "Windows Vista"
                    if ostype == "win7":
                        ostype = "Windows 7, 2008 R2"
                    if ostype == "win8":
                        ostype = "Windows 8, 2012"
                    if ostype == "win10":
                        ostype = "Windows 10, 2016, 2019"
                    if ostype == "other":
                        ostype = "Autre"
                    if ostype == "win11":
                        ostype = "Windows 11, 2022"
                # ajout de l'os type à l'embed
                embed.add_field(name="💻 Système d'exploitation", value=ostype, inline=False)
                # ajout de l'adresse IP à l'embed
                embed.add_field(name="💻 Réseau", value=str(config['net0']), inline=False)
                # taille du disque de la vm
                # si disque ide0 est configuré
                if 'ide0' in config:
                    # ajout du disque ide0 à l'embed
                    embed.add_field(name="💾 Disque Ide", value=str(config['ide0']) + "B", inline=False)
                # si disque scsi0 est configuré
                elif 'scsi0' in config:
                    # ajout du disque scsi0 à l'embed
                    embed.add_field(name="💾 Disque Scsi", value=str(config['scsi0']) + "B", inline=False)
                # si aucun disque n'est configuré
                else:
                    # ajout d'un message disant qu'il n'y a pas de disque configuré
                    embed.add_field(name="💾 Disque", value="Aucun disque configuré", inline=False)
                # envoie de l'embed
                await ctx.respond(embed=embed)
                # fin de la fonction
                return
    # si la vm n'est pas trouvé
    # envoie d'un message d'erreur
    await ctx.respond("Il n'y aucune VM ou CT avec le vmid {}".format(vmid))
    
# commande listvm
@bot.command(guild_ids=[717011432947974218], name="listvm", description="Affiche la liste des VM et CT.")
async def listvm(ctx):
    # récupération du nom du noeud
    vms = proxmox.cluster.resources.get(type='vm')
    # création de l'embed VM
    embedvm = discord.Embed(title=f"Liste des VM de {proxmox_node}", color=0x3232ff)
    # Icone proxmox
    embedvm.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
    # création de l'embed LXC
    embedlxc = discord.Embed(title=f"Liste des containers LXC de {proxmox_node}", color=0x3232ff)
    # Icone proxmox
    embedlxc.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
    # pour chaque vm
    for vm in vms:
        # si la vm est en marche
        if vm['status'] == "running":
            # Création de la variable status
            status = "🟢 En marche"
        # si la vm est arrêtée
        elif vm['status'] == "stopped":
            # Création de la variable status
            status = "🔴 Arrêtée"
        # si la vm est un lxc
        if vm['type'] == "lxc":
            # ajout de la vm à l'embed lxc
            embedlxc.add_field(name=vm['name'], value=f"ID : {vm['vmid']}  | Statut : ({status})", inline=False)
        # si la vm est une vm
        if vm['type'] == "qemu":
            # ajout de la vm à l'embed vm
            embedvm.add_field(name=vm['name'], value=f"ID : {vm['vmid']}  | Statut : ({status})", inline=False)
            
    # envoie des embeds lxc et vm
    await ctx.respond(embed=embedlxc)
    await ctx.respond(embed=embedvm)


# commande startvm
@bot.command(guild_ids=[717011432947974218], name="startvm", description="Démarrer une VM ou CT.")
async def startvm(ctx, vmid: int):
    # récupération des vm
    vms = proxmox.cluster.resources.get(type='vm')
    # pour chaque vm
    for vm in vms:
        # si le vmid saisi est le même que celui de la vm
        if vm['vmid'] == vmid:
            # si la vm est une vm
            if vm['type'] == "lxc":
                # si la vm est en marche
                if vm['status'] == "running":
                    # envoie d'un message d'erreur
                    await ctx.respond("Le container est déjà démarré.")
                    return
                # si la vm est arrêtée
                else:
                    # démarrage de la vm
                    proxmox.nodes(proxmox_node).lxc(vmid).status.start.post()
                    # création de l'embed
                    startembed = discord.Embed(title="Le container a démarré.", color=0x3232ff)
                    # Icone proxmox
                    startembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
                    # ajout des informations du container
                    startembed.add_field(name="Nom du container", value=vm['name'], inline=False)
                    # ajout du vmid du container
                    startembed.add_field(name="ID du container", value=vm['vmid'], inline=False)
                    # ajout du statut du container
                    startembed.add_field(name="Statut du container", value="🟢 En marche", inline=False)
                    # ajout du type du container
                    startembed.add_field(name="Type", value="LXC", inline=False)
                    # envoie de l'embed
                    await ctx.respond(embed=startembed)
                    return
            # si la vm est une vm
            elif vm['type'] == "qemu":
                # si la vm est en marche
                if vm['status'] == "running":
                    # envoie d'un message d'erreur
                    await ctx.respond("La VM est déjà démarré.")
                    return
                # si la vm est arrêtée
                else:
                    # démarrage de la vm
                    proxmox.nodes(proxmox_node).qemu(vmid).status.start.post()
                    # création de l'embed
                    startembed = discord.Embed(title="La VM a démarré.", color=0x3232ff)
                    # Icone proxmox
                    startembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
                    # ajout des informations de la vm
                    startembed.add_field(name="Nom de la VM", value=vm['name'], inline=False)
                    # ajout du vmid de la vm
                    startembed.add_field(name="ID de la VM", value=vm['vmid'], inline=False)
                    # ajout du statut de la vm
                    startembed.add_field(name="Statut de la VM", value="🟢 En marche", inline=False)
                    # ajout du type de la vm
                    startembed.add_field(name="Type", value="QEMU", inline=False)
                    # envoie de l'embed
                    await ctx.respond(embed=startembed)
                    return
                
    # si le vmid saisi n'est pas le même que celui de la vm
    await ctx.respond("Il n'y aucune VM ou CT avec le vmid {}".format(vmid))


# commande stopvm    
@bot.command(guild_ids=[717011432947974218], name="stopvm", description="Démarrer une VM ou CT.")
# récupération du vmid
async def stopvm(ctx, vmid: int):
    # récupération des vm
    vms = proxmox.cluster.resources.get(type='vm')
    # pour chaque vm
    for vm in vms:
        # si le vmid saisi est le même que celui de la vm
        if vm['vmid'] == vmid:
            # si la vm est une lxc
            if vm['type'] == "lxc":
                # si la vm est éteinte
                if vm['status'] == "stopped":
                    # envoie d'un message d'erreur
                    await ctx.respond("Le container est déjà éteint.")
                    return
                # si la vm est en marche
                else:
                    # arrêt de la vm
                    proxmox.nodes(proxmox_node).lxc(vmid).status.stop.post()
                    # création de l'embed
                    stopembed = discord.Embed(title="Le container est éteint.", color=0x3232ff)
                    # Icone proxmox
                    stopembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
                    # ajout des informations du container
                    stopembed.add_field(name="Nom du container", value=vm['name'], inline=False)
                    # ajout du vmid du container
                    stopembed.add_field(name="ID du container", value=vm['vmid'], inline=False)
                    # ajout du statut du container
                    stopembed.add_field(name="Statut du container", value="🔴 Arrêté", inline=False)
                    # ajout du type du container
                    stopembed.add_field(name="Type", value="LXC", inline=False)
                    # envoie de l'embed
                    await ctx.respond(embed=stopembed)
                    return
            # si la vm est une vm
            elif vm['type'] == "qemu":
                # si la vm est éteinte
                if vm['status'] == "stopped":
                    # envoie d'un message d'erreur
                    await ctx.respond("La VM est déjà éteinte.")
                    return
                # si la vm est en marche
                else:
                    # arrêt de la vm
                    proxmox.nodes(proxmox_node).qemu(vmid).status.stop.post()
                    # création de l'embed
                    stopembed = discord.Embed(title="La VM est éteinte.", color=0x3232ff)
                    # Icone proxmox
                    stopembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
                    # ajout des informations de la vm
                    stopembed.add_field(name="Nom de la VM", value=vm['name'], inline=False)
                    # ajout du vmid de la vm
                    stopembed.add_field(name="ID de la VM", value=vm['vmid'], inline=False)
                    # ajout du statut de la vm
                    stopembed.add_field(name="Statut de la VM", value="🔴 Arrêté", inline=False)
                    # ajout du type de la vm
                    stopembed.add_field(name="Type", value="LXC", inline=False)
                    # envoie de l'embed
                    await ctx.respond(embed=stopembed)
                    return
                
    # si le vmid saisi n'est pas le même que celui de la vm
    await ctx.respond("Il n'y aucune VM ou CT avec le vmid {}".format(vmid))
        

# Liste des musiques en cours de lecture
musics = {}
# Liste des musiques en attente
ytdl = youtube_dl.YoutubeDL()

# Fonction qui permet de charger une vidéo youtube en mp3
class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

# Commande pour que le bot quitte le salon vocal
@bot.command(name="leave" , description="Faire quitter le bot du salon vocal.")
async def leave(ctx):
    # Récupération du client
    client = ctx.guild.voice_client
    # Si le client n'existe pas ou n'est pas connecté
    if not client or not client.is_connected():
        # Envoie d'un message d'erreur
        await ctx.respond("Aucune musique n'est en train d'être jouée.")
        return
    # Déconnexion du client
    await client.disconnect()
    # Suppression de la liste des musiques
    musics[ctx.guild] = []
    # Envoie d'un message de confirmation
    await ctx.respond("Le bot a quitté le salon vocal.")

# Commande pour relancer la musique
@bot.command(name="resume" , description="Relance la musique.")
async def resume(ctx):
    # Récupération du client
    client = ctx.guild.voice_client
    # Si le client n'existe pas ou n'est pas connecté
    if not client or not client.is_connected():
        # Envoie d'un message d'erreur
        await ctx.respond("Aucune musique n'est en train de jouer.")
        return
    # Si la musique est déjà en train de jouer
    if client.is_playing():
        # Envoie d'un message d'erreur
        await ctx.respond("La musique est déjà en train de jouer.")
        return
    # Si la musique est en pause
    if client.is_paused():
        # Relance la musique
        client.resume()
        # Envoie d'un message de confirmation
        await ctx.respond("La musique est relancée.")
        
# Commande pour mettre pause à la musique
@bot.command(name="pause" , description="Mettre en pause la musique.")
async def pause(ctx):
    # Récupération du client
    client = ctx.guild.voice_client
    # Si le client n'existe pas ou n'est pas connecté
    if client is None or client.is_playing() is False:
        # Envoie d'un message d'erreur
        await ctx.respond("Aucune musique en cours de lecture ou musique déjà en pause.")
        return
    # Mise en pause de la musique
    client.pause()
    await ctx.respond("La musique est en pause.")


# Commande pour skip une musique
@bot.command(name="skip" , description="Passe à la musique suivante.")
async def skip(ctx):
    # Récupération du client
    client = ctx.guild.voice_client
    # Si le client n'existe pas ou n'est pas connecté
    if client is None or not client.is_playing():
        # Envoie d'un message d'erreur
        await ctx.respond("Aucune musique n'est en train d'être lue.")
        return
    # Arrêt de la musique
    client.stop()
    # Envoie d'un message de confirmation
    await ctx.respond("La musique est skip.")


def play_song(client, queue, song):
    # Récupération de la source de la musique
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
    # Fonction qui permet de passer à la musique suivante
    def next(_):
        # Si la liste des musiques n'est pas vide
        if len(queue) > 0:
            # Récupération de la prochaine musique
            new_song = queue[0]
            # Suppression de la musique de la liste
            del queue[0]
            # Lecture de la musique
            play_song(client, queue, new_song)
        # Sinon
        else:
            # Déconnexion du client
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)
    # Lecture de la musique
    client.play(source, after=next)

# Fonction qui permet de vérifier si l'URL est valide
def is_valid_music_url(url):
    # Regex pour vérifier si l'URL est valide
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    match = re.match(youtube_regex, url)
    # Si l'URL est valide
    if match:
        return True
    # Sinon
    else:
        return False

# Commande pour jouer une musique
@bot.command(name="play", description="Lance une musique")
async def play(ctx, url):
    # Récupération du client
    client = ctx.guild.voice_client

    # Si la musique n'est pas valide
    if not is_valid_music_url(url):
        # Envoie d'un message d'erreur
        await ctx.respond("Lien non valide, veuillez fournir une URL valide vers une musique")
        return

    try:
        # Si le client est connecté
        if client and client.channel:
            # Récupération de la vidéo
            video = Video(url)
            # Ajout de la musique à la liste
            musics[ctx.guild].append(video)
            # Envoie d'un message de confirmation
            custom_embed = discord.Embed(title="Musique ajoutée à la file d'attente", description=f"Musique ajoutée à la file d'attente : {video.url}", color=0x3232ff)
            custom_embed.set_author(name="Musique ajoutée à la file d'attente", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
            youtube_miniature = f"https://img.youtube.com/vi/{video.url.split('=')[1]}/0.jpg"
            custom_embed.set_image(url=youtube_miniature)
            # Envoie d'un message de confirmation
            await ctx.respond(embed=custom_embed)
        # Sinon
        else:
            # Récupération du channel vocal
            channel = ctx.author.voice.channel
            # Récupération de la vidéo
            video = Video(url)
            # Création de la liste des musiques
            musics[ctx.guild] = []
            # Ajout de la musique à la liste
            client = await channel.connect()
            # Envoie d'un message de confirmation
            custom_embed = discord.Embed(title="Musique en cours de lecture", description=f"Musique en cours de lecture : {video.url}", color=0x3232ff)
            custom_embed.set_author(name="Musique en cours de lecture", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
            youtube_miniature = f"https://img.youtube.com/vi/{video.url.split('=')[1]}/0.jpg"
            custom_embed.set_image(url=youtube_miniature)
            # Envoie d'un message de confirmation
            await ctx.respond(embed=custom_embed)
            # Lecture de la musique
            play_song(client, musics[ctx.guild], video)
        
    except TimeoutError:
        await ctx.respond("Erreur : Le délai d'attente a été dépassé.")

        
        
        
        
# Commande pour mettre de la musique
@bot.command(name="ratio" , description="Lance une musique ratio")
async def ratio(ctx):
    url="https://www.youtube.com/watch?v=NXcfIYmor0M"
    print("play")
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
        custom_embed = discord.Embed(title="Musique en cours de lecture", description=f"Musique en cours de lecture : {video.url}", color=0x3232ff)
        custom_embed.set_author(name="Musique en cours de lecture", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
        youtube_miniature = f"https://img.youtube.com/vi/{video.url.split('=')[1]}/0.jpg"
        await ctx.respond(embed=custom_embed)
        custom_embed.set_image(url=youtube_miniature)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        custom_embed = discord.Embed(title="Musique en cours de lecture", description=f"Musique en cours de lecture : {video.url}", color=0x3232ff)
        custom_embed.set_author(name="Musique en cours de lecture", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
        youtube_miniature = f"https://img.youtube.com/vi/{video.url.split('=')[1]}/0.jpg"
        custom_embed.set_image(url=youtube_miniature)
        await ctx.respond(embed=custom_embed)
        play_song(client, musics[ctx.guild], video)
        
# Commande pour mettre de la musique
@bot.command(name="erika" , description="Lance une musique erika")
async def erika(ctx):
    url="https://www.youtube.com/watch?v=UQSM3M1I5y8"
    print("play")
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
        custom_embed = discord.Embed(title="Musique en cours de lecture", description=f"Musique en cours de lecture : {video.url}", color=0x3232ff)
        custom_embed.set_author(name="Musique en cours de lecture", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
        youtube_miniature = f"https://img.youtube.com/vi/{video.url.split('=')[1]}/0.jpg"
        custom_embed.set_image(url=youtube_miniature)
        await ctx.respond(embed=custom_embed)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        custom_embed = discord.Embed(title="Musique en cours de lecture", description=f"Musique en cours de lecture : {video.url}", color=0x3232ff)
        custom_embed.set_author(name="Musique en cours de lecture", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
        youtube_miniature = f"https://img.youtube.com/vi/{video.url.split('=')[1]}/0.jpg"
        custom_embed.set_image(url=youtube_miniature)
        await ctx.respond(embed=custom_embed)
        play_song(client, musics[ctx.guild], video)


@bot.command(name="set_welcome_channel", description="Définir le canal de bienvenue et le rôle à attribuer aux nouveaux membres.")
async def set_welcome_channel(ctx, channel: discord.TextChannel, role: discord.Role):
    guild_id = str(ctx.guild.id)
    # Enregistrer le canal de bienvenue et le rôle dans un fichier JSON
    with open("config.json", "r") as f:
        welcome_channels = json.load(f)
    welcome_channels[guild_id] = {"channel_id": channel.id, "role_id": role.id}
    with open("config.json", "w") as f:
        json.dump(welcome_channels, f)
    await ctx.respond(f"Canal de bienvenue défini sur {channel.mention} avec le rôle {role.name}.")
    
@bot.event
async def on_member_join(member):
    # Charger le canal de bienvenue et le rôle enregistrés dans le fichier JSON
    with open("config.json", "r") as f:
        welcome_channels = json.load(f)
    guild_id = str(member.guild.id)
    guild = member.guild
    if guild_id in welcome_channels:
        channel = bot.get_channel(welcome_channels[guild_id]["channel_id"])
        role = guild.get_role(welcome_channels[guild_id]["role_id"])
        # Envoyer un message de bienvenue dans le canal de bienvenue choisi et attribuer le rôle défini
        welcome_embed = discord.Embed(title=f"{member} viens de rejoindre notre serveur !", description=f"Bienvenue sur ce serveur {member.mention} ! Nous espérons que t'a visite sera agréable.", color=0x3232ff)
        welcome_embed.set_author(name="Bienvenue", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
        await channel.send(embed=welcome_embed)
        await member.add_roles(role)

@bot.command()
async def ban(ctx, user: discord.Member, reason=None):
    await ctx.guild.ban(user, reason=reason)
    ban_embed = discord.Embed(title=f"{user} a été banni", color=0x3232ff)
    if reason:
        ban_embed.add_field(name="Raison", value=reason)
    ban_channel = bot.get_channel(1069334147564306542)
    await ban_channel.respond(embed=ban_embed)

@bot.command()
async def kick(ctx, user: discord.Member, reason=None):
    await ctx.guild.kick(user, reason=reason)
    kick_embed = discord.Embed(title=f"{user} a été kick", color=0x3232ff)
    if reason:
        kick_embed.add_field(name="Raison", value=reason)
    kick_channel = bot.get_channel(1069334147564306542)
    await kick_channel.respond(embed=kick_embed)
     
@bot.event
async def on_voice_state_update(member, before, after):
    server_id = str(member.guild.id)
    with open("config.json", "r") as f:
        config = json.load(f)

    if server_id in config:
        voice_channel_id = config[server_id]["voice_channel_id"]
        temp_channel_name = config[server_id]["temp_channel_name"]

        # Check if member joined the specified voice channel
        if after.channel and after.channel.id == voice_channel_id:
            count = 1
            # Loop to check if a channel with the same name exists
            while True:
                channel_name = f"{temp_channel_name} #{count} - {member.display_name}"
                existing_channel = discord.utils.get(after.channel.guild.voice_channels, name=channel_name)
                if existing_channel is None:
                    break
                count += 1

            # Create a new temporary voice channel with the member's name
            temporary_voice_channel = await after.channel.guild.create_voice_channel(
                name=channel_name,
                category=after.channel.category
            )

            # Move the member to the temporary voice channel
            await member.move_to(temporary_voice_channel)

        # Check if the member left the temporary voice channel
        if before.channel and before.channel.name.startswith(temp_channel_name) and before.channel.name.endswith(member.display_name):
            # Delete the empty temporary voice channel
            await before.channel.delete()

        
@bot.command()
async def set_voice_channel_config(ctx, voice_channel: discord.VoiceChannel, temp_channel_name: str):
    server_id = str(ctx.guild.id)
    with open("config.json", "r") as f:
        config = json.load(f)

    config[server_id] = {
        "voice_channel_id": voice_channel.id,
        "temp_channel_name": temp_channel_name
    }

    with open("config.json", "w") as f:
        json.dump(config, f)
    await ctx.respond(f"Configuration du salon vocal définie sur {voice_channel.mention} avec le préfixe {temp_channel_name}.")


        
@bot.command(name="avatar", description="Affiche l'avatar d'un utilisateur")
async def avatar(ctx, member: discord.Member):
    embed = discord.Embed(color=0x3232ff)
    embed.set_author(name=f"Avatar de {member}", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
    embed.set_image(url=member.avatar.url)
    await ctx.respond(embed=embed)
    
@bot.command(name='clear', description='Supprime un nombre de messages')
async def clearmsg(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.respond(f"{amount} messages ont été supprimés !")

@bot.command(name='say', description='Fait dire un message au bot')
async def say(ctx, *, message):
    await ctx.respond(message)
    


# Lancement du bot
bot.run(bot_token)
