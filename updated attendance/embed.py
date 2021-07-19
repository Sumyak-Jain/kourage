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


#logger = Logger("kourage-boilerplate")
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

def show_leaves(start_date,end_date,user_id,check_username):
    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()
    


    def daterange(start_date, end_date):
      for n in range(int((end_date - start_date).days)):
          yield start_date + timedelta(n)
 
    leaves_Embed=simple_embed(title="Leaves for : "+str(check_username)+"\n",description="")

    leave_list=""
    
    for single_date in daterange(start_date, end_date):
      dates=str(single_date.strftime("%Y-%m-%d"))
      leave_list=leave_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n"
    
      cur.execute('''SELECT Time FROM Attendance_DB WHERE  Attendance_DB.User_ID= ? AND Attendance_DB.Date=?''',[user_id,dates]) 
      attendance = cur.fetchall()
      
      time_list=[]
      time=str(attendance)
      bad_chars = ['(', ')', ',', "'"]
      for i in bad_chars: 
        time=time.replace(i, '')
      
      time_list.append(time);
      
    
      for j in time_list:
       full_day="ME"
       morning="M"
       evening="E"
       
       if((j.count(morning)==0) and (j.count(evening)==0 )): 
            leave_list=leave_list+"Full Day leave"+"\n"
       elif (j.count(full_day)>0):
            leave_list=leave_list+"Full Day Present"+"\n"
       elif((j.count(morning)==0) and j.count(evening)>0 ):
            leave_list=leave_list+"Absent in morning"+"\n" 
       elif((j.count(evening)==0) and (j.count(morning)>0)):
            leave_list=leave_list+"Absent in evening shift"+"\n"   
      
    leaves_Embed.add_field(name='Leave List', value = leave_list, inline=False)  
   
     
    return leaves_Embed
    




def show_attendance(start_date,end_date,user_id,check_username):
    conn = sqlite3.connect('Attendance_DB.sqlite')
    cur = conn.cursor()
    def daterange(start_date, end_date):
      for n in range(int((end_date - start_date).days)):
          yield start_date + timedelta(n)
 
    attendence_Embed=simple_embed(title="Attendance for : "+str(check_username)+"\n",description="")

    attendance_list=""
    attendance_dates=0
    full_present=0
    morning_present=0
    evening_present=0
    absent=0
    for single_date in daterange(start_date, end_date):
      dates=str(single_date.strftime("%Y-%m-%d"))
      attendance_dates=attendance_dates+1
      attendance_list=attendance_list+"\n𝗗𝗔𝗧𝗘: "+dates+"\n"
    
      cur.execute('''SELECT Time FROM Attendance_DB WHERE  Attendance_DB.User_ID= ? AND Attendance_DB.Date=?''',[user_id,dates]) 
      attendance = cur.fetchall()
      
      time_list=[]
      time=str(attendance)
      bad_chars = ['(', ')', ',', "'"]
      for i in bad_chars: 
        time=time.replace(i, '')
      
      time_list.append(time);
      
    
      for j in time_list:
       full_day="ME"
       morning="M"
       evening="E"
       
       if((j.count(morning)==0) and (j.count(evening)==0 )): 
            attendance_list=attendance_list+"Full Day Absent"+"\n"
            absent=absent+1
       elif (j.count(full_day)>0):
            attendance_list=attendance_list+"Full Day Present"+"\n"
            full_present=full_present+1
       elif((j.count(morning)==0) and j.count(evening)>0 ):
            evening_present=evening_present+1
            attendance_list=attendance_list+"Present in Evening shift"+"\n" 
       elif((j.count(evening)==0) and (j.count(morning)>0)):
            morning_present=morning_present+1
            attendance_list=attendance_list+"Present in Morning shift"+"\n"   
      
    attendence_Embed.add_field(name='Attendance List', value = attendance_list, inline=False)  
    
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
    plt.title('Attendance Graph for @'+str(check_username))
    plt.ylabel('values')
    
    plt.xticks(x_pos, data)
    plt.savefig(save_filename,dpi=100)
    plt.close()
    
    
    return attendence_Embed,save_filename;
    

    
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