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

def show(start_date, end_date, user_id, username):
    """
    This module shows attendance and leaves
    :params: start_date(str), end_date(str), user_id(int), username(str)
    :return: None
    """
    logger.info("Show attendance called")
    dates=str(single_date.strftime("%Y-%m-%d"))

    attendance_list=""
    attendance_list=attendance_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n"

    conn = sqlite3.connect('ATTENDANCE.sqlite')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM ATTENDANCE WHERE ''')
    data = cur.fetchone()

    if not data: # TODO Check if this is working
      logger.warning("No attendance data found between those dates")
      return None
    else:
      members=set(data[0][3][1:-1].split(', '))
      morning_only, evening_data, full_day = {}, {}, {}

      # TODO
      # Convert string to set back without string manipulation
      # Absentees
      for each in data:
          selected_dates = []
          if each[1] == "M":
              morning_only[each[0]] = set(each[3][1: -1].split(', ')) # Adding absentees
          elif each[1] == "E":
              evening_only[each[0]] = set(each[3][1: -1].split(', ')) # Adding absentees
          selected_dates.append(each[0])
      selected_dates = set(selected_dates) # Unique dates

    # -- Collide
    #  ~leaves - All - Kore
    #  ~leaves - @mention if not ctx.mention:
    #  ~leaves - Not Kore - Yours
    #  ~leaves - @mention - Not Kore - Warning(You cant check)

    #  ~attendance - All
    #  ~attendance - @mention
    #  ~attendance - Not Kore - Yours
    #  ~attendance - @mention - Not Kore - Warning(You can't check)

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

     for each in morning_only:
         print(each)

        # Calculating all possible dates and adding members accordingly

        selected_dates = set(selected_dates) # For finding unique dates
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

def show_attendance(start_date, end_date, user_id, check_username):
    logger.info("Show attendance called")
    conn = sqlite3.connect('ATTENDANCE.sqlite')
    cur = conn.cursor()
    def daterange(start_date, end_date):
      for n in range(int((end_date - start_date).days)):
          yield start_date + timedelta(n)

    attendance_embed=simple_embed(title="Attendance for : "+str(username)+"\n",description="")
    attendance_list=""
    attendance_dates=0
    full_present=0
    morning_present=0
    evening_present=0
    absent=0

    for single_date in daterange(start_date, end_date):
      present_morning=False
      present_evening=False
      absent_morning=False
      absent_evening=False
      dates=str(single_date.strftime("%Y-%m-%d"))
      attendance_dates=attendance_dates+1
      attendance_list=attendance_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n"

      cur.execute('''SELECT PRESENTEES FROM Attendance_table WHERE DATE = ? AND SHIFT = ?''', [dates,"M"])
      morning_presentees = (cur.fetchone())
      if(str(morning_presentees)=="None"):
          morning_presentees=="None"
      else:
          str0 = morning_presentees[0][1:-1]
          morning_presentees=set(str0.split(', '))
          for i in morning_presentees:
              if(i==str(user_id)):
                present_morning=True

      cur.execute('''SELECT ABSENTEES FROM Attendance_table WHERE DATE = ? AND SHIFT = ?''', [dates,"M"])
      morning_absentees= (cur.fetchone())
      if(str(morning_absentees)=="None"):
          morning_absentees=="None"

      else:
        str1 = morning_absentees[0][1:-1]
        morning_absentees=set(str1.split(', '))
        for i in morning_absentees:
             if(i==str(user_id)):
                absent_morning=True

      cur.execute('''SELECT PRESENTEES FROM Attendance_table WHERE DATE = ? AND SHIFT = ?''', [dates,"E"])
      evening_presentees = (cur.fetchone())
      if(str(evening_presentees)=="None"):
          evening_presentees=="None"
      else:
            str2 = evening_presentees[0][1:-1]
            evening_presentees=set(str2.split(', '))
            for i in evening_presentees:
               if(i==str(user_id)):
                  present_evening=True

      cur.execute('''SELECT ABSENTEES FROM Attendance_table WHERE DATE = ? AND SHIFT = ?''', [dates,"E"])
      evening_absentees= (cur.fetchone())
      if(str(evening_absentees)=="None"):
         evening_absentees=="None"
      else:
           str3 = evening_absentees[0][1:-1]
           evening_absentees=set(str3.split(', '))
           for i in evening_absentees:
             if(i==str(user_id)):
                absent_evening=True

      if((present_morning==True) and (present_evening==True)):
          attendance_list=attendance_list+"Present full day\n"
          full_present=full_present+1
      elif((present_morning==False) and (present_evening==True)):
          attendance_list=attendance_list+"Present in evening only\n"
          evening_present=evening_present+1
      elif((present_morning==True) and (present_evening==False)):
          attendance_list=attendance_list+"Present in morning only\n"
          morning_present=morning_present+1
      elif((absent_morning==True) and (absent_evening==True)):
          attendance_list=attendance_list+"Absent full day\n"
          absent=absent+1

    attendance_embed.add_field(name='Attendance List', value = attendance_list, inline=False)

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
