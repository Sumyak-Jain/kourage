import asyncio
import platform
import time
import discord
import sqlite3
import datetime
import discord
from discord.ext import commands
from datetime import date, timedelta
from discord import client
import datetime
from urllib import parse, request
import sqlite3
from matplotlib import pyplot as plt
import numpy as np
import asyncio
from uuid import uuid4
import datetime
from urllib import parse, request
from sqlite3.dbapi2 import Cursor
import sqlite3
from colorama import init
from termcolor import colored

machine = platform.node()
init()

class Logger:
    def __init__(self, app):
        self.app = app
    def info(self, message):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', 'yellow'))
    def warning(self, message):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', 'green'))
    def error(self, message):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', 'red'))
    def color(self, message, color):
        print(colored(f'[{time.asctime(time.localtime())}] [{machine}] [{self.app}] {message}', color))

logger = Logger("kourage-Attendance")
def attendance(opening_time, closing_time):
    embed = discord.Embed(title="Attendance System",
                          description="Please react before closing time else the message will disappear ",
                          color=0x11806a)
    embed.set_author(name="Mark you attendance by reacting ⬆️ emoji")
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/700257704723087360/819643015470514236/SYM_TEAL.png?width=455"
            "&height=447")
    embed.add_field(name="Opening Time", value=opening_time, inline=False)
    embed.add_field(name="Closing Time", value=closing_time, inline=False)
    embed.set_footer(text="Made with ❤️️  by Koders")
    return embed

def attendance_dm(date, time, day):
    embed = discord.Embed(title="Thank you for marking your attendance!", color=0x11806a)
    embed.set_author(name="Attendance")
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/700257704723087360/819643015470514236/SYM_TEAL.png?width=455"
            "&height=447")
    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Time", value=time,  inline=True)
    embed.add_field(name="Day", value=day, inline=True)
    return embed

def attendance_missed_dm(date, time, day):
    embed = discord.Embed(title="Yo have not marked your attendance yet. Only 5 minutes remaining", color=0x11806a)
    embed.set_author(name="Attendance")
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/700257704723087360/819643015470514236/SYM_TEAL.png?width=455"
            "&height=447")
    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Time", value=time,  inline=True)
    embed.add_field(name="Day", value=day, inline=True)
    return embed

def leave_and_attendance(ctx, bot, start_date, end_date, users, mode):
    """
    This module shows attendance and leaves
    :params: start_date(str), end_date(str), user_id(int), username(str)
    :return: None
    :mode: 1 - for attendance, 2 - leaves
    """
    logger.info("Show attendance called")

    conn = sqlite3.connect('ATTENDANCE.sqlite')
    cur = conn.cursor()
    if mode == 1:
        cur.execute('''SELECT DATE, SHIFT, PRESENTEES FROM ATTENDANCE WHERE DATE BETWEEN ? AND ?''', str(start_date), str(end_date))
    if mode == 2:
        cur.execute('''SELECT DATE, SHIFT, ABSENTEES FROM ATTENDANCE WHERE DATE BETWEEN ? AND ?''', str(start_date), str(end_date))
    data = cur.fetchone()

    if not data: # TODO Check if this is working
      logger.warning("No attendance data found between those dates")
      return None
    else:
    # TODO - try with string strips
      morning_only, evening_data, full_day = {}, {}, {}

      for each in data:
          selected_dates = []
          if each[1] == "M":
              morning_only[each[0]] = set(each[2].strip('"{}').split(', ')) # Adding members
          elif each[1] == "E":
              evening_only[each[0]] = set(each[2].strip('"{}').split(', ')) # Adding members
          selected_dates.append(each[0])

        # Calculating all possible dates and adding members accordingly
        selected_dates = set(selected_dates) # For finding unique dates
        for each_date in selected_dates:
            for each_person in morning_only[each_date]:
                try:
                    if each_person in evening_only[each_date]:
                        full_day[each_date].append(each_person)

                        # if full day is found. removing from morning and evening
                        morning_only.remove(each_person)
                        evening_only.remove(each_person)
                except Exception as err:
                    logger.error("Something went wrong while fetching the full day attendance")

    if users:
        if mode == 1:
            status = "Present"
        elif mode == 2:
            status = "Absent"

        for user in users:
            message=""
            for each_date in selected_dates:
                try:
                    if user in full_day[each_date]:
                        message += each_date + ": " + status + " in full day \n"
                    elif user in morning_only[each_date]:
                        message += each_date + ": " + status + " in morning only \n"
                    elif user in evening[each_date]:
                        message += each_date + ": " + status + " in evening only \n"
                except Exception as e:
                    pass # handling KeyError in dict

            embed=simple_embed(title="Result for: "+str(bot.get_user(user)+"\n",description="")
            embed.add_field(name='Here are the details', value=message, inline=False)
            await ctx.send(embed=embed, delete_after=60)

async def data_input(ctx, bot):
    start_date_embed=discord.Embed(title="Enter start date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
    start=await ctx.send(embed=start_date_embed,delete_after=60)
    start_date1 = await ctx_input(ctx, bot, start)
    if not start_date1:
        return

    end_date_embed=discord.Embed(title="Enter end date",description="Please enter in this format only 'yyyy-mm-dd'",colour=0x11806a)
    end=await ctx.send(embed=end_date_embed,delete_after=60)
    end_date1 = await ctx_input(ctx, bot, end)
    if not end_date1:
        return

    start_date = datetime.datetime.strptime(start_date1, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date1, '%Y-%m-%d')

    return start_date, end_date;

    attendance_embed=simple_embed(title="Leaves for : "+str(username)+"\n",description="")
    attendance_embed.add_field(name='Leaves List', value = attendance_list, inline=False)

    return attendance_embed

def attendance(ctx, bot, start_date, end_date, user_id, mode, flag):
    """
    This module shows attendance and leaves
    :params: start_date(str), end_date(str), user_id(int), username(str)
    :return: None
    """
    logger.info("Attendance function called")

    attendance_list=""
    attendance_list=attendance_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n"

    conn = sqlite3.connect('ATTENDANCE.sqlite')
    cur = conn.cursor()

    # TODO
    # Fix sql query
    if flag == 1:
        cur.execute('''SELECT DATE, SHIFT, PRESENTEES FROM ATTENDANCE WHERE ''')
    elif flag == 2:
        cur.execute('''SELECT DATE, SHIFT, ABSENTEES FROM ATTENDANCE WHERE ''')
    data = cur.fetchone()

    if not data: # TODO Check if this is working
      logger.warning("No attendance data found between those dates")
      return None
    else:
      morning_only, evening_data, full_day = {}, {}, {}

      for each in data:
          selected_dates = []
          # TODO
          # Check strip
          if each[1] == "M":
              morning_only[each[0]] = set(each[2].strip("'{}'").split(', ')) # Adding members
          elif each[1] == "E":
              evening_only[each[0]] = set(each[2].strip("'{}'").split(', ')) # Adding members
          selected_dates.append(each[0])
      selected_dates = set(selected_dates) # Unique dates

    for each_date in selected_dates:
        for each_person in morning_only[each_date]:
            try:
                if each_person in evening_only[each_date]:
                    full_day[each_date].append(each_person) # this should be in try and catch

                    # if full day is found. removing from morning and evening
                    morning_only.remove(each_person)
                    evening_only.remove(each_person)
            except Exception as err:
                logger.error("Something went wrong while fetching the full day attendance")

    return morning_only, evening_only, full_day
    morning_only[dates] = set of presntees


      if((present_morning==True) and (present_evening==True)):
          attendance_list=attendance_list+"Present full day\n"
      elif((present_morning==False) and (present_evening==True)):
          attendance_list=attendance_list+"Absent in morning\n"
      elif((present_morning==True) and (present_evening==False)):
          attendance_list=attendance_list+"Absent in evening\n"
      elif((absent_morning==True) and (absent_evening==True)):
          attendance_list=attendance_list+"Absent full day\n"

    attendance_embed=simple_embed(title="Leaves for : "+str(username)+"\n",description="")
    attendance_embed.add_field(name='Leaves List', value = attendance_list, inline=False)

    return attendance_embed

    #graph
    def addlabels(x,y):
        for i in range(len(x)):
         plt.text(i, y[i], y[i], ha = 'center',
                 Bbox = dict(facecolor = 'grey', alpha =.8))
    value = [attendance_dates,full_present,morning_present,evening_present,absent]
    data = ('Total\nDates', 'Full Day\nPresent', 'Morning\nPresent','Evening\nPresent','Absent')
    x_pos = np.arange(len(data))
    save_filename='test.png'
    plt.bar(x_pos, value, color = ['darkcyan'])
    addlabels(data, value)
    plt.title('Attendance Graph for @'+str(username))
    plt.ylabel('values')

    plt.xticks(x_pos, data)
    plt.savefig(save_filename,dpi=100)
    plt.close()

    return attendence_embed,save_filename;

def simple_embed(title, description):
    embed = discord.Embed(
            title = title,
            description = description,
            colour=0x11806a
            )
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/700257704723087360/819643015470514236/SYM_TEAL.png?width=455&height=447")
    embed.set_footer(text="Made with ❤️️  by Koders")
    embed.timestamp = datetime.datetime.utcnow()
    return embed

_rxn_no = {'1️⃣':1, '2️⃣':2, '3️⃣':3,'4️⃣':4}

async def take_reaction_no(ctx, rxn_amnt, _embed, bot, timeout=300.0):
    rxn = dict()
    _i = 1
    for i in _rxn_no:
        if _i > rxn_amnt:
            break
        rxn[i] = _i
        _i += 1

    for i in rxn:
        await _embed.add_reaction(i)

    def check(reaction, user):
        _c1 = user.bot is not True and user == ctx.author
        return _c1 and str(reaction.emoji) in rxn

    try:
        result = await bot.wait_for('reaction_add', check=check, timeout=timeout)
        reaction, user = result

        ret = (None, rxn[str(reaction)]) [ str(reaction) in rxn ]
        return ret, _embed

    except asyncio.TimeoutError:
        await ctx.delete()

async def ctx_input(ctx, bot, embed, timeout = 60.0):
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
        )
        if msg:
            await embed.delete()
            _id = msg.content
            await msg.delete()
            return _id
    except asyncio.TimeoutError as err:
        await embed.delete()
        await ctx.send('Cancelling due to timeout.', delete_after = timeout)
        return None
