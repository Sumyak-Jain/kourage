import requests
from datetime import date
from matplotlib import pyplot as plt
import numpy as np
from discord.ext import commands
import discord
import  os
import embeds
from discord.ext.tasks import loop
hdr1 = {'X-Redmine-API-Key':os.environ.get("REDMINE_KEY")}
bot = commands.Bot(command_prefix="~")
logger = embeds.Logger("kourage-Spent-Time")

#TODO 
#we can add delete after for embeds

@loop(hours=24)
async def spent_time():
 logger.info("spent_time called")
 await bot.wait_until_ready()
 channel = bot.get_channel(int(877467665084600320))
 #url = "https://www.kore.koders.in/time_entries.json?utf8=%E2%9C%93&set_filter=1&sort=spent_on%3Adesc&f%5B%5D=spent_on&op%5Bspent_on%5D=t&f%5B%5D=&c%5B%5D=project&c%5B%5D=spent_on&c%5B%5D=user&c%5B%5D=activity&c%5B%5D=issue&c%5B%5D=comments&c%5B%5D=hours&group_by=&t%5B%5D=hours&t%5B%5D="
 url="https://www.kore.koders.in/time_entries.json?utf8=%E2%9C%93&set_filter=1&sort=spent_on%3Adesc&f%5B%5D=spent_on&op%5Bspent_on%5D=%3D&v%5Bspent_on%5D%5B%5D=2021-06-15&f%5B%5D=&c%5B%5D=project&c%5B%5D=spent_on&c%5B%5D=user&c%5B%5D=activity&c%5B%5D=issue&c%5B%5D=comments&c%5B%5D=hours&group_by=&t%5B%5D=hours&t%5B%5D="
 payload={}
 headers = hdr1

 response = requests.request("GET", url, headers=headers, data=payload).json()
 
 
 if (response["total_count"])==0: 
   today_date=date.today()
   embed=embeds.simple_embed(title="No one logged there data on "+str(today_date),description="")
   await channel.send(embed=embed)
   logger.info("no data found")
 
 else: 
  today_date=response["time_entries"][0]["spent_on"]
  time_list=[]
  data_list=[]
  
  for i in response["time_entries"]:
    keys=list(i.keys())
    if "issue" not in keys:  
     data_list.append(str(i["user"]["name"])+" "+"(No issue)")
     time_list.append(int(i["hours"]))
    else:  
     data_list.append(str(i["user"]["name"])+" "+"(Issue#"+str(i["issue"]["id"])+")")
     time_list.append(int(i["hours"]))
  
  
  value =time_list
  data = data_list
  save_filename='test.png'
  
  plt.bar(data, value, color = ['darkcyan'], width = 0.4)
  plt.xticks(rotation = 90)
  plt.title("Spent time graph of "+str(today_date))
  plt.ylabel('spent time in hrs')
  plt.xlabel("Names and issues id")
  
  plt.tight_layout()
  plt.savefig(save_filename,dpi=100)
  plt.close() 

  await channel.send(file=discord.File(save_filename))
  logger.info("spent time graph shown of "+str(today_date))




if __name__ == "__main__":
    try:
        logger.info("spent time running")
        spent_time.start()
        bot.run(os.environ.get("TOKEN"))

    except Exception as _e:
        logger.warning("Exception found at main worker. Reason: " + str(_e), exc_info=True)
