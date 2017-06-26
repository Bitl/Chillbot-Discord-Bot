#include files
import discord
from discord.ext import commands
import asyncio
import logging
import random
import aiohttp
from time import localtime, strftime
from datetime import date
import json

#logger for the internal console, the discordAPI, and chillbot itself.
logger = logging.getLogger('chillbot_console')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

logger2 = logging.getLogger('discord')
logger2.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='chillbot_discordAPI.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger2.addHandler(handler)

logger3 = logging.getLogger('chillbot')
logger3.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='chillbot_logfile.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger3.addHandler(handler)

#init chillbot
print('Chillbot Loading...')
logger3.debug("Chillbot Loading...")

#init bot
bot = commands.Bot(command_prefix="c!", description="Basic Discord bot for Chaos' Chillspot server.")
aiosession = aiohttp.ClientSession(loop=bot.loop)

#these first 2 arrays show a whitelist for users to post links, and a bot list for deleting replies made by bots.
whitelist = ["226441820467494914", "159985870458322944", "185476724627210241", "109338686889476096", "115385224119975941", "172002275412279296"]
botlist = ["185476724627210241", "172002275412279296"]
#role whitelist for the commands themselves.
role_whitelist = ["311918364886827008", "311888772646174721", "311889124544217098", "311918312814673922"]
owner_list = ["184013824850919425", "226441820467494914"]
#logs
logging_channel_general = "294994191489171467"
logging_channel_joins_leaves = "294994789361909761"
logging_channel_deleted = "294994109028892673"
logging_channel_edited = "294994142600232961"

bot_summon_id = '315533031718912002'

#game list. for fun.
game_list = ["Team Fortress 2", "Garry's Mod", "Portal", "Portal 2", "Left 4 Dead", "Left 4 Dead 2", "Half-Life 2", "Half-Life", "Counter-Strike: Global Offensive", 
"BioShock Infinite", "BioShock", "BioShock 2", "Killing Floor", "Killing Floor 2", "Borderlands", "Borderlands 2", "Fallout 3", "Fallout New Vegas", "Fallout 4", "DOOM", 
"Wolfenstein: The New Order", "Wolfenstein: The Old Blood", "The Ultimate DOOM", "DOOM II", "Final DOOM", "Quake", "Quake II", "Quake III Arena", "Wolfenstein 3D",
"Quake Live", "Synergy", "Terraria", "Minecraft", "ROBLOX", "Spore", "System Shock 2", "Duke Nukem 3D", "POSTAL 2", "Shadow Warrior", "Shadow Warrior 2", "Shadow Warrior Classic",
"Counter-Strike", "Counter-Strike Source", "Serious Sam: The First Encounter", "Serious Sam: The Second Encounter", "Serious Sam 3: BFE", "Pong", "Tetris", "Super Mario Bros.",
"Pac-Man", "Mrs. Pac-Man", "Sonic the Hedgehog", "Reflex Arena", "Overwatch", "League Of Legends", "Dota 2", "Halo Combat Evolved", "Halo Custom Edition", "Halo Online", 
"ElDewrito", "Team Fortress 2 Classic", "Synergy", "FIREFIGHT RELOADED", "Unreal Tournament", "GZDOOM", "ZDOOM", "GLQuake", "WinQuake", "Spacewar!"]

config = {}

with open('config.json') as json_config_file:
     config = json.load(json_config_file)

#global vars.
riotmode = False
deletelinksmode = False
deletebotsmode = False
antiadvertising = False

riotmode_config = config["riotmode"]

if riotmode_config == "True":
     riotmode = True
else:
     riotmode = False
	 
deletelinksmode_config = config["deletelinksmode"]

if deletelinksmode_config == "True":
     deletelinksmode = True
else:
     deletelinksmode = False
	 
deletebotsmode_config = config["deletebotsmode"]

if deletebotsmode_config == "True":
     deletebotsmode = True
else:
     deletebotsmode = False
	 
antiadvertising_config = config["antiadvertising"]

if antiadvertising_config == "True":
     antiadvertising = True
else:
     antiadvertising = False

#april fools recode.
today = date.today()
tom_foolery = date(today.year, 4, 1)
        
#ready event.
@bot.event
async def on_ready():
  print('Logged in!')
  print('---------')
  print('Name: ' + bot.user.name)
  print('ID: ' + bot.user.id)
  print('---------')
  print('User Whitelist (as User IDs):')
  print(whitelist)
  print('---------')
  print('Blocked Bot List (as User IDs):')
  print(botlist)
  print('---------')
  print('Role Whitelist (as Role IDs):')
  print(role_whitelist)
  print('---------')
  print('Modes enabled:')
  print('---------')
  if riotmode == True:
    print('Riot Mode: Enabled')
  else:
    print('Riot Mode: Disabled')
  if deletelinksmode == True:
    print('Delete Links: Enabled')
  else:
    print('Delete Links: Disabled')
  if deletebotsmode == True:
    print('Delete Bot Responses: Enabled')
  else:
    print('Delete Bot Responses: Disabled')
  if antiadvertising == True:
    print('Delete Server Advertisements: Enabled')
  else:
    print('Delete Server Advertisements: Disabled')
  print('---------')
  print('Chillbot Loaded.')
  print('---------')
  print('To invite to your server use')
  print('https://discordapp.com/api/oauth2/authorize?client_id=' + bot.user.id + '&scope=bot&permissions=0')
  print('---------')
  bot.loop.create_task(change_game())
  
async def change_game():
  await bot.wait_until_ready()
  while not bot.is_closed:
    chosen_game = random.choice(game_list)
    logger.debug("Now Playing:")
    logger.debug(chosen_game)
    await bot.change_presence(game=discord.Game(name=chosen_game))
    await asyncio.sleep(1800)

#event on message.
@bot.event
async def on_message(message):
  await message_event_func(message)
  
#event on message edit.
@bot.event
async def on_message_edit(before, after):
  await message_event_func(after)
  
  if before.content == after.content:
     return
  if before.author == bot.user:
     return
  
  member = before.author
  channel = discord.Object(id=logging_channel_edited)
  leavemsgdebug = '[{0.content}] -> [{1.content}]'.format(before, after)
  msgtime = strftime("%d/%m/%Y [%I:%M:%S %p] (%Z)", localtime())
  usermsg = "{0} <{1}> ({2}) | {3}".format(member, member.id, before.channel.name, msgtime).replace("'", "")
  em = discord.Embed(title='Message Edited', description=leavemsgdebug, colour=0xF46900)
  em.set_author(name=usermsg, icon_url=member.avatar_url)
  await bot.send_message(channel, embed=em)

#event on message delete.
@bot.event
async def on_message_delete(message):
  if message.author == bot.user:
     return
  
  member = message.author
  channel = discord.Object(id=logging_channel_deleted)
  deletmsgdebug = '[{0.content}]'.format(message)
  msgtime = strftime("%d/%m/%Y [%I:%M:%S %p] (%Z)", localtime())
  usermsg = "{0} <{1}> ({2}) | {3}".format(member, member.id, message.channel.name, msgtime).replace("'", "")
  em = discord.Embed(title='Message Deleted', description=deletmsgdebug, colour=0xF41400)
  em.set_author(name=usermsg, icon_url=member.avatar_url)
  await bot.send_message(channel, embed=em)

#message fucntion
async def message_event_func(message):
  #make sure we don't mention ourselves.
  if message.author == bot.user:
    return
    
  #log messages
  member = message.author
  channel = discord.Object(id=logging_channel_general)
  normalmsgdebug = '[{0.content}]'.format(message)
  msgtime = strftime("%d/%m/%Y [%I:%M:%S %p] (%Z)", localtime())
  usermsg = "{0} <{1}> ({2}) | {3}".format(member, member.id, message.channel.name, msgtime).replace("'", "")
  em = discord.Embed(title='Message', description=normalmsgdebug, colour=0x7ED6DE)
  em.set_author(name=usermsg, icon_url=member.avatar_url)
  await bot.send_message(channel, embed=em)

  #format messages
  linkmsg = '{0.author.mention}, please post links in #media_dump.'.format(message)
  botmsg = '{0.author.mention}, please post bot commands in #bot_summon.'.format(message)
  admsg = '{0.author.mention}, please dont promote other servers here.'.format(message)
  
  #execute the modes if specified to do so.
  if deletelinksmode == True:
    if user_notadmin(message):
      if 'http://' in message.content:
       try:
          await bot.delete_message(message)
          await response(message, linkmsg)
          logger.debug("Deleted a link!")
          logger3.debug("Deleted a link!")
       except Exception as e:
          logger.debug("Failed to delete a link!")
          logger3.debug("Failed to delete a link!")
      
      if 'https://' in message.content:
       try:
          await bot.delete_message(message)
          await response(message, linkmsg)
          logger.debug("Deleted a link!")
          logger3.debug("Deleted a link!")
       except Exception as e:
          logger.debug("Failed to delete a link!")
          logger3.debug("Failed to delete a link!")
     
  if deletebotsmode == True:
    if user_isbot(message):
      try:
       await bot.delete_message(message)
       await response(message, botmsg)
       logger.debug("Deleted a bot response!")
       logger3.debug("Deleted a bot response!")
      except Exception as e:
       logger.debug("Failed to delete a bot response!")
       logger3.debug("Failed to delete a bot response!")
       
  if riotmode == True:
    if user_notadmin_role(message):
      try:
       await bot.delete_message(message)
       logger.debug("Deleted unnecessary drama!")
       logger3.debug("Deleted unnecessary drama!")
      except Exception as e:
       logger.debug("Failed to delete unnecessary drama!")
       logger3.debug("Failed to delete unnecessary drama!")

  if antiadvertising == True:
    if user_notadmin(message):
      if 'https://discord.gg/' in message.content:
        try:
         await bot.delete_message(message)
         await response(message, admsg)
         logger.debug("Deleted server advertisement!")
         logger3.debug("Deleted server advertisement!")
        except Exception as e:
         logger.debug("Failed to delete server advertisement!")
         logger3.debug("Failed to delete server advertisement!")
         
      if 'https://discordapp.com/invite/' in message.content:
        try:
         await bot.delete_message(message)
         await response(message, admsg)
         logger.debug("Deleted server advertisement!")
         logger3.debug("Deleted server advertisement!")
        except Exception as e:
         logger.debug("Failed to delete server advertisement!")
         logger3.debug("Failed to delete server advertisement!")
         
  await bot.process_commands(message)
     
#on user join event
@bot.event
async def on_member_join(member):
  server = member.server
  await bot.send_typing(server)
  welcomemsg = '{0.mention}, welcome to the Chillspot! Be sure to have fun!'.format(member)
  welcomemsg_gangsta = 'Yo {0.mention}, welcome ta tha Chillspot son! Be shizzle ta have fun!'.format(member)
  if today == tom_foolery:
     em = discord.Embed(title='Yo, welcome!', description=welcomemsg_gangsta, colour=0x7ED6DE)
  else:
     em = discord.Embed(title='Welcome!', description=welcomemsg, colour=0x7ED6DE)
  em.set_author(name=member.name, icon_url=member.avatar_url)
  await bot.send_message(server, embed=em)
  await bot.send_file(server, 'welcomebanner.png')
  channel = discord.Object(id=logging_channel_joins_leaves)
  welcomemsgdebug = '{0.name} joined the server.'.format(member)
  msgtime = strftime("%d/%m/%Y [%I:%M:%S %p] (%Z)", localtime())
  usermsg = "{0} <{1}> | {2}".format(member, member.id, msgtime).replace("'", "")
  em = discord.Embed(title='Member Joined', description=welcomemsgdebug, colour=0x7ED6DE)
  em.set_author(name=usermsg, icon_url=member.avatar_url)
  await bot.send_message(channel, embed=em)
  logger.debug(welcomemsgdebug)
  logger3.debug(welcomemsgdebug)

#on user leave event
@bot.event
async def on_member_remove(member):
  server = member.server
  await bot.send_typing(server)
  leavemsg = '{0.name} has left the server.'.format(member)
  leavemsg_gangsta = 'Yo homies, {0.name} has left tha serva.'.format(member)
  if today == tom_foolery:
     em = discord.Embed(title='See ya dawg!', description=leavemsg_gangsta, colour=0xF41400)
  else:
     em = discord.Embed(title='Bye!', description=leavemsg, colour=0xF41400)
  em.set_author(name=member.name, icon_url=member.avatar_url)
  await bot.send_message(server, embed=em)
  channel = discord.Object(id=logging_channel_joins_leaves)
  leavemsgdebug = '{0.name} left the server.'.format(member)
  msgtime = strftime("%d/%m/%Y [%I:%M:%S %p] (%Z)", localtime())
  usermsg = "{0} <{1}> | {2}".format(member, member.id, msgtime).replace("'", "")
  em = discord.Embed(title='Member Left', description=leavemsgdebug, colour=0xF41400)
  em.set_author(name=usermsg, icon_url=member.avatar_url)
  await bot.send_message(channel, embed=em)
  logger.debug(leavemsgdebug)
  logger3.debug(leavemsgdebug)
     
#these two are for checking the whitelist and blocklist.
def user_notadmin(message):
  author = message.author
  if author.id in str(whitelist):
     adminmsg = 'User {0.author.name} is on the whitelist!'.format(message)
     logger3.debug(adminmsg)
     return False
  else:
     notadminmsg = 'User {0.author.name} is not on the whitelist!'.format(message)
     logger3.debug(notadminmsg)
     return True
   
def user_isbot(message):
  author = message.author
  if author.id in str(botlist):
     botmsg = 'User {0.author.name} is on the botlist!'.format(message)
     logger3.debug(botmsg)
     return True
  else:
     notbotmsg = 'User {0.author.name} is not on the botlist!'.format(message)
     logger3.debug(notbotmsg)
     return False
      
@bot.group(pass_context=True, no_pm=True)
async def riot(ctx):
  """Mods - Mutes all users except for administration"""
  message = ctx.message
  
  if user_admin_role(message):
    if ctx.invoked_subcommand is None:
      await response(message, "Help: c!riot <on/off>")

@riot.command(name='on', pass_context=True, no_pm=True)
async def riot_on(ctx):
  global riotmode
  message = ctx.message

  if user_admin_role(message):
    if riotmode == False:
       riotmode = True
       await response(message, "Riot Mode has been enabled due to drama. Please listen to the server administration.")
       logger.debug("Enabled riot mode!")
       logger3.debug("Enabled riot mode!")
    
@riot.command(name='off', pass_context=True, no_pm=True)
async def riot_off(ctx):
  global riotmode
  message = ctx.message

  if user_admin_role(message):
    if riotmode == True:
       riotmode = False
       await response(message, "Riot Mode has been disabled.")
       logger.debug("Disabled riot mode!")
       logger3.debug("Disabled riot mode!")
     
@bot.group(pass_context=True, no_pm=True)
async def deletelinks(ctx):
  """Mods - Deletes links from all users except for those in the whitelist"""
  message = ctx.message
  
  if user_admin_role(message):
    if ctx.invoked_subcommand is None:
      await response(message, "Help: c!deletelinks <on/off>")

@deletelinks.command(name='on', pass_context=True, no_pm=True)
async def deletelinks_on(ctx):
  global deletelinksmode
  message = ctx.message

  if user_admin_role(message):
    if deletelinksmode == False:
       deletelinksmode = True
       await response(message, "Link Deleting Mode has been enabled.")
       logger.debug("Enabled link deleting mode!")
       logger3.debug("Enabled link deleting mode!")
    
@deletelinks.command(name='off', pass_context=True, no_pm=True)
async def deletelinks_off(ctx):
  global deletelinksmode
  message = ctx.message

  if user_admin_role(message):
    if deletelinksmode == True:
       deletelinksmode = False
       await response(message, "Link Deleting Mode has been disabled.")
       logger.debug("Disabled link deleting mode!")
       logger3.debug("Disabled link deleting mode!")

@bot.group(pass_context=True, no_pm=True)
async def deletebots(ctx):
  """Mods - Deletes Bot Responces from blacklisted bots"""
  message = ctx.message
  
  if user_admin_role(message):
    if ctx.invoked_subcommand is None:
      await response(message, "Help: c!deletebots <on/off>")

@deletebots.command(name='on', pass_context=True, no_pm=True)
async def deletebots_on(ctx):
  global deletebotsmode
  message = ctx.message

  if user_admin_role(message):
    if deletebotsmode == False:
       deletebotsmode = True
       await response(message, "Bot Response Deleting Mode has been enabled.")
       logger.debug("Enabled Bot Response deleting mode!")
       logger3.debug("Enabled Bot Response deleting mode!")
    
@deletebots.command(name='off', pass_context=True, no_pm=True)
async def deletebots_off(ctx):
  global deletebotsmode
  message = ctx.message

  if user_admin_role(message):
    if deletebotsmode == True:
       deletebotsmode = False
       await response(message, "Bot Response Deleting Mode has been disabled.")
       logger.debug("Disabled Bot Response deleting mode!")
       logger3.debug("Disabled Bot Response deleting mode!")
       
@bot.group(pass_context=True, no_pm=True)
async def deleteads(ctx):
  """Mods - Deletes server advertisements from all users except whitelisted"""
  message = ctx.message

  if user_admin_role(message):
    if ctx.invoked_subcommand is None:
      await response(message, "Help: c!deleteads <on/off>")

@deleteads.command(name='on', pass_context=True, no_pm=True)
async def deleteads_on(ctx):
  global antiadvertising
  message = ctx.message

  if user_admin_role(message):
    if antiadvertising == False:
       antiadvertising = True
       await response(message, "Server Advertisement Deleting Mode has been enabled.")
       logger.debug("Enabled server advertisement deleting mode!")
       logger3.debug("Enabled server advertisement deleting mode!")
    
@deleteads.command(name='off', pass_context=True, no_pm=True)
async def deleteads_off(ctx):
  global antiadvertising
  message = ctx.message

  if user_admin_role(message):
    if antiadvertising == True:
       antiadvertising = False
       await response(message, "Server Advertisement Deleting Mode has been disabled.")
       logger.debug("Disabled server advertisement deleting mode!")
       logger3.debug("Disabled server advertisement deleting mode!")
       
@bot.command(pass_context=True, no_pm=True)
async def avatar(ctx, url=None):
  """Mods - Changes the bot's avatar. Must be an attachment. (Bot Owners Only)"""
  message = ctx.message
  
  if user_owner(message):
     if message.attachments:
        thing = message.attachments[0]['url']
     else:
        await response(message, "Please upload your avatar in a attachment.")
        return

     try:
        with aiohttp.Timeout(10):
         async with aiosession.get(thing) as res:
           await bot.edit_profile(avatar=await res.read())
           await response(message, "Avatar Changed.")
     except Exception as e:
        await response(message, "Unable to change avatar.")
        
@bot.command(pass_context=True, no_pm=True)
async def msg(ctx, *, msgstr=None):
  """Mods - Sends a message to a specific channel. (Bot Owners Only)"""
  message = ctx.message
  
  if user_owner(message):
     channel = discord.Object(id='254715477593423891')
     await bot.send_message(channel, msgstr)
     
#these two are for checking the role whitelist.
def user_notadmin_role(message):
  author = message.author
  if author.top_role.id in str(role_whitelist):
     adminmsg = 'User {0.author.name} is on the role whitelist!'.format(message)
     logger3.debug(adminmsg)
     return False
  else:
     notadminmsg = 'User {0.author.name} is not on the role whitelist!'.format(message)
     logger3.debug(notadminmsg)
     return True
   
def user_admin_role(message):
  author = message.author
  if author.top_role.id in str(role_whitelist):
     adminmsg = 'User {0.author.name} is on the role whitelist!'.format(message)
     logger3.debug(adminmsg)
     return True
  else:
     notadminmsg = 'User {0.author.name} is not on the role whitelist!'.format(message)
     logger3.debug(notadminmsg)
     return False
     
def user_owner(message):
  author = message.author
  if author.id in str(owner_list):
     ownermsg = 'User {0.author.name} is on the ownerlist!'.format(message)
     logger3.debug(ownermsg)
     return True
  else:
     notownermsg = 'User {0.author.name} is not on the ownerlist!'.format(message)
     logger3.debug(notownermsg)
     return False
     
async def response(message, content):
  await bot.send_typing(message.channel)
  if today == tom_foolery:
     em = discord.Embed(title='Yo fucka, heres a serva message', description=content, colour=0x7ED6DE)
  else:
     em = discord.Embed(title='Server Message', description=content, colour=0x7ED6DE)
  em.set_author(name=bot.user.display_name, icon_url=bot.user.avatar_url)
  await bot.send_message(message.channel, embed=em)

print('Connecting...')
logger3.debug("Chillbot Connecting...")
try:
 file = open('token.txt', 'r') 
 bot.run(file.readline())
 file.close()
 logger3.debug("Chillbot Connected!")
except Exception as e:
 logger3.debug("Chillbot failed to connect with Discord!")
except:
 bot.logout()
