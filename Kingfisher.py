from __future__ import print_function

import asyncio
import aiofiles
import codecs
import datetime
import json
import logging
import math
import nltk
import operator
import os
import pickle
import platform
import random
import re
import sched
import sys
import time
import threading
import traceback
import uuid
import cProfile


import discord  # the crown jewel
import aiohttp
import gspread
import pytz
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageDraw, ImageColor
from ruamel.yaml import YAML
from operator import itemgetter

version = "0.3a Roll v2"


# TODO: add self-tagging, servers
# TODO: ranking rework
# TODO: add server configuration
# TODO: migrate to db

clientloop = asyncio.new_event_loop()
asyncio.set_event_loop(clientloop)
owner = [138340069311381505]  # hyper#4131
gms= []

stdlogger = logging.basicConfig(level=logging.INFO)
# https://github.com/Rapptz/discord.py/search?q=on_command_error&unscoped_q=on_command_error
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=f'discordTEST.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setup the Sheets API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets.readonly']
credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread.json', scope)
gc = gspread.authorize(credentials)

feed=[[],[],[]]
# kingfisher reference doc
with open("Reference.txt", 'r') as f:
        reference=f.read()
RefSheet = gc.open_by_key(reference) # kf reference doc
sheet = RefSheet.worksheet("Wounds") # wd20
feed[0] = sheet.get_all_values()
sheet_SD=RefSheet.worksheet("Wounds_SD") # skitterdice
feed[1] = sheet_SD.get_all_values()
sheet_WD=RefSheet.worksheet("Wounds_WD") # original weaverdice
feed[2] = sheet_WD.get_all_values()
tagsSheet = RefSheet.worksheet("Tags")
tags = tagsSheet.get_all_values()
perksSheet = RefSheet.worksheet("Perks")
perksfeed = perksSheet.get_all_values()
augSheet = RefSheet.worksheet("Augments")
augfeed = augSheet.get_all_values()
triggerSheet = RefSheet.worksheet("Triggers")
triggerfeed = triggerSheet.get_all_values()
pactfeed = RefSheet.worksheet("Pactluck")
pactfeed = pactfeed.get_all_values()

#Factions

rp_factions = {"gh":{"neutral":(255,255,255), "independent":(163, 145, 108)},"dh":{"neutral":(255,255,255), "independent":(163, 145, 108)},
                "ssn":{"neutral":(255,255,255), "independent":(163, 145, 108)}}
#"x":ImageColor.getrgb("x"),
# discord default colours: https://www.reddit.com/r/discordapp/comments/849bxc/what_are_the_hex_values_of_all_the_default_role/dvo5k3g/

#vials
VialDoc = gc.open_by_key("1yksmYY7q1GKx4tXVpb7oSxffgEh--hOvXkDwLVgCdlg") # arcan's vial doc
sheet = VialDoc.worksheet("Full Vials")
vialfeed = sheet.get_all_values()
sPlanner = sched.scheduler(time.time, time.sleep) # class sched.scheduler(timefunc=time.monotonic, delayfunc=time.sleep)

#################
#global variables
#################
macros={}
fools=False
b_task=None
b_task2=None

#Map path, used for claim image editing
rp_areas = {"gh":[(330.00,352.00),(412.00,226.00),(724.00,224.00),(688.00,350.00),(842.00,386.00),(936.00,212.00),(1164.00,410.00),(1300.00,214.00),(1424.00,160.00),
            (1524.00,50.00),(1538.00,176.00),(1402.00,328.00),(1520.00,352.00),(1528.00,498.00),(1414.00,476.00),(1098.00,536.00),(858.00,550.00),(690.00,508.00),(464.00,424.00),
            (494.00,524.00),(358.00,604.00),(376.00,714.00),(486.00,754.00),(686.00,656.00),(718.00,726.00),(640.00,728.00),(972.00,624.00),(1360.00,696.00),(1502.00,676.00),
            (1610.00,696.00),(1630.00,908.00),(1322.00,796.00),(1090.00,816.00),(828.00,808.00),(734.00,914.00),(750.00,1036.00),
            (498.00,976.00),(512.00,1082.00),(582.00,1110.00),(412.00,1260.00),(628.00,1302.00),(750.00,1190.00),(876.00,1054.00),(1090.00,1044.00),(1064.00,1174.00),(1202.00,1168.00),
            (1034.00,1320.00),(1218.00,1402.00),(1312.00,1046.00),(1488.00,1058.00),(1646.00,1326.00),(1456.00,1288.00),(1392.00,1406.00),(1044.00,1428.00),(824.00,1406.00),
            (576.00,1430.00),(486.00,1512.00),(420.00,1402.00),(426.00,1528.00),(606.00,1652.00),(890.00,1664.00),(1096.00,1646.00),(1260.00,1640.00),(1440.00,1624.50),(1489.50,1438.50),
            (1608.00,1599.00)],
            "dh":  [(213.00,67.50),
                    (106.50,216.00),
                    (63.00,525.00),
                    (90.00,760.50),
                    (253.50,610.50),
                    (297.00,456.00),
                    (313.50,327.00),
                    (288.00,211.50),
                    (498.00,85.50),
                    (508.50,202.50),
                    (564.00,471.00),
                    (634.50,676.50),
                    (769.50,793.50),
                    (775.50,589.50),
                    (736.50,457.50),
                    (711.00,253.50),
                    (709.50,76.50),
                    (912.00,96.00),
                    (943.50,285.00),
                    (885.00,442.50),
                    (1024.50,486.00),
                    (1006.50,655.50),
                    (912.00,838.50),
                    (1087.50,886.50),
                    (1206.00,750.00),
                    (1219.50,619.50),
                    (1200.00,462.00),
                    (1137.00,336.00),
                    (1075.50,180.00),
                    (1294.50,184.50),
                    (1420.50,238.50),
                    (1224.00,355.50),
                    (1408.50,370.50),
                    (1432.50,540.00),
                    (1449.00,690.00),
                    (1422.00,985.50)]}

rp_areas_dict= {"ssn": {'A1':(444.00,174.00),
                'A2':(363.00,867.00),
                'A3':(1341.00,561.00),
                'A4':(942.00,438.00),
                'A5':(1041.00,588.00),
                'A6':(1074.00,945.00),
                'A7':(903.00,762.00),
                'A8':(798.00,969.00),
                'A9':(588.00,882.00),
                'A10':(693.00,441.00),
                'B1':(720.00,1413.00),
                'B2':(384.00,1539.00),
                'B3':(621.00,1617.00),
                'B4':(537.00,1809.00),
                'B5':(372.00,1860.00),
                'B6':(261.00,1671.00),
                'C1':(1329.00,2070.00),
                'C2':(1395.00,2187.00),
                'C3':(1314.00,2301.00),
                'C4':(1122.00,2202.00),
                'C5':(1215.00,1977.00),
                'D1':(2532.00,2184.00),
                'D2':(2280.00,2097.00),
                'D3':(2436.00,1971.00),
                'D4':(2304.00,1812.00),
                'D5':(2148.00,2022.00),
                'D6':(2139.00,1821.00),
                'E1':(2823.00,1683.00),
                'E2':(2679.00,1488.00),
                'E3':(2805.00,1341.00),
                'E4':(2889.00,1263.00),
                'E5':(2802.00,1050.00),
                'E6':(2607.00,1023.00),
                'F1':(1977.00,252.00),
                'F2':(2358.00,822.00),
                'F3':(1962.00,417.00),
                'F4':(1983.00,513.00),
                'F5':(1962.00,594.00),
                'F6':(1965.00,699.00),
                'F7':(1956.00,822.00)}}

typ_colours = {"Bash":0x0137f6,"Pierce":0xffa500,"Cut":0xb22649,"Freeze":0x00ecff,"Shock":0xd6ff00,"Rend":0x9937a5,"Burn":0x0fe754, "Poison":0x334403,
               "Armor":0x565759,"Engine":0x565759,"Wheel":0x565759,"System":0x565759,"Structural":0x565759}
muted_usr = []


# Here you can modify the bot's prefix and description and whether it sends help in direct messages or not.
bot = Bot(description=f"Thinkerbot version {version}", command_prefix=(">",";"), pm_help=False, case_insensitive=True,owner_id=138340069311381505)
bot.stance_array={}


# This is what happens every time the bot launches. In this case, it prints information like server count, user count the bot is connected to, and the bot id in the console.
# Do not mess with it because the bot can break, if you wish to do so, please consult me or someone trusted.
@bot.event
async def on_connect():
    print("connected!")
    await bot.change_presence(activity=discord.Game(name='>help | >nest'))

    global b_task
    global b_task2
    b_task=bot.loop.create_task(account_decay())
    b_task2=bot.loop.create_task(rank_decay())

    #roll macros
    global macros
    with open(f"roll_macros.txt",mode="r") as f:
        macros = json.load(f)

    return


@bot.event
async def on_ready():
    print('--------')
    print('Logged in as '+bot.user.name+' (ID:'+str(bot.user.id)+') | Connected to '+str(len(bot.guilds))+' servers | Connected to '+str(len(set(bot.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')

    if sPlanner.empty():
        loop = asyncio.get_event_loop()
        try:
            with open(f"reminders.kf",mode="rb+") as f:
                try:
                    reminders = pickle.load(f)
                except EOFError:
                    reminders = []
            for i in reminders:
                #print(i["embed"].description)
                channel=bot.get_channel(i["channel"])
                try:
                    sPlanner.enterabs(i["timer"], 10, asyncio.run_coroutine_threadsafe,
                                      argument=(channel.send(i["reactlist"],embed=i["embed"]),loop,), kwargs={})
                except AttributeError:
                    print(i.embed.description)
        except FileNotFoundError:
            print("No reminders file!")
    with open(f"reminders.kf",mode="wb+") as f:
        pickle.dump([],f)
    print('Reminders loaded.')
    print('--------')

    #grab the GH gms for some command checks
    if len(bot.guilds)>1:
        global gms
        grand_haven=discord.utils.get(bot.guilds,id=465651565089259521)
        if grand_haven is None:
            gms=[owner]
        gm_iter=grand_haven.members
        gm_list = [[x for y in x.roles if y.name=="Assistant Game Master"] for x in gm_iter]
        gms= [[x.id for x in y] for y in gm_list]
        gms= [item for sublist in gms for item in sublist]
    else:
        gms=owner
    print(f"Listed GMs: {gms}")
    print('--------')

    global rp_factions

    with open(f"rp_factions.yaml",mode="r+") as f:
        rp_factions=yaml.load(f)
        rp_factions=dict(rp_factions) #YAML can't handle tuples, so we have convert back
        for guilds in rp_factions:
            rp_factions[guilds]=dict(rp_factions[guilds]) #we're also getting rid of all these fuck-annoying ordereddicts
        for guilds in rp_factions.keys():
            for k in rp_factions[guilds].keys():
                rp_factions[guilds][k]=tuple(rp_factions[guilds][k])

    print('Ready!')


###Functions
#to add new factions
#add new faction colour
#add faction to legend via gimp
#requires PIL 5.1.0 for some godforsaken reason b/c of floodfill
async def mapUpdate(faction,square,sid):
    detroitmap = Image.open(f"map_{sid}/factionmap.png")
    legend = Image.open(f"map_{sid}/Legend_alpha.png")

    ImageDraw.floodfill(detroitmap, rp_areas[sid][square-1], (255,255,255))
    ImageDraw.floodfill(detroitmap, rp_areas[sid][square-1], rp_factions[sid][faction])

    detroitmap.save(f"map_{sid}/factionmap.png") #only the coloured squares
    detroitmap = Image.alpha_composite(detroitmap,legend)
    detroitmap.save(f"map_{sid}/map.png") #output

async def mapUpdateDict(faction,square,sid):
    square=square.upper()
    detroitmap = Image.open(f"map_{sid}/factionmap.png")
    legend = Image.open(f"map_{sid}/Legend_alpha.png")

    ImageDraw.floodfill(detroitmap, rp_areas_dict[sid][square], (255,255,255))
    ImageDraw.floodfill(detroitmap, rp_areas_dict[sid][square], rp_factions[sid][faction])

    detroitmap.save(f"map_{sid}/factionmap.png") #only the coloured squares
    detroitmap = Image.alpha_composite(detroitmap,legend)
    detroitmap.save(f"map_{sid}/map.png") #output


#used to display rankings
async def int_to_roman(input):
    if not isinstance(input,int):
        raise TypeError(f"expected integer, got {type(input)}")
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = ""
    for i in range(len(ints)):
        count = int(input / ints[i])
        result += nums[i] * count
        input -= ints[i] * count
    return result


#figure out which server this command runs on. Remind me to actually write server configs one day. One day. xd.
async def sid(loc):
    if loc==465651565089259521:
        sid="gh"
    elif loc==573815526133071873:
        sid="gh" #shardforge server, attached to GH
    elif loc==434729592352276480:
        sid="test" #aka nest, aka test server
    elif loc==406587085278150656:
        sid="segovia"
    elif loc==457290411698814980:
        sid="la"
    elif loc==521547663641018378:
        sid="autumn lane"
    elif loc==343748202379608065:
        sid="gaming_inc"
    elif loc==570300070252249089:
        sid="portland"
    elif loc==636431438916616192:
        sid="deathland"
    elif loc==656862194918490112:
        sid="Benelux"
    elif loc==691221976311660595:
        sid="dh"
    elif loc==721135308497748048:
        sid="ssn" #sunset nova
    elif loc==619043630187020299 or loc==721792672683130880:
        sid="wd6"
    else:
        sid=str(loc)
    return sid

async def sizeof_fmt(num, suffix='B'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


async def rem_depickle(rem_dict):

    with open(f"reminders.kf",mode="rb+") as f:
        reminders = pickle.load(f)

        for i in reminders:
            if (i["channel"]==rem_dict["channel"] and i["embed"].description==rem_dict["embed"].description and
                    i["embed"].description==rem_dict["embed"].description and
                    i["embed"].timestamp==rem_dict["embed"].timestamp) and i["ID"]==rem_dict["ID"]:
                reminders.remove(i)

        f.seek(0)
        pickle.dump(reminders,f)


def naming(guild,id):
    usr= guild.get_member(int(id))
    if usr is None:
        return "KF_Unknown"
    return usr.display_name


def cleaner(ctx,text): #removes usermentions and replaces them with @display_name
    p_pattern=re.compile("<@!*(\d*)>")
    p_match=p_pattern.finditer(text)
    pings={}
    for i in p_match:
        pings[i]=naming(ctx.guild,i.group(1))
    for i in pings:
        text=text.replace(i.group(0),f"@{pings[i]}")
    return text


#Deals with special wounds that require more interaction. Most commonly used to roll the effects chains for critical wounds.
specWounds=("Demolished","Cremated","Disintegrated (shock)","Iced Over","Whited Out","Devastated","Annihilated","Spreading","Infused")


async def specialWounds(bot,ctx,case,f,aim):
    #f distinguishes which system is used
    ctx.invoked_with="wound"
    if case=="Demolished":
        bashes=[]
        if aim=="Any":
            limb=random.choice(["Arm","Legs","Head"])
        else:
            limb=aim
        for i in feed[f]:
            if i[0]=="Bash":
                if i[1]=="Moderate":
                    if i[2].casefold()==limb.casefold():
                        bashes.append(i)
            embed = discord.Embed(title="__**Effect**__",colour=discord.Colour(typ_colours["Bash"]))
            embed.set_footer(text=f"Rolled for {ctx.message.author.name} | {case}",icon_url=ctx.message.author.avatar_url)
            for i in bashes:
                embed.add_field(name=f"**{i[3]}**", value=f"{i[4]}\n*Location: {i[2]}, Stage: {i[1]}*")
        await ctx.message.channel.send(embed=embed)
    elif (case=="Cremated") or (case=="Whited Out") or (case=="Disintegrated (shock)"):
        if case=="Cremated":
            typ="Burn"
        elif case=="Disintegrated (shock)":
            typ="Shock"
        elif case=="Whited Out":
            typ="Freeze"
        await ctx.invoke(wound,typus=typ,tag=case,title="__**Effect**__")
        while random.randint(0,1) < 1:
            await asyncio.sleep(0.2)
            await ctx.invoke(wound,typus=typ,tag=case)
        await ctx.message.channel.send("Tails.")
    elif (case=="Iced Over"):
        await asyncio.sleep(0.2)
        await ctx.invoke(wound,typus="Freeze",tag=case,title="__**Effect**__")
    elif (case=="Spreading"):
        await asyncio.sleep(0.2)
        await ctx.invoke(wound,typus="Poison",severity="Lesser",tag=case,title="__**Effect**__")
    elif (case=="Infused"):
        await asyncio.sleep(0.2)
        await ctx.invoke(wound,typus="Poison",severity="Lesser",tag=case,title="__**Effect**__")
    elif (case=="Devastated"):
        typ=random.choice(["Cut","Bash","Pierce"])
        await asyncio.sleep(0.1)
        await ctx.invoke(wound,severity="Lesser",typus=typ,tag=case)
    elif (case=="Annihilated"):
        await ctx.invoke(roll,"3D7+0")


#Translates wound severity from our shorthands back to the longer explicit version.
async def severity_short(arg):
    if (arg=="lesser") or (arg=="les") or (arg=="l"):
        return "lesser"
    elif (arg=="moderate") or (arg=="mod") or (arg=="m"):
        return "moderate"
    elif (arg=="critical") or (arg=="crit") or (arg=="c"):
        return "critical"
    else:
        print("Comprehension Error in severity_short")


#check if a user is the bot itself
def is_me(m):
    return m.author == bot.user


def not_me(m):
    return m.author != bot.user


def owner_only(ctx):
    return ctx.message.author.id in owner


def gm_only(ctx):
    return ctx.message.author.id in gms


#global check to make sure blocked people can't mess around
@bot.check
def mute_user(ctx):
    return ctx.message.author.id not in muted_usr


@bot.event
async def on_member_join(member):
    # own = bot.get_user(owner[0])
    server=await sid(member.guild.id)
    if (server=="gh"):
        target_guild = member.guild
        target =       discord.utils.find(lambda m:m.id==505835786810294272,target_guild.channels)
        await target.send(f"New player joined {member.guild.name}: {member.name} \n Account creation on {member.created_at}")
    if (server=="test"):
        target_guild = member.guild
        target =       discord.utils.find(lambda m:m.id==731108234785587210,target_guild.channels)
        await target.send(f"New player joined {member.guild.name}: {member.name} \n Account creation on {member.created_at}")


@bot.event
async def on_member_remove(member):
     # own = bot.get_user(owner[0])
    server=await sid(member.guild.id)
    if (server=="gh"):
        target_guild = member.guild
        target =       discord.utils.find(lambda m:m.id==505835786810294272,target_guild.channels)
        await target.send(f"{member.name} left {member.guild.name}")
    if (server=="test"):
        target_guild = member.guild
        target =       discord.utils.find(lambda m:m.id==731108234785587210,target_guild.channels)
        await target.send(f"{member.name} left {member.guild.name}")

@bot.event
async def on_guild_join(guild):
    target_guild = discord.utils.find(lambda m:m.id==434729592352276480,bot.guilds)
    target =       discord.utils.find(lambda m:m.id==731108234785587210,target_guild.channels)
    await target.send(f"Joined {guild.name}, owner is {guild.owner.display_name}.")

@bot.event
async def on_guild_remove(guild):
    target_guild = discord.utils.find(lambda m:m.id==434729592352276480,bot.guilds)
    target =       discord.utils.find(lambda m:m.id==731108234785587210,target_guild.channels)
    await target.send(f"Left {guild.name}, owner is {guild.owner.display_name}.")

@bot.event
async def on_message_edit(before,after):
    global fools
    if fools: #april fools, enforce entity-speak ("AGREEMENT.")
        if (after.channel.id==435874236297379861) or (after.channel.id==465651565089259523) or (after.channel.id==478240151987027978):
            await after.delete()

@bot.event
async def on_raw_reaction_add(payload):
    #print(payload)
    if payload.channel_id==435874236297379861 or payload.channel_id==731913135916711976:
        guild = discord.utils.get(bot.guilds, id=payload.guild_id)
        member = discord.utils.get(guild.members, id=payload.user_id)
        utopia_role = discord.utils.get(guild.roles, name="U.T.O.P.I.A")
        channel = discord.utils.get(guild.channels, id=payload.channel_id)
        if utopia_role not in member.roles:
            await channel.send(f"Voting machine goes brrrr. And {member.mention} is getting banned.")
            message = await channel.fetch_message(payload.message_id)
            for i in message.reactions:
                async for user in i.users():
                    if user==member:
                        await i.remove(user)

            #remove react



@bot.event
async def on_message(message):
    try:
        #checks-public 587718887936753710
        #checks-private 587718930483773509

        #talk-private 603035662018543618
        #talk-private-archive 614168400523952181

        #quest-request 601810695583039557

        #test-beta 538633337191923714
        #test-dev 435874236297379861
        if not_me(message):
            
            #Forward DMs to whispers channel
            if message.channel.type==discord.ChannelType.private:
                target_guild = discord.utils.find(lambda m:m.id==434729592352276480,bot.guilds)
                target =       discord.utils.find(lambda m:m.id==731108234785587210,target_guild.channels)
                await target.send(f"DM \n {message.content} \n by {message.author.name}")


            #function for having channels people can declare stuff into
            #deletes the postings in one channel, then sends them to a different one
            #declare-public
            #TODO: change this to embeds!/make it pretty
            if message.channel.id==587718887936753710:
                target=discord.utils.find(lambda m:m.id==587718930483773509,message.guild.channels)
                await target.send(f"{message.content} \n*sent by {message.author.name}, ID `{message.author.id}` at {message.created_at}*")
                await message.delete()

            #declare public for duskhaven
            elif message.channel.id==694012416639369297:
                target=discord.utils.find(lambda m:m.id==694012447002066995,message.guild.channels)
                await target.send(f"**{message.content}** sent by {message.author.name}, ID `{message.author.id}` at {message.created_at}")
                await message.delete()

            #declare public for sunsetnova
            elif message.channel.id==721220887910547486:
                target=discord.utils.find(lambda m:m.id==721220928796885082,message.guild.channels)
                await target.send(f"**{message.content}** sent by {message.author.name}, ID `{message.author.id}` at {message.created_at}")
                await message.delete()

            #private-talk
            elif message.channel.id==603035662018543618:
                target=discord.utils.find(lambda m:m.id==614168400523952181,message.guild.channels)
                await target.send(f"{message.author.name}: {message.content}")
            #quest-requests
            elif message.channel.id==601810695583039557:
                target=await message.channel.fetch_message(601812539319386123)
                target=discord.utils.get(target.reactions,emoji="\U0000270d") #writing hand
                usrs=await target.users().flatten()
                if message.author not in usrs:
                    await message.channel.send(f"{message.author.mention}: Think you're above the rules, huh? **Read the pins**, you illiterate baboon. Denied.")
                    await message.delete()
            elif message.channel.id==721206670730068050:
                target=await message.channel.fetch_message(731041156519034880)
                target=discord.utils.get(target.reactions,emoji="\U0001F476") #babu
                usrs=await target.users().flatten()
                if message.author not in usrs:
                    await message.channel.send(f"{message.author.mention}: Think you're above the rules, huh? **Read the pins**.", 
                                                " Whatever god you pray to shall no longer accept your soul.")
                    await message.delete()

        global fools
        if fools: #april fools, enforce entity-speak ("AGREEMENT.")
            if (message.channel.id==435874236297379861) or (message.channel.id==465651565089259523) or (message.channel.id==478240151987027978):
                try:
                    deletion_trigger=False
                    reason_caps=False
                    reason="Message deleted. Remember: \n"

                    counter=0
                    async for old_message in message.channel.history(limit=2):
                        #print("old message: "+old_message.content)
                        counter+=1
                        if old_message.author==message.author and counter==2:
                            deletion_trigger=True
                            reason+="No consecutive messages!\n"
                    print("channel: "+message.channel.name)
                    print(message.author.name)
                    speak=message.content
                    print("**** speak: "+speak)

                    if message.attachments:
                        await message.delete()

                    #make sure we don't delete pings
                    p_pattern=re.compile("<@(!|&)\d+>")
                    p_match=p_pattern.sub("",speak)
                    #print("p_match: "+p_match)
                    #Make sure the message contains only nouns
                    n_match=nltk.tag.pos_tag(p_match.split())
                    #print(n_match)
                    #if p_match==speak:
                    #    deletion_trigger=True

                    punctuation=["-","'","_"]
                    if any(e in p_match for e in punctuation):
                        await message.delete()

                    #CD NN NNS NNP NNPS
                    for i,j in n_match:
                        print(i+","+j)
                        if j not in ["CD", "NN", "NNS", "NNP", "NNPS","VB"]:
                            deletion_trigger= True

                    if deletion_trigger:
                        reason+="Nouns only! \n"

                    print(speak)
                    if p_match[-1]!=".":
                        deletion_trigger= True
                        reason+="Full stop at the end only! \n"

                    print("p_match: "+p_match)
                    for i in p_match[:-1]:
                        #print("i: "+i)
                        if not (i.isupper() or i==" "):
                            deletion_trigger= True
                            reason_caps=True
                    if reason_caps:
                        reason+="Caps only! \n"

                    len_split=p_pattern.sub("",speak)
                    len_split=len(len_split.split())
                    if (len_split>1):
                        #print("1 word deletion triggered")
                        deletion_trigger= True
                        reason+="One word only! \n"

                    if deletion_trigger:
                        try:
                            await message.author.send(reason)
                        except Exception as e:
                            print(e)

                        await message.delete()
                        print("DELETED")
                    print("------------------------")
                except:
                    print("April failed:", sys.exc_info())
                    raise

        #custom messages. Mostly jokes.
        if message.content==("DOCTOR NEFARIOUS"):
            await message.channel.send("🍋")
        elif message.content==("Kingfisher, play Despacito"):
            await message.channel.send("ɴᴏᴡ ᴘʟᴀʏɪɴɢ: Despacito \n ───────────────⚪─────────────────── \n  ◄◄⠀▐▐ ⠀►►⠀⠀ ⠀ 1:17 / 3:48 ⠀ ───○ 🔊⠀ ᴴᴰ ⚙ ❐ ⊏⊐")
        elif message.content==("F"):
            await message.channel.send("f")

        await bot.process_commands(message)

    except:
        await bot.process_commands(message)


@bot.event
async def on_command_error(context, exception):
        print(exception)
        print(type(exception))

        if hasattr(context.command, 'on_error'):
            return

        cog = context.cog
        if cog:
            if Cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        if type(exception)==discord.ext.commands.errors.CommandOnCooldown:
            await context.send(exception)

        if not type(exception)==discord.ext.commands.errors.CommandNotFound:
            print(f'Channel: {context.message.channel.name} \n Server: {context.guild.name} \n Ignoring exception in command {context.command}:', file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


@commands.check(owner_only)
@bot.command(description="Makes the bot leave the server.",hidden=True)
async def order67(ctx):
    if ctx.message.author.id not in owner:
        await ctx.send("😰")
        return
    await ctx.send("Macht’s gut, und danke für den Fisch.")
    await ctx.message.guild.leave()


@bot.command(description="Deletes channels of a selected category.",hidden=True)
async def order66(ctx,cat_id=None):
    if ctx.message.author.id not in owner:
        await ctx.send("I'm going to make you regret that.")
        return
    if cat_id is None:
        cat_id=ctx.channel.category_id
    else:
        cat_id=int(cat_id)
    category = discord.utils.get(ctx.guild.categories,id=cat_id)
    msg=await ctx.send(f"Please confirm you want to **__DELETE__** all channels in the {category.name} category by pressing 🚮!")
    await msg.add_reaction('🚮')

    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == '🚮'

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send(f"Process terminated.")
        await msg.remove_reaction('🚮',member=ctx.message.guild.me)
        return
    else:
        pass
    await ctx.send(f"Deleting the {category.name} category. {len(category.text_channels)} channels. Please stand by.")
    for i in category.text_channels:
        await ctx.send(f"Deleting {i.name}.")
        await i.delete()
    #await category.delete()  # keeping the empty category is actually a better idea
    await ctx.send(f"TERMINATION. AGREEMENT.")


@bot.command(description="How many channels are in this server?",hidden=False)
async def channels(ctx,):
    counter=len(ctx.guild.channels)
    await ctx.send(f"There are {counter} channels in this server.")


@commands.check(owner_only)
@bot.command(description="Prints memory usage.",hidden=True)
async def mem(ctx,):
    text="Locals --------"
    print(f"MEM Variables, memory useage: \n  {text:>20}")

    for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
                         key= lambda x: -x[1])[:10]:
        print("{:>30}: {:>8}".format(name, await sizeof_fmt(size)))

    text="Globals --------"
    print(f"{text:>20}")

    for name, size in sorted(((name, sys.getsizeof(value)) for name, value in globals().items()),
                         key= lambda x: -x[1])[:10]:
        print("{:>30}: {:>8}".format(name, await sizeof_fmt(size)))
    

@bot.command(description="Need help? Want to ask for new features? Visit the Nest, the central server for all your Kingfisher needs.")
async def nest(ctx):
    await ctx.send("https://discord.gg/gxQVAbA")


@bot.command(description="Default link to invite KF to your server. You need to be the owner or an admin!")
async def invite(ctx):
    await ctx.send("https://discordapp.com/oauth2/authorize?client_id=434701766425313280&scope=bot&permissions=271961280")


@bot.command(description="Deletes message content",hidden=True)
async def purge(ctx,limiter=100):
    if ctx.message.author.id not in owner:
        await ctx.send("😰")
        return
    try:
        await ctx.message.channel.purge(limit=limiter,bulk=True)
    except discord.Forbidden:
        await ctx.send("Insufficient priviliges.")


@bot.command(description="Accepts a message, puts out information on who reacted to it",hidden=True)
async def emojiwatch(ctx,id):
    target=await ctx.message.channel.fetch_message(id)
    print(target.reactions)
    target=discord.utils.get(target.reactions,emoji="\U0000270d") #writing hand
    usrs=await target.users().flatten()
    print(usrs)
    print(usrs[0])
    if ctx.author in usrs:
        print("True!")


@bot.command(description="""Reminds you of stuff. Time should be specified as 13s37m42h12d leaving away time steps as desired. Reacting to the emoji will also ping you
             when it fires. The original author will always be pinged.""", aliases=["rem"],rest_is_raw=False)
async def remind(ctx,times,*,message=""):
    loop = asyncio.get_event_loop()
    timer=0
    chunk=re.compile("\d+[shmd]*")
    chunkers=["s","h","m","d"]
    chunks=chunk.findall(times)
    for i in chunks:
        if "s" in i:
            times=int(i[:-1])
            timer=timer+times
        if "m" in i:
            times=int(i[:-1])*60
            timer=timer+times
        if "h" in i:
            times=int(i[:-1])*60*60
            timer=timer+times
        if "d" in i:
            times=int(i[:-1])*60*60*24
            timer=timer+times
        elif not any(x in i for x in chunkers):
            await ctx.send("You need to specify a time! Time should be specified as 13s37m42h12d leaving away time steps as desired.")
            return
    await ctx.message.add_reaction('\N{Timer Clock}')
    message=cleaner(ctx,message)

    embed = discord.Embed(colour=discord.Colour(0xf1e5d6),description=f"[Jump]({ctx.message.jump_url}) \n\n{message}", timestamp=datetime.datetime.utcfromtimestamp(time.time()))
    embed.set_author(name=ctx.message.author.display_name,icon_url=ctx.message.author.avatar_url)
    reactlist=ctx.message.author.mention

    def check(reaction, user):
        return user != ctx.message.author and str(reaction.emoji) == '\N{Timer Clock}' and user != bot.user

    timer_out=min(120.0,timer)
    try: #ping everyone that also reacts to our react emoji
        reaction, user = await bot.wait_for('reaction_add', timeout=timer_out, check=check)
    except asyncio.TimeoutError:
        pass
    else:
        reactlist=reactlist+f" {user.mention}"

    identifier=uuid.uuid4()
    rem_dict={"timer":time.time()+timer-timer_out,"channel":ctx.message.channel.id,"reactlist":reactlist,"embed":embed,"ID":identifier}

    sPlanner.enter(timer-timer_out, 10, asyncio.run_coroutine_threadsafe, argument=(ctx.message.channel.send(reactlist,embed=embed),loop,), kwargs={})

    with open(f"reminders.kf",mode="rb+") as f:
        try:
            embeds = pickle.load(f)
        except EOFError:
            embeds = []
        embeds.append(rem_dict)

        f.seek(0)
        pickle.dump(embeds,f)

    sPlanner.enter(timer-timer_out+2, 11, asyncio.run_coroutine_threadsafe, argument=(rem_depickle(rem_dict),loop,), kwargs={})


@bot.command(description="Shuts the bot down. Owner only.",hidden=True)
async def die(ctx):
    if ctx.message.author.id not in owner:
        await ctx.send("No. Fuck off.")
        return

    global b_task
    global b_task2
    b_task.cancel()
    b_task2.cancel()

    schedstop.set()
    # todo add warning to fights in progress
    # global 

    # TODO needs to save og nickname 
    # servs=bot.guilds
    # for i in servs:
    #     await i.me.edit(nick="Restarting...")

    await bot.close()


@bot.command(description="Shuts the bot down. Owner only.",hidden=True)
async def diehard(ctx):
    if ctx.message.author.id not in owner:
        await ctx.send("No. Fuck off.")
        return
    await bot.close()


@bot.command(description="Ping people who reacted to a specific message. Works with message ID or message link.")
async def qping(ctx,msg):

    try:
        message= await discord.ext.commands.MessageConverter().convert(ctx,msg)
    except:
        for i in ctx.guild.channels:
            try:
                message=await i.fetch_message(int(msg))
            except:
                pass
                #print(f"{i.name} did not find message")

    pinglist=""
    for i in message.reactions:
        async for user in i.users():
            pinglist=pinglist+(user.mention)+" "
    #print(pinglist)
    embed = discord.Embed(colour=discord.Colour(int("b5d7e4",16)),description=f"[Jump to orginal message]({message.jump_url})", timestamp=message.created_at)
    await ctx.send(f"{ctx.author.display_name} questpings {pinglist}",embed=embed)

@commands.check(owner_only)
@bot.command(description="Assign a specific role to everyone who has reacted to this message.")
async def qrole(ctx,msg,roleid):
    role=ctx.guild.get_role(int(roleid))
    for i in ctx.guild.channels:
        try:
            message=await i.fetch_message(int(msg))
        except:
            pass

    #message = await ctx.channel.fetch_message(int(msg))
    pinglist=0
    print(message.reactions)
    for i in message.reactions:
        async for user in i.users():
            try:
                await user.add_roles(role)
            except Exception as e:
                            print(e)
            await asyncio.sleep(10)
            pinglist += 1
    #print(pinglist)
    await ctx.send(f"{role.mention} has been assigned to {pinglist} users.")


#TODO: fix
@bot.command(description="Used to send messages via Kingfisher to all servers.",hidden=True)
async def announce(ctx,*message:str):
    if ctx.message.author.id not in owner:
        return
    servs=bot.guilds
    for i in servs:
        await ctx.send(i.name)
    targets=[]
    for i in servs:
        await ctx.send(f"{i.name} {i.system_channel} {i.member_count}")
        targets.append(i.system_channel)
    for i in targets:
        #await i.send(" ".join(message))
        return


@bot.command(description="Used to send messages via Kingfisher to a specific channel.",hidden=True)
async def tell(ctx,channel:int,*message:str):
    if ctx.message.author.id not in owner:
        return
    target=bot.get_channel(channel)
    await target.send(" ".join(message))


@bot.command(name='eval')
async def _eval(ctx, *, code):
    if ctx.message.author.id not in owner:
        return
    """A bad example of an eval command"""
    await ctx.send(eval(code))


@bot.command(description="Refreshes the data from the reference docs. Owner only.",hidden=True)
async def updateFeed(ctx):
    if ctx.message.author.id not in owner:
        await ctx.send("You weren't even a challenge.")
        return
    global feed
    global tags
    global vialfeed
    global perksfeed
    global augfeed
    global triggerfeed
    global rp_factions
    credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread.json', scope)
    gc = gspread.authorize(credentials)
    RefSheet = gc.open_by_key(reference)
    sheet = RefSheet.worksheet("Wounds")
    feed[0] = sheet.get_all_values()
    sheet_SD=RefSheet.worksheet("Wounds_SD")
    feed[1] = sheet_SD.get_all_values()
    sheet_WD=RefSheet.worksheet("Wounds_WD")
    feed[2] = sheet_WD.get_all_values()
    tagsSheet = RefSheet.worksheet("Tags")
    tags = tagsSheet.get_all_values()
    VialDoc = gc.open_by_key("1yksmYY7q1GKx4tXVpb7oSxffgEh--hOvXkDwLVgCdlg")
    sheet = VialDoc.worksheet("Full Vials")
    vialfeed = sheet.get_all_values()
    perksSheet = RefSheet.worksheet("Perks")
    perksfeed = perksSheet.get_all_values()
    augSheet = RefSheet.worksheet("Augments")
    augfeed = augSheet.get_all_values()
    triggerSheet = RefSheet.worksheet("Triggers")
    triggerfeed = triggerSheet.get_all_values()
    pactfeed = RefSheet.worksheet("Pactluck")
    pactfeed = pactfeed.get_all_values()
    with open(f"rp_factions.yaml",mode="r+") as f:
        rp_factions=yaml.load(f)
        #rp_factions=repr(dict(rp_factions))
        print(rp_factions)
        rp_factions=dict(rp_factions) #YAML can't handle tuples, so we have convert back
        for guilds in rp_factions:
            rp_factions[guilds]=dict(rp_factions[guilds]) #we're also getting rid of all these fucki-annoying ordereddicts
        for guilds in rp_factions.keys():
            for k in rp_factions[guilds].keys():
                rp_factions[guilds][k]=tuple(rp_factions[guilds][k])

    await ctx.message.add_reaction("\U00002714")


#fetch vials from the google sheet earlier for performance reasons. Then just format the stuff we're given. Easy. Has to account for some missing data.
@bot.command(description="Fetches vials from our vial sheet. Use *>vial* to roll a random vial, or *>vial Name* to look up a specific one.")
async def vial(ctx, avial=None):
    global vialfeed
    n=0
    vials=[[None]]*int((len(vialfeed)/4))
    output=None
    for i in range(1,len(vialfeed)):
        if vialfeed[i][0]!='':
            vials[n]=vialfeed[i]
            vials[n].extend(vialfeed[i+1])
            vials[n].extend(vialfeed[i+2])
            n=n+1

    if avial is not None:
        for i in range(0,len(vials)):
            if vials[i][0][:-1].casefold()==avial.casefold():
                output=vials[i]
    else:
        out=random.randint(0,len(vials)-1)
        output=vials[out]

    if output is None:
        await ctx.send(f"Vial {avial} not found.")
        return

    vialcolour=discord.Colour(0x00ffc4)
    embed = discord.Embed(title=f"__{output[0][:-1]}__", colour=vialcolour,url="https://docs.google.com/spreadsheets/d/1yksmYY7q1GKx4tXVpb7oSxffgEh--hOvXkDwLVgCdlg")
    embed.add_field(name="O [Desirability]",value=output[1][3:],inline=False)
    embed.add_field(name="P [Power]",value=output[5][3:],inline=False)
    if len(output[9][3:])>0:
        embed.add_field(name="R [Reliability]",value=output[9][3:],inline=False)
    embed.add_field(name=f"Case #1", value=output[3],inline=False)
    embed.add_field(name=f"Case #2", value=output[7],inline=False)
    if len(output[11])>0:
        embed.add_field(name=f"Case #3", value=output[11],inline=False)
    await ctx.send(embed=embed)


@bot.command(description="Perks and flaws. Use *>perk* to roll perks, *>flaw* to roll flaws. *>perk life* and *>flaw life* for life perks. Use *>perk start* to roll your starting perks. Can also look up perks and flaws (*>perk profundum*). Can also use WD's *>luck*.",aliases=["flaw","luck"])
async def perk(ctx, category=None):
    global perksfeed
    typus=0
    #2 perk life
    #3 perk power
    #4 flaw life
    #5 flaw power
    typus_name=[None,None,"Perk Life","Perk Power","Flaw Life","Flaw Power"]
    typus_colour=[None,None,discord.Colour(0xB6D7A8),discord.Colour(0x93C47D),discord.Colour(0xEA9999),discord.Colour(0xE06666)]

    if ctx.invoked_with.casefold()=="perk".casefold():
        #perk is column 2 and 3
        typus=typus+3
    elif ctx.invoked_with.casefold()=="flaw".casefold():
        #flaw is column 4 and 5
        typus=typus+5
    elif ctx.invoked_with.casefold()=="luck".casefold():
        category="luck"

    if (category is None) or (category=="power"):
        category="power" #we default to power perks
    elif category=="luck":
        luck=[None, None]
        luck[0]=random.randint(0,3)
        luck[1]=random.randint(0,3)
        typus=luck[0]+2
        if luck[1]==0:
            ctx.invoked_with="perk"
            await ctx.invoke(perk,category="power")
        elif luck[1]==1:
            ctx.invoked_with="perk"
            await ctx.invoke(perk,category="life")
        elif luck[1]==2:
            ctx.invoked_with="flaw"
            await ctx.invoke(perk,category="power")
        elif luck[1]==3:
            ctx.invoked_with="flaw"
            await ctx.invoke(perk,category="life")
    elif category=="life":
        typus=typus-1
    elif category.casefold()=="start":
        ctx.invoked_with="perk"
        await ctx.invoke(perk,category="power")
        await ctx.invoke(perk,category="life")
        ctx.invoked_with="flaw"
        await ctx.invoke(perk,category="power")
        await ctx.invoke(perk,category="life")
        return
    else:
        perkname=category
        for typus in range(2,6):
            for i in range(1,len(perksfeed)-2):
                p_pattern=re.compile("(\w*\,?\s?\-?\/?\'?)+\.")
                p_match=p_pattern.search(perksfeed[i][typus])
                if p_match: #required because there are some empty fields, and those don't return a p_match object at all, sadly
                    if (p_match.group()[:-1].casefold()==perkname.casefold()) or (p_match.group()[:-1].casefold().replace(" ","")==perkname.casefold()):
                        embed = discord.Embed(title=p_match.group()[:-1],description=perksfeed[i][typus][p_match.end():],colour=typus_colour[typus])
                        embed.set_footer(text=f"{typus_name[typus]}")
                        try:
                            await ctx.send(embed=embed)
                        except discord.HTTPException:
                            await ctx.send(perksfeed[i][typus])
        return

    out=random.randint(1,len(perksfeed)-3) ##roll a random perk on the table
    while perksfeed[out][typus]=="":
        out=random.randint(1,len(perksfeed)-3) #re-pick when we rolled an empty cell

    p_pattern=re.compile("(\w*\,?\s?\-?\/?\'?)+\.")
    p_match=p_pattern.search(perksfeed[out][typus])

    #dealing with banned perks
    bannedperks=[] #no perks are banned currently
    while p_match.group()[:-1].casefold().replace(" ","") in bannedperks:
        print(f"banned perk rolled: {p_match.group()[:-1]}")
        out=random.randint(1,len(perksfeed)-3)
        while perksfeed[out][typus]=="":
            out=random.randint(1,len(perksfeed)-3)
        p_pattern=re.compile("(\w*\,?\s?\-?\/?\'?)+\.")
        p_match=p_pattern.search(perksfeed[out][typus])
    #print(perksfeed[out][typus])
    embed = discord.Embed(title=p_match.group()[:-1],description=perksfeed[out][typus][p_match.end():],colour=typus_colour[typus])
    embed.set_footer(text=f"{typus_name[typus]}")
    try: #sadly there are some perks that are too long for the embed field.
        await ctx.send(embed=embed)
    except discord.HTTPException:
        await ctx.send(perksfeed[out][typus])


@bot.command(description="Roll augments. *>aug tinker*, or look up augs with *>aug tinker world*. You can see the short interpretation of the tarot card with *>aug world*",aliases=["aug"])
async def augment(ctx, classification=None, card=None):
    global augfeed
    if classification is None:
        await ctx.send("Need to know the classification. Blaster, Breaker, etc.")
        return
    augcolour=discord.Colour(0xBF9000)
    classifications=["blaster","breaker","brute","changer","master","mover","shaker","stranger","striker","tinker","thinker","trump"]
    cards=["fool","magician","priestess","empress","emperor","hierophant","lovers","chariot","strength","hermit","wheel","justice","hanged","death","temperance","devil","tower","star","moon","sun","judgement","world"]
    if classification in cards:
        await ctx.send(augfeed[cards.index(classification)+1][1])
        return
    augindex=classifications.index(classification.casefold())+2
    if card is None:
        out=random.randint(1,len(augfeed)-1)
        if augfeed[out][augindex]!="":
            embed = discord.Embed(title=f"{classification.title()} Augment",description=augfeed[out][augindex],colour=augcolour)
            embed.set_image(url=f"https://www.hivewiki.de/kingfisher/cards/{out-1}_{cards[out-1]}.png")
            await ctx.send(embed=embed)
            #await ctx.send(augfeed[out][augindex])
        else:
            embed = discord.Embed(title=f"{classification.title()} Augment - General",description=f"**{augfeed[out][0].title()}**: {augfeed[out][1]}",colour=augcolour) 
            embed.set_image(url=f"https://www.hivewiki.de/kingfisher/cards/{out-1}_{cards[out-1]}.png")
            await ctx.send(embed=embed)
            #await ctx.send(f"**{augfeed[out][0].title()}**: {augfeed[out][1]}")
    else:
        augs=[i[augindex] for i in augfeed]
        p_pattern=re.compile("\w*\.")
        for i in range(0,len(augs)):
            p_match=p_pattern.search(augs[i])
            if p_match:
                if p_match.group()[:-1].casefold()==card.casefold():
                    embed=discord.Embed(title=f"{classification.title()} Augment",description=augs[i],colour=augcolour)
                    embed.set_image(url=f"https://www.hivewiki.de/kingfisher/cards/{i-1}_{cards[i-1]}.png")
                    await ctx.send(embed=embed)
                    return
                    #await ctx.send(augs[i])
        await ctx.send(f"No {card.title()} augment defined.")


@bot.command(description="Roll on the pact augment table. Upright or Reverse.",aliases=["pluck"])
async def pactluck(ctx, judgement=None):
    global pactfeed
    #print(pactfeed)
    if judgement is None:
        await ctx.send("Need to know the judgement. Upright or reverse (good or bad)?")
        return
    augcolour=discord.Colour(0xBF9000)
    #cards=["Fool","Magician","Priestess","Empress","Emperor","Hierophant","Lovers","Chariot","Justice","Hermit","Wheel of Fortune","Strength","Hanged Man","Death","Temperance","Devil","Tower","Star","Moon","Sun","Judgement","World"]
    if judgement=="upright" or judgement=="u":
        augindex=1
    elif judgement=="reverse" or judgement=="r":
        augindex=2
    else:
        await ctx.send("Need to know the judgement. Upright or reverse (good or bad)?")
        return
    out=random.randint(1,len(pactfeed)-1)
    if pactfeed[out][augindex]!="":
            embed = discord.Embed(title=f"{pactfeed[out][0]} Augment",description=pactfeed[out][augindex],colour=augcolour)
            await ctx.send(embed=embed)


@bot.command(description="Trigger warning.")
async def trigger(ctx, id=None):
    global triggerfeed
    if id is None:
        out=random.randint(0,len(triggerfeed))
        while triggerfeed[out][0]=="":
            out=random.randint(0,len(triggerfeed))
        await ctx.send(f"Trigger #{out+1}: {triggerfeed[out][0]}")
    else:
        id=int(id)
        await ctx.send(f"Trigger #{id} by {triggerfeed[id-1][1]}: {triggerfeed[id-1][0]}")


@bot.command(description="Posts the google sheet document we use for our battle maps.", name="map", aliases=["maps"])
async def _map(ctx):
    playmap_gh="https://docs.google.com/spreadsheets/d/1lPJuANN3ZX2PPSHWHGlPVUkQqexP7YUtkBvLm1YlBPo/edit#gid=0"
    await ctx.send(playmap_gh)


@bot.command(description="Use this command to claim squares on the map. Faction name needs to be spelled right. Use >claim to see the current map. Use >claim factions to see available factions")
async def claim(ctx,faction=None,square = None):
    try:
        square = int(square)
    except (TypeError, ValueError):
        if square==None:
            pass
        else:
            pass

    guild=await sid(ctx.message.guild.id)
    authorized_channels=[358409511838547979,435874236297379861,478240151987027978,691405676920176751,721206828297617498]
    authorized_guilds = []
    if (ctx.message.channel.id not in authorized_channels and ctx.guild.id not in authorized_guilds):
        auth_channel=False
        for i in ctx.guild.channels:
            if i.id in authorized_channels:
                auth_channel=i.id
        if auth_channel:
            await ctx.send(f"Can only claim in <#{auth_channel}>!")
        else:
            await ctx.send("This server is not configured to utilize the claim system.")
        return

    cacher=random.randint(1, 100000000000)
    if faction=="factions":
        await ctx.send(", ".join(list(rp_factions[guild].keys())))
        return
    elif faction is None and square is None:
        await ctx.send(f"https://www.hivewiki.de/kingfisher/map_{guild}/map.png?nocaching={cacher}")
        return
    elif faction is not None and square is None:
        await ctx.send("Correct format: >claim Faction Square")
    #try:
    if type(square)==int:
        await mapUpdate(faction.casefold(),square,guild)
    else:
        await mapUpdateDict(faction.casefold(),square,guild)
    # # # # except (KeyError,IndexError):
    # # # #     await ctx.message.add_reaction("❌")
    # # # #     return
    await ctx.send(f"Map updated. https://www.hivewiki.de/kingfisher/map_{guild}/map.png?nocaching={cacher}")


@bot.command(description="Bullying.",hidden=True)
async def worm(ctx,*args):
    await ctx.send("Take that, you 🐛")


@bot.command(description="Repeats famous catchphrases.")
async def lysa(ctx):
    sweat_emoji = discord.utils.get(bot.emojis, name='sweats')
    phraselist = ["oof", "Uh", "Wew", "Weary", "sweats", "Rip", "nice", "Unfortunate", sweat_emoji, "listen\nit's fine", "paps"]
    await ctx.send(random.choice(phraselist))


#await ctx.message.add_reaction("❌")
#await ctx.message.add_reaction("✅")

@bot.group(description=""" Make a copyable link of your message. Using *link* simply gives you a link.
                            Sub-commands are Make, Add, Remove, Show, Owners. You need to first *make* a Bookmark, which is essentially a folder you will
                            put links into via the *add* command. The add command will either create a link to your adding message, or it takes custom URLs.
                            You can create multi-user bookmarks, too! Add your friends to collaborate onbookmarks via *owners*.""", aliases=["bm"])
async def bookmark(ctx,):
    if ctx.invoked_subcommand is None:
        await ctx.send("You need to use a subcommand like >bm show, or use >help bm.")


@bookmark.command(description="Gives the link of your selfsame message.",)
async def link(ctx,title):
    await ctx.send(ctx.message.jump_url)


@bookmark.command(description="Create a Bookmark to add links to. Needs a Title to identify it with!",)
async def make(ctx,title):
    new_bm=[{"Title":title,"Owners":[ctx.author.id],"Content":[]},]
    with open(f"bm.yaml",mode="r+") as f:
        old_bm=yaml.load(f)
    for k in old_bm:
        if k["Title"]==title:
            await ctx.send(f"Title already taken!")
            return
    old_bm.extend(new_bm)
    with open(f"bm.yaml",mode="w+") as f:
        f.seek(0)
        yaml.dump(old_bm,f)
    await ctx.send(f"Successfully added {title} to bookmarks!")


@bookmark.command(description="""Add links to your bookmark. Make sure to include the title of the bookmark you want to add it to, as well as
                                a short comment identify this link. If no URL is given, the link defaults to your own message. You can also use any URL.
                                Make sure it is formatted properly, including the http:// header!""", aliases=["a"])
async def add(ctx,title,comment=None,url=None):
    if comment is None:
        await ctx.send("Comment is required!")
        return
    with open(f"bm.yaml",mode="r") as f:
        bm_feed=yaml.load(f)
    for k in bm_feed:
        for i,j in k.items():
            if i=="Title" and j==title:
                if ctx.author.id in k["Owners"]:
                    if url is None:
                        content={"Comment":comment,"URL":ctx.message.jump_url}
                    else:
                        content={"Comment":comment,"URL":url}
                    k["Content"].append(content)
                else:
                    await ctx.send("Not your Bookmark!")
                    return
    with open(f"bm.yaml",mode="w+") as f:
        f.seek(0)
        yaml.dump(bm_feed,f)
    await ctx.message.add_reaction("✅")


#TODO: fix this
@bookmark.command(description="""Remove links from your bookmark. Use this CAREFULLY!
                                If you have multiple entries with the same comment, you *should* specify exactly which one should get deleted by also
                                including the content.""",)
async def remove(ctx,title,comment,content=False):
    with open(f"bm.yaml",mode="r") as f:
        bm_feed=yaml.load(f)
    for k in bm_feed:
        if ctx.author.id in k["Owners"]:
            if k["Title"]==title:
                #k["Content"] is a (ordered set of) list containing the dict of the comment,url pairs
                for i in k["Content"]:
                    if i["Comment"]==comment:
                        if i["Content"]==content or content is False:
                            k["Content"].remove(i)
        else:
            await ctx.send("Not your Bookmark!")
    with open(f"bm.yaml",mode="w+") as f:
        f.seek(0)
        yaml.dump(bm_feed,f)
    await ctx.message.add_reaction("✅")


@bookmark.command(description="Display a bookmark.", aliases=["s"])
async def show(ctx,title):
    bm_icon="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/google/146/bookmark_1f516.png"
    with open(f"bm.yaml",mode="r") as f:
        bm_feed=yaml.load(f)
        #print(bm_feed)
    for k in bm_feed:
        for i,j in k.items():
            if i=="Title" and j==title:
                embed = discord.Embed(title=title, colour=discord.Colour(0x6766b))

                ownerstring=""
                for o in k["Owners"]:
                    try:
                        usr=await bot.fetch_user(o)
                        ownerstring=f"{ownerstring}, {usr.name}"
                    except:
                        ownerstring=f"{ownerstring}, Unknown"

                embed.set_footer(text=f"Owners: {ownerstring[1:]}", icon_url=bm_icon)
                #embed.set_footer(text=f"Owners: {', '.join(map(str,k['Owners']))}", icon_url=bm_icon)

                #for each content, add content
                i=1
                for c in k["Content"]:
                    embed.add_field(name=str(i),value=f"[{c['Comment']}]({c['URL']})")
                    i=i+1
                await ctx.send(embed=embed)
                return


@bookmark.command(description="""Add an owner to your bookmark. Needs their user ID, or their account name.
                                Can also remove them by using the remove keyword.""",)
async def owners(ctx,title,new_owner,remove="add"):
    try:
        new_owner_id=int(new_owner)
    except ValueError:
        try:
            new_owner_id=ctx.guild.get_member_named(new_owner).id
        except:
            await ctx.send("I don't know who you're trying to add. Try using their account name or ID.")
            return
    with open(f"bm.yaml",mode="r") as f:
        bm_feed=yaml.load(f)
    for k in bm_feed:
        for i,j in k.items():
            if i=="Title" and j==title:
                if ctx.author.id in k["Owners"]:
                    if remove=="remove":
                        k["Owners"].remove(new_owner_id)
                    else:
                        k["Owners"].append(new_owner_id)
                #else:
                    #await ctx.send("Not your Bookmark!")
    with open(f"bm.yaml",mode="w+") as f:
        f.seek(0)
        yaml.dump(bm_feed,f)
    await ctx.message.add_reaction("✅")


@bot.command(description="Forgot a simple URL? I got you.")
async def wiki(ctx,*args):
    await ctx.send("https://www.hivewiki.de/start")


@bot.command(description="Link a cape's hivewiki article.")
async def cape(ctx,*cape):
    cape=str(cape).replace(" ", "_")
    cape="".join(cape)
    cape=re.sub('\'|\,|\(|\)', '',cape)
    loc=ctx.message.guild.id
    guild=await sid(loc)
    if loc=="undefined":
        await ctx.message.add_reaction("❌")
    domain=f"https://www.hivewiki.de/{guild}/cape/{cape}"
    #async with aiohttp.get(domain, allow_redirects=False) as r:
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(domain) as response:
            response_text = await response.text()
            #print(r.text)
            status="Status"
            if status in response_text:
                await ctx.send(domain)
            else:
                await ctx.send("No such article. Create it at "+domain)
        session.close


@bot.command(description="Fetch a user's avatar. Follow your Jadmin dreams.\nFormatting is tricky, check that you're matching case. Copy the discriminator too.")
async def avatar(ctx, user):
    if user is None:
        await ctx.send(">avatar [name]")
    user=ctx.message.guild.get_member_named(user)
    if user is None:
        await ctx.message.add_reaction("❌")
    await ctx.send(user.avatar_url)


@bot.command(description="No more %vial 5.",hidden=True)
async def stopspam(ctx, i:int):
    if ctx.message.author.id not in owner:
        return
    try:
        await ctx.message.channel.purge(limit=i)
    except discord.Forbidden:
        await ctx.send("Insufficient priviliges.")


@bot.command(description="Prevents a user from using any KF commands.",hidden=True)
async def mute(ctx,usr):
    if not ((ctx.message.author.id in owner) or ((ctx.message.author.id in gms) and await sid(ctx.message.guild.id)=="gh")):
        await ctx.send("This would be a fun game. But you already lost.")
        return
    

    
    user= await discord.ext.commands.UserConverter().convert(ctx,usr)
    usr_id=user.id
    if usr_id in owner:
        if ctx.message.author.id in owner:
            return
        await ctx.send("Oh, you're approaching me?")
        await ctx.invoke(mute,usr=str(ctx.message.author.id))
        return

    global muted_usr
    muted_usr.append(usr_id)
    await ctx.send("I told them. Warned them.")
    print(f"{usr} has been muted.")


@bot.command(description="un-Fuck you.",hidden=True)
async def unmute(ctx,usr):
    if not ((ctx.message.author.id in owner) or ((ctx.message.author.id in gms) and await sid(ctx.message.guild.id)=="gh")):
        await ctx.send("No Release.")
        return
    global muted_usr
    user= await discord.ext.commands.UserConverter().convert(ctx,usr)
    usr_id=user.id
    muted_usr.remove(usr_id)
    await ctx.send("Finally free.")
    print(f"{usr} has been unmuted.")


@bot.command(description="Wer ist der Bürgermeister von Wesel?",hidden=True)
async def echo(ctx,*echo):
    if ctx.message.author.id not in owner:
        await ctx.send("Esel, Esel!")
        return
    print(" ".join(echo))
    print(ctx.message.channel)
    print(ctx.message.channel.id)
    await ctx.send(" ".join(echo))


@bot.command(description="Math.", aliases=["m"],hidden=True)
async def calc(ctx,formula):
    if ctx.message.author.id not in owner:
        await ctx.send("Math is banned.")
        return
    await ctx.send(f"`{formula}`= {eval(formula)}") #using eval is quite unsafe


#rp_factions
@bot.group(description="Add factions to the list of factions available to mapClaim",aliases=[])
async def faction(ctx):
    global rp_factions
    if ctx.message.author.id not in owner:
        await ctx.send(f"Bzzt! Not authorized.")
        return
    if ctx.invoked_subcommand is None:
        try:
            with open(f"rp_factions.yaml",mode="r+") as f:
                rp_factions=yaml.load(f)
                rp_factions=dict(rp_factions) #YAML can't handle tuples, so we have convert back
                for guilds in rp_factions:
                    rp_factions[guilds]=dict(rp_factions[guilds]) #we're also getting rid of all these fucki-annoying ordereddicts
                for guilds in rp_factions.keys():
                    for k in rp_factions[guilds].keys():
                        rp_factions[guilds][k]=tuple(rp_factions[guilds][k])
                print(rp_factions)
        except:
            print("Error when loading factions file.")
        await ctx.send(f"Faction list refreshed.")


@faction.command(description="Prints the rp_factions variable to the console.",aliases=[],hidden=True)
async def check(ctx):
    print(rp_factions)


@faction.command(description="Colour should be in discord (hex) format", aliases=[],hidden=True)
async def add(ctx,name,color):
    guild=await sid(ctx.message.guild.id)
    if ctx.message.author.id not in owner:
        await ctx.send(f"Bzzt! Not authorized.")
        return
    global rp_factions
    for guilds in rp_factions:
        for k in guilds:
            if k==name:
                await ctx.send(f"Name already taken!")
                return
    try:
        rp_factions[guild][name.casefold()]=ImageColor.getrgb(color)
    except Exception as e:
        await ctx.send(f"Error when converting colour.")
        print(e)
        return

    print(rp_factions[guild])
    with open(f"rp_factions.yaml",mode="w+") as f:
        f.seek(0)
        yaml.dump(rp_factions,f)
    await ctx.send(f"Successfully added **{name}** to faction list.")


@faction.command(description="Removes a faction", aliases=[],hidden=True)
async def remove(ctx,name):
    guild=await sid(ctx.message.guild.id)
    if ctx.message.author.id not in owner:
        await ctx.send(f"Bzzt! Not authorized.")
        return
    global rp_factions
    for k in rp_factions[guild]:
        if k==name:
            del rp_factions[guild][k]
            await ctx.send(f"Removed {k}.")
    print(rp_factions[guild])
    with open(f"rp_factions.yaml",mode="w+") as f:
        f.seek(0)
        yaml.dump(rp_factions,f)


@bot.command(description="Manually increment accounts.")
async def dh_increment(ctx,):
    loc=ctx.message.guild.id

    if not (ctx.author.id==242389360320839681 or ctx.author.id==138340069311381505):
        await ctx.send("Not authorized.")
        return
    MF_channel = bot.get_channel(691369881039536178) #MF imperial-bank-of-dusthaven
    #test_channel=bot.get_channel(435874236297379861) #nest test-dev
    #691221976311660595

    if os.path.isfile(f"cash{loc}.txt"):
        print("Cash file exists")
        with open(f"cash{loc}.txt",mode="r+") as g:
            accounts = json.load(g)
            g.seek(0)
            g.truncate()
            for i in accounts:
                i[1]=i[1]+(i[2])
            json.dump(accounts,g)
        await MF_channel.send(f"Income computed.")
    else:
        await ctx.send(f"No accounts on file.")


@bot.command(description="Manually increment accounts.")
async def ssn_increment(ctx,):
    loc=ctx.message.guild.id

    if not (ctx.author.id==242389360320839681 or ctx.author.id==138340069311381505):
        await ctx.send("Not authorized.")
        return
    MF_channel = bot.get_channel(721141339567161415) #battle-ooc for now

    if os.path.isfile(f"cash{loc}.txt"):
        print("Cash file exists")
        with open(f"cash{loc}.txt",mode="r+") as g:
            accounts = json.load(g)
            g.seek(0)
            g.truncate()
            for i in accounts:
                i[1]=i[1]+(i[2])
            json.dump(accounts,g)
        await MF_channel.send(f"Income computed.")
    else:
        await ctx.send(f"No accounts on file.")

@bot.command(name="time",description="Stuck in bubble hell? Wonder when giao will be back?")
async def _time(ctx,):
    utc=datetime.datetime.now(tz=pytz.utc)
    hyper = pytz.timezone('Europe/Berlin')
    zan= pytz.timezone('Europe/London')
    giao= pytz.timezone('Asia/Manila')
    kiwis = pytz.timezone('Pacific/Auckland')
    aussies = pytz.timezone('Australia/Canberra')
    pacific=pytz.timezone("America/Los_Angeles")
    mountain=pytz.timezone('America/Denver')
    central=pytz.timezone('America/Chicago')
    eastern=pytz.timezone('America/New_York')
    jakarta=pytz.timezone("Asia/Jakarta")

    hyper_dt=utc.astimezone(hyper)
    zan_dt=utc.astimezone(zan)
    giao_dt=utc.astimezone(giao)
    kiwis_dt=utc.astimezone(kiwis)
    pacific_dt=utc.astimezone(pacific)
    mountain_dt=utc.astimezone(mountain)
    central_dt=utc.astimezone(central)
    eastern_dt=utc.astimezone(eastern)
    aussies_dt=utc.astimezone(aussies)
    jakarta_dt=utc.astimezone(jakarta)

    fmt = '%H:%M:%S'
    utcfmt = '%H:%M:%S %a %d %b'
    fmt_offset = "(%Z %z)"

    embed = discord.Embed(title="Kingfisher World Clock", colour=discord.Colour(0xffffff))
    #embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Clock_simple.svg/1024px-Clock_simple.svg.png")
    embed.set_footer(text=f"Sponsored by Insomniacs Anonymous",icon_url=ctx.message.author.avatar_url)
    embed.add_field(name=f"UTC", value=utc.strftime(utcfmt),inline=False)
    embed.add_field(name=f"Auckland {kiwis_dt.strftime(fmt_offset)}", value=kiwis_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Manila {giao_dt.strftime(fmt_offset)}", value=giao_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Jakarta {jakarta_dt.strftime(fmt_offset)}", value=jakarta_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Berlin {hyper_dt.strftime(fmt_offset)}", value=hyper_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"London {zan_dt.strftime(fmt_offset)}", value=zan_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"New York {eastern_dt.strftime(fmt_offset)}", value=eastern_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Chicago {central_dt.strftime(fmt_offset)}", value=central_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Denver {mountain_dt.strftime(fmt_offset)}", value=mountain_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Seattle {pacific_dt.strftime(fmt_offset)}", value=pacific_dt.strftime(fmt), inline=True)
    embed.add_field(name=f"Canberra {aussies_dt.strftime(fmt_offset)}", value=aussies_dt.strftime(fmt), inline=True)

    await ctx.send(embed=embed)


@bot.command(description="Let the fun begin.")
@commands.check(gm_only)
async def toggleFool(ctx):
    global fools
    if fools:
        fools=False
        await ctx.send("Disabled.")
    else:
        fools=True
        await ctx.send("Enabled.")


@bot.command(description="Saves a copy of the channel on the hivewiki server.")
@commands.check(gm_only)
async def archive(ctx,channel_id=None,cat_name=None):
    if channel_id is None:
        channel_id=ctx.channel.id
    chan=discord.utils.get(ctx.guild.text_channels,id=int(channel_id))
    await ctx.send(f"Collecting messages in {chan.name}....")
    
    if not os.path.exists(f"archives/{ctx.guild.name}/"):
        os.mkdir(f"archives/{ctx.guild.name}/")
    
    if cat_name is not None:
        if not os.path.exists(f"archives/{ctx.guild.name}/{cat_name}"):
            os.mkdir(f"archives/{ctx.guild.name}/{cat_name}/")
        if not os.path.exists(f"archives/{ctx.guild.name}/{cat_name}/{chan.name}/"):
            os.mkdir(f"archives/{ctx.guild.name}/{cat_name}/{chan.name}/")
        path = f"archives/{ctx.guild.name}/{cat_name}/{chan.name}/"
    elif cat_name is None:
        if not os.path.exists(f"archives/{ctx.guild.name}/{chan.name}/"):
            os.mkdir(f"archives/{ctx.guild.name}/{chan.name}/")
        path = f"archives/{ctx.guild.name}/{chan.name}/"
    
    messages = await chan.history(limit=None).flatten()
    messages.reverse()
    #print(len(messages))
    
    output = f"{chan.name}\nThis archive was created at {datetime.datetime.now()} by {ctx.author.name}\n"
    output += f"\nPINNED MESSAGES START\n"
    for i in await chan.pins():
        output += f"[{i.created_at}] {i.author}: {i.content}\n"
    output += "PINNED MESSAGES END\n\n"
    for i in messages:
        output += f"[{i.created_at}] {i.author}: {i.content}\n"
        if i.embeds:
            for x in i.embeds:
                mbd=x.to_dict()
                #print(mbd)
                if "title" in mbd:
                    if ('footer' in mbd) and ('description' in mbd):
                        output += f"EMBED {mbd['footer']['text']} **{mbd['title']}** {mbd['description']}\n"
                else:
                    if "fields" in mbd:
                        for y in mbd["fields"]:
                            #print(y)
                            output += f"EMBED "
                            output += f"{y['name']} {y['value']}\n"
                    else:
                        if ('description' in mbd):
                            output += f"EMBED {mbd['description']}\n"
        if i.attachments:
            #print(i.attachments)
            async with aiohttp.ClientSession() as session:
                for j in i.attachments:
                    url = j.url
                    output += f"UPLOADED FILE {j.id}_{j.filename}\n"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(f'{path}/{j.id}_{j.filename}', mode='wb')
                            await f.write(await resp.read())
                            await f.close()
    with open(f'{path}/log.txt',mode="w",encoding="utf-8") as f:
        print(output,file=f)
    await ctx.send(f"Archival completed.")


@bot.command(description="Saves a copy of all channels in the category on the hivewiki server.")
@commands.check(gm_only)
async def cat_archive(ctx,cat_id=None):
    if cat_id is None:
        cat_id=ctx.channel.category_id
    else:
        cat_id=int(cat_id)
    category = discord.utils.get(ctx.guild.categories,id=cat_id)
    await ctx.send(f"Archiving the {category.name} category. {len(category.text_channels)} channels. Please be patient.")
    for i in category.text_channels:
        #print(i.name)
        await ctx.invoke(archive,channel_id=i.id,cat_name=category.name)
    await ctx.send(f"Category archival completed.")
    await ctx.invoke(order66,cat_id=cat_id)


#TODO: Better QoL, list options, better configuration
@bot.command(description="Gives (or removes) self-serve roles.")
async def toggle(ctx, req_role="Active"):
    bye_emoji = discord.utils.get(bot.emojis, name='byedog')
    user = ctx.message.author
    loc=await sid(ctx.message.guild.id)
    opproles=["RED","BLUE","DEEP","GOLD"]
    if req_role.casefold()=="Active".casefold():
        role = discord.utils.get(user.guild.roles, name="Active")
        if role is None:
            await ctx.send("No Active role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            await user.add_roles(role)
            await ctx.send("Remember, spamming 1v1s is punishable by death.")

    elif req_role.casefold()=="Smithy".casefold():
        role = discord.utils.get(user.guild.roles, name="Smithy ⚔️")
        if role is None:
            await ctx.send("No Smithy role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            await user.add_roles(role)
            await ctx.send("Welcome to the Smithy.")

    elif req_role.casefold()=="Roleplay".casefold():
        role = discord.utils.get(user.guild.roles, name="Roleplay 📝")
        if role is None:
            await ctx.send("No Roleplay role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            await user.add_roles(role)
            await ctx.send("You're the Best! This coupon may be redeemed for 1 (one) hug.")

    elif (req_role.casefold()=="news".casefold()) and (loc=="test"):
        role = discord.utils.get(user.guild.roles, name="news")
        if role is None:
            await ctx.send("No news role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send("Who reads this stuff anyways?")
        else:
            await user.add_roles(role)
            await ctx.send("All caught up.")

    elif req_role.casefold()=="RED".casefold():
        role = discord.utils.get(user.guild.roles, name="RED")

        if role is None:
            await ctx.send("No RED role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            for opprole in opproles:
                opprole= discord.utils.get(user.guild.roles, name=opprole)
                if opprole in user.roles:
                    await ctx.send("Oy! No peeking, you cheeky fuck!")
                    return
            await user.add_roles(role)
            await ctx.message.add_reaction("\U00002666")
            await ctx.send("Go Team Red Star!")

    elif req_role.casefold()=="BLUE".casefold():
        role = discord.utils.get(user.guild.roles, name="BLUE")

        if role is None:
            await ctx.send("No BLUE role defined.")

        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            for opprole in opproles:
                opprole= discord.utils.get(user.guild.roles, name=opprole)
                if opprole in user.roles:
                    await ctx.send("Oy! No peeking, you cheeky fuck!")
                    return
            await user.add_roles(role)
            await ctx.message.add_reaction("\U0001f6e1")
            await ctx.send("Go Team Blue Shield!")

    elif req_role.casefold()=="DEEP".casefold():
        role = discord.utils.get(user.guild.roles, name="DEEP")

        if role is None:
            await ctx.send("No DEEP role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            for opprole in opproles:
                opprole= discord.utils.get(user.guild.roles, name=opprole)
                if opprole in user.roles:
                    await ctx.send("Oy! No peeking, you cheeky fuck!")
                    return
            await user.add_roles(role)
            await ctx.message.add_reaction("🌃")
            await ctx.send("To boldly go where no man has gone before.")

    elif req_role.casefold()=="GOLD".casefold():
        role = discord.utils.get(user.guild.roles, name="GOLD")
        if role is None:
            await ctx.send("No GOLD role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            for opprole in opproles:
                opprole= discord.utils.get(user.guild.roles, name=opprole)
                if opprole in user.roles:
                    await ctx.send("Oy! No peeking, you cheeky fuck!")
                    return
            await user.add_roles(role)
            await ctx.message.add_reaction("🦅")
            await ctx.send("This is Gold Leader. Starting attack run.")

    elif req_role.casefold()=="interlude".casefold():
        role = discord.utils.get(user.guild.roles, name="Interlude")
        if role is None:
            await ctx.send("No Interlude role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            await user.add_roles(role)
            await ctx.send("You can now post in #interludes. Role will be automatically revoked after an hour.")
            await asyncio.sleep(60*60*1)
            await user.remove_roles(role)

    elif (req_role.casefold()=="news".casefold()) and (loc=="gh"):
        role = discord.utils.get(user.guild.roles, name="News")
        #print(user.guild.roles)
        if role is None:
            await ctx.send("No News role defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            await user.add_roles(role)
            await ctx.send("You can now post in #news-board. Role will be automatically revoked after 30 minutes.")
            await asyncio.sleep(60*30)
            await user.remove_roles(role)

    elif req_role.casefold() in ["he/him".casefold(),"she/her".casefold(),"they/them".casefold()]:
        role = discord.utils.get(user.guild.roles, name=req_role.casefold())
        if role is None:
            await ctx.send(f"No {req_role.casefold()} roles defined.")
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.message.add_reaction(bye_emoji)
        else:
            await user.add_roles(role)
            await ctx.message.add_reaction("✅")


#Rolls wounds off of the Weaverdice wound table.
@bot.command(aliases=["bash","pierce","cut","freeze","shock","rend","burn", "poison"],
             description="You like hurting people, huh? Use this to roll your wound effect. >Damage_Type Severity [Aim] [Number]"
             " Use >wound 'Hit Vitals' to find specific wounds.")
async def wound(ctx, severity="Moderate", aim="Any", repeats=1,**typus):
    loc=await sid(ctx.message.guild.id)
    #0 is wd20, 1 is skitterdice, 2 is original wd
    if loc=="gh":
        f=0
    elif loc=="detroit":
        f=1 #detroit uses skitterdice
    elif loc=="la" or loc=="gaming_inc" or loc=="autumn lane" or loc=="portland" or loc=="Benelux" or loc=="wd6":
        f=2
    elif loc=="test":
        f=0
    else:
        f=0 #default is wd20

    if aim.isdigit():
        repeats=int(aim)
        aim="Any"

    if severity.isdigit():
        repeats=int(severity)
        severity="Moderate"

    if repeats>8:
        if ctx.message.author.id not in owner:
            await ctx.send("/metalgearchittychittybangbang")
            return

    if ctx.invoked_with.casefold() == "Bash".casefold():
        typ="Bash"
    elif ctx.invoked_with.casefold() == "Pierce".casefold():
        typ="Pierce"
    elif ctx.invoked_with.casefold() == "Cut".casefold():
        typ="Cut"
    elif ctx.invoked_with.casefold() == "Freeze".casefold():
        typ="Freeze"
    elif ctx.invoked_with.casefold() == "Shock".casefold():
        typ="Shock"
    elif ctx.invoked_with.casefold() == "Rend".casefold():
        typ="Rend"
    elif ctx.invoked_with.casefold() == "Burn".casefold():
        typ="Burn"

    elif ctx.invoked_with.casefold() == "Poison".casefold():
        typ="Poison"

    if "typus" in typus: #kwarg
        typ=typus['typus']
    elif (ctx.invoked_with.casefold() == "Wound".casefold()) or (ctx.invoked_with.casefold() == "tag".casefold()):
        for i in feed[f]:
            if i[3].casefold()==severity.casefold(): #severity is actually the wound we're looking for here
                await ctx.send(f"**{i[3]}**: {i[4]} *({i[0]}, {i[1]}, {i[2]})*")
                return True
        return
    elif "typ" not in locals():
        await ctx.message.add_reaction("❌")
        return
    #shorthand code
    repeatlist=[]
    severitylist=[]
    shorthand=re.compile("\d[cml]")
    sm=shorthand.findall(severity)
    #what if nothing is found?

    if len(sm)!=0:
        for i in range(0,len(sm)):
            repeatlist.append(int(sm[i][0]))
            severitylist.append(sm[i][1])
    else:
        repeatlist.append(repeats)
        severitylist.append(severity)
        sm=["def"]

    for j in range(0,len(sm)):
        severity= await severity_short(severitylist[j].casefold())
        exclusive=False
        limbaim=False
        if "x" in aim:
            exclusive=True
            aimt=aim[1:]
        else:
            aimt=aim
        if aimt.upper() not in ["ANY","HEAD","TORSO","ARM","LEGS"]:
            if aimt.casefold() not in ["h","t","a","l"]:
                if aimt.casefold() == "limbs":
                    limbaim=True
                else:
                    await ctx.message.add_reaction("❌")
                    return
            elif aimt.casefold()=="h":
                aimt="Head"
            elif aimt.casefold()=="t":
                aimt="Torso"
            elif aimt.casefold()=="a":
                aimt="Arm"
            elif aimt.casefold()=="l":
                aimt="Legs"
        typlist=[]
        for i in feed[f]:
            if i[0].casefold()==typ.casefold():
                if i[1].casefold()==severity.casefold():
                    if exclusive is True:
                        if (i[2].casefold()==aimt.casefold()):
                            typlist.append(i)
                    elif limbaim is True:
                        if exclusive is True:
                            if i[2].casefold() in ["arm".casefold(),"legs".casefold()]:
                                typlist.append(i)
                        else:
                            if i[2].casefold() in ["arm".casefold(),"legs".casefold(),"any".casefold()]:
                                typlist.append(i)
                    elif (i[2].casefold()==aimt.casefold()) or (aimt.casefold()=="Any".casefold()) or (i[2]=="Any"):
                        typlist.append(i)
        embed=[]
        if "title" in typus:
            embed = discord.Embed(title=typus["title"],colour=discord.Colour(typ_colours[typ]))
        else:
            embed = discord.Embed(colour=discord.Colour(typ_colours[typ]))
        if "tag" in typus:
            embed.set_footer(text=f"Rolled for {ctx.message.author.name} | {typus['tag']}",icon_url=ctx.message.author.avatar_url)
        else:
            embed.set_footer(text=f"Rolled for {ctx.message.author.name} | {severity} {aim.casefold()} {repeatlist[j]}",icon_url=ctx.message.author.avatar_url)
        damages=[]
        for _ in range(0,repeatlist[j]):
            luck=random.randint(0,len(typlist)-1)
            damages.append(typlist[luck])
            embed.add_field(name=f"**{typlist[luck][3]}**", value=f"{typlist[luck][4]}\n*Location: {typlist[luck][2]}, Stage: {typlist[luck][1]}*", inline=False)
        await ctx.send(embed=embed)
        for i in damages:
            if i[3] in specWounds:
                await specialWounds(bot,ctx,i[3],f,aimt)
            #embed.add_field(name="Severity", value=severity, inline=True)
            #embed.add_field(name="Aim", value=aim, inline=True)
    return True


#Resolves stances
@bot.command(aliases=["s"],
             description="")
async def stance(ctx, choice):
    chan=ctx.channel.id

    #delete the message!

    
    choice=choice.upper()
    stance_bonuses = {"ST":{"atk":"Inflict the Stunned status effect","def":"Heal one lesser wound damage (not effect)"},
                    "AO":{"atk":"+1 lesser effect","def":"+1 defense crit range"},
                    "OF":{"atk":"Push your opponent one square (and/or follow them). Cannot wallbang","def":"Halve your opponent's movement on their next turn."},
                    "CS":{"atk":{"ST":"Disable limb for a round","AO":"Confuse opponent for a round","OF":"Stagger opponent for a round","CS":"undefined"},
                            "def":{"ST":"Disable limb for a round","AO":"Confuse opponent for a round","OF":"Stagger opponent for a round","CS":"undefined"}}}

    if choice[0:2]=="||" and choice[-2:]=="||":
        choice=choice[2:-2]

    
    if choice not in ["ST","AO","OF","CS"]:
        await ctx.send("Sorry, but I don't recognize that stance. Please use the shorthands inside spoilers (e.g. ||ao||)!")
        return
    

    if chan in bot.stance_array.keys():
        bot.stance_array[chan].append({"player":ctx.author.display_name,"choice":choice})
    else:
        bot.stance_array[chan]=[{"player":ctx.author.display_name,"choice":choice}]

    resolve=False
    if len(bot.stance_array[chan])==2:
        resolve = True   
    if resolve==True:
        for i in range(0,len(bot.stance_array[chan])):
            if i != 0:
                attacker_choice=bot.stance_array[chan][0]['choice']
                defender_choice=bot.stance_array[chan][i]['choice']
                await ctx.send(f"Attacker {bot.stance_array[chan][0]['player']} picked {attacker_choice} \n"
                               f"Defender {bot.stance_array[chan][i]['player']} picked {defender_choice}")
                if attacker_choice=="ST":
                    if defender_choice=="ST":
                        payoff="d6 winner gets 3"
                    elif defender_choice=="AO":
                        payoff="Attacker gains 1 Edge"
                    elif defender_choice=="OF":
                        payoff="Defender gets 2 Edge"
                    elif defender_choice=="CS":
                        payoff="Attacker gets 1 Edge"
                if attacker_choice=="AO":
                    if defender_choice=="ST":
                        payoff="Defender gets 1 Edge"
                    elif defender_choice=="AO":
                        payoff="d6 winner gets 3"
                    elif defender_choice=="OF":
                        payoff="Attacker gets 3 Edge"
                    elif defender_choice=="CS":
                        payoff="Defender gets 2 Edge"
                if attacker_choice=="OF":
                    if defender_choice=="ST":
                        payoff="Attacker gets 2 Edge"
                    elif defender_choice=="AO":
                        payoff="Defender gets 3 Edge"
                    elif defender_choice=="OF":
                        payoff="d6 winner gets 3"
                    elif defender_choice=="CS":
                        payoff="Attacker gets 1 Edge"
                if attacker_choice=="CS":
                    if defender_choice=="ST":
                        payoff="Defender gets 1 Edge"
                    elif defender_choice=="AO":
                        payoff="Attacker gains 2 Edge"
                    elif defender_choice=="OF":
                        payoff="Defender gets 1 Edge"
                    elif defender_choice=="CS":
                        payoff="d6 winner gets 3"
                await ctx.send(f"**{payoff}**")
                if attacker_choice=="CS" or defender_choice=="CS":
                    if attacker_choice=="CS" and defender_choice=="CS":
                        await ctx.send(f"Attacker may gain {stance_bonuses[attacker_choice]['atk'][defender_choice]} \n"
                                f"Defender may gain {stance_bonuses[defender_choice]['def'][attacker_choice]}")
                    elif attacker_choice=="CS" and defender_choice!="CS":
                        await ctx.send(f"Attacker may gain {stance_bonuses[attacker_choice]['atk'][defender_choice]} \n"
                                f"Defender may gain {stance_bonuses[defender_choice]['def']}")
                    elif attacker_choice!="CS" and defender_choice=="CS":
                        await ctx.send(f"Attacker may gain {stance_bonuses[attacker_choice]['atk']} \n"
                                f"Defender may gain {stance_bonuses[defender_choice]['def'][attacker_choice]}")
                else:
                    await ctx.send(f"Attacker may gain {stance_bonuses[attacker_choice]['atk']} \n"
                                f"Defender may gain {stance_bonuses[defender_choice]['def']}")
    #print(bot.stance_array)
    
    #await ctx.send(result)


@bot.group(description="Save macros for use with the >roll function. Usage is >macro save $title 3d20+4 3d6x4 #comment - then use >roll $title.\
 Nb that each word in the comment has to be preceded by the # sign!",alias="m")
async def macro(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Available commands: save, delete, update, show.')


@macro.command()
async def save(ctx,title,*formulas):
    global macros
    if not title[0]=="$":
        await ctx.send("First letter of your title HAS to be the $ sign!")
        return
    user=ctx.message.author.id
    user=str(user)
    if user not in macros:
        macros[user]={}
    macros[user][title]=[]
    for i in formulas:
        if i[0]=="#":
            try:
                r_formula=macros[user][title].pop()
            except IndexError:
                await ctx.send("Need a roll code before any comments!")
                return
            macros[user][title].append(r_formula+i)
        else:
            macros[user][title].append(i)
    with open(f"roll_macros.txt",mode="w+") as f:
        json.dump(macros,f)
    await ctx.send(f"{title} has been saved.")
    return


@macro.command()
async def delete(ctx,title):
    global macros
    user=ctx.message.author.id
    user=str(user)
    macros[user].pop(title)
    await ctx.send(f"{title} has been removed from your macros.")
    with open(f"roll_macros.txt",mode="w+") as f:
        json.dump(macros,f)
    return


@macro.command()
async def update(ctx,title,*formulas):
    global macros
    user=ctx.message.author.id
    user=str(user)
    macros[user].pop(title)
    macros[user][title]=[]
    for i in formulas:
        if i[0]=="#":
            try:
                r_formula=macros[user][title].pop()
            except IndexError:
                await ctx.send("Need a roll code before any comments!")
                return
            macros[user][title].append(r_formula+i)
        else:
            macros[user][title].append(i)
    with open(f"roll_macros.txt",mode="w+") as f:
        json.dump(macros,f)
    await ctx.send(f"{title} has been updated.")
    return


@macro.command()
async def show(ctx,title=None,user=None):
    user=ctx.message.author.id
    user=str(user)
    macro_list=[]
    for i in macros[user]:
        macro_list.append(f"Title: {i}, Formulas: {' '.join(macros[user][i])}\n")
    await ctx.send(f"Saved macros for {ctx.message.author.name} are:\n{''.join(macro_list)}")
    return


@bot.command(description="See >tag roll for help",aliases=["nr"])
async def newroll(ctx,formula="default",*comment):
    loc=ctx.message.guild.id
    base_modifier=0

    s_id = await sid(loc)

    if formula[0]=="$": #indicates a user macro
        user=str(ctx.message.author.id)
        if formula in macros[user]:
            for i in macros[user][formula]:
                if "#" in i:
                    form=i.split("#")
                    await ctx.invoke(roll,form[0]," ".join(form[1:]))
                else:
                    await ctx.invoke(roll,formula=i)
        return
    formula_in=formula

    if comment==():
        comment=""
    if formula[0]=="#": #this is a fully standard roll, with a comment attached
        comment2=(formula[1:],)
        if comment!="":
            comment=comment2+comment
        else:
            comment=comment2
        formula="default"

    if (s_id=="portland") and (formula=="default"):
        formula="1d6"
    elif formula=="default":
        formula="1d20,1d6+0"
    
    modifier=0
    print("formula: "+formula)
    
    bracketed=""
    if ("(" in formula) and (")" in formula):
        bracketed=[]
        b_pattern=re.compile(r"\([^)]*\)") #everything enclosed in ()
        b_match=b_pattern.finditer(formula)
        for i in b_match:
            #print(f"bracket_match: {i}")
            bracketed.append(formula[i.start()+1:i.end()-1])
        print("Bracketed "+str(bracketed))
    
    f_pattern=re.compile(r"(?P<node>(?P<prestack>[^(),dc]*\d*)(?P<dice>(?:D|C)*\d*)(?P<poststack>[^dD,()]*))",re.I)
    # We're trying to identify the strings for each dice node
    # a dice node being centered on a specific dice size, and then modified as needed
    # There's dice nodes and then the full stack
    # the stack applies to the full roll and is applied last
    #pre and post stack are not functionally different, just a quality of life thing
    #pre-stack can include how many dice are rolled (and taken highest of) but post cannot
    
    f_match=f_pattern.findall(formula)
    start=0
    groups=[]
    rest_collector=[]
    print(f"f_match {f_match}")
    for i in f_match:  ##   CONTINUE HERE - make sure stuff outside of node isnt lost!
        #print(f"f_match_i: {i}")
        if any(i):
            groups.append(i)
    print(f"groups: {groups}")

    rest=re.sub(f_pattern,"",formula)
    print("rest: "+rest)

    #dice=int(d_match.group()[1:])

    # if (s_id=="portland"):
    #     dice=6
    # else:
    #     dice=20 #TODO wd6
    # keep=True

    #stack variables are the ones that affect the entire formula, not just single nodes of it
    stack_modifier=0
    stack_repeats=1
    stack_keep=True
    stack_brief=False
    stack_explode=False
    stack_high_low="High"
    stack_crit=""
    
    stacks=len(groups)
    print(f"stacks: {stacks}")
    dice_s=[None]*stacks
    dice_i=[1]*stacks
    modifier=[0]*stacks
    repeats=[1]*stacks
    keep=[True]*stacks
    brief=[False]*stacks
    explode=[False]*stacks
    bracket=[False]*stacks
    high_low=["High"]*stacks
    results=[None]*stacks
    crit=[""]*stacks
    

    for node in range(0,stacks): #working through all the parts of the formula

        print(f"group-node: {groups[node]}")
        t_rest=list(groups[node])
        t_rest[3]+=rest
        print(f"group-node: {rest}")
        groups[node]=tuple(t_rest)

        #node 3 is the one containing all the flags

        print(f"node: {groups[node]}")
        print(f"node2: {groups[node][2]}")

        if groups[node][0] in bracketed:
            bracket[node]=True
            print("Bracketed stack detected")


        if (groups[node][0]==groups[node][1]) and (groups[node][0].isdigit()): #making sure the shorthand 1,1 etc works.
            if node==0:
                dice_s[node]=20
                dice_i[node]=int(groups[node][1])
                print(f"dice: d-{dice_s[node]}")
                if stacks==1:
                    modifier[node]=4
                continue
            if node==1:
                dice_s[node]=6
                dice_i[node]=int(groups[node][1])
                print(f"dice: d-{dice_s[node]}")
                continue

        if groups[node][2]=="": #determining die size (d20, d6 etc)
            if node==0:
                dice_s[node]=20
            elif node==1:
                dice_s[node]=6
            else:
                print("Unknown die size!")
        elif "c" in groups[node]:
            dice_s[node]=10
            modifier[node]=5
            keep[node]=True
        else:
            dice_s[node]=int(groups[node][2][1:])
        
        print(f"dice: d-{dice_s[node]}")

        if groups[node][1]: #determining how many dice are rolled
            try:
                dice_i[node]=int(groups[node][1])
                print(f"dice_i: {dice_i}")
            except (TypeError,ValueError):
                await ctx.send("dice_i Error")

        for part in groups[node]:
            if ("+" in part) or ("-" in part): #determining modifier
                if ("++" in part) or ("--" in part):
                    mod_pattern=re.compile("(\+\+|\-\-)(\d)+")
                    mod_match=mod_pattern.search(part)
                    print(bracket[node])
                    if bracket[node]:
                        modifier[node]=int(mod_match.group()[1:])
                    else:
                        stack_modifier=int(mod_match.group()[1:])
                    
                    if "c" in part.casefold():
                        modifier[node]+=5
                    else:
                        if bracket[node]:
                            modifier[node]+=base_modifier
                        else:
                            stack_modifier+=base_modifier
                else:
                    mod_pattern=re.compile("(\+|\-)+(\d)+")
                    mod_match=mod_pattern.search(part)
                    print(mod_match)
                    if bracket[node]:
                        modifier[node]=int(mod_match.group())
                    else:
                        stack_modifier=int(mod_match.group())

            else:
                if dice_s[node]==20:
                    modifier[node]=base_modifier+modifier[node]
                
            print(f"modifier: {modifier},{stack_modifier}")


        if "b" in groups[node][3]:
            if bracket[node]:
                brief[node]=True
            else:
                stack_brief=True

        if "x" in groups[node][3]:
            if "xb" in groups[node][3]:
                if bracket[node]:
                    brief[node]=True
                else:
                    stack_brief=True
                x_pattern=re.compile("xb(\d)*")
                x_match=x_pattern.search(groups[node][3])
                if x_match:
                    if bracket[node]:
                        repeats[node]=int(x_match.group()[2:])
                    else:
                        stack_repeats=int(x_match.group()[2:])
            else:
                # if bracket[node]:
                #     brief[node]=True
                # else:
                #     stack_brief=True
                x_pattern=re.compile("x(\d)*")
                x_match=x_pattern.search(groups[node][3])
                if x_match:
                    if bracket[node]:
                        repeats[node]=int(x_match.group()[1:])
                    else:
                        stack_repeats=int(x_match.group()[1:])
        else:
            if bracket[node]:
                repeats[node]=1
            else:
                stack_repeats=1
            
        print(f"repeats: {stack_repeats}, {repeats[node]}")

        if "!" in groups[node][3]:
            if bracket[node]:
                explode[node]=True
            else:
                stack_explode=True

        if "D" in groups[node][2]:
            if bracket[node]:
                keep[node]=False
            else:
                stack_keep=False

        if "p" in groups[node][3]:
            if bracket[node]:
                high_low[node]="Low"
            else:
                stack_high_low="Low"
        
        if (stack_repeats>10e2) or (repeats[node]>10e3) or (dice_s[node]>10e7) or (dice_i[node]>10e3): #safeguard against unnecessarily large rolls
            await ctx.send("BRB, driving to the dice store. Oh no, looks like they're all out of dice, just like I am of fucks to give about your spammy rolls.")
            return

    requester=ctx.message.author.name
    out_roll=[f"{requester}: `{formula}` ("] #this will be our output

    for stack_repeat_loop in range(0,stack_repeats):
        stack_crit=""
        if stack_repeat_loop !=0:
            out_roll.append(", ")
        for node in range(0,stacks):
            if node!=0:
                out_roll.append(", (")
            if repeats[node]>1:
                    results[node]=[None]*repeats[node]
            for repeat in range(0,repeats[node]): #bracketed
                if (repeat!=0):
                    out_roll.append(", (")
                result=[]
                for x in range(0,dice_i[node]):
                    result.append(random.randint(1,dice_s[node]))
                if explode[node] or stack_explode:
                    loops=len(result)
                    k=0
                    while (k < loops):
                        #print(k)
                        if result[k]==dice_s[node]:
                            result.append(random.randint(1,dice_s[node]))
                            loops=len(result)
                        k=k+1
                        if k>100: #save us from infinite loops
                            await ctx.send("Too many exploding dice! Help, everything is on fire!")
                            break
                result_i= [int(i) for i in result] #convert result to int

                if keep[node] or stack_keep:
                    if high_low[node]=="Low":
                        highest=min(result_i)
                    else:
                        highest=max(result_i)
                else:
                    highest=sum(result)
                #print(keep)
                if keep[node] or stack_keep:
                    for x in range(0,len(result_i)):
                        if result_i[x]!=highest:
                            out_roll.append("~~")
                            out_roll.append(str(result_i[x]))
                            out_roll.append("~~")
                        else:
                            out_roll.append(str(result_i[x]))
                        if x!=len(result_i)-1:
                            out_roll.append("+")
                else:
                    highest=sum(result)
                    for x in range(0,len(result_i)):
                            out_roll.append(str(result_i[x]))
                            if x!=len(result_i)-1:
                                out_roll.append("+")
                out_roll.append(")")
                if modifier[node]>0:
                    out_roll.append("+")
                if dice_s[node]==highest: #crit check
                    crit[node]="__"
                    if modifier[node] != 0:
                        out_roll.append(f"{modifier[node]}=__**{highest+modifier[node]}**__")
                    else:
                        out_roll.append(f"=__**{highest+modifier[node]}**__")
                elif modifier[node]==0:
                    out_roll.append(f"=**{highest}**")
                else:
                    out_roll.append(f"{modifier[node]}=**{highest+modifier[node]}**")
                
                if repeats[node]>1:
                    results[node][repeat]=highest
                else:
                    results[node]=highest

                #print(out_roll)
            if brief[node] or stack_brief: #convert into shorthand if desired
                out_saved=out_roll
                out_roll=[f"{requester}: "]
                brief_pattern=re.compile("\*\*-*\d+\*\*")
                brief_match=brief_pattern.findall(''.join(out_saved))
                for k in range(0,len(brief_match)):
                    if k==len(brief_match)-1:
                        critcheck=brief_match[k].replace("*","")
                        if (int(critcheck)-modifier[node])==dice_s[node]:
                            out_roll.append(f"__{brief_match[k]}__")
                        else:
                            out_roll.append(f"{brief_match[k]}")
                    else:
                        critcheck=brief_match[k].replace("*","")
                        if (int(critcheck)-modifier[node])==dice_s[node]:
                            out_roll.append(f"__{brief_match[k]}__, ")
                        else:
                            out_roll.append(f"{brief_match[k]}, ")
            if dice_s[node]==20 and crit[node]=="__":
                stack_crit="__"
                
        out_roll.append(" => ")
        print(f"results: {results}")
        final_result=sum(results) #arrayize TODO
        if final_result==sum(dice_s):
            stack_crit="__"
        
        if stack_modifier>0:
            out_roll.append("+")
        if stack_modifier != 0: 
            out_roll.append(f"{stack_modifier}={stack_crit}**{final_result+stack_modifier}**{stack_crit}")
            if any(bracket): # make sure each bracketed result gets added
                for i in results:
                    out_roll.append(f"{stack_crit}**{i+stack_modifier}**{stack_crit}")
        else:
            if any(bracket): # make sure each bracketed result gets added
                print(results)
                for i in results:
                    out_roll.append(f"{stack_crit}**{i+stack_modifier}**{stack_crit}")
            else:
                out_roll.append(f"{stack_crit}**{final_result+stack_modifier}**{stack_crit}")
            
    
    if comment!="":
        if comment[0]=="#" and comment[1]=="#":
            comment=comment[1:]
        out_roll.append(f" #{' '.join(comment)}")
    try:
        await ctx.send(''.join(out_roll))
    except discord.ext.commands.errors.CommandInvokeError:
        await ctx.send("Message too long!")


#dice rolling.
@bot.command(description="See >tag roll for help",aliases=["r"])
async def roll(ctx,formula="default",*comment):
    loc=ctx.message.guild.id
    s_id = await sid(loc)

    if formula[0]=="$":
        user=str(ctx.message.author.id)
        if formula in macros[user]:
            for i in macros[user][formula]:
                if "#" in i:
                    form=i.split("#")
                    await ctx.invoke(roll,form[0]," ".join(form[1:]))
                else:
                    await ctx.invoke(roll,formula=i)
        return
    formula_in=formula

    if comment==():
        comment=""
    if formula[0]=="#":
        comment2=(formula[1:],)
        if comment!="":
            comment=comment2+comment
        else:
            comment=comment2
        formula="default"

    if ((s_id=="portland") or (s_id=="wd6")) and (formula=="default"):
        formula="1d6"
    elif formula=="default":
        formula="3d20+4"
    modifier=0
    if "d" in formula.casefold():
        d_pattern=re.compile("(d|D)(\d)*")
        d_match=d_pattern.search(formula)
        if d_match.group()[0]=="D":
            keep=False
        else:
            keep=True
        dice=int(d_match.group()[1:])
    else:
        if "c" in formula.casefold():
            dice=10
            modifier=5
            keep=True
        else:
            if ((s_id=="portland") or (s_id=="wd6")):
                dice=6
            else:
                dice=20
            keep=True
    #print(f"dice: {dice}")

    if ("+" in formula) or ("-" in formula):
        if ("++" in formula) or ("--" in formula):
            mod_pattern=re.compile("(\+\+|\-\-)(\d)*")
            mod_match=mod_pattern.search(formula)
            modifier=int(mod_match.group()[1:])
            if "c" in formula.casefold():
                modifier=5+modifier
            else:
                modifier=4+modifier
        else:
            mod_pattern=re.compile("(\+|\-)+(\d)*")
            mod_match=mod_pattern.search(formula)
            modifier=int(mod_match.group())
    else:
        if dice==20:
            modifier=4+modifier
    #print(f"modifier: {modifier}")

    brief=False
    if "b" in formula:
        brief=True
    if "x" in formula:
        if "xb" in formula:
            brief=True
            x_pattern=re.compile("xb(\d)*")
            x_match=x_pattern.search(formula)
            if x_match:
                repeats=int(x_match.group()[2:])
        else:
            brief=False
            x_pattern=re.compile("x(\d)*")
            x_match=x_pattern.search(formula)
            if x_match:
                repeats=int(x_match.group()[1:])
    else:
        repeats=1
    #print(f"repeats: {repeats}")

    i_pattern=re.compile("(\A)(\d)*")
    i_match=i_pattern.search(formula)
    if i_match:
        try:
            i=int(i_match.group())
        except ValueError:
            if dice==20:
                if formula_in[0]=="d":
                    if "d20" in formula_in:
                        i=1
                else:
                    i=3
            else:
                i=1
            #print("ValueError")
    else:
        print("i-error in roll!")
        return
    #print(f"die #s: {i}")

    if "!" in formula:
        explode=True
    else:
        explode=False

    requester=ctx.message.author.name
    out_roll=[f"{requester}: ("]

    #print(repeats)
    #print(dice)
    #print(i)
    if (repeats>10e2) or (dice>10e7) or (i>10e3):
        await ctx.send("BRB, driving to the dice store. Oh no, looks like they're all out of dice, just like I am of fucks to give about your spammy rolls.")
        return
    for j in range(0,repeats):
        if (j!=0):
            out_roll.append(", (")
        result=[]
        for x in range(0,i):
            result.append(random.randint(1,dice))
        if explode is True:
            loops=len(result)
            k=0
            while (k < loops):
                #print(k)
                if result[k]==dice:
                    result.append(random.randint(1,dice))
                    loops=len(result)
                k=k+1
                if k>100: #save us from infinite loops
                    break
        result_i= [int(i) for i in result]

        if keep is True:
            if "p" in formula:
                highest=min(result_i)
            else:
                highest=max(result_i)
        else:
            highest=sum(result)
        #print(keep)
        if keep is True:
            for x in range(0,len(result_i)):
                if result_i[x]!=highest:
                    if keep is True:
                        out_roll.append("~~")
                        out_roll.append(str(result_i[x]))
                        out_roll.append("~~")
                    else:
                        out_roll.append(str(result_i[x]))
                else:
                    out_roll.append(str(result_i[x]))
                if x!=len(result_i)-1:
                    out_roll.append("+")
        else:
            highest=sum(result)
            for x in range(0,len(result_i)):
                    out_roll.append(str(result_i[x]))
                    if x!=len(result_i)-1:
                        out_roll.append("+")
        out_roll.append(")")
        if modifier>0:
            out_roll.append("+")
        if dice==highest:
            if modifier != 0:
                out_roll.append(f"{modifier}=__**{highest+modifier}**__")
            else:
                out_roll.append(f"=__**{highest+modifier}**__")
        elif modifier==0:
            out_roll.append(f"=**{highest}**")
        else:
            out_roll.append(f"{modifier}=**{highest+modifier}**")
        #print(out_roll)
    if brief is True:
        out_saved=out_roll
        out_roll=[f"{requester}: "]
        brief_pattern=re.compile("\*\*-*\d+\*\*")
        brief_match=brief_pattern.findall(''.join(out_saved))
        for k in range(0,len(brief_match)):
            if k==len(brief_match)-1:
                critcheck=brief_match[k].replace("*","")
                if (int(critcheck)-modifier)==dice:
                    out_roll.append(f"__{brief_match[k]}__")
                else:
                    out_roll.append(f"{brief_match[k]}")
            else:
                critcheck=brief_match[k].replace("*","")
                if (int(critcheck)-modifier)==dice:
                    out_roll.append(f"__{brief_match[k]}__, ")
                else:
                    out_roll.append(f"{brief_match[k]}, ")
    if comment!="":
        if comment[0]=="#" and comment[1]=="#":
            comment=comment[1:]
        out_roll.append(f" #{' '.join(comment)}")
    try:
        await ctx.send(''.join(out_roll))
    except discord.ext.commands.errors.CommandInvokeError:
        await ctx.send("Message too long!")

tag_muted=False #global


#tags are text blocks, useful for re-posting common infomration like character appearance etc. Also memes. So many memes.
@bot.command(description="Memorize Texts. Add a tag by writing >tag create title content; update by >tag update title newcontent; delete by >tag delete title",aliases=["effect","t"])
async def tag(ctx, tag=None, content1=None, *,content2=None):
    global tags
    if (tag is None) or (tag.casefold()=="empty"):
        await ctx.message.add_reaction("❌")
    elif tag.casefold()=="create".casefold() or tag.casefold()=="make".casefold():
        global tag_muted
        if tag_muted is True:
            await ctx.send("Disabled until you fuckers calm down.")
            return
        elif (content1 is None) or (content2 is None):
            await ctx.send("Need a name and content for the tag.")
            return
        elif any(e[0].casefold() == content1.casefold() for e in tags):
            await ctx.send("Name already taken.")
            return
        if "@everyone" in content2 or "@here" in content2:
            await ctx.send("How about you don't try that.")
            return

        gc = gspread.authorize(credentials)
        RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
        tagsSheet = RefSheet.worksheet("Tags")
        new_tag=tagsSheet.find("empty")
        tagsSheet.update_cell(new_tag.row,new_tag.col, content1.casefold())
        tagsSheet.update_cell(new_tag.row,new_tag.col+1, content2)
        tagsSheet.update_cell(new_tag.row,new_tag.col+2, str(ctx.message.author.id))
        tagsSheet.update_cell(new_tag.row+1,new_tag.col, "empty")
        tags = tagsSheet.get_all_values()
        await ctx.send(f"{content1} has been created.")
    elif tag_muted is False:
        if tag.casefold()=="list":
            await ctx.send("List of all current tags: https://docs.google.com/spreadsheets/d/e/2PACX-1vRjroKacZBQrkIEayrhHuFtA_5mAL_C48Y-4taCjZ5k0mNXAPTi5diZAiZ-7l-Uai5xvbNomF_s1-0m/pubhtml")
        elif tag.casefold()=="owner":
            gc = gspread.authorize(credentials)
            RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
            tagsSheet = RefSheet.worksheet("Tags")
            try:
                target_tag=tagsSheet.find(content1.casefold())
            except gspread.exceptions.CellNotFound:
                await ctx.send(f"Tag not found!")
                return
            ownerID=tagsSheet.cell(target_tag.row,target_tag.col+2).value
            #print(f"{ownerID} in {target_tag.row}")
            #print("hello?")
            tagowner=discord.utils.get(bot.get_all_members(), id=int(ownerID))
            if tagowner is None:
                await ctx.send(f"{content1} is owned by an unknown user.")
                return
            await ctx.send(f"{content1} is owned by {tagowner.name}.")
            return
        elif tag.casefold()=="delete":
            gc = gspread.authorize(credentials)
            RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
            tagsSheet = RefSheet.worksheet("Tags")
            target_tag=tagsSheet.find(content1.casefold())
            if ctx.message.author.id==int(tagsSheet.cell(target_tag.row, target_tag.col+2).value) or ctx.message.author.id==138340069311381505:
                tagsSheet.delete_row(target_tag.row)
                tags = tagsSheet.get_all_values()
                await ctx.send(f"{content1} deleted.")
            else:
                await ctx.send("Not your tag!")
        elif tag.casefold()=="update":
            if "@everyone" in content2 or "@here" in content2:
                await ctx.send("How about you don't try that.")
                return
            gc = gspread.authorize(credentials)
            RefSheet = gc.open_by_key('1LOZkywwxIWR41e8h-xIMFGNGMe7Ro2cOYBez_xWm6iU')
            tagsSheet = RefSheet.worksheet("Tags")
            target_tag=tagsSheet.find(content1.casefold()) #change to findall, discard non-titles
            if target_tag.col!=1:
                print("tag column error!")
                return
            if ctx.message.author.id==int(tagsSheet.cell(target_tag.row, target_tag.col+2).value) or ctx.message.author.id==138340069311381505:
                tagsSheet.update_cell(target_tag.row,target_tag.col+1, content2)
                tags = tagsSheet.get_all_values()
                await ctx.send(f"{content1} updated.")
            else:
                await ctx.send("Not your tag!")
        elif any(e[0] == tag.casefold() for e in tags):
            for i in tags:
                if i[0]==tag.casefold():
                    response=cleaner(ctx,i[1])
                    await ctx.send(response)
        else:
            if not (await ctx.invoke(wound,severity=str(tag))):
                await ctx.message.add_reaction("❌")


#Can use this to stop tag abuse
@bot.command(hidden=True)
async def tagToggle(ctx):
    global tag_muted
    if ctx.message.author.id not in owner:
        await ctx.send("🌚")
        return
    if tag_muted is False:
        tag_muted=True
        await ctx.message.add_reaction("🔥")
    elif tag_muted is True:
        tag_muted=False
        await ctx.message.add_reaction("🌊")
    else:
        await ctx.send("Beep Boop. Error.")


#convert from inches to cm. Very, very basic.
@bot.command(aliases=["conv"],description="Fuck the Imperial System.")
async def convert(ctx, inches):
    ft_symbol="'"
    ft = inches.find(ft_symbol)
    if ft != -1:
        inch=12*int(inches[:ft])
        if not inches.endswith(ft_symbol):
            inch=inch+int(inches[ft+1:])
    else:
        inch=int(inches)
    await ctx.send(f"{inches} is equal to {inch*2.54}cm")

####################
#Turn Tracker module
####################
turn_tracker={}

# The turn tracker allows you to keep combat flowing by automatically pinging people when it is their turn.
# First, everyone enters their initiative score by using >init 11
# If two people need to roll off (say both roll an 11), the winner of the rolloff should enter their initiative as 11.5
# Once everyone has entered their score, simply use >start to get going!
# if you have finished your turn, simply use >end
# When your fight is done, use >clear to empty the initiative queue


@bot.command(description="""The turn tracker allows you to keep combat flowing by automatically pinging people when it is their turn.
                    First, everyone enters their initiative score by using >init 11 etc.
                    If two people need to roll off (say both roll an 11), the winner of the rolloff should enter their initiative as 11.5
                    Once everyone has entered their score, simply use >start to get going!
                    If you have finished your turn, simply use >end

                    You can remove people (like KO'd characters) by using the >kick command on their turn, or entering their name.

                    When your fight is done, use >clear to empty the initiative queue

                    You can set reminders (e.g. willpowered wounds returning in 2 rounds) by using >turn 2 wp expires

                    This also supports re-shuffling init in the middle of a fight.

                    If you are a QG, you can add NPCs via *>init 11 NPC1*
                    """)
async def init(ctx, score:float, alias=None):
    chan=ctx.channel.id
    global turn_tracker
    if alias is None:
        a_id=ctx.author.id
    else:
        a_id=alias 

    if chan in turn_tracker.keys():
        turn_tracker[chan]["init"].update({a_id:score})
    else:
        turn_tracker[chan]={"init":{a_id:score},"turn":0,"round":1,"started":False}

    if "owner" in turn_tracker[chan]:
        turn_tracker[chan]["owner"].update({a_id:ctx.author.id})
    else:
        turn_tracker[chan]["owner"]={a_id:ctx.author.id}
    await ctx.message.add_reaction("✅")
    #print(sorted(turn_tracker[chan]["init"].items(), key=lambda x:x[1],reverse=True))
    #print(turn_tracker)


@bot.command(description="Once everyone has entered their score, simply use >start to get going!")
async def start(ctx):
    chan=ctx.channel.id
    global turn_tracker
    turn_tracker[chan]["order"]=sorted(turn_tracker[chan]["init"].items(), key=operator.itemgetter(1),reverse=True)
    turn_tracker[chan]["started"]=True
    cur_turn=turn_tracker[chan]["turn"]
    cur_round=turn_tracker[chan]["round"]
    #await ctx.invoke(end,"True",start)
    if cur_round==1 and cur_turn==0:
        player=turn_tracker[chan]["owner"][turn_tracker[chan]['order'][cur_turn][0]]
        if player!=turn_tracker[chan]['order'][cur_turn][0]:
            player=f"**{turn_tracker[chan]['order'][cur_turn][0]}** controlled by <@!{player}>"
        else:
            player=f"<@!{player}>"
        await ctx.send(f"{player} goes first!")
        turn_tracker[chan].update({"turn":cur_turn+1})


@bot.command(description="Once you have finished your turn, simply use >end")
async def end(ctx, force=False,invoked=False,): #start=False

    chan=ctx.channel.id
    if chan in turn_tracker:
        cur_turn=turn_tracker[chan]["turn"]
    else:
        await ctx.send("No fight saved. If you were in a fight, the bot might just have restarted.")
        return
    rem_turn=cur_turn
    cur_round=turn_tracker[chan]["round"]
    #print(f"end: cur_turn {cur_turn} cur_round {cur_round}")
    if invoked is False:
        if ((turn_tracker[chan]['order'][cur_turn-1][0] != ctx.author.id) and 
            (turn_tracker[chan]['owner'][turn_tracker[chan]['order'][cur_turn-1][0]] != ctx.author.id)  and 
            (force is False)):
            await ctx.send("Not your turn! If player is afk or else, use >end True")
            return

    if turn_tracker[chan]["turn"]>=len(turn_tracker[chan]["order"]):
        turn_tracker[chan].update({"round":cur_round+1})
        await ctx.send(f"Round {turn_tracker[chan]['round']} begins.")
        turn_tracker[chan].update({"turn":0})

        cur_turn=turn_tracker[chan]["turn"]
        cur_round=turn_tracker[chan]["round"]
        rem_turn=cur_turn

    player=turn_tracker[chan]["owner"][turn_tracker[chan]['order'][cur_turn][0]]
    if player!=turn_tracker[chan]['order'][cur_turn][0]:
        player=f"**{turn_tracker[chan]['order'][cur_turn][0]}** controlled by <@!{player}>"
    else:
        player=f"<@!{player}>"
    await ctx.send(f"Turn {turn_tracker[chan]['round']} for {player}")

    #turn reminder logic
    if "reminder" in turn_tracker[chan]:
        for i in turn_tracker[chan]["reminder"]:

            #print(f"cur_turn {cur_turn} rem_turn {rem_turn} looking for {i[3]}")
            #print(f"round {cur_round} looking for {i[1]}")

            if (i[3]==rem_turn) and (i[1]==cur_round):
                name=naming(ctx.guild,i[0])
                await ctx.send(f"Reminder for {name}: {i[2]}")
                turn_tracker[chan]["reminder"].remove(i)

    turn_tracker[chan].update({"turn":cur_turn+1})
    #print(f"end2: cur_turn {cur_turn} cur_round {cur_round}")
    #print("--------")


@bot.command(description="Shows current Initiative order. Use *>show init* to check what re*>start*ing would look like.")
async def show(ctx,init="False"):
    chan=ctx.channel.id

    #print(turn_tracker[chan])
    init_list=[]
    init_str=""

    order_list=[]
    order_str=""

    if (turn_tracker[chan]["started"] is False) or init.casefold()=="init":
        for i,j in turn_tracker[chan]["init"].items():
            init_list.append((i,j))
        #print(init_list)
        init_list.sort(key=itemgetter(1),reverse=True)
        init_list=list(enumerate(init_list,1))
        init_str=[f"Init so far:"+os.linesep]
        for i in init_list:
            try:
                usr= ctx.guild.get_member(i[1][0])
            except:
                usr=i[1][0]
            #print(type(usr))
            #print(usr)
            if isinstance(usr, discord.member.Member):
                init_str+=((f"**{i[0]}**. {usr.display_name}  *{i[1][1]}*"+os.linesep))
            else:
                init_str+=((f"**{i[0]}**. {i[1][0]}  *{i[1][1]}*"+os.linesep))
        init_str=''.join(init_str)
        await ctx.send(init_str)

    if turn_tracker[chan]["started"] is True:
        for i in turn_tracker[chan]["order"]:
            order_list.append((i[0],i[1]))
        order_list=list(enumerate(order_list,1))
        order_str=[f"Current Init order in {ctx.message.channel.name}"+os.linesep]
        for i in order_list:
            try:
                usr= ctx.guild.get_member(i[1][0])
            except:
                usr=i[1][0]
            if isinstance(usr, discord.member.Member):
                order_str+=((f"**{i[0]}**. {usr.display_name}  *{i[1][1]}*"+os.linesep))
            else:
                order_str+=((f"**{i[0]}**. {i[1][0]}  *{i[1][1]}*"+os.linesep))
        order_str=''.join(order_str)
        await ctx.send(order_str)

    #init_list+f"{i}"+os.linesep


@bot.command(description="You can remove people (like KO'd characters) by using the >kick command on their turn, or entering their name.")
@commands.cooldown(1,5,commands.BucketType.channel)
async def kick(ctx,*user):
    #kick whoevers turn it is by default
    chan=ctx.channel.id
    global turn_tracker

    if user==():
        cur_turn=turn_tracker[chan]["turn"]
        for i in turn_tracker[chan]["order"]:
            if turn_tracker[chan]['order'][cur_turn-1][0]==i[0]:
                usr=ctx.guild.get_member(i[0])
                try:
                    await ctx.send(f"<@!{usr.id}> has been removed on Turn {turn_tracker[chan]['turn']}, Round {turn_tracker[chan]['round']}")
                except AttributeError:
                    await ctx.send(f"<@!{i[0]}> has been removed on Turn {turn_tracker[chan]['turn']}, Round {turn_tracker[chan]['round']}")
                turn_tracker[chan]["order"].remove(i)
                await ctx.message.add_reaction("✅")
                turn_tracker[chan]["turn"]-=1
                await ctx.invoke(end,"True",True)
                return

    user=" ".join(user)
    #usr to id
    #id
    usr=None
    try:
        usr = ctx.guild.get_member(user)
    except:
        pass

    #nick
    try:
        if usr is None:
            usr = ctx.guild.get_member_named(user)
    except:
        pass

    if usr is None:
        await ctx.send("No fucking clue who that is.")
        return
    #ping
    for i in turn_tracker[chan]["order"]:
        if usr.id==i[0]:
            turn_tracker[chan]["order"].remove(i)
            turn_tracker[chan]["turn"]-=1
            await ctx.send(f"<@!{usr.id}> has been removed on Turn {turn_tracker[chan]['turn']}, Round {turn_tracker[chan]['round']}")
            #await ctx.invoke(end,"True",True)
            return


@bot.command(description="When your fight is done, use >clear to empty the initiative queue", aliases=["gg"])
async def clear(ctx,):
    chan=ctx.channel.id
    global turn_tracker
    if chan in turn_tracker:
        del turn_tracker[chan]
        await ctx.send(random.choice(["GG!","Well played!","It's over, I have the high ground!","Commencing fightspam.","Battle is joined.","1v1 me bro","Good luck!"]))
    else:
        await ctx.message.add_reaction("\U00002b50")


@bot.command(description="You can set reminders (e.g. willpowered wounds returning in 2 rounds) by using >turn 2 wp expires.")
async def turn(ctx,number:int,*comment):
    chan=ctx.channel.id
    usr=ctx.author

    global turn_tracker

    comment=" ".join(comment)
    cur_round=turn_tracker[chan]["round"]
    cur_turn=turn_tracker[chan]["turn"]
    #if cur_round==1 and cur_turn==1:
    #cur_round=cur_round-1
    if "reminder" in turn_tracker[chan]:
        turn_tracker[chan]["reminder"].append((usr.id,cur_round+number,comment,cur_turn-1))
    else:
        turn_tracker[chan].update({"reminder":[(usr.id,cur_round+number,comment,cur_turn-1)]})
    await ctx.message.add_reaction("✅")


#################
#New Skill module
@bot.group()
async def rank2(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Available commands: show, make, update')


#TODO: Replace with trueSkill
#GLICKO MODUlE
#defining parameters for the glicko system
scale=173.7178
tau=0.3
#name, rating, rd
#-------------
test="test"


@bot.group()
async def rank(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Available commands: show, make, update, ladder')


@rank.command()
async def ladder(ctx, mode="lax"):
    loc=ctx.message.guild.id
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    sort_rank=sorted(rankings,key=operator.itemgetter(1), reverse=True)
    ladder_names=[]
    if mode.casefold()=="strict":
        RD_cutoff=100
    elif mode.casefold()=="lax":
        RD_cutoff=200
    else:
        try:
            RD_cutoff=int(mode)
        except ValueError:
            RD_cutoff=200 #lax
    for i in sort_rank:
        if i[2]<RD_cutoff:
            ladder_names.append([i[0],int(round(i[1],0))])
    ladder_list=list(enumerate(ladder_names,1))
    ladder_str=[f"Ladder for {ctx.message.guild}"+os.linesep]
    for x in ladder_list:
        pos = await int_to_roman(x[0])
        ladder_str+=((f"**{pos}**. {x[1][0]}  *{x[1][1]}*"+os.linesep))
    ladder_str=''.join(ladder_str)
    ladder_str+=f"_Only capes under {RD_cutoff} RD are included here. NB this only reflects 1v1 performance._"
    await ctx.send(ladder_str)


@rank.command()
async def show(ctx, cape=None):
    loc=ctx.message.guild.id
    if cape is None:
        await ctx.send(f"Forgot something? Maybe your name, {ctx.message.author.display_name}?")
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    #print(rankings)
    for i in rankings:
        if i[0]==cape.casefold():
            await ctx.send(f"{cape} - Rating: {round(i[1],1)}, RD: {round(i[2],1)}, sigma: {round(i[3],3)}")
            return
    await ctx.send(f"{cape} not found.")
    #print(rankings)


@rank.command(name="help")
async def _help(ctx,cape=None):
    await ctx.send("To enter your cape into the database, use "">rank make halcyon"". If you finish a fight, use "">rank update luke vader win"". In this one, luke won against vader. If luke had lost, you would write "">rank update luke vader loss"". Only one person needs to do this, the other's rank is updated automatically. You can see your rating by using "">rank show halcyon"". This is still a pretty early build, so expect bugs and shit. Consider this a beta that will probably get wiped at some point.")


@rank.command(aliases=["create"])
async def make(ctx,cape=None):
    loc=ctx.message.guild.id
    if cape is None:
        await ctx.send("I do need a name for you if this is going to work.")
    entry=[]
    cape=cape.casefold()
    entry.append(cape)
    entry.append(1500) #default values. Rating, Rating deviation, volatility
    entry.append(350)
    entry.append(0.06)
    if os.path.isfile(f"glicko{loc}.txt"):
        with open(f"glicko{loc}.txt",mode="r+") as f:
            rankings = json.load(f)
            if cape in sum(rankings,[]):
                await ctx.send("Duplicate name.")
                return
            f.seek(0)
            f.truncate()
            rankings.append(entry)
            json.dump(rankings,f)
    else:
        with open(f"glicko{loc}.txt",mode="w+") as f:
            rankings=[]
            f.seek(0)
            f.truncate()
            rankings.append(entry)
            json.dump(rankings,f)
    await ctx.send(f"{cape} added to database. Rating: 1500")
    #print(rankings)


@rank.command()
async def odds(ctx,cape1,cape2):
    loc=ctx.message.guild.id
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    c1=False
    c2=False
    for i in rankings:
        if i[0]==cape1.casefold():
            c1=i
        if i[0]==cape2.casefold():
            c2=i
    if c1 is False:
        await ctx.send(f"Cannot find {cape1}.")
        return
    elif c2 is False:
        await ctx.send(f"Cannot find {cape2}.")
        return
    rating_cape=c1[1]
    rd_cape=c1[2]
    rating_opponent=c2[1]
    rd_opponent=c2[2]

    def g(rd):
        q=math.log(10)/400
        return 1/math.sqrt(1+3*(q**2)*(rd**2)/(math.pi**2))

    #print(g(math.sqrt(rd_cape**2+rd_opponent**2)))
    e=1/(1+10**(-g(math.sqrt(rd_cape**2+rd_opponent**2))*(rating_cape-rating_opponent)/400))
    prob=round(e*100,0)
    dec_odds=round(100/prob,2)
    dec_odds_loss=round(100/(100-prob),2)
    await ctx.send(f"{cape1} beats {cape2} with {prob}% chance. This represents odds of {dec_odds} for a win. ({dec_odds_loss} if you bet on {cape2}).")
    #print(e)


@rank.command(aliases=["u"], )
async def update(ctx,cape, opponent, outcome,inv=False):
    loc=ctx.message.guild.id
    if type(outcome)==str:
        if outcome=="win":
            outcome=1
        elif outcome=="loss":
            outcome=0
        else:
            outcome=int(outcome)
            if outcome!=1 and outcome!=0:
                await ctx.send("Outcome must be win or loss!")
                return
    #print(f"Start: {outcome}, {inv}, {cape}, {opponent}")
    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    c1=False
    c2=False
    for i in rankings:
        if i[0]==cape.casefold():
            c1=i
        elif i[0]==opponent.casefold():
            c2=i
    if c1 is False:
        await ctx.send(f"Cannot find {cape}.")
        return
    elif c2 is False:
        await ctx.send(f"Cannot find {opponent}.")
        return
    rating_cape=(c1[1]-1500)/scale
    rd_cape=c1[2]/scale
    vola_cape=c1[3]
    rating_opponent=(c2[1]-1500)/scale
    rd_opponent=c2[2]/scale
    g_phi_op=g_phi(rd_opponent)
    #print(f"g phi of opponent: {g_phi_op}")
    e=1/(1+math.exp((-g_phi_op)*(rating_cape-rating_opponent)))

    #print(f"E: {e} by {-g_phi_op}*({rating_cape}-{rating_opponent})")
    variance=1/((g_phi_op**2*e*(1-e)))
    #print(f"variance is {variance}")

    if variance>6:
        #print(f"variance corrected from {variance}")
        variance=6

    #change in rating, based on outcomes only
    delta=variance*(g_phi_op*(outcome-e))
    #print(f"delta is {delta} via {variance}*({g_phi_op}*({outcome}-{e}))")

    #new sigma
    a=math.log(vola_cape**2)
    epsilon=0.000001

    def f(x):
        result=(math.exp(x)*(delta**2-rd_cape**2-variance-math.exp(x))/2*(rd_cape**2+variance+math.exp(x))**2)-((x-a)/tau**2)
        return result
    alpha=a
    #print(f"delta squared: {delta**2}")
    #print(f"RD times variance: {rd_cape**2+variance}")
    if ((delta**2)>(rd_cape**2+variance)):
        b=math.log(delta**2-rd_cape**2-variance)
        #print("big delta")
    elif((delta**2)<=(rd_cape**2+variance)):
        k=1
        #print("smol delta")
        while (f(a-k*tau)<0):
            k+=1
        b=a-k*tau
    else:
        print("ERROR in volatility update")
        return
    f_a,f_b = f(alpha),f(b)
    while (abs(b-alpha)>epsilon):
        c=alpha+(alpha-b)*f_a/(f_b-f_a)
        f_c=f(c)
        if (f_c*f_b<0):
            alpha=b
            f_a=f_b
        else:
            f_a=f_a/2
        b=c
        f_b=f_c
    sigma_new=math.exp(alpha/2)

    rd_period=math.sqrt(rd_cape**2+sigma_new**2)
    rd_new=1/(math.sqrt((1/rd_period**2)+(1/variance)))
    rating_new=rating_cape+((rd_new**2)*(g_phi_op*(outcome-e)))

    rd_new=scale*rd_new
    rating_new=(scale*rating_new)+1500
    up_func=bot.get_command("rank update")

    if inv is False:
        await ctx.invoke(up_func,cape=opponent,opponent=cape,outcome=abs(1-outcome),inv=True)
    #capename, ranking, RD, volatility

    #is RD is over 350, reset to the maximum of 350
    if rd_new>350:
        rd_new=350

    with open(f"glicko{loc}.txt") as f:
        rankings = json.load(f)
    for i in rankings:
        if i[0]==cape.casefold():
            i[1]=rating_new
            i[2]=rd_new
            i[3]=sigma_new
            #print(f" {cape} Rating, RD, sigma:{rating_new}, {rd_new}, {sigma_new}")

    with open(f"glicko{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(rankings,f)

    if inv is False:
        for i in rankings:
            if i[0]==opponent.casefold():
                op_rating=round(i[1],1)
        await ctx.send(f"Ratings updated. New rating for {cape}: {round(rating_new,1)} New rating for {opponent}: {op_rating}")


def g_phi(rd_cape):
    g_phi_r=1/(math.sqrt(1+(3*(rd_cape**2)/math.pi**2)))
    return g_phi_r


@bot.group(description="Available commands: show, make, update, income. Show your balance, Make an account, Update your balance, Increase your weekly income.",aliases=["acc"])
async def account(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Available commands: show, make, update, income. Show your balance, Make an account, Update your balance, Increase your weekly income.')


@account.command(description="Check how many more donuts you can afford.")
async def show(ctx, cape=None):
    loc=ctx.message.guild.id
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    for i in accounts:
        if i[0]==cape.casefold():
            await ctx.send(f"Balance for {cape}: {i[1]}$. Income: {i[2]}$.")


@account.command(description="Use this to add your cape to the database and gain access to the other commands. Your cape name is your 'key'.", alias="create")
async def make(ctx,cape=None,amount=0,income=0):
    loc=ctx.message.guild.id
    authorized_channels=[478240151987027978,435874236297379861,537152965375688719,638118490628292612,691369881039536178,721141339567161415]
    authorized_guilds=[457290411698814980]
    if (ctx.message.channel.id not in authorized_channels and ctx.guild.id not in authorized_guilds):
        auth_channel=False
        for i in ctx.guild.channels:
            if i.id in authorized_channels:
                auth_channel=i.id
        if auth_channel:
            await ctx.send(f"BoK only operates in <#{auth_channel}>!")
        else:
            await ctx.send("This server is not configured to utilize the accounts system.")
        return
    if cape is None:
        await ctx.send("I do need a name for you if this is going to work.")
    entry=[]
    entry.append(cape.casefold())
    entry.append(int(amount))
    entry.append(int(income))
    if os.path.isfile(f"cash{loc}.txt"):
        with open(f"cash{loc}.txt",mode="r+") as f:
            accounts = json.load(f)
            if cape.casefold() in sum(accounts,[]):
                await ctx.send("Duplicate name.")
                return
            f.seek(0)
            f.truncate()
            accounts.append(entry)
            json.dump(accounts,f)
    else:
        with open(f"cash{loc}.txt",mode="w+") as f:
            accounts=[]
            f.seek(0)
            f.truncate()
            accounts.append(entry)
            json.dump(accounts,f)
    await ctx.send(f"Account opened for {cape}. Amount: {amount}$. Income: {income}$. Welcome to Bank of Kingfisher!")


@account.command(aliases=["u"], description="Keep track of expenses and gains with this.")
async def update(ctx,cape, amount):
    loc=ctx.message.guild.id
    authorized_channels=[478240151987027978,435874236297379861,537152965375688719,638118490628292612,691369881039536178,721141339567161415]
    authorized_guilds=[457290411698814980]
    if (ctx.message.channel.id not in authorized_channels and ctx.guild.id not in authorized_guilds):
        auth_channel=False
        for i in ctx.guild.channels:
            if i.id in authorized_channels:
                auth_channel=i.id
        if auth_channel:
            await ctx.send(f"BoK only operates in <#{auth_channel}>!")
        else:
            await ctx.send("This server is not configured to utilize the accounts system.")
        return
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    c1=False
    for i in accounts:
        if i[0]==cape.casefold():
            c1=i
    if c1 is False:
        await ctx.send(f"Cannot find {cape}.")
    for i in accounts:
        if i[0]==cape.casefold():
            i[1]=i[1]+int(amount)
            await ctx.send(f"New balance for {cape}: {i[1]}$")
    with open(f"cash{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(accounts,f)


@account.command(aliases=["s"], description="Send money to another account.")
async def send(ctx,cape,target, amount):
    loc=ctx.message.guild.id
    authorized_channels=[478240151987027978,435874236297379861,537152965375688719,638118490628292612,691369881039536178,721141339567161415]
    authorized_guilds=[457290411698814980]
    if (ctx.message.channel.id not in authorized_channels and ctx.guild.id not in authorized_guilds):
        auth_channel=False
        for i in ctx.guild.channels:
            if i.id in authorized_channels:
                auth_channel=i.id
        if auth_channel:
            await ctx.send(f"BoK only operates in <#{auth_channel}>!")
        else:
            await ctx.send("This server is not configured to utilize the accounts system.")
        return
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    c1=False
    c2=False
    for i in accounts:
        if i[0]==cape.casefold():
            c1=i
        if i[0]==target.casefold():
            c2=i
    if c1 is False:
        await ctx.send(f"Cannot find sender {cape}.")
    if c2 is False:
        await ctx.send(f"Cannot find receiver {target}.")
    for i in accounts:
        if i[0]==cape.casefold():
            i[1]=i[1]+int(amount)*-1
            await ctx.send(f"New balance for {cape}: {i[1]}$")
        if i[0]==target.casefold():
            i[1]=i[1]+int(amount)
            await ctx.send(f"New balance for {target}: {i[1]}$")
    with open(f"cash{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(accounts,f)


@account.command(aliases=["i"], description="Adjust your periodic income here. Use the weekly amount.")
async def income(ctx,cape, amount):
    loc=ctx.message.guild.id
    authorized_channels=[478240151987027978,435874236297379861,537152965375688719,638118490628292612,691369881039536178,721141339567161415]
    authorized_guilds=[457290411698814980]
    if (ctx.message.channel.id not in authorized_channels and ctx.guild.id not in authorized_guilds):
        auth_channel=False
        for i in ctx.guild.channels:
            if i.id in authorized_channels:
                auth_channel=i.id
        if auth_channel:
            await ctx.send(f"BoK only operates in <#{auth_channel}>!")
        else:
            await ctx.send("This server is not configured to utilize the accounts system.")
        return
    with open(f"cash{loc}.txt") as f:
        accounts = json.load(f)
    c1=False
    for i in accounts:
        if i[0]==cape.casefold():
            c1=i
    if c1 is False:
        await ctx.send(f"Cannot find {cape}.")
    for i in accounts:
        if i[0]==cape.casefold():
            i[2]=i[2]+int(amount)
            await ctx.send(f"New income for {cape}: {i[2]}$")
    with open(f"cash{loc}.txt",mode="r+") as f:
        f.seek(0)
        f.truncate()
        json.dump(accounts,f)


async def account_decay():
    await asyncio.sleep(60*1) #make sure the bot is initialized - this can be fixed better.
    while True:

        locs=[465651565089259521,457290411698814980,] #testing 434729592352276480
        #The servers that money decay and income is enabled for.
        #Currently Grand Haven 465651565089259521 and WD LA 457290411698814980
        # duskhaven 691221976311660595

        decay=0.9**(1/7) #10% decay per week
        GH_channel = bot.get_channel(478240151987027978) #GH facacs # channel ID goes here
        LA_channel = bot.get_channel(457640092240969730) #la battle-ooc
        MF_channel = bot.get_channel(691369881039536178) #MF imperial-bank-of-dusthaven
        #test_channel=bot.get_channel(435874236297379861) #nest test-dev

        last_updated=[]
        for loc in locs:
            print(loc)
            if os.path.isfile(f"decay{loc}.txt"):
                print(f"decay{loc}.txt checked and exists")
                with open(f"decay{loc}.txt",mode="r+") as f:
                    last_updated = json.load(f)
                    if last_updated[0]-time.time()<-60*60*24: #runs every day
                        print("decaying...")
                        if os.path.isfile(f"cash{loc}.txt"):
                            print("Cash file exists")
                            with open(f"cash{loc}.txt",mode="r+") as g:
                                accounts = json.load(g)
                                g.seek(0)
                                g.truncate()
                                wealth=0
                                for i in accounts:
                                    if loc==465651565089259521 or loc==434729592352276480:
                                        i[1]=round(i[1]*decay)
                                    if loc==691221976311660595 or loc==721135308497748048:
                                        i[1]=i[1]+(i[2])
                                    else:
                                        i[1]=i[1]+round((i[2]/7))
                                    wealth+=i[1]
                                json.dump(accounts,g)

                            print("Daily wealth message block reached")
                            if loc==465651565089259521:
                                print("printing Daily wealth message")
                                await GH_channel.send(f"Daily Expenses computed. Total accrued wealth: {wealth}$")
                            if loc==457290411698814980:
                                await LA_channel.send(f"Daily Expenses computed. Total accrued wealth: {wealth}$")
                            if loc==691221976311660595:
                                await MF_channel.send(f"Daily Income computed.")
                            #if loc==434729592352276480:
                            #      print(test_channel)
                            #      await test_channel.send("henlo")
                            #      await test_channel.send(f"Daily Expenses computed. Total accrued wealth: {wealth}$")
                        else:
                            print(f"No accounts on file for {loc}.")
                        f.seek(0)
                        f.truncate()
                        last_updated=[]
                        last_updated.append(time.time())
                        json.dump(last_updated,f)
            else:
                with open(f"decay{loc}.txt",mode="w+") as f:
                    print("No decay file.")
                    f.seek(0)
                    f.truncate()
                    last_updated=[]
                    last_updated.append(time.time())
                    json.dump(last_updated,f)
        await asyncio.sleep(60*60*3) # task runs every 3 hours


async def rank_decay():
    await asyncio.sleep(60*1) #make sure the bot is initialized - this can be fixed better.
    c= 60 # c = 60, assuming a rating decay period of a month, and a typical rating of 150
    # c is the result of 350=sqroot(typical rating**2+rating decay period*c)
    loc=465651565089259521
    #gh loc="465651565089259521"
    #vanwiki loc="434729592352276480"
    channel = bot.get_channel(478240151987027978) # channel ID goes here
    #GH 478240151987027978 facacs
    #vanwiki 435874236297379861 testing
    last_updated=[]
    while True:
        if os.path.isfile(f"glicko_decay{loc}.txt"):
            with open(f"glicko_decay{loc}.txt",mode="r+") as f:
                last_updated = json.load(f)
                if last_updated[0]-time.time()<-60*60*24:
                    if os.path.isfile(f"glicko{loc}.txt"):
                        with open(f"glicko{loc}.txt",mode="r+") as g:
                            ranks = json.load(g)
                            g.seek(0)
                            g.truncate()
                            avg_rank=0
                            avg_rd=0
                            for i in ranks:
                                if i[2]>150:
                                    i[2]=min(round(math.sqrt(i[2]**2+(c/2)**2),2),350)
                                else:
                                    i[2]=min(round(math.sqrt(i[2]**2+(c/3)**2),2),350)
                                avg_rank+=i[1]
                                avg_rd+=i[2]
                            json.dump(ranks,g)
                        await channel.send(f"Daily RD decay computed. Average Rating: {round(avg_rank/len(ranks),0)} Average RD: {round(avg_rd/len(ranks),0)}")
                    else:
                        channel.send("No ranks existing!")
                    f.seek(0)
                    f.truncate()
                    last_updated=[]
                    last_updated.append(time.time())
                    json.dump(last_updated,f)
        else:
            with open(f"glicko_decay{loc}.txt",mode="w+") as f:
                f.seek(0)
                f.truncate()
                last_updated=[]
                last_updated.append(time.time())
                json.dump(last_updated,f)
        await asyncio.sleep(60*60*3) # task runs every 3 hours


###Bot runs here
schedstop = threading.Event()


def timer():
    while not schedstop.is_set():
        sPlanner.run(blocking=False)
        time.sleep(1)


schedthread = threading.Thread(target=timer)
schedthread.start()
with open("Token.txt", 'r') as f:
        token=f.read()
yaml=YAML()
yaml.default_flow_style=False
bot.run(token)
