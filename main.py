import asyncio
import datetime
import os
import logging
import platform
import time
import sqlite3
from sqlite3.dbapi2 import Cursor
from discord import channel, message
from discord.enums import MessageType
from discord.utils import get
import discord
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

logger = embed.Logger("kourage Attendance")

intents = discord.Intents.default()
intents.members = True

# FOR PRODUCTION
bot = commands.Bot(command_prefix="~", intents=intents)

@bot.event
async def on_ready():  # Triggers when bot is ready
   # logger.warning("Kourage is running at version {0}".format(CONFIG.VERSION))
    db = sqlite3.connect('Attendance_DB.sqlite')
    cursor = db.cursor()
    # Users Attendance_DB for Attendance

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users_DB_Attendance(
            User_ID TEXT
            )
        ''')
        db.commit()
    except Exception as err:
        logger.error("'~on_ready': " + err.__class__ + " " + str(err))
        return

    logger.info("Users_DB_Attendance table created")
    # Attendance Attendance_DB
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attendance_DB(
            User_ID TEXT,
            Date TEXT,
            Time TEXT
            )
        ''')
        db.commit()
    except Exception as err:
        logger.error("'~on_ready': " + err.__class__ + " " + str(err))
        return

    logger.info("Attendance_DB table made")
    logger.info("kourage Attendance bot is running at version 0.1.0")

'''
@bot.event
async def on_member_join(member):  # Triggers when members joins the server
    #await member.send('Thank you for joining Koders') # Have an embed there
    role = get(member.guild.roles, id=850274364556705815)
    await member.add_roles(role)
'''

# Attendance System
def check(reaction, user):
    return str(reaction.emoji) == '⬆️' and user.bot is not True


async def take_reaction(ctx,shift_status, timeout=1200.0):
    logger.info("'~take_reaction' called.")

    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()

    shift_status=shift_status
    start = time.time()
    try:
        result = await bot.wait_for('reaction_add', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        await ctx.delete()
    else:
     reaction, user = result
     channel = await user.create_dm()
     date_time = datetime.datetime.now()
     embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))
     await channel.send(embed=embed)

     end = time.time()
     timeout = timeout - (end - start)
     logger.info(str(user.id) + '/' + user.name + ' reacted.')
     today = datetime.date.today()
     today=datetime.date.today()
     date=str(today.strftime("%Y-%m-%d"))

     try:
        cur.execute('''SELECT Time FROM Attendance_DB WHERE User_ID = ? AND Date = ?''', [str(user.id), date])
        status = str(cur.fetchone())
     except Exception as err:
        logger.error(err.__class__ + " " + str(err))

     bad_chars = ['(', ')', ',', "'"]
     for j in bad_chars:
        status=status.replace(j, '')

     if status=="None":
        try:
            cur.execute('''INSERT INTO Attendance_DB(User_ID, Date, Time) VALUES (?, ?, ?)''', (str(user.id),date,shift_status))
            conn.commit()
            logger.info(str(user) + ", "+str(shift_status)+" - attendance marked")
        except Exception as err:
            logger.error(err.__class__ + " " + str(err))

     else:
        status = status + shift_status
        status = str(status)
        try:
            cur.execute('''UPDATE Attendance_DB SET Time = ? WHERE User_ID = ? AND Date = ?''', [status, str(user.id),date ])
            conn.commit()
            logger.info(str(user)+", "+str(shift_status)+" - attendance updated")
        except Exception as err:
            logger.error(err.__class__ + " " + str(err))

     await take_reaction(ctx,shift_status=shift_status, timeout=timeout)

#@bot.command()
async def take_attendance_morning(ctx):
    logger.info("'take_attendance_morning' called.")

    embed = EMBEDS.attendance("11:00", "11:20")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji="⬆️")
    shift_status="M"
    try:
        await take_reaction(msg,shift_status)
    except Exception as err:
        logger.error("'take_attendance_morning': " + err)
        return
    logger.info("'take_attendance_morning' executed successfully")

#@bot.command()
async def take_attendance_lunch(ctx):
    logger.info("'take_attendance_lunch' called.")

    embed = EMBEDS.attendance("3:00", "3:20")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji="⬆️")
    shift_status="E"
    try:
        await take_reaction(msg,shift_status)
    except Exception as err:
        logger.error("'take_attendance_lunch': " + err)
        return
    logger.info("'take_attendance_lunch' executed successfully")

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
    msg = await ctx.send(embed=embed)
    await msg.add_reaction(emoji="⬆️")
    try:
        await take_reaction(msg,shift_status)
    except Exception as err:
        logger.error("'manual_fire': " + err)
        return
    logger.info("'manual_fire' executed successfully.")

#@bot.command()
async def absentees_morning(ctx):
    logger.info("'~absentees_morning' called.")

    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()

    today=datetime.date.today()
    current_date = today.strftime("%Y-%m-%d")
    leave_Embed=embed.simple_embed(title="Absent Users on :"+str(current_date)+" morning",description="")
    
    try:
        cur.execute('''SELECT DISTINCT Users_DB_Attendance.User_ID FROM Users_DB_Attendance WHERE NOT EXISTS (SELECT Attendance_DB.User_ID FROM Attendance_DB WHERE Users_DB_Attendance.User_ID = Attendance_DB.User_ID AND Attendance_DB.Date = ?)''', [current_date])
    except Exception as err:
        logger.error(err.__class__ + " " + str(err))

    morning_absent = cur.fetchall()
    morning_leave_list=""
    
    for i in morning_absent:
        user_id=str(i)
        bad_chars = ['(', ')', ',', "'"]
        for i in bad_chars:
            user_id=user_id.replace(i, '')

        username = await bot.fetch_user(user_id)
        morning_leave_list=morning_leave_list+str(username)+"\n"

    leave_Embed.add_field(name='Users list:', value = morning_leave_list+"\n\n\n", inline=False)
    await ctx.send(embed = leave_Embed,delete_after=1200.0)
    logger.info("'absentees_morning' done successfully.")

#@bot.command()
async def absentees_evening(ctx):
    logger.info("'~absentees_evening' called successfully.")

    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()

    today=datetime.date.today()
    current_date = today.strftime("%Y-%m-%d")
    leave_Embed=embed.simple_embed(title="Absent Users on :"+str(current_date)+" evening",description="")
    try:
        cur.execute('''SELECT DISTINCT Users_DB_Attendance.User_ID FROM Users_DB_Attendance WHERE NOT EXISTS (SELECT Attendance_DB.User_ID FROM Attendance_DB WHERE Users_DB_Attendance.User_ID = Attendance_DB.User_ID AND Attendance_DB.Date = ?)''', [current_date])
    except Exception as err:
        logger.error(err.__class__ + " " + str(err))

    morning_absent = cur.fetchall()
    morning_leave_list=""
    evening_leave_list=""
    for i in morning_absent:
        user_id=str(i)
        bad_chars = ['(', ')', ',', "'"]
        for i in bad_chars:
            user_id=user_id.replace(i, '')

        username = await bot.fetch_user(user_id)
        morning_leave_list=morning_leave_list+str(username)+"\n"

    leave_Embed.add_field(name='Users list absent in morning and evening both :', value = morning_leave_list+"\n\n\n", inline=False)
   
    #evening
    half_leave_list=[]
    try:
        cur.execute('''SELECT DISTINCT Users_DB_Attendance.User_ID FROM Users_DB_Attendance WHERE (SELECT Attendance_DB.User_ID   FROM Attendance_DB WHERE Users_DB_Attendance.User_ID=Attendance_DB.User_ID AND Attendance_DB.Date=? ) ''',[current_date])
    except Exception as err:
        logger.error(err.__class__ + " " + str(err))

    half_absent = cur.fetchall()

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
                cur.execute('''SELECT Time FROM Attendance_DB WHERE  Attendance_DB.User_ID= ? AND Attendance_DB.Date=?''',[j,current_date])
                leave=str(cur.fetchone())
            except Exception as err:
                logger.error(err.__class__ + " " + str(err))

            bad_chars = ['(', ')', ',', "'"]
            for i in bad_chars:
                leave=leave.replace(i, '')

            if (leave.count(full_day)>0):
                logger.info("present full day")
            elif(leave.count(morning)==0):
                logger.info("present in morning")
            elif(leave.count(evening)==0):
                username = await bot.fetch_user(j)
                evening_leave_list=evening_leave_list+str(username)+"\n"

    leave_Embed.add_field(name='Users list absent in evening :', value = evening_leave_list+"\n\n\n", inline=False)
    await ctx.send(embed = leave_Embed,delete_after=1200.0)
    logger.info("'~absentees_evening' done successfully.")

#manual mark specific
@bot.command()
async def mark_morning(ctx, *,user: discord.Member):
    logger.info("'~mark_morning' called.")

    check_opening_time=datetime.datetime.now()
    if check_opening_time.hour < 15 and check_opening_time.hour >=11:
        conn = sqlite3.connect('Attendance_DB.sqlite')
        cur = conn.cursor()

        today=datetime.date.today()
        current_date = today.strftime("%Y-%m-%d")

        shift_status="M"
        today=datetime.date.today()
        date=str(today.strftime("%Y-%m-%d"))

        try:
          cur.execute('''SELECT Time FROM Attendance_DB WHERE User_ID = ? AND Date = ?''', [str(user.id), current_date])
          status = str(cur.fetchone())
        except Exception as err:
          logger.error(err.__class__ + " " + str(err))

        bad_chars = ['(', ')', ',', "'"]
        for j in bad_chars:
         status=status.replace(j, '')

        if status=="None":
          try:
            cur.execute('''INSERT INTO Attendance_DB(User_ID, Date, Time) VALUES (?, ?, ?)''', (str(user.id),date,shift_status))
            conn.commit()
          except Exception as err:
            logger.error(err.__class__ + " " + str(err))

          logger.info(str(user) + ", "+str(shift_status)+" - attendance marked")
          channel = await user.create_dm()
          date_time = datetime.datetime.now()
          embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))
          embed.add_field(name='Attendance marked for:', value = "Morning shift"+"\n\n\n", inline=False)
          await channel.send(embed=embed)
          await ctx.send(embed=embed,delete_after=30)
          
        else:
          else_embed=discord.Embed(title="Sorry attendance already marked",description="",colour=0x11806a)
          end=await ctx.send(embed=else_embed,delete_after=60)
          logger.warning(str(user.id)+" already marked")
    elif check_opening_time.hour > 14: 
        else_embed=discord.Embed(title="Sorry time limit reached",description="",colour=0x11806a)
        end=await ctx.send(embed=else_embed,delete_after=60)
        logger.warning(str(user.id)+" time limit reached")
        
    
@bot.command()
async def mark_evening(ctx, *,user: discord.Member):
   logger.info("'~mark_evening' called.")
   check_opening_time=datetime.datetime.now()
   full_day="ME"
   morning="M"
   evening="E"
   if check_opening_time.hour <= 19 and check_opening_time.hour >=15:
        conn = sqlite3.connect('Attendance_DB.sqlite')
        cur = conn.cursor()

        today=datetime.date.today()
        current_date = today.strftime("%Y-%m-%d")

        shift_status="E"
        try:
          cur.execute('''SELECT Time FROM Attendance_DB WHERE User_ID = ? AND Date = ?''', [str(user.id), current_date])
          status = str(cur.fetchone())
        except Exception as err:
          logger.error(err.__class__ + " " + str(err))

        bad_chars = ['(', ')', ',', "'"]
        for j in bad_chars:
         status=status.replace(j, '')

        if status=="None":
          try:
            cur.execute('''INSERT INTO Attendance_DB(User_ID, Date, Time) VALUES (?, ?, ?)''', (str(user.id),current_date,shift_status))
            conn.commit()
          except Exception as err:
            logger.error(err.__class__ + " " + str(err))

          logger.info(str(user) + ", "+str(shift_status)+" - attendance marked")
          channel = await user.create_dm()
          date_time = datetime.datetime.now()
          embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))
          embed.add_field(name='Attendance marked for:', value = "Evening shift"+"\n\n\n", inline=False)
          await channel.send(embed=embed)
          await ctx.send(embed=embed,delete_after=30)
        
        else: 
            if((status.count(full_day)>0)): 
                else_embed=discord.Embed(title="already marked",description="",colour=0x11806a)
                end=await ctx.send(embed=else_embed,delete_after=60)
                logger.warning(str(user.id)+" time limit reached")
            elif((status.count(morning)>0) and (status.count(evening)==0)): 
               status = status + shift_status
               status = str(status)
               try:
                cur.execute('''UPDATE Attendance_DB SET Time = ? WHERE User_ID = ? AND Date = ?''', [status, str(user.id),current_date ])
                conn.commit()
               except Exception as err:
                logger.error(err.__class__ + " " + str(err))

               logger.warning(str(user)+", "+str(shift_status)+" - attendance updated")
               channel = await user.create_dm()
               date_time = datetime.datetime.now()
               embed = EMBEDS.attendance_dm(date_time.strftime("%D"), date_time.strftime("%H:%M:%S"), date_time.strftime("%A"))
               embed.add_field(name='Attendance marked for:', value = "Evening shift"+"\n\n\n", inline=False)
               await channel.send(embed=embed)
               await ctx.send(embed=embed,delete_after=30)
   elif check_opening_time.hour > 18:
        else_embed=discord.Embed(title="Sorry time limit reached",description="",colour=0x11806a)
        end=await ctx.send(embed=else_embed,delete_after=60)
        logger.warning(str(user.id)+" time limit reached")
    
# check all user leaves
@bot.command()
@commands.has_any_role("@Kore")
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
      


        #full leave
        try:
            cur.execute('''SELECT DISTINCT Users_DB_Attendance.User_ID FROM Users_DB_Attendance WHERE NOT EXISTS (SELECT Attendance_DB.User_ID FROM Attendance_DB WHERE Users_DB_Attendance.User_ID = Attendance_DB.User_ID AND Attendance_DB.Date = ?)''', [dates])
            full_absent = cur.fetchall()
        except Exception as err:
            logger.error(err.__class__ + " " + str(err))
            

        for i in full_absent:
            user_id=str(i)
            bad_chars = ['(', ')', ',', "'"]
            for i in bad_chars:
                user_id=user_id.replace(i, '')

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
                cur.execute('''SELECT Time FROM Attendance_DB WHERE  Attendance_DB.User_ID= ? AND Attendance_DB.Date=?''',[j,dates])
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

    await ctx.send(embed=leave_Embed,delete_after=90)
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
        await ctx.send(embed=leaves, delete_after = 90)
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
            await ctx.send(embed=leaves, delete_after = 90)
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
        await ctx.send(embed=attendance,file=discord.File(save_filename), delete_after = 90)
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
            await ctx.send(embed=attendance, delete_after = 90)
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
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "11:22":
            logger.info("Ran morning absentees")
            await absentees_morning(channel)
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "15:00":
            logger.info("Ran post lunch attendance.")
            await take_attendance_lunch(channel)
        if working_day == date_time.strftime("%A") and date_time.strftime("%H:%M") == "15:22":
            logger.info("Ran post lunch absentees.")
            await absentees_evening(channel)
    logger.info("Waiting for tasks...")


# Remind command
@bot.command()
@commands.has_any_role("Koders")
async def remind(msg, *args):
    await msg.message.delete()
    await asyncio.sleep(float(args[0]) * 60 * 60)
    embed = discord.Embed(title="Hello there! You have a reminder ^_^",
                          color=0x57b28f)
    embed.add_field(name="Don't forget to:",
                    value="{0}".format(args[1]),
                    inline=False)
    embed.add_field(name="By yours truly :ghost:",
                    value="Kourage",
                    inline=False)
    embed.set_thumbnail(url="https://www.flaticon.com/svg/static/icons/svg/2919/2919780.svg")
    embed.set_footer(text="Made with ❤️️  by Koders")
    await msg.send(embed=embed)
    if len(args) > 2:
        msg = await msg.send(args[2])
        await msg.delete()  # Deletes @person message who got tagged




# Poll command
@bot.command()
@commands.has_any_role('Koders')
async def poll(msg, question, *options: str):
    await msg.message.delete()
    embed = discord.Embed(title="Hello there! Please vote. ^_^",
                          description=question,
                          color=0x54ab8a)
    embed.set_author(name="Koders")
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
    for _x, option in enumerate(options):
        embed.add_field(name=reactions[_x],
                        value=option,
                        inline=True)
    embed.set_footer(text="Made with ❤️️  by Koders")
    react_message = await msg.send(embed=embed)
    for reaction in reactions[:len(options)]:
        await react_message.add_reaction(reaction)


if __name__ == "__main__":
    try:
        attendance_task.start()
        bot.run(os.environ.get('TOKEN'))
    except Exception as _e:
        logging.warning("Exception found at main worker. Reason: " + str(_e), exc_info=True)
