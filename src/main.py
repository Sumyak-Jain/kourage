import json
import embeds
import os
import datetime
import discord
import requests
import redmine_api
from discord.ext import commands
from discord.ext.tasks import loop
import discord
from discord import client
from discord.ext import commands
import function
from urllib import parse, request
from discord.ext import commands
from discord.utils import get




logger = embeds.Logger("kourage-operations")

bot = commands.Bot(command_prefix="~")

## Change the webpage accordingly.
webpage = "http://sumyak.m.redmine.org/"

hdr1 = {'X-Redmine-API-Key' : os.environ.get('REDMINE_KEY'),
        'Content-Type': 'application/json'}

@bot.event
async def on_ready():
    logger.info("Kourage is running at version {0}".format("0.1.0"))



@bot.command()
async def show_issues(ctx):
    logger.info("~show_info called by "+str(ctx.author.name))
    await ctx.channel.purge(limit = 1)
    
    project_dict,project_list,project_id=function.project_list()
    initial_embed=embeds.simple_embed(title="This is the current list of project", description=project_list)
    initial_embed.set_author(name = f'Bot initialized for  {ctx.message.author}', icon_url = f'{ctx.author.avatar_url}')
    message  = await ctx.send(embed = initial_embed,delete_after=60)

   
    due_embed=discord.Embed(title="Enter the s.no of the project of which you want to see issues", description="Please just give a number only eg: 1",colour=0x11806a)
    message=await ctx.send(embed=due_embed,delete_after=70)
    project_number = await embeds.ctx_input(ctx, bot, message)
    if not project_number:
      return 
     
    project_name=str(project_dict[int(project_number)])
    logger.info(project_name)
    response=function.issues(project_name)
    due_embed=discord.Embed(title="List of issues", description=response, color=0x11806a)
    await ctx.send(embed=due_embed,delete_after=90)
    logger.info("List of issues shown to: "+str(ctx.author.name))

# Channel creation
@bot.command()
async def channel(ctx, name):
   
    await ctx.guild.create_text_channel(name=name)

@bot.command()
async def new_project(ctx):
    await ctx.channel.purge(limit = 1)

    initial_embed=embeds.simple_embed(title="New project bot", description="")
    initial_embed.set_author(name = f'Bot initialized for  {ctx.message.author}', icon_url = f'{ctx.author.avatar_url}')
    message  = await ctx.send(embed = initial_embed,delete_after=60)

   
    due_embed=discord.Embed(title="", description="Enter the name of the project", colour=0x11806a)
    message=await ctx.send(embed=due_embed,delete_after=70)
    name = await embeds.ctx_input(ctx, bot, message)
    if not name:
      return 
    due_embed=discord.Embed(title="", description="Enter the identifier for the project", colour=0x11806a)
    message=await ctx.send(embed=due_embed,delete_after=70)
    identifier = await embeds.ctx_input(ctx, bot, message)
    if not identifier:
      return 
    response=function.new_project(name,identifier)
    await ctx.guild.create_text_channel(name=name)
    due_embed=discord.Embed(title="", description=response, color=0x11806a)
    await ctx.send(embed=due_embed,delete_after=60)
  
    
     
@bot.command()
async def add_user(ctx):
    logger.info("add_user called")
    project_dict,project_list,project_id_dict=function.project_list()
    initial_embed=embeds.simple_embed(title="This is the current list of project", description=project_list)
    initial_embed.set_author(name = f'Bot initialized for  {ctx.message.author}', icon_url = f'{ctx.author.avatar_url}')
    message  = await ctx.send(embed = initial_embed,delete_after=30)

   
    due_embed=discord.Embed(title="Enter the s.no of the project in which you want to add members", description="Please just give a number only eg: 1",colour=0x11806a)
    message=await ctx.send(embed=due_embed,delete_after=70)
    project_number = await embeds.ctx_input(ctx, bot, message)
    if not project_number:
      return 
     
    project_id=str(project_id_dict[int(project_number)])
    project_name=str(project_dict[int(project_number)])
    logger.info(str(project_name))
    await function.add_person(ctx,bot,project_id,project_name)
    #logger.info("member added")


@bot.command()
async def remove_user(ctx):
    logger.info("remove_user called")
    project_dict,project_list,project_id_dict=function.project_list()
    initial_embed=embeds.simple_embed(title="This is the current list of project", description=project_list)
    initial_embed.set_author(name = f'Bot initialized for  {ctx.message.author}', icon_url = f'{ctx.author.avatar_url}')
    message  = await ctx.send(embed = initial_embed,delete_after=30)

   
    due_embed=discord.Embed(title="Enter the s.no of the project of which you want to remove members", description="Please just give a number only eg: 1",colour=0x11806a)
    message=await ctx.send(embed=due_embed,delete_after=70)
    project_number = await embeds.ctx_input(ctx, bot, message)
    
    if not project_number:
      return 
     
    project_id=str(project_id_dict[int(project_number)])
    project_name=str(project_dict[int(project_number)])
    logger.info(str(project_name))
    await function.remove_mem(ctx,bot,project_id,project_name)
    logger.info("members removed")
    
    

    


if __name__ == "__main__":
    try:
        bot.run(os.environ.get('TOKEN'))
    except Exception as _e:
        logger.error("Exception found at main worker.\n" + str(_e))
