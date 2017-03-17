#include files
import discord
import asyncio
import logging
import random

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

#init Discord
client = discord.Client()

#these first 2 arrays show a whitelist for users to post links, and a bot list for deleting replies made by bots.
whitelist = ["226441820467494914", "159985870458322944", "185476724627210241", "109338686889476096", "115385224119975941", "172002275412279296"]
botlist = ["185476724627210241", "172002275412279296"]
#when you add commands, also add it along with its arguments here.
commlist = ["c!riot <on/off>", "c!deletelinks <on/off>", "c!deletebots <on/off>", "c!help"]
#role whitelist for the commands themselves.
role_whitelist = ["254725867056398349", "266385101871513610", "254725919627935744", "288107558349307906"]

#global vars.
riotmode = False
deletelinksmode = False
deletebotsmode = False
        
#ready event.
@client.event
async def on_ready():
  print('Logged in!')
  print('---------')
  print('Name: ' + client.user.name)
  print('ID: ' + client.user.id)
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
  print('Command List:')
  print(commlist)
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
  print('---------')
  print('Chillbot Loaded.')
  print('---------')
  print('To invite to your server use')
  print('https://discordapp.com/api/oauth2/authorize?client_id=' + client.user.id + '&scope=bot&permissions=0')

#event on message.
@client.event
async def on_message(message):
  await message_event_func(message)
  
#event on message edit.
@client.event
async def on_message_edit(before, after):
  await message_event_func(after)

#message fucntion
async def message_event_func(message):
  #make sure we don't mention ourselves.
  if message.author == client.user:
    return

  #format messages
  linkmsg = '{0.author.mention}, please post links in #media_dump.'.format(message)
  botmsg = '{0.author.mention}, please post bot commands in #bot_summon.'.format(message)
  #parse the commands.
  await parse_commands(message)
  
  #execute the modes if specified to do so.
  if deletelinksmode == True:
    if user_notadmin(message):
      if 'http://' in message.content:
       try:
          await client.delete_message(message)
          await response(message, linkmsg)
          logger.debug("Deleted a link!")
          logger3.debug("Deleted a link!")
       except Exception as e:
          logger.debug("Failed to delete a link!")
          logger3.debug("Failed to delete a link!")
      
      if 'https://' in message.content:
       try:
          await client.delete_message(message)
          await response(message, linkmsg)
          logger.debug("Deleted a link!")
          logger3.debug("Deleted a link!")
       except Exception as e:
          logger.debug("Failed to delete a link!")
          logger3.debug("Failed to delete a link!")
     
  if deletebotsmode == True:
    if user_isbot(message):
      try:
       await client.delete_message(message)
       await response(message, botmsg)
       logger.debug("Deleted a bot response!")
       logger3.debug("Deleted a bot response!")
      except Exception as e:
       logger.debug("Failed to delete a bot response!")
       logger3.debug("Failed to delete a bot response!")
	   
  if riotmode == True:
    if user_notadmin_role(message):
      try:
       await client.delete_message(message)
       logger.debug("Deleted unnecessary drama!")
       logger3.debug("Deleted unnecessary drama!")
      except Exception as e:
       logger.debug("Failed to delete unnecessary drama!")
       logger3.debug("Failed to delete unnecessary drama!")
	 
#on user join event
@client.event
async def on_member_join(member):
  server = member.server
  welcomemsg = '{0.name}, welcome to the Chillspot! Be sure to have fun!'.format(member)
  em = discord.Embed(title='Welcome!', description=welcomemsg, colour=0x7ED6DE)
  em.set_author(name=member.name, icon_url=member.avatar_url)
  await client.send_message(server, embed=em)
  await client.send_file(server, 'welcomebanner.png')
  welcomemsgdebug = '{0.name} joined the server.'.format(member)
  logger.debug(welcomemsgdebug)
  logger3.debug(welcomemsgdebug)

#on user leave event
@client.event
async def on_member_remove(member):
  server = member.server
  leavemsg = '{0.name} has left the server.'.format(member)
  em = discord.Embed(title='Bye!', description=leavemsg, colour=0xF41400)
  em.set_author(name=member.name, icon_url=member.avatar_url)
  await client.send_message(server, embed=em)
  leavemsgdebug = '{0.name} left the server.'.format(member)
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

#parse our commands.
async def parse_commands(message):
  global riotmode
  global deletelinksmode
  global deletebotsmode
  
  if user_admin_role(message):
    if 'c!riot on' in message.content:
       if riotmode == False:
         riotmode = True
         await response(message, "Riot Mode has been enabled due to drama. Please listen to the server administration.")
         logger.debug("Enabled riot mode!")
         logger3.debug("Enabled riot mode!")
         
    if 'c!riot off' in message.content:
      if riotmode == True:
         riotmode = False
         await response(message, "Riot Mode has been disabled.")
         logger.debug("Disabled riot mode!")
         logger3.debug("Disabled riot mode!")
     
    if 'c!deletelinks on' in message.content:
      if deletelinksmode == False:
         deletelinksmode = True
         await response(message, "Link Deleting Mode has been enabled.")
         logger.debug("Enabled link deleting mode!")
         logger3.debug("Enabled link deleting mode!")
     
    if 'c!deletelinks off' in message.content:
      if deletelinksmode == True:
         deletelinksmode = False
         await response(message, "Link Deleting Mode has been disabled.")
         logger.debug("Disabled link deleting mode!")
         logger3.debug("Disabled link deleting mode!")
     
    if 'c!deletebots on' in message.content:
      if deletebotsmode == False:
         deletebotsmode = True
         await response(message, "Bot Response Deleting Mode has been enabled.")
         logger.debug("Enabled bot response deleting mode!")
         logger3.debug("Enabled bot response deleting mode!")
     
    if 'c!deletebots off' in message.content:
      if deletebotsmode == True:
         deletebotsmode = False
         await response(message, "Bot Response Deleting Mode has been enabled.")
         logger.debug("Disabled bot response deleting mode!")
         logger3.debug("Disabled bot response deleting mode!")

    if 'c!help' in message.content:
      await response(message, "Commands (Admin Only) - c!riot <on/off>, c!deletelinks <on/off>, c!deletebots <on/off>, c!help")
     
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
	 
async def response(message, content):
  em = discord.Embed(title='Chillbot Message', description=content, colour=0x7ED6DE)
  em.set_author(name=client.user.name, icon_url=client.user.avatar_url)
  await client.send_message(message.channel, embed=em)

print('Connecting...')
logger3.debug("Chillbot Connecting...")
try:
 file = open('token.txt', 'r') 
 client.run(file.readline())
 logger3.debug("Chillbot Connected!")
except Exception as e:
 logger3.debug("Chillbot failed to connect with Discord!")
