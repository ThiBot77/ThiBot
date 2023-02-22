'''
ThiBot - Bot Discord pour le serveur Discord de Thibault
Fonction : Gestion du serveur Proxmox SRV-HADES et du serveur Discord de Thibault
Auteur : Thibault BECHARD
Etat : En cours de développement
Version Python : 3.8.5
Version py-cord : 1.6.0
Version proxmoxer : 1.1.1
Version mariadb : 1.5.5
'''


# Importation des modules nécessaires au bon fonctionnement du bot
# Module discord pour la gestion du bot discord et des commandes discord (py-cord)
import discord
# Module proxmoxer pour la gestion du serveur Proxmox (proxmoxer)
from proxmoxer import ProxmoxAPI
# Module re pour la gestion des expressions régulières
import re
# Module datetime pour la gestion des dates et heures
import datetime
# Module random pour les réponses aléatoires du bot
import random
# Module youtube_dl pour la lecture de musique youtube pour la fonction play du bot
import youtube_dl
# Module asyncio pour la synchronisation des tâches asynchrones du bot discord
import asyncio
# Module mariadb pour la gestion de la base de données MariaDB du bot discord
import mariadb
# Module pytube pour la gestion des vidéos youtube
import pytube
# Module configparser pour la gestion du fichier de configuration
import configparser

# Récupération des informations de configuration dans le fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')


# Obtenir la valeur d'une option dans une section particulière
proxmox_host = config.get('PROXMOX', 'proxmox_host')
username = config.get('PROXMOX', 'username')
proxmox_node = config.get('PROXMOX', 'proxmox_node')
token_name = config.get('PROXMOX', 'token_name')
token_value = config.get('PROXMOX', 'token_value')
bot_token = config.get('DISCORD', 'bot_token')
version = config.get('DISCORD', 'version')
mariadb_host = config.get('MARIADB', 'mariadb_host')
mariadb_user = config.get('MARIADB', 'mariadb_user')
mariadb_password = config.get('MARIADB', 'mariadb_password')
mariadb_database = config.get('MARIADB', 'mariadb_database')

# Connexion au serveur Proxmox en utilisant un jeton d'authentification
# --------------------------------------------------------------------
proxmox = ProxmoxAPI(proxmox_host, user=username, token_name=token_name, token_value=token_value, verify_ssl=False)

# Déclaration du bot discord avec les intents de gestion des messages et des réactions discord (py-cord)
# -----------------------------------------------------------------------------------------------------
bot = discord.Bot(intents=discord.Intents.all())


# Début du code du bot discord
# ----------------------------

# Fonction qui affiche les informations du bot discord lors de son démarrage
# ------------------------------------------------------------------------
@bot.event
async def on_ready():
    print("Bot en ligne !")
    print("Connecté en tant que : ")
    print(bot.user.name)
    print(bot.user.id)
    # Vérification de la connexion au serveur Proxmox, si la connexion échoue, affichage d'un message d'erreur sinon affichage d'un message de connexion réussie
    if proxmox is None :
        print("Erreur de connexion au serveur Proxmox")
    else:
        print("Connecté au serveur Proxmox")   
    print("------")
    # Affichage de l'activité du bot discord, ici "Erika Game"
    activity = discord.Activity(name='Erika Game', type=discord.ActivityType.playing)
    await bot.change_presence(activity=activity)
    

# Fonction qui récupère le prochain vmid disponible pour la commande createCT
# --------------------------------------------------------------------------
def nextvmid():
    # Déclaration des variables
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


# Fonction qui génère des reponses automatiques au bot discord lors de l'envoi de messages 
# ---------------------------------------------------------------------------------------
@bot.event
async def on_message(message):
    # On vérifie que le bot ne réponde pas à lui même
    if message.author == bot.user:
        return
    
    # Connexion à la base de données MariaDB
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    if conn is None:
        print("Erreur de connexion à la base de données MariaDB")
    else:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS levels (server_id BIGINT(255), user_id BIGINT(255), xp BIGINT(255))")
        cursor.execute("SELECT xp FROM levels WHERE user_id = %s AND server_id = %s", (message.author.id, message.guild.id))
        result = cursor.fetchone()
        if result is not None:
            current_xp = result[0]
            new_xp = current_xp + 1
            cursor.execute("UPDATE levels SET xp = %s WHERE user_id = %s AND server_id = %s", (new_xp, message.author.id, message.guild.id))
        else:
            cursor.execute("INSERT INTO levels (user_id, server_id, xp) VALUES (%s, %s, %s)", (message.author.id, message.guild.id, 1))
            current_xp = 0
        conn.commit()
        
        level = (current_xp + 1) // 10 + 1
        if current_xp % 10 == 0 and current_xp > 0:
            await message.channel.send(f"Félicitations {message.author.mention}, vous avez atteint le niveau {level} sur ce serveur!")
            print(f"{message.author.name} a atteint le niveau {level} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
        cursor.close()
        conn.close()

    # le bot répond a salut et bonjour avec une réponse aléatoire
    if message.content.lower() in ["bonjour", "salut"]:
        responses = [f"Salut {message.author.name} !", f"Bonjour {message.author.name} !", f"Salutations {message.author.name} !"]
        await message.channel.send(random.choice(responses))
        print(f"{message.author.name} a dit bonjour, le bot a répondu")
    # le bot répond a salut avec une réponse
    if "merci" in message.content.lower():
        await message.channel.send("De rien!")
        print(f"{message.author.name} a dit merci, le bot a répondu")
    # le bot répond a salut avec une réponse
    if "arabe" in message.content.lower():
        probability = 0.3 # 50% chance of sending
        if random.random() < probability:
            responses = ["Oui, ils sont gentils", "Arrêtez de vous moquer des Arabes !", "Ce n'est pas très gentil ça !"]
            await message.channel.send(random.choice(responses))
            print(f"{message.author.name} a dit arabe, le bot a répondu")
    # le bot répond a salut avec une réponse
    if "bombe" in message.content.lower():
        await message.channel.send("La spécialité de Narcos")
        print(f"{message.author.name} a dit bombe, le bot a répondu")
    # le bot répond a salut avec une réponse
    if "xeinmod" in message.content.lower():
        await message.channel.send("Il est moche !")
    if message.content.lower() in ["ratio", "Ratio","RATIO"]:
        responses = [discord.utils.get(message.guild.emojis, name="ratio"), discord.utils.get(message.guild.emojis, name="ratio_argentin"), discord.utils.get(message.guild.emojis, name="ratio_nazi")]
        await message.channel.send(random.choice(responses))
        print(f"{message.author.name} a dit ratio, le bot a répondu ratio")
    # le répond a quoi avec une réponse feur    
    if "quoi" in message.content.lower():
        await message.channel.send("feur")
        print(f"{message.author.name} a dit quoi, le bot a répondu")
        

# Fonction qui permet d'afficher le level d'un membre
# Exemple : level @ThiBot
# ----------------------------------------------------------
class levelview(discord.ui.View):
    @discord.ui.button(label="🏆 Leaderboard", style=discord.ButtonStyle.green) 
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("Prochaine update !")

@bot.command(name="level", description="Affiche le niveau d'un membre")
async def level(ctx, member: discord.Member):
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    cursor.execute("SELECT xp FROM levels WHERE user_id = %s AND server_id = %s", (member.id, ctx.guild.id))
    result = cursor.fetchone()
    if result:
        xp = result[0]
        level = xp // 10 + 1
        xp_next_level = (level * 10) - xp
        progress_percent = xp / (level * 10) * 100

        # Création de la barre de progression
        filled_bars = int(progress_percent / 5)
        empty_bars = 20 - filled_bars
        progress_bar = f"[{'■' * filled_bars}{'-' * empty_bars}] {xp}/{level*10} XP"
        level = f"Niveau {level}"
        custom_embed = discord.Embed(title=f"🏆 Niveau du membre", description=f"Voici les informations disponibles sur {member}.", color=0x43d9bd)
        custom_embed.add_field(name="📊 Level", value=level)
        custom_embed.add_field(name="📈 Barre de progression", value=progress_bar, inline=False)
        custom_embed.set_thumbnail(url=member.avatar.url)
        await ctx.respond(embed=custom_embed, view=levelview())
        print(f"{ctx.author.name} a demandé le level de {member.name} sur le serveur {ctx.guild.name} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
    else:
        await ctx.respond(f"{member.mention} n'a pas encore de niveau sur ce serveur !")
        print(f"{ctx.author.name} a demandé le level de {member.name} sur le serveur {ctx.guild.name} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
        
    cursor.close()    
    conn.close()
    

# Fonction qui permet d'afficher le classement du serveur
# Exemple : leaderboard
# -----------------------------------------------------------   
@bot.command(name = "leaderboard", description = "Affiche le classement du serveur")
async def leaderboard(ctx):
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, xp FROM levels WHERE server_id = %s ORDER BY xp DESC", (ctx.guild.id,))
    result = cursor.fetchall()
    if result:
        custom_embed = discord.Embed(title=f"🏆 Classement du serveur", description=f"Voici les 10 meilleurs membres de ce serveur.", color=0x43d9bd)
        for i in range(10):
            if i < len(result):
                user_id = result[i][0]
                user = await bot.fetch_user(user_id)
                xp = result[i][1]
                level = xp // 10 + 1
                if i == 0:
                    custom_embed.add_field(name=f"🥇 {user}", value=f"Level {level} - {xp} XP", inline=False)
                if i == 1:
                    custom_embed.add_field(name=f"🥈 {user}", value=f"Level {level} - {xp} XP", inline=False)
                if i == 2:
                    custom_embed.add_field(name=f"🥉 {user}", value=f"Level {level} - {xp} XP", inline=False)
                if i > 2:
                    custom_embed.add_field(name=f"🏅 {user}", value=f"Level {level} - {xp} XP", inline=False)
            custom_embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.respond(embed=custom_embed)
        print(f"{ctx.author.name} a demandé le leaderboard du serveur {ctx.guild.name} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
    else:
        custom_embed = discord.Embed(title=f"Classement du serveur", description=f"Ce serveur n'a pas encore de classement.", color=0x43d9bd)
        custom_embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.respond(embed=custom_embed)
        print(f"{ctx.author.name} a demandé le leaderboard du serveur {ctx.guild.name} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')} mais il n'a pas de leaderboard")
    cursor.close()
    conn.close()


# Fonction qui permet de mettre un nombre d'xp à un membre
# Exemple : setxp @ThiBot 100
# -----------------------------------------------------------        
@bot.command(name="setxp", description="Permet de mettre un nombre d'xp à un membre.", usage="setxp <membre> <nombre>")
async def setxp(ctx, member: discord.Member, amount: int):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Vous n'avez pas la permission d'utiliser cette commande.")
        print(f"{ctx.author.name} a tenté d'utiliser la commande setxp mais il n'a pas la permission le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
        return
    
    if amount < 0:
        await ctx.respond("Vous ne pouvez pas mettre un nombre négatif.")
        print(f"{ctx.author.name} a tenté d'utiliser la commande setxp mais il a mis un nombre négatif le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
        return
    if amount > 999999:
        await ctx.respond("Vous ne pouvez pas mettre un nombre supérieur à 1 000 000.")
        print(f"{ctx.author.name} a tenté d'utiliser la commande setxp mais il a mis un nombre supérieur à 1 000 000 le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
        return
    
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    cursor.execute("SELECT xp FROM levels WHERE user_id = %s AND server_id = %s", (member.id, ctx.guild.id))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO levels (user_id, server_id, xp) VALUES (%s, %s, %s)", (member.id, ctx.guild.id, amount))
        await ctx.respond(f"L'utilisateur {member} a été ajouté avec le niveau d'xp {amount}.")
        print(f"{ctx.author.name} a ajouté l'utilisateur {member.name} avec le niveau d'xp {amount} sur le serveur {ctx.guild.name} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
    else:
        cursor.execute("UPDATE levels SET xp = %s WHERE user_id = %s AND server_id = %s", (amount, member.id, ctx.guild.id))
        await ctx.respond(f"Le niveau d'xp de {member} a été modifié avec succès.")
        print(f"{ctx.author.name} a modifié le niveau d'xp de {member.name} avec le niveau d'xp {amount} sur le serveur {ctx.guild.name} le {datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')}")
    conn.commit()
    cursor.close()
    conn.close()
    

# Fonction qui affiche une fiche utilisateur a la suite de la commande userinfo
# Exemple : /userinfo @member
# --------------------------------------------------------------------------------
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
    embed = discord.Embed(title=f"Informations sur {member}", description=f"Voici les informations disponibles sur {member}.", color=0x43d9bd)
    # Id de l'utilisateur
    embed.add_field(name="🆔 ID de l'utilisateur", value=member.id, inline=False)
    # Nom de l'utilisateur
    embed.add_field(name="✅ Statut", value=status, inline=False)
    # Rôles de l'utilisateur
    embed.add_field(name="🔖 Rôles", value=", ".join(roles), inline=False)
    # Date de création du compte
    
    # Récupérez la date d'anniversaire enregistrée
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    
    cursor.execute("SELECT birthday_date FROM members WHERE member_id = %s", (member.id,))
    result = cursor.fetchone()
    result = datetime.datetime.strftime(result[0], "%d/%m/%Y") if result else None
    # Affichez la date d'anniversaire
    if result:
        embed.add_field(name="🎂 Date d'anniversaire", value=result, inline=False)
    else:
        embed.add_field(name="🎂 Date d'anniversaire", value="Non défini", inline=False)
        
    cursor.close()
    conn.close()
        
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
    print("Commande userinfo effectuée par " + str(ctx.author) + " sur " + str(member) + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui affiche les informations du serveur avec la commande serverinfo
# Exemple : /serverinfo
# --------------------------------------------------------------------------------
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
    embed = discord.Embed(title=f"Informations sur {guild.name}", description=f"Voici les informations disponibles sur {guild.name}.", color=0x43d9bd)
    # Ajout des informations
    # Propriétaire du serveur
    embed.add_field(name="👑 Propriétaire", value=guild.owner, inline=False)
    # Date de création du serveur
    embed.add_field(name="📆 Création", value=guild.created_at, inline=False)
    # Nombre de membres
    embed.add_field(name="🌐 Nombre total de membres", value=guild.member_count, inline=False)
    # Nombre de membres en ligne
    embed.add_field(name="🟢 Membres en ligne", value=online, inline=False)
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    cursor.execute("SELECT xp FROM levels WHERE server_id = %s", (guild.id,))
    result = cursor.fetchall()
    if result:
        moyenne_xp = int(sum([i[0] for i in result]) / len(result))
        embed.add_field(name="📈 Moyenne d'XP", value=round(moyenne_xp, 2), inline=False)
    else:
        embed.add_field(name="📈 Moyenne d'XP", value="Aucune donnée", inline=False)
    cursor.close()
    conn.close()

    # Nombre de salons textuels et vocaux
    embed.add_field(name="💬 Nombre de salons textuels", value=text_channels, inline=False)
    embed.add_field(name="🔊 Nombre de salons vocaux", value=voice_channels, inline=False)
    
    # Ajout de l'icône du serveur
    embed.set_thumbnail(url=ctx.guild.icon.url)
    # Envoi de l'embed
    await ctx.respond(embed=embed)
    print("Commande serverinfo effectuée par " + str(ctx.author)  + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui affiche les informations du bot  avec la commande botinfo
# Exemple : /botinfo
# --------------------------------------------------------------------------------
@bot.command(name="botinfo", description="Affiche les informations du bot.")
async def botinfo(ctx):
    # Informations sur le bot
    embed = discord.Embed(title="Informations de ThiBot", color=0x43d9bd, description="Un bot pour gérer les noeuds Proxmox de l'infrastructure de Thibault")
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
    print("Commande botinfo effectuée par " + str(ctx.author)  + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Menu d'aide avec la commande aide
# Exemple : /aide
# --------------------------------------------------------------------------------
@bot.command(name="aide", description="Affiche les commandes disponibles.")
async def aide(ctx):
    # Création du menu
    help_embed = discord.Embed(title="Aide pour les commandes", color=0x43d9bd)
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
    help_embed.add_field(name="register_birthday {membre}, {date}", value="Permet de s'enregistrer pour la fête d'anniversaire", inline=False)
    help_embed.add_field(name="birthday", value="Permet d'afficher la liste des membres qui ont leur anniversaire aujourd'hui", inline=False)
    help_embed.add_field(name="vote {question}, {réponse1,réponse2,etc}", value="Permet de créer un sondage", inline=False)
    help_embed.set_footer(text="ThiBot - Version " + version)
    help_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")

    # Envoi du menu
    await ctx.respond(embed=help_embed)
    print("Commande aide effectuée par " + str(ctx.author)  + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui affiche la date et l'heure
# Exemple : /date
# --------------------------------------------------------------------------------
@bot.command(name="date", description="Affiche la date et l'heure.")
async def date(ctx):
    # Affichage de la date et de l'heure
    now = datetime.datetime.now()
    await ctx.respond(f"Nous sommes le {now.day}/{now.month}/{now.year} et il est {now.hour}:{now.minute}")
    print("Commande date effectuée par " + str(ctx.author)  + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui permet de ping le bot
# Exemple : /ping
# -------------------------------------------------------------------------------- 
@bot.command(name="ping", description="Affiche le ping du bot.")
async def ping(ctx):
    # Affichage du ping
    await ctx.respond(f"Je suis sur {len(bot.guilds)} serveurs et mon ping est de {round(bot.latency * 1000)}ms")
    print("Commande ping effectuée par " + str(ctx.author)  + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui permet de créer un embed personnalisé
# Exemple : /custom_embed "Titre" "Description"
# --------------------------------------------------------------------------------
@bot.command(name="custom_embed", description="Crée un embed personnalisé.")
async def custom_embed(ctx, name: str, description: str):
    embed = discord.Embed(title=name, description=description, color=0x43d9bd)
    embed.set_footer(text="ThiBot", icon_url="https://images-ext-2.discordapp.net/external/fLkC9Af3Wm2PqMHffcw48pdoswl2boTQmmDrmKD19HI/%3Fsize%3D1024/https/cdn.discordapp.com/icons/717011432947974218/a7853be6f55749f86dabef85add88ca5.png")
    await ctx.respond(embed=embed)
    print("Commande custom_embed effectuée par " + str(ctx.author)  + " à " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui crée un CT
# Exemple : /createct password
# -------------------------------------
@bot.command(guild_ids=[717011432947974218], name="createct", description="Crée un conteneur LXC sur Proxmox avec votre nom.")
# Vérification que l'utilisateur a bien rentré un mot de passe
async def createct(ctx, password, os: str):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Vous n'avez pas la permission d'utiliser cette commande.")
        return
    
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
    elif os == "ubuntu":
        # on récupère le template ubuntu 22.10
        os = "local:vztmpl/ubuntu-22.10-standard_22.10-1_amd64.tar.zst"
    # si l'os est vide
    elif os == None:
        # on affiche un message d'erreur
        await ctx.respond("Vous devez choisir un OS")
        print("Le membre " + str(ctx.author) + " n'a pas rentré d'OS")
        return
    # si l'os n'est pas debian ou ubuntu
    elif os != "debian" or os != "ubuntu":
        #
        await ctx.respond("Vous devez choisir un OS valide")
        print("Le membre " + str(ctx.author) + " n'a pas rentré d'OS valide")
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
    print("Commande createct effectuée par " + str(ctx.author)  + " le " + str(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui permet d'afficher les informations d'une VM
# Exemple : /vminfo 100
# -----------------------
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
                embed = discord.Embed(title="✅ CT ID: {}".format(vm['vmid']), description="Name: {}".format(config['hostname']), color=0x43d9bd)
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
                uptime = vm['uptime'] # nombre de secondes
                if uptime == 0:
                    embed.add_field(name="⏱️ Uptime", value="Il n'y a pas d'uptime car le CT est éteint", inline=False)
                else:    
                    jours = uptime // 86400
                    heures = (uptime % 86400) // 3600
                    minutes = (uptime % 3600) // 60
                    embed.add_field(name="⏱️ Uptime", value=f"{jours} jours, {heures} heures, {minutes} minutes", inline=False)
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
                print ("Le membres {} a utilisé la commande infovm, avec le vmid {}, sur le noeud {} le {}".format(ctx.author, vmid, vm['node'], datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M'))) 
                # fin de la fonction
                return
            # si la vm est une machine virtuelle
            else:
                # récupération des informations de la vm
                config = proxmox.nodes(vm['node']).qemu(vm['vmid']).config.get()
                # création de l'embed
                # ID de la vm
                embed = discord.Embed(title="✅ VM ID: {}".format(vm['vmid']), description="Name: {}".format(config['name']), color=0x43d9bd)
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
                uptime = vm['uptime'] # nombre de secondes
                if uptime == 0:
                    embed.add_field(name="⏱️ Uptime", value="Il n'y a pas d'uptime car la VM est éteint", inline=False)
                else:    
                    jours = uptime // 86400
                    heures = (uptime % 86400) // 3600
                    minutes = (uptime % 3600) // 60
                    embed.add_field(name="⏱️ Uptime", value=f"{jours} jours, {heures} heures, {minutes} minutes", inline=False)
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
                print ("Le membres {} a utilisé la commande infovm, avec le vmid {}, sur le noeud{} le {}".format(ctx.author, vmid, vm['node'], datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
                # fin de la fonction
                return
    # si la vm n'est pas trouvé
    # envoie d'un message d'erreur
    await ctx.respond("Il n'y aucune VM ou CT avec le vmid {}".format(vmid))
    print ("Le membres {} a utilisé la commande infovm, mais la vmid {} n'a pas été trouvé le {}".format(ctx.author, vmid, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    
# commande listvm
# Exemple: /listvm
# -----------------
class listvmview(discord.ui.View):
    @discord.ui.button(label="<<", style=discord.ButtonStyle.grey) 
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Previous page", ephemeral=True)
    @discord.ui.button(label=">>", style=discord.ButtonStyle.grey)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Next page", ephemeral=True)
        
        
@bot.command(guild_ids=[717011432947974218], name="listvm", description="Affiche la liste des VM et CT.")
async def listvm(ctx):
    # récupération du nom du noeud
    vms = proxmox.cluster.resources.get(type='vm')
    # création de l'embed VM
    embedvm = discord.Embed(title=f"Liste des VM de {proxmox_node}", color=0x43d9bd)
    # Icone proxmox
    embedvm.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1068147965472034896/proxmox.png")
    # création de l'embed LXC
    embedlxc = discord.Embed(title=f"Liste des containers LXC de {proxmox_node}", color=0x43d9bd)
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
    await ctx.respond(embed=embedlxc, view=listvmview())
    await ctx.respond(embed=embedvm, view=listvmview())
    print("Le membres {} a utilisé la commande listvm le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Commande startvm qui permet de démarrer une vm ou ct
# Exemple : /startvm 100
# ----------------------------------------------
@bot.command(guild_ids=[717011432947974218], name="startvm", description="Démarrer une VM ou CT.")
async def startvm(ctx, vmid: int):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Vous n'avez pas la permission d'utiliser cette commande.")
        return
    
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
                    startembed = discord.Embed(title="Le container a démarré.", color=0x43d9bd)
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
                    print ("Le membres {} a utilisé la commande startvm pour démarrer le container {} le {}.".format(ctx.author, vm['name'], datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
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
                    startembed = discord.Embed(title="La VM a démarré.", color=0x43d9bd)
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
                    print("Le membres {} a utilisé la commande startvm pour démarrer la VM {} le {}".format(ctx.author, vm['name'], datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
                    return
                
    # si le vmid saisi n'est pas le même que celui de la vm
    await ctx.respond("Il n'y aucune VM ou CT avec le vmid {}".format(vmid))
    print("Le membres {} a utilisé la commande startvm pour démarrer une VM ou CT avec le vmid {} mais il n'y a aucune VM ou CT avec ce vmid le {}".format(ctx.author, vmid, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Commande stopvm qui permet d'arrêter une vm ou un container
# Exemple : /stopvm 100
# -------------------------------------------------------------------
@bot.command(guild_ids=[717011432947974218], name="stopvm", description="Démarrer une VM ou CT.")
# récupération du vmid
async def stopvm(ctx, vmid: int):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Vous n'avez pas la permission d'utiliser cette commande.")
        return
    
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
                    stopembed = discord.Embed(title="Le container est éteint.", color=0x43d9bd)
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
                    print("Le membres {} a utilisé la commande stopvm pour arrêter le container {} le {}".format(ctx.author, vm['name'], datetime.datetime.now()))
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
                    stopembed = discord.Embed(title="La VM est éteinte.", color=0x43d9bd)
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
                    print("Le membres {} a utilisé la commande stopvm pour arrêter la VM {} le {}".format(ctx.author, vm['name'], datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
                
    # si le vmid saisi n'est pas le même que celui de la vm
    await ctx.respond("Il n'y aucune VM ou CT avec le vmid {}".format(vmid))
    print("Le membres {} a utilisé la commande stopvm pour arrêter une VM ou CT avec le vmid {} mais il n'y a aucune VM ou CT avec ce vmid le {}".format(ctx.author, vmid, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
       

# Fonction pour jouer de la musique
# ----------------------------------------------
# Initialisez la liste d'attente et la variable voice_client
queue = []
voice_client = None

# Fonction qui permet de vérifier si l'URL est valide
# ----------------------------------------------
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
    

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice: # Si l'utilisateur n'est pas dans un salon vocal
        await ctx.respond("Vous n'êtes pas dans un salon vocal.")
        print("Le membres {} a utilisé la commande play mais il n'est pas dans un salon vocal le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
        return
    if not ctx.author.voice.channel.permissions_for(ctx.me).connect: # Si le bot n'a pas la permission de se connecter au salon vocal
        await ctx.respond("Le bot n'a pas la permission de se connecter au salon vocal.")
        print("Le membres {} a utilisé la commande play mais le bot n'a pas la permission de se connecter au salon vocal le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
        return
    if not ctx.author.voice.channel.permissions_for(ctx.me).speak: # Si le bot n'a pas la permission de parler dans le salon vocal
        await ctx.respond("Le bot n'a pas la permission de parler dans le salon vocal.")
        print("Le membres {} a utilisé la commande play mais le bot n'a pas la permission de parler dans le salon vocal le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
        return
    if not is_valid_music_url(url):
        await ctx.respond("L'URL n'est pas valide.")
        print("Le membres {} a utilisé la commande play mais l'URL n'est pas valide le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
        return
    
    global voice_client

    voice_channel = ctx.author.voice.channel

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    youtube = pytube.YouTube(url)
    video = youtube.streams.get_audio_only()
    video.download('audio/')

    # Add a delay of one second between requests
    await asyncio.sleep(1)

    source = discord.FFmpegPCMAudio('audio/'+video.default_filename)
    queue.append(source)
    custom_embed = discord.Embed(title="Musique ajoutée à la file d'attente", color=0x43d9bd)
    custom_embed.add_field(name="Titre", value=youtube.title, inline=False)
    miniature = youtube.thumbnail_url
    custom_embed.set_image(url=miniature)
    await ctx.respond(embed=custom_embed)
    print("Le membres {} a utilisé la commande play pour ajouter la musique {} à la file d'attente le {}".format(ctx.author, youtube.title, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    if not voice_client.is_playing():
        await play_queue(ctx)

async def play_queue(ctx):
    global voice_client
    if not queue:
        return
    source = queue.pop(0)
    voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_queue(ctx), bot.loop).result())
    await ctx.respond('Lecture de la prochaine musique dans la file d\'attente...')
    print("Le bot a joué la musique suivante dans la file d'attente le {}".format(datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
        queue.clear()
        await ctx.respond('La file d\'attente a été vidée et le client vocal a été déconnecté.')
        print("Le membres {} a utilisé la commande stop pour arrêter la musique et déconnecter le client vocal le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    else:
        await ctx.respond('Le client vocal n\'est pas connecté.')
        print("Le membres {} a utilisé la commande stop pour arrêter la musique mais le client vocal n'est pas connecté le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))

@bot.command()
async def next(ctx):
    if queue:
        voice_client = ctx.voice_client
        if not voice_client.is_playing():
            source = queue.pop(0)
            voice_client.play(source)
            await ctx.respond('Passage à la musique suivante.')
            print("Le membres {} a utilisé la commande next pour passer à la musique suivante le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    else:
        await ctx.respond('La file d\'attente est vide.')
        print("Le membres {} a utilisé la commande next pour passer à la musique suivante mais la file d'attente est vide le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


@bot.command()
async def listmusic(ctx):
    if queue:
        custom_embed = discord.Embed(title="Liste des musiques", color=0x43d9bd)
        for i in range(len(queue)):
            custom_embed.add_field(name="Musique {}".format(i+1), value=queue[i], inline=False)
        await ctx.respond(embed=custom_embed)
        print("Le membres {} a utilisé la commande listmusic pour afficher la liste des musiques le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    else:
        await ctx.respond('La file d\'attente est vide.')
        print("Le membres {} a utilisé la commande listmusic pour afficher la liste des musiques mais la file d'attente est vide le {}".format(ctx.author, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))



# Commande pour définir le canal de bienvenue
# Exemple : /set_welcome_channel #bienvenue @role
# ----------------------------------------------
@bot.command(name="set_welcome_channel", description="Définir le canal de bienvenue et le rôle à attribuer aux nouveaux membres.")
async def set_welcome_channel(ctx, channel: discord.TextChannel, role: discord.Role):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Vous n'avez pas la permission d'utiliser cette commande.")
        return
    
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    
    # Create the voice_channels table if it does not exist
    sql = "CREATE TABLE IF NOT EXISTS welcome_channels (guild_id VARCHAR(255) PRIMARY KEY, channel_id VARCHAR(255), role_id VARCHAR(255))"
    cursor.execute(sql)
    
    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)
    role_id = str(role.id)
    
    # Check if the guild_id exists in the voice_channels table
    sql = f"SELECT * FROM welcome_channels WHERE guild_id='{guild_id}'"
    cursor.execute(sql)
    result = cursor.fetchone()
    
    if result:
        # Update the channel_id and role_id
        sql = f"UPDATE welcome_channels SET channel_id='{channel_id}', role_id='{role_id}' WHERE guild_id='{guild_id}'"
        cursor.execute(sql)
        conn.commit()
    else:
        # Insert the guild_id, channel_id and role_id
        sql = f"INSERT INTO welcome_channels (guild_id, channel_id, role_id) VALUES ('{guild_id}', '{channel_id}', '{role_id}')"
        cursor.execute(sql)
    
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.respond(f"Canal de bienvenue défini sur {channel.mention} avec le rôle {role.name}.")
    print("Le membres {} a utilisé la commande set_welcome_channel pour définir le canal de bienvenue sur {} avec le role {} sur le serveur {} le {}".format(ctx.author, channel.mention, role.name, ctx.guild, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui accueille les nouveaux membres
# Exécuté quand un nouveau membre rejoint le serveur
# -----------------------------------------------
@bot.event
async def on_member_join(member):
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()

    guild_id = str(member.guild.id)
    # Load the welcome channel and role from the database
    load_query = "SELECT channel_id, role_id FROM welcome_channels WHERE guild_id = %s"
    cursor.execute(load_query, (guild_id,))
    result = cursor.fetchone()
    

    # Close the connection to the database
    cursor.close()
    conn.close()

    if result is not None:
        channel = bot.get_channel(int(result[0]))
        role = member.guild.get_role(int(result[1]))
        # Send a welcome message in the welcome channel and assign the defined role
        welcome_embed = discord.Embed(title=f"{member} viens de rejoindre notre serveur !", description=f"Bienvenue sur ce serveur {member.mention} !", color=0x43d9bd)
        welcome_embed.add_field(name="Règles", value="Merci de lire les règles du serveur avant de commencer à discuter !")
        welcome_embed.set_author(name="ThiBot", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
        await channel.send(embed=welcome_embed)
        print("Le membres {} a rejoint le serveur le {}".format(member, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
        await member.add_roles(role)
        print("Le membres {} a reçu le rôle {} le {}".format(member, role, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
        
    
# Commande pour bannir un membres
# Exemple : /ban @user raison
#--------------------------------
@bot.command()
async def ban(ctx, user: discord.Member, reason=None):
    await ctx.guild.ban(user, reason=reason)
    ban_embed = discord.Embed(title=f"{user} a été banni", color=0x43d9bd)
    if reason:
        ban_embed.add_field(name="Raison", value=reason)
    ban_channel = bot.get_channel(1069334147564306542)
    await ban_channel.respond(embed=ban_embed)
    print("Le membres {} a utilisé la commande ban pour bannir le membres {} le {}".format(ctx.author, user, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Commande pour kick un membres
# Exemple : /kick @user raison
#--------------------------------
@bot.command()
async def kick(ctx, user: discord.Member, reason=None):
    await ctx.guild.kick(user, reason=reason)
    kick_embed = discord.Embed(title=f"{user} a été kick", color=0x43d9bd)
    if reason:
        kick_embed.add_field(name="Raison", value=reason)
    kick_channel = bot.get_channel(1069334147564306542)
    await kick_channel.respond(embed=kick_embed)
    print("Le membres {} a utilisé la commande kick pour kick le membres {} le {}".format(ctx.author, user, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    
    
# Commande pour définir le canal vocal
# Exemple : /set_vocal_channel #vocal prefix
#--------------------------------
@bot.command()
async def set_vocal_channel(ctx, channel: discord.VoiceChannel, prefix: str):
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Vous n'avez pas la permission d'utiliser cette commande.")
        return
    
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()

    # Create the voice_channels table if it does not exist
    sql = "CREATE TABLE IF NOT EXISTS voice_channels (guild_id VARCHAR(30) PRIMARY KEY, channel_id VARCHAR(30), prefix VARCHAR(20) CHARACTER SET utf8mb4)"
    cursor.execute(sql)

    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)

    # Check if the guild_id exists in the voice_channels table
    sql = f"SELECT * FROM voice_channels WHERE guild_id='{guild_id}'"
    cursor.execute(sql)
    result = cursor.fetchone()

    if result:
        # Update the channel_id and prefix for the guild_id
        sql = f"UPDATE voice_channels SET channel_id='{channel_id}', prefix='{prefix}' WHERE guild_id='{guild_id}'"
        cursor.execute(sql)
    else:
        # Insert a new row for the guild_id, channel_id, and prefix
        sql = "REPLACE INTO voice_channels (guild_id, channel_id, prefix) VALUES (%s, %s, %s)"
        cursor.execute(sql, (guild_id, channel.id, prefix))

        
    conn.commit()
    cursor.close()
    conn.close()
    await ctx.respond(f"Le channel vocal a été défini sur '{channel.name}'.")
    print("Le membres {} a utilisé la commande set_vocal_channel pour définir le channel vocal sur {} le {}".format(ctx.author, channel, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))


# Fonction qui permet de créer un channel vocal temporaire
# -----------------------------------------------
@bot.event
async def on_voice_state_update(member, before, after):
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS temporary_voice_channels (guild_id VARCHAR(30), channel_id VARCHAR(30), prefix VARCHAR(20) CHARACTER SET utf8mb4, created_at DATETIME)")

    guild_id = str(member.guild.id)
    sql = f"SELECT * FROM voice_channels WHERE guild_id='{guild_id}'"
    cursor.execute(sql)
    result = cursor.fetchone()

    if result:
        prefix = result[2]
        channel_id = result[1]

        if after.channel is not None and after.channel.id == int(channel_id):
            temporary_channel = await member.guild.create_voice_channel(name=f"{prefix} {member.name}", category=after.channel.category)
            await member.move_to(temporary_channel)
            print("Le membres {} a créé un channel vocal temporaire le {}".format(member, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))

            now = datetime.datetime.now()
            sql = f"INSERT INTO temporary_voice_channels (guild_id, channel_id, prefix, created_at) VALUES ('{guild_id}', '{temporary_channel.id}', '{prefix}', '{now}')"
            cursor.execute(sql)
            conn.commit()

            def check_empty(channel):
                return channel.members == []

    cursor.close()
    conn.close()
    

async def check_temporary_channels():
    await bot.wait_until_ready()
    while not bot.is_closed():
        conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
        cursor = conn.cursor()

        now = datetime.datetime.now()
        sql = f"SELECT * FROM temporary_voice_channels WHERE created_at < '{now}'"
        cursor.execute(sql)
        results = cursor.fetchall()

        for result in results:
            guild = bot.get_guild(int(result[0]))
            channel = guild.get_channel(int(result[1]))

            if channel is not None and len(channel.members) == 0:
                await channel.delete()
                sql = f"DELETE FROM temporary_voice_channels WHERE channel_id='{channel.id}'"
                cursor.execute(sql)
                conn.commit()

        cursor.close()
        conn.close()
        await asyncio.sleep(1)

bot.loop.create_task(check_temporary_channels())

@bot.command()
async def renametemp_channel(ctx, channel: discord.VoiceChannel, name: str):
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM temporary_voice_channels WHERE channel_id = ?", (channel.id,))
    result = cursor.fetchone()
    if result is not None:
        await channel.edit(name=name)
        await ctx.respond(f"Le channel vocal temporaire a été renommé en '{name}'.")
        print("Le membres {} a utilisé la commande renametemp_channel pour renommer le channel vocal temporaire en {} le {}".format(ctx.author, name, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    else:
        await ctx.respond("Ce channel vocal n'est pas temporaire.")
        print("Le membres {} a utilisé la commande renametemp_channel pour renommer le channel vocal temporaire en {} le {}".format(ctx.author, name, datetime.datetime.now().strftime('%d/%m/%Y à %Hh%M')))
    cursor.close()
    conn.close()

    
# Fonction pour afficher l'avatar d'un utilisateur
# Exemple d'utilisation : /avatar @user (Affiche l'avatar de l'utilisateur)
# ---------------------------------------------------------------------------------------------        
@bot.command(name="avatar", description="Affiche l'avatar d'un utilisateur")
async def avatar(ctx, member: discord.Member):
    embed = discord.Embed(color=0x43d9bd)
    embed.set_author(name=f"Avatar de {member}", icon_url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
    embed.set_image(url=member.avatar.url)
    await ctx.respond(embed=embed)
    print("Le membres {} a utilisé la commande avatar pour afficher l'avatar de {}".format(ctx.author, member))


# Fonction pour supprimer un nombre de messages
# Exemple d'utilisation : /clear 10 (Supprime 10 messages)
# ---------------------------------------------------------------------------------------------
@bot.command(name='clear', description='Supprime un nombre de messages')
async def clearmsg(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.respond(f"{amount} messages ont été supprimés !")
    print("Le membres {} a utilisé la commande clear pour supprimer {} messages".format(ctx.author, amount))
    

# Fonction pour faire dire un message au bot
# Exemple d'utilisation : /say Bonjour
# ---------------------------------------------------------------------------------------------
@bot.command(name='say', description='Fait dire un message au bot')
async def say(ctx, *, message):
    await ctx.respond(message)
    print("Le membres {} a utilisé la commande say pour faire dire {} au bot".format(ctx.author, message))
    
    
# Fonction pour enregistrer la date d'anniversaire d'un membre
# Exemple d'utilisation : /register_birthday 01/01/2000 @Membre
# ---------------------------------------------------------------------------------------------
@bot.command(name="register_birthday", description="Enregistre la date d'anniversaire d'un membre.")
async def register_birthday(ctx, birthday, member: discord.Member = None):
    # Vérifiez si l'ID du membre et la date d'anniversaire ont été spécifiés sinon renvoyez une erreur et arrêtez l'exécution de la fonction avec return
    member_id = member.id if member else ctx.author.id
    if member_id is None:
        await ctx.respond("Vous n'avez pas spécifié l'ID du membre.")
        print("Le membres {} a utilisé la commande register_birthday sans spécifier l'ID du membre".format(ctx.author))
        return
    if birthday is None:
        await ctx.respond("Vous n'avez pas spécifié de date d'anniversaire.")
        print("Le membres {} a utilisé la commande register_birthday sans spécifier la date d'anniversaire".format(ctx.author))
        return
    if not re.match(r"\d{2}/\d{2}/\d{4}", birthday):
        await ctx.respond("La date d'anniversaire doit être au format JJ/MM/AAAA.")
        print("Le membres {} a utilisé la commande register_birthday avec une date d'anniversaire au mauvais format".format(ctx.author))
        return
    
    # Connexion à la base de données MariaDB
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    # Créez la table si elle n'existe pas
    cursor.execute("CREATE TABLE IF NOT EXISTS members (id INT AUTO_INCREMENT PRIMARY KEY, member_id BIGINT(50), birthday_date DATE)")

    # Convertir la date d'anniversaire en objet date
    birthday_date = datetime.datetime.strptime(birthday, '%d/%m/%Y').date()

    # Selectionne la date d'anniversaire du membre en fonction du member_id et vérifiez si le membre existe déjà dans la base de données.
    cursor.execute(f"SELECT birthday_date FROM members WHERE member_id='{member_id}'")
    # Récupérer le résultat de la requête
    result = cursor.fetchone()
    # Si le membre existe déjà dans la base de données, mettez à jour la date d'anniversaire sinon insérez une nouvelle ligne dans la base de données
    if result:
        cursor.execute(f"UPDATE members SET birthday_date='{birthday_date}' WHERE member_id='{member_id}'")
        conn.commit()
        await ctx.respond("Votre date d'anniversaire a été mise à jour avec succès.")
        print("Le membres {} a utilisé la commande register_birthday pour mettre à jour une date d'anniversaire".format(ctx.author))
    # Sinon, insérez une nouvelle ligne dans la base de données
    else:
        cursor.execute(f"INSERT INTO members (member_id, birthday_date) VALUES ('{member_id}', '{birthday_date}')")
        conn.commit()
        await ctx.respond("Votre date d'anniversaire a été enregistrée avec succès.")
        print("Le membres {} a utilisé la commande register_birthday pour enregistrer une date d'anniversaire".format(ctx.author))
    # Fermer la connexion à la base de données
    cursor.close()
    conn.close()
    
# Fonction pour afficher les anniversaires des membres
# Exemple de commande : /show_birthdays
# ----------------------------------------------
@bot.command(name="show_birthdays", description="Affiche les anniversaires des membres")
async def show_birthdays(ctx):
    # Connexion à la base de données
    conn = mariadb.connect(user=mariadb_user, password=mariadb_password, host=mariadb_host, database=mariadb_database)
    cursor = conn.cursor()
    
    # Récupérer les anniversaires des membres de la base de données
    cursor.execute("SELECT member_id, birthday_date FROM members")
    members = cursor.fetchall()

    # Créer un embed pour afficher les anniversaires
    embed = discord.Embed(title="Anniversaires des membres", color=0x43d9bd)
    # Ajouter les anniversaires des membres à l'embed
    for member in members:
        member_id, birthday_date = member
        # Récupérer les informations du membre à partir de son ID Discord
        member_info = bot.get_user(member_id)
        # Convertir la date d'anniversaire en chaîne de caractères sous le format JJ/MM/AAAA
        birthday_date = birthday_date.strftime("%d/%m/%Y")
        # Ajouter le membre et sa date d'anniversaire à l'embed
        embed.add_field(name=f"{member_info}", value=birthday_date, inline=False)
        # Ajouter une image à l'embed (optionnel)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/695658154326753284/1070102817911623710/portfolio-2.jpg")
    
    # Fermer la connexion à la base de données
    cursor.close()
    conn.close()

    # Envoyer l'embed à Discord
    await ctx.respond(embed=embed)
    print("Le membres {} a utilisé la commande show_birthdays".format(ctx.author))
    

# Fonction qui permet de créer un embed de sondage selon plusieurs réponses donné via une commande
# Exemple : /vote "Quel est votre plat préféré ?" "Pizza, Hamburger, Lasagne"
# -----------------------------------------------------------------------------------------------------
@bot.command(name="vote", description="Crée un sondage")
async def vote(ctx, question:str, options: str):
    # On vérifie si la question et les options ont été spécifiées
    if question is None:
        await ctx.respond("Vous n'avez pas spécifié de question.")
        print("Le membres {} a utilisé la commande vote sans spécifier de question".format(ctx.author))
        return
    if options is None:
        await ctx.respond("Vous n'avez pas spécifié d'options.")
        print("Le membres {} a utilisé la commande vote sans spécifier d'options".format(ctx.author))
        return
    if question is None and options is None:
        await ctx.respond("Vous n'avez pas spécifié de question et d'options.")
        print("Le membres {} a utilisé la commande vote sans spécifier de question et d'options".format(ctx.author))
        return
    
    # On sépare les options avec un séparateur
    options = options.split(",")
    
    # On vérifie si le nombre d'options est inférieur ou égal à 9 et supérieur ou égal à 2
    if len(options) > 9:
        await ctx.respond("Vous ne pouvez pas créer un sondage avec plus de 9 options, veuillez saisir les choix comme cela : choix1, choix2, choix3, etc.")
        print("Le membres {} a utilisé la commande vote avec plus de 9 options".format(ctx.author))
        return
    if len(options) < 2:
        await ctx.respond("Vous devez créer un sondage avec au moins 2 options, veuillez saisir les choix comme cela : choix1, choix2, choix3, etc.")
        print("Le membres {} a utilisé la commande vote avec moins de 2 options".format(ctx.author))
        return
    # et on lance le sondage
    else:
        # On crée une liste d'emojis
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    
        # On crée un embed avec le titre du sondage
        custom_embed = discord.Embed(title=question, color=0x43d9bd)
        # On ajoute les options, avec un emoji correspondant à chaque option (1️⃣ pour la première option, 2️⃣ pour la deuxième, etc.)
        for i, option in enumerate(options):
                custom_embed.add_field(name=f"{option}", value=f"{emojis[i]}", inline=False)
        # On ajoute un footer et un auteur à l'embed
        custom_embed.set_footer(text="Réagissez avec l'emoji correspondant à votre choix.")
        # On ajoute un auteur à l'embed
        custom_embed.set_author(name="Sondage de {}".format(ctx.author.name), icon_url=ctx.author.avatar.url)
        # On envoie l'embed
        message = await ctx.send(embed=custom_embed)
        # On ajoute les réactions correspondant aux options
        for i in range(len(options)):
            await message.add_reaction(emojis[i])
        # On envoie un message de confirmation
        await ctx.respond("Sondage créé avec succès.")
        print("Le membres {} a utilisé la commande vote".format(ctx.author))

# Fonction qui permet de ban un membre défini si elle rejoint un vocal
# -----------------------------------------------------------------------------------------------------
async def ban_member_if_join_voice_channel(): 
    member = bot.get_user(325744347637088261) # ID du membre à bannir
    if member.voice is not None:
        await member.ban(reason="Membre banni automatiquement pour avoir rejoint un vocal")
        await bot.get_channel(1069334147564306542).send("Le membre {} a été banni automatiquement pour avoir rejoint un vocal.".format(member))
        print("Le membre {} a été banni automatiquement pour avoir rejoint un vocal.".format(member))
        

# Lancement du bot avec le token du bot Discord (à remplacer par le token de votre bot dans le fichier config.py)
# ---------------------------------------------------------------------------------------------------------------
bot.run(bot_token)
