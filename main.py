import asyncio
import datetime
import json
import os
import logging
import platform
import time
import sqlite3
import sys
import traceback
from sqlite3.dbapi2 import Cursor
from discord import channel, message
from discord.enums import MessageType
import embed as embed
from discord.utils import get
import discord
import requests
from colorama import init
from discord.ext import commands
from discord.ext.tasks import loop
from termcolor import colored
from discord.ext.commands import bot
from datetime import date, timedelta
from datetime import date
machine = platform.node()
init()

import embed as EMBEDS  # Capitals for global
import embed

# TODO
# Database correction

logger = embed.Logger("kourage-attendance")


intents = discord.Intents.default()
intents.members = True

# FOR PRODUCTION
bot = commands.Bot(command_prefix="~", intents=intents)

async def member_loader():
    member_list = []
    guild = bot.get_guild("add koder id") # Koders's guild id 534406455709663233
    role = discord.utils.get(guild.roles, name="Koders")
    for member in guild.members:
        if role in member.roles:
            member_list.append(member.id)
    return member_list

@bot.event
async def on_ready():  # triggers when bot is ready
    db = sqlite3.connect('ATTENDANCE.sqlite')
    cursor = db.cursor()
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attendance_table(
            DATE TEXT,
            SHIFT TEXT,
            PRESENTEES TEXT,
            ABSENTEES TEXT
            )
        ''')
        db.commit()
        logger.warning("checking integrity of attendance db")
        
    except Exception as err:
        logger.error("exception caught at creating attendance db action: " + err.__class__ + " " + str(err))
        return

# helper functions
def check(reaction, user):
    return str(reaction.emoji) == '⬆️' and user.bot is not True

async def take_reaction(msg, shift_status, timeout=1200.0, presentees=[]):
    shift_status=shift_status
    start = time.time()
    try:
        result = await bot.wait_for('reaction_add', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await msg.delete()

        # TODO
        # CTX for absent showing on attendance channel
        ctx = bot.get_channel(os.environ.get("ADMIN_CHANNEL_ID")) # Channel id goes here

        # Database entry
        today=datetime.date.today()
        date=str(today.strftime("%Y-%m-%d"))
        presentees = set(presentees)
        if not presentees: 
            presentees.add("NULL")
        members = set(await member_loader())
        absentees = members - presentees

        conn = sqlite3.connect('ATTENDANCE.sqlite')
        cur = conn.cursor()
        try:
          cur.execute('''INSERT INTO Attendance_table(DATE, SHIFT, PRESENTEES, ABSENTEES) VALUES (?, ?, ?, ?)''', (date,shift_status,str(presentees).replace("'",""),str(absentees).replace("'","")))
          conn.commit()
          logger.warning("Attendance added to db. \nPresentees - " + str(presentees)  + "\nAbsentees - "+str(absentees))
          embed=await show_absentees(date, shift_status, absentees)
          await ctx.send(embed=embed, delete_after=120)
          logger.info("absentees shown")
        except Exception as err:
            logger.error(str(err.__class__) + " " + str(err))

   # TODO - What to do with this else part?
    else:
     reaction, user = result
     channel = await user.create_dm()
     
     date_time = datetime.datetime.now()
     embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))
     await channel.send(embed=embed)

     end = time.time()
     timeout = timeout - (end - start)
     logger.info(str(user.id) + '/' + user.name + ' reacted to attendance.')

     presentees.append(user.id)
     await take_reaction(msg, shift_status=shift_status, timeout=timeout, presentees=presentees)


async def take_attendance(channel, start_time, end_time):
    # TODO ctx = bot.get_channel() # channel id goes here
    logger.info("function take attendance called")
    if(type(start_time)==datetime.datetime): 
        if start_time.hour>15: 
             shift_status="E"
        elif start_time.hour<15: 
             shift_status="M"  
        start_time =str(start_time.strftime(r"%I:%M"))
        end_time = str(end_time.strftime(r"%I:%M")) 
    logger.warning("sending attendance")
    embed = embed.attendance(start_time,end_time)
    msg = await channel.send(embed=embed)
    await msg.add_reaction(emoji="⬆️")
  
    

    if start_time == "11:00" and end_time == "11:20":
        shift_status="M"
    elif start_time == "15:00" and end_time == "15:20":
        shift_status="E"
    else: 
        shift_status=shift_status

    try:
        await take_reaction(msg, shift_status)
    except Exception as err:
        logger.error("exception caught at taking attendance" + str(err))
        return
    logger.info("function take attendance executed successfully")

# TODO - Add kore properities
@bot.command()
async def manual_fire(ctx):
    logger.info("function manual fire called by " + str(ctx.author.name))

    start_time = datetime.datetime.now()
    timestamp = datetime.datetime.now()
    end_time = timestamp + datetime.timedelta(minutes = 20)
    channel = bot.get_channel(ctx.channel.id)
    embed = await take_attendance(channel, start_time, end_time)
    
    try:
       msg = await ctx.send(embed=embed)
       await msg.add_reaction(emoji="⬆️")
    except Exception as err:
        logger.error("exception caught at manual fire" + str(err))
    logger.info("function manual fire executed successfully.")

async def show_absentees(date, shift_status, absentees):
    logger.info("function show_absentees called.")

    if shift_status == "M":
        message = "Morning"
    elif shift_status == "E":
        message = "Evening"

    message=""
    for absentee in absentees:
        username = await bot.fetch_user(absentee)
        message += str(username)+"\n"

    embed=embed.simple_embed(title="Absent Users on :"+str(date)+"\nShift: "+message,description="")
    embed.add_field(name='Users list:', value=message+"\n\n\n", inline=False)
    logger.info("List of absentees has been sent to the channel")

    return embed

@bot.command()  #TODO: add koders kore property
async def leaves(ctx, *args):
   
     if str(ctx.author.roles[2]) != "Koders" and args:
        not_access_embed=discord.Embed(title="Sorry You dont have access to view others leaves!",description="",colour=0x11806a)
        await ctx.send(embed=not_access_embed,delete_after=60)
        logger.warning(str(ctx.author.id)+" dont have access")
        return

     start_date, end_date = await embed.data_input(ctx,bot)

    # TODO - set index accordingly to roles only
    # TODO - koders needs to be changed to Kore

     if not args: #check all attendances
        if str(ctx.author.roles[2]) == "Koders":
          users=await member_loader() 
          await embed.leave_and_attendance(ctx, bot, start_date, end_date, users, 1)

        elif str(ctx.author.roles[2]) != "Koders":
          await embed.leave_and_attendance(ctx, bot, start_date, end_date, ctx.author.id, 1)
     else:
        users = []
        for arg in args:
            arg:discord.Member
            users.append(str(arg.strip("!@<>")))
        
        await embed.leave_and_attendance(ctx, bot, start_date, end_date, users, 1)

# Attendance Leave Info
@bot.command()   #TODO: add koders kore property
async def attendance(ctx, *args):
     
     if str(ctx.author.roles[2]) != "Koders" and args:
        not_access_embed=discord.Embed(title="Sorry You dont have access to view others leaves!",description="",colour=0x11806a)
        await ctx.send(embed=not_access_embed,delete_after=60)
        logger.warning(str(ctx.author.id)+" dont have access")
        return

     start_date, end_date = await embed.data_input(ctx,bot)

    # TODO - set index accordingly to roles only
    # TODO - koders needs to be changed to Kore

     if not args: #check all attendances
        if str(ctx.author.roles[2]) == "Koders":
         users=await member_loader()
         
         await embed.leave_and_attendance(ctx, bot, start_date, end_date, users, 2)

        elif str(ctx.author.roles[2]) != "Koders":
         await embed.leave_and_attendance(ctx, bot, start_date, end_date, ctx.author.id, 2)
     else:
        users = []
        for arg in args:
           arg:discord.Member
           users.append(str(arg.strip("!@<>")))
        await embed.leave_and_attendance(ctx, bot, start_date, end_date, users, 2)

#manual mark specific
@bot.command()
async def mark_attendance(ctx):
    logger.info("Mark attendance function called")
    
    check_opening_time=datetime.datetime.now()
    conn = sqlite3.connect('ATTENDANCE.sqlite')
    cur = conn.cursor()
    today=datetime.date.today()
    current_date = today.strftime("%Y-%m-%d")
    #TODO change time in prodcution
    if check_opening_time.hour < 15 and check_opening_time.hour >=11:
        shift_status="M"
    elif check_opening_time.hour <= 19 and check_opening_time.hour >= 15: 
        shift_status="E"     

    try:
        cur.execute('''SELECT PRESENTEES,ABSENTEES FROM Attendance_table WHERE DATE = ? AND SHIFT = ?''', [current_date,shift_status])
        users = (cur.fetchone())
        
    except Exception as err:
        logger.error("error fetching detail " + str(err))
 
    if(str(users)=="None"): 
        logger.error("No content found")
    elif(str(users[1])=="{No Absentees}"): 
        logger.error("No Absentees found")
        no_absentees_embed=discord.Embed(title="No Absentees found on Date: "+str(current_date),description="",colour=0x11806a)
        await ctx.send(embed=no_absentees_embed,delete_after=20)
    else:
     presentees=set(users[0][1:-1].split(', '))
     absentees=set(users[1][1:-1].split(', '))
     absentees_dict =dict() 
     absentees_string=""
     idx=1
       
     for absentee in absentees:
        
        absentees_dict[idx]=absentee
        absentees_string += str(idx)+" - "+ str(await bot.fetch_user(int(absentee))) + "\n"
        idx +=1
        
     user_list_embed = EMBEDS.simple_embed('Absentees list for Date: '+current_date, 'Choose the numbers(space seperated) corresponding to the users to mark attendance.' + '\n\n' + absentees_string)
     sent = await ctx.send(embed = user_list_embed)
     user_list = await EMBEDS.ctx_input(ctx, bot, sent)
     if not user_list:
        logger.error('User list timed out.')
        return
     user_list = list(map(int, user_list.split()))
     for i in user_list:
        if i < 1 or i >= idx:
            logger.error('Invalid index ' + str(i))
            return

     for i in user_list:
        presentees.add((absentees_dict[i]))
        user=await bot.fetch_user(int(absentees_dict[i]))
        channel = await user.create_dm()
        date_time = datetime.datetime.now()
        embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))
        embed.add_field(name='(M-morning shift , E-evening shift)', value ="Your attendance marked for: "+str(shift_status), inline=False)
        await channel.send(embed=embed)
        embed.add_field(name='Username', value =user, inline=False)
        await ctx.send(embed=embed,delete_after=30)
        
        absentees.remove(absentees_dict[i])
        logger.info("dm sent to "+str(user))
        
     try:
       if not absentees: 
           absentees.add("No Absentees")
       cur.execute('''UPDATE Attendance_table SET PRESENTEES = ? , ABSENTEES = ? WHERE DATE = ? AND SHIFT = ?''', [str(presentees).replace("'",""),str(absentees).replace("'",""), current_date,shift_status ]) 
       conn.commit()
       logger.warning("changes made to db")
     except Exception as err:
      logger.error(err.__class__ + " " + str(err))
    
@loop(minutes=1)
async def attendance_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(859680300783370252)  # TODO  - Add koders' channel id
    working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    date_time = datetime.datetime.now()
    for working_day in working_days:
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "11:00":
            logger.info("Ran morning attendance.")
            await take_attendance(channel, "11:00", "11:20")
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "15:00":
            logger.info("Ran post lunch attendance.")
            await take_attendance(channel, "15:00", "15:20")
    logger.info("Waiting for tasks...")
           
if __name__ == "__main__":
    try:
        
        attendance_task.start()
        bot.run(os.environ.get("TOKEN"))
        
    except Exception as _e:
        logging.warning("Exception found at main worker. Reason: " + str(_e), exc_info=True)
