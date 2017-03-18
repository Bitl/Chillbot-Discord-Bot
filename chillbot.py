#include files
import discord
from discord.ext import commands
import asyncio
import logging
import random
import aiohttp

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            content = 'Now playing ' + str(self.current)
            em = discord.Embed(title='Server Message', description=content, colour=0x7ED6DE)
            em.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await self.bot.send_message(self.current.channel, embed=em)
            self.current.player.start()
            await self.play_next_song.wait()

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
bot = commands.Bot(command_prefix=commands.when_mentioned_or('c!'), description="Basic Discord bot for Chaos' Chillspot server.")
aiosession = aiohttp.ClientSession(loop=bot.loop)

#these first 2 arrays show a whitelist for users to post links, and a bot list for deleting replies made by bots.
whitelist = ["226441820467494914", "159985870458322944", "185476724627210241", "109338686889476096", "115385224119975941", "172002275412279296"]
botlist = ["185476724627210241", "172002275412279296"]
#when you add commands, also add it along with its arguments here.
commlist = ["c!riot <on/off>", "c!deletelinks <on/off>", "c!deletebots <on/off>", "c!deleteads <on/off>", "c!help"]
#role whitelist for the commands themselves.
role_whitelist = ["254725867056398349", "266385101871513610", "254725919627935744", "288107558349307906"]

#game list. for fun.
game_list = ["Team Fortress 2", "Garry's Mod", "Portal", "Portal 2", "Left 4 Dead", "Left 4 Dead 2", "Half-Life 2", "Half-Life", "Counter-Strike: Global Offensive", 
"BioShock Infinite", "BioShock", "BioShock 2", "Killing Floor", "Killing Floor 2", "Borderlands", "Borderlands 2", "Fallout 3", "Fallout New Vegas", "Fallout 4", "DOOM", 
"Wolfenstein: The New Order", "Wolfenstein: The Old Blood", "The Ultimate DOOM", "DOOM II", "Final DOOM", "Quake", "Quake II", "Quake III Arena", "Wolfenstein 3D",
"Quake Live", "Synergy", "Terraria", "Minecraft", "ROBLOX", "Spore", "System Shock 2", "Duke Nukem 3D", "POSTAL 2", "Shadow Warrior", "Shadow Warrior 2", "Shadow Warrior Classic",
"Counter-Strike", "Counter-Strike Source", "Serious Sam: The First Encounter", "Serious Sam: The Second Encounter", "Serious Sam 3: BFE"]

voice_states = {}

#global vars.
riotmode = False
deletelinksmode = False
deletebotsmode = False
antiadvertising = True
        
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
  if antiadvertising == True:
    print('Delete Server Advertisements: Enabled')
  else:
    print('Delete Server Advertisements: Disabled')
  print('---------')
  print('Chillbot Loaded.')
  print('---------')
  chosen_game = random.choice(game_list)
  print('Now Playing:')
  print(chosen_game)
  await bot.change_presence(game=discord.Game(name=chosen_game))
  print('---------')
  print('To invite to your server use')
  print('https://discordapp.com/api/oauth2/authorize?client_id=' + bot.user.id + '&scope=bot&permissions=0')
  
async def change_game():
  await bot.wait_until_ready()
  while not bot.is_closed:
      chosen_game = random.choice(game_list)
      logger.debug("Now Playing:")
      logger.debug(chosen_game)
      await bot.change_presence(game=discord.Game(name=chosen_game))
      #hourly updates.
      await asyncio.sleep(3600)

#event on message.
@bot.event
async def on_message(message):
  await message_event_func(message)
  
#event on message edit.
@bot.event
async def on_message_edit(before, after):
  await message_event_func(after)

#message fucntion
async def message_event_func(message):
  #make sure we don't mention ourselves.
  if message.author == bot.user:
    return

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
  welcomemsg = '{0.mention}, welcome to the Chillspot! Be sure to have fun!'.format(member)
  em = discord.Embed(title='Welcome!', description=welcomemsg, colour=0x7ED6DE)
  em.set_author(name=member.name, icon_url=member.avatar_url)
  await bot.send_message(server, embed=em)
  await bot.send_file(server, 'welcomebanner.png')
  welcomemsgdebug = '{0.name} joined the server.'.format(member)
  logger.debug(welcomemsgdebug)
  logger3.debug(welcomemsgdebug)

#on user leave event
@bot.event
async def on_member_remove(member):
  server = member.server
  leavemsg = '{0.name} has left the server.'.format(member)
  em = discord.Embed(title='Bye!', description=leavemsg, colour=0xF41400)
  em.set_author(name=member.name, icon_url=member.avatar_url)
  await bot.send_message(server, embed=em)
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
  """Mods - Changes the bot's avatar."""
  message = ctx.message
  
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
	 
def get_voice_state(server):
  state = voice_states.get(server.id)
  if state is None:
     state = VoiceState(bot)
     voice_states[server.id] = state

  return state

async def create_voice_client(channel):
  voice = await bot.join_voice_channel(channel)
  state = get_voice_state(channel.server)
  state.voice = voice

def __unload():
  for state in voice_states.values():
     try:
      state.audio_player.cancel()
      if state.voice:
         bot.loop.create_task(state.voice.disconnect())
     except:
       pass
	   
@bot.command(pass_context=True, no_pm=True)
async def join(ctx, *, channel : discord.Channel):
  """Music - Joins a voice channel."""
  message = ctx.message
  if ctx.args is None:
     await response(message, "Help: c!join <voice channel>")
     return
  
  try:
     await create_voice_client(channel)
  except discord.ClientException:
     await response(message, 'Already in a voice channel...')
  except discord.InvalidArgument:
     await response(message, 'This is not a voice channel...')
  else:
     await response(message, 'Ready to play audio in ' + channel.name)

@bot.command(pass_context=True, no_pm=True)
async def summon(ctx):
  """Music - Summons the bot to join your voice channel."""
  summoned_channel = ctx.message.author.voice_channel
  message = ctx.message
  if summoned_channel is None:
     await response(message, 'You are not in a voice channel.')
     return False

  state = get_voice_state(ctx.message.server)
  if state.voice is None:
     state.voice = await bot.join_voice_channel(summoned_channel)
  else:
     await state.voice.move_to(summoned_channel)

  return True

@bot.command(pass_context=True, no_pm=True)
async def play(ctx, *, song : str):
  """Music - Plays a song.
  If there is a song currently in the queue, then it is
  queued until the next song is done playing.
  This command automatically searches as well from YouTube.
  The list of supported sites can be found here:
  https://rg3.github.io/youtube-dl/supportedsites.html
  """
  message = ctx.message
  if ctx.args is None:
     await response(message, "Help: c!play <YouTube URL>")
     return
	 
  state = get_voice_state(ctx.message.server)
  opts = {
     'default_search': 'auto',
     'quiet': True,
  }

  if state.voice is None:
     success = await ctx.invoke(summon)
     if not success:
       return

  try:
     player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
  except Exception as e:
     fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
     await bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
  else:
     player.volume = 0.6
     entry = VoiceEntry(ctx.message, player)
     await response(message, 'Enqueued ' + str(entry))
     await state.songs.put(entry)

@bot.command(pass_context=True, no_pm=True)
async def volume(ctx, value : int):
  """Music - Sets the volume of the currently playing song."""
  message = ctx.message
  if ctx.args is None:
     await response(message, "Help: c!volume <volume amount>")
     return
	 
  state = get_voice_state(ctx.message.server)
  if state.is_playing():
     player = state.player
     player.volume = value / 100
     await response(message, 'Set the volume to {:.0%}'.format(player.volume))

@bot.command(pass_context=True, no_pm=True)
async def pause(ctx):
  """Music - Pauses the currently played song."""
  
  message = ctx.message
  state = get_voice_state(ctx.message.server)
  if state.is_playing():
     player = state.player
     player.pause()

@bot.command(pass_context=True, no_pm=True)
async def resume(ctx):
  """Music - Resumes the currently played song."""
  message = ctx.message
  state = get_voice_state(ctx.message.server)
  if state.is_playing():
     player = state.player
     player.resume()

@bot.command(pass_context=True, no_pm=True)
async def stop(ctx):
  """Music - Stops playing audio and leaves the voice channel.
  This also clears the queue.
  """
  server = ctx.message.server
  state = get_voice_state(server)

  if state.is_playing():
     player = state.player
     player.stop()

  try:
     state.audio_player.cancel()
     del voice_states[server.id]
     await state.voice.disconnect()
  except:
     pass

@bot.command(pass_context=True, no_pm=True)
async def skip(ctx):
  """Music - Vote to skip a song. The song requester can automatically skip.
  3 skip votes are needed for the song to be skipped.
  """
  message = ctx.message
  state = get_voice_state(ctx.message.server)
  if not state.is_playing():
     await response(message, 'Not playing any music right now...')
     return

  voter = ctx.message.author
  if voter == state.current.requester:
     await response(message, 'Requester requested skipping song...')
     state.skip()
  elif voter.id not in state.skip_votes:
     state.skip_votes.add(voter.id)
     total_votes = len(state.skip_votes)
     if total_votes >= 3:
       await response(message, 'Skip vote passed, skipping song...')
       state.skip()
     else:
       await response(message, 'Skip vote added, currently at [{}/3]'.format(total_votes))
  else:
       await response(message, 'You have already voted to skip this song.')

@bot.command(pass_context=True, no_pm=True)
async def playing(ctx):
  """Music - Shows info about the currently played song."""
  message = ctx.message
  state = get_voice_state(ctx.message.server)
  if state.current is None:
     await response(message, 'Not playing anything.')
  else:
     skip_count = len(state.skip_votes)
     await response(message, 'Now playing {} [skips: {}/3]'.format(state.current, skip_count))
	 
async def response(message, content):
  em = discord.Embed(title='Server Message', description=content, colour=0x7ED6DE)
  em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
  await bot.send_message(message.channel, embed=em)

print('Connecting...')
logger3.debug("Chillbot Connecting...")
try:
 bot.loop.create_task(change_game())
 file = open('token.txt', 'r') 
 bot.run(file.readline())
 logger3.debug("Chillbot Connected!")
except Exception as e:
 logger3.debug("Chillbot failed to connect with Discord!")
