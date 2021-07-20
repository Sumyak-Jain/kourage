import asyncio
import datetime
import json

# Logging format
import logging
import platform
import time
import sqlite3
import sys
import traceback
from sqlite3.dbapi2 import Cursor
from discord import channel, message
from discord.enums import MessageType

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

logger = embed.Logger("kourage-attendance")

intents = discord.Intents.default()
intents.members = True

# TODO
# CHANGE DB NAME TO ATTENDANCE

# FOR PRODUCTION
bot = commands.Bot(command_prefix="~", intents=intents)

async def member_loader():
    member_list = []
    guild = bot.get_guild(850274364556705812)
    role = discord.utils.get(guild.roles, name="Koders")
    for member in guild.members:
        if role in member.roles:
            member_list.append(member.id)
    return member_list

@bot.event
async def on_ready():  # Triggers when bot is ready
    #logger.warning("Kourage is running at version {0}".format(CONFIG.VERSION))
    db = sqlite3.connect('Attendance_DB.sqlite')
    cursor = db.cursor()

    # TODO
    # Create attendance db, if not present
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
    except Exception as err:
        logger.error("'~on_ready': " + err.__class__ + " " + str(err))
        return
    logger.info("kourage-attendance is running at version 0.1.0")

# Attendance System
def check(reaction, user):
    return str(reaction.emoji) == '⬆️' and user.bot is not True

async def take_reaction(msg, shift_status, timeout=30.0, presentees=[]):
    shift_status=shift_status
    start = time.time()
    try:
        result = await bot.wait_for('reaction_add', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await msg.delete() # For deleting the attendance embed

        # Database entry
        today=datetime.date.today()
        date=str(today.strftime("%Y-%m-%d"))
        presentees = set(presentees)
        all_member=set(await member_loader())
        absentees = all_member - presentees

        conn = sqlite3.connect('Attendance_DB.sqlite')
        cur = conn.cursor()

        try:
          cur.execute('''INSERT INTO Attendance_table(DATE, SHIFT, PRESENTEES, ABSENTEES) VALUES (?, ?, ?, ?)''', (date,shift_status,str(presentees),str(absentees)))
          conn.commit()
          logger.info("Attendance marked. \nPresentees - " + str(presentees)  + "\nAbsentees - "+str(absentees))
          leave_embed=await show_absentees(date, shift_status, absentees)
          await ctx.send(embed = leave_embed,delete_after=20)
          logger.info("Absentees shown")
        except Exception as err:
            logger.error(str(err.__class__) + " " + str(err))

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

@bot.command()
async def take_attendance(ctx, shit_status):
    # ctx = bot.get_channel() # channel id goes here
    logger.info("'take_attendance_morning' called.")

    if shift_status == "M":
        start = "11:00"
        end = "11:20"
    elif shift_status == "E":
        start = "15:00"
        end = "15:20"

    embed = EMBEDS.attendance(start, end)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji="⬆️")
    try:
        await take_reaction(msg,shift_status)
    except Exception as err:
        logger.error("'take_attendance_morning': " + str(err))
        return
    logger.info("'take_attendance_morning' executed successfully")

# TODO
# Add permissions of only to be used by Kore role
@bot.command()
async def manual_fire(ctx):
    logger.info("'manual_fire' called by " + str(ctx.author.name))

    timestamp = datetime.datetime.now()
    delta=timestamp + datetime.timedelta(minutes = 20)
    check_opening_time=datetime.datetime.now()

    if check_opening_time.hour < 15:
        shift_status="M"
    elif check_opening_time.hour > 15:
        shift_status="E"

    opening_time=str(timestamp.strftime(r"%I:%M %p"))
    ending_time=str(delta.strftime(r"%I:%M %p"))
    embed = EMBEDS.attendance(opening_time, ending_time)
    msg = await ctx.send(embed=embed,delete_after=20)
    await msg.add_reaction(emoji="⬆️")
    try:
        await take_reaction(msg,shift_status)
    except Exception as err:
        logger.error("'manual_fire': " + err)
        return
    logger.info("'manual_fire' executed successfully.")

async def show_absentees(date, shift_status, absentees):
    logger.info("function show_absentees called.")

    message = None
    if shift_status == "M":
        message = "Morning"
    elif shift_status == "E":
        message = "Evening"

    leave_embed=embed.simple_embed(title="Absent Users on :"+str(date)+"\nShift: "+message,description="")
    leave_list=""

    for i in absentees:
        username =await bot.fetch_user(i)
        leave_list = leave_list+str(username)+"\n"
    print(leave_list)
    leave_embed.add_field(name='Users list:', value =leave_list+"\n\n\n", inline=False)
    logger.info("List of absentees has been sent to the channel")

    return leave_embed

# TODO
# Add admin perms in production
# Manual marking of attendance
@bot.command()
async def mark(ctx, *,user: discord.Member):
    logger.info("'mark_morning' called.")

    check_opening_time=datetime.datetime.now()
    if check_opening_time.hour < 11 and check_opening_time.hour >=19:
        conn = sqlite3.connect('Attendance_DB.sqlite')
        cur = conn.cursor()

        today=datetime.date.today()
        current_date = today.strftime("%Y-%m-%d")

        if check_opening_time.hour > 11 and check_opening_time.hour < 15:
            shift_status = "M":
        elif check_opening_time.hour > 15 and check_opening_time.hour < 19:
            shift_status = "E":

        try:
          cur.execute('''SELECT PRESENTEES, ABSENTEES FROM Attendance_DB WHERE SHIFT = ? AND Date = ?''', [shift_status, current_date])
          status = str(cur.fetchone())
        except Exception as err:
          logger.error(err.__class__ + " " + str(err))

          channel = await user.create_dm()
          date_time = datetime.datetime.now()
          embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))

          if shift_status == "M":
              value = "Morning"
          elif shift_status == "E":
              value = "Evening"
          embed.add_field(name='Attendance marked for:', value=value+"\n\n\n", inline=False)
          await channel.send(embed=embed)
        else:
          else_embed=discord.Embed(title="Sorry attendance already marked",description="",colour=0x11806a)
          end=await ctx.send(embed=else_embed,delete_after=60)
          logger.warning(str(user.id)+" already marked")
    else:
        else_embed=discord.Embed(title="Sorry time limit reached",description="",colour=0x11806a)
        end=await ctx.send(embed=else_embed,delete_after=60)
        logger.warning(str(user.id)+" time limit reached")

# check all user leaves
@bot.command()
#@commands.has_any_role("@Kore")
async def check_leaves(ctx):
    logger.info("Check leaves function called")
    start_date_embed=discord.Embed(title="Enter start date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
    start=await ctx.send(embed=start_date_embed,delete_after=60)
    start_date1 = await embed.ctx_input(ctx, bot, start)
    if not start_date1:
        return

    end_date_embed=discord.Embed(title="Enter end date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
    end=await ctx.send(embed=end_date_embed,delete_after=60)
    end_date1 = await embed.ctx_input(ctx, bot, end)
    if not end_date1:
        return

    start_date = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date1, '%Y-%m-%d')

    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    leave_Embed=embed.simple_embed(title="Absent Users\n",description="")

    for single_date in daterange(start_date, end_date):
        dates=str(single_date.strftime("%Y-%m-%d"))
        full_leave_list=""
        full_leave_list=full_leave_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n\n"

        morning_leave_list=""
        morning_leave_list=morning_leave_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n\n"

        evening_leave_list=""
        evening_leave_list=evening_leave_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n\n"

        # PUT ABSENTEES
        username = await bot.fetch_user(user_id)
        full_leave_list=full_leave_list+str(username)+"\n"

        leave_Embed.add_field(name='Users absent full day:', value = full_leave_list+"\n\n\n", inline=False)


        #half leave
        half_leave_list=[]
        try:
            cur.execute('''SELECT DISTINCT Users_DB_Attendance.User_ID FROM Users_DB_Attendance WHERE (SELECT Attendance_DB.User_ID   FROM Attendance_DB WHERE Users_DB_Attendance.User_ID=Attendance_DB.User_ID AND Attendance_DB.Date=? ) ''',[dates])
            half_absent = cur.fetchall()
        except Exception as err:
            logger.error(err.__class__ + " " + str(err))


        for i in half_absent:
            user_id=str(i)
            bad_chars = ['(', ')', ',', "'"]
            for i in bad_chars:
                user_id=user_id.replace(i, '')

            half_leave_list.append(user_id)

        for j in half_leave_list:
            full_day="ME"
            morning="M"
            evening="E"
            try:
                cur.execute('''SELECT SHIFT Attendance_DB WHERE  Attendance_DB.User_ID= ? AND Attendance_DB.Date=?''',[j,dates])
                leave=str(cur.fetchone())
            except Exception as err:
                logger.error(err.__class__ + " " + str(err))

            bad_chars = ['(', ')', ',', "'"]
            for i in bad_chars:
                leave=leave.replace(i, '')

            if (leave.count(full_day)>0):
                logger.info("present full day")
            elif(leave.count(morning)==0):
                username = await bot.fetch_user(j)
                morning_leave_list=morning_leave_list+str(username)+"\n"
            elif(leave.count(evening)==0):
                username = await bot.fetch_user(j)
                evening_leave_list=evening_leave_list+str(username)+"\n"

        leave_Embed.add_field(name='User absent in 1st half(Morning):', value = morning_leave_list+"\n\n\n", inline=False)
        leave_Embed.add_field(name='User absent in 2nd half(Evening):', value = evening_leave_list+"\n\n\n", inline=False)

    await ctx.send(embed=leave_Embed,delete_after=60)
    logger.warning("full leaves sent")
#Specific user leave
@bot.command()
async def specific_leaves(ctx, *,user: discord.Member):
    logger.info("specific leaves function called")
    user_author = ctx.author.id
    check_user = user.id
    check_username=ctx.author.name
    author_role = ctx.author.roles
    #print(author_role)

    if user_author == check_user:
        start_date_embed=discord.Embed(title="Enter start date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
        start=await ctx.send(embed=start_date_embed,delete_after=60)
        start_date1 = await embed.ctx_input(ctx, bot, start)
        if not start_date1:
            logger.error("'start_date' timed out.")
            return

        end_date_embed=discord.Embed(title="Enter end date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
        end=await ctx.send(embed=end_date_embed,delete_after=60)
        end_date1 = await embed.ctx_input(ctx, bot, end)
        if not end_date1:
            logger.error("'end_date' timed out.")
            return

        start_date = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date1, '%Y-%m-%d')
        leaves=embed.show_leaves(start_date,end_date,check_user,check_username)
        await ctx.send(embed=leaves, delete_after = 80)
        logger.warning(str(check_username)+" leaves shown")

    if user_author != check_user:
        role=""
        for i in author_role:
            if str(i)=="kore":
                role=str(i)
                break;
            else:
                role="not admin"

        if role=="kore":

            start_date_embed=discord.Embed(title="Enter start date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
            start=await ctx.send(embed=start_date_embed,delete_after=60)
            start_date1 = await embed.ctx_input(ctx, bot, start)
            if not start_date1:
                logger.error("'start_date1' timed out.")
                return

            end_date_embed=discord.Embed(title="Enter end date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
            end=await ctx.send(embed=end_date_embed,delete_after=60)
            end_date1 = await embed.ctx_input(ctx, bot, end)
            if not end_date1:
                logger.error("'end_date1' timed out.")
                return

            start_date = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date1, '%Y-%m-%d')
            leaves=embed.show_leaves(start_date,end_date,check_user,check_username)
            await ctx.send(embed=leaves, delete_after = 80)
            logger.warning(str(check_username)+" leaves shown")

        else:
            end_date_embed=discord.Embed(title="Sorry You dont have access to view others leaves!",description="",colour=0x11806a)
            end=await ctx.send(embed=end_date_embed,delete_after=60)
            logger.warning(str(user_author)+" dont have access")


# Attendance Leave Info
@bot.command()
async def check_attendance(ctx, *,user: discord.Member):
    logger.info("check attendance called")
    user_author = ctx.author.id
    check_user = user.id
    check_username=ctx.author.name
    author_role = ctx.author.roles
    #print(author_role)

    if user_author == check_user:
        start_date_embed=discord.Embed(title="Enter start date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
        start=await ctx.send(embed=start_date_embed,delete_after=60)
        start_date1 = await embed.ctx_input(ctx, bot, start)
        if not start_date1:
            logger.error("'start_date1' timed out.")
            return

        end_date_embed=discord.Embed(title="Enter end date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
        end=await ctx.send(embed=end_date_embed,delete_after=60)
        end_date1 = await embed.ctx_input(ctx, bot, end)
        if not end_date1:
            logger.error("'end_date1' timed out.")
            return

        start_date = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date1, '%Y-%m-%d')
        attendance,save_filename=embed.show_attendance(start_date,end_date,check_user,check_username)
        await ctx.send(embed=attendance,file=discord.File(save_filename), delete_after = 80)
        logger.warning(str(check_username)+" Attendace shown")

    if user_author != check_user:
        role=""
        for i in author_role:
            if str(i)=="kore":
                role=str(i)
                break;
            else:
                role="not admin"


        if role=="kore":
            start_date_embed=discord.Embed(title="Enter start date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
            start=await ctx.send(embed=start_date_embed,delete_after=60)
            start_date1 = await embed.ctx_input(ctx, bot, start)
            if not start_date1:
                logger.error("'start_date1' timed out.")
                return

            end_date_embed=discord.Embed(title="Enter end date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
            end=await ctx.send(embed=end_date_embed,delete_after=60)
            end_date1 = await embed.ctx_input(ctx, bot, end)
            if not end_date1:
                logger.error("'end_date1' timed out.")
                return

            start_date = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date1, '%Y-%m-%d')
            attendance=embed.show_attendance(start_date,end_date,check_user,check_username)
            await ctx.send(embed=attendance, delete_after = 80)
            logger.warning(str(check_username)+" Attendace shown")
        else:
            end_date_embed=discord.Embed(title="Sorry You dont have access to view others attendance!",description="",colour=0x11806a)
            end=await ctx.send(embed=end_date_embed,delete_after=60)
            logger.warning(str(user_author)+" dont have access")

@loop(minutes=1)
async def attendance_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(859680300783370252)  # attendance channel id
    working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    date_time = datetime.datetime.now()
    for working_day in working_days:
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "11:00":
            logger.info("Ran morning attendance.")
            await take_attendance_morning(channel)
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "15:00":
            logger.info("Ran post lunch attendance.")
            await take_attendance_lunch(channel)
    logger.info("Waiting for tasks...")

if __name__ == "__main__":
    try:
        attendance_task.start()
        bot.run("")
    except Exception as _e:
        logging.warning("Exception found at main worker. Reason: " + str(_e), exc_info=True)
