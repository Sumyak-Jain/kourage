
import discord
from discord import client
from discord.ext import commands
import datetime
import funtion
from urllib import parse, request
import re
import asyncio
import embed
from discord.ext import commands

bot = commands.Bot(command_prefix='~', description="This is a Helper Bot")



@bot.command()
async def feedback(ctx):
    
    channel = bot.get_channel("channel ID") 
    front_embed=discord.Embed(title="CLIENT FEEDBACK BOT", description="As a software company we at Koders, value our clients feedback and want to have a continuous developing service and growth.We would really appreciate if you could spare a few minutes and fill in the details of this form so as to help us in improving or Quality and service.Your input would be highly confidential and valuable. \n\n For any queries please feel free to contact us :\nMail - support@koders.in\nPhone Number - 7008493497,7017799756",colour=0x11806a)
    front_embed.set_thumbnail(url="https://media.discordapp.net/attachments/700257704723087360/819643015470514236/SYM_TEAL.png?width=455&height=447")
    front_embed.set_image(url ="https://cdn.discordapp.com/attachments/860047404903956480/860926678784278528/Black_and_Blue_Business_Linkedln_Banner_11.png")
    front_embed.set_footer(text="Thank you for choosing Koders ❤️️")
    front_embed.set_author(name = f'Bot initialized for  {ctx.message.author}', icon_url = f'{ctx.author.avatar_url}')
    front_embed.timestamp = datetime.datetime.utcnow()
    front=await ctx.send(embed=front_embed)
    
    project_name_embed=discord.Embed(title="",description="What was your Project/Channel Name ?",colour=0x11806a)
    project=await ctx.send(embed=project_name_embed,delete_after=60)
    project_name = await embed.ctx_input(ctx, bot, project)
    if not project_name:
         return 
    hear_us= {1:"News/Banners", 2:"Social media handles", 3:"Recommendation",4:"others"} 
    hear_embed=discord.Embed(title="How did you hear about us?",description="1) News/Banners\n2) Social media handles\n3) Recommendation\n4) Others",colour=0x11806a)
    hear_0=await ctx.send(embed=hear_embed)
    var,hear_embed=await embed.take_reaction_no(ctx,4,hear_0,bot)
    if(var==4): 
        other_embed=discord.Embed(title="",description="What is the other source?",colour=0x11806a)
        other_source=await ctx.send(embed=other_embed,delete_after=60)
        hear_us = await embed.ctx_input(ctx, bot, other_source)
        if not hear_us:
         return
    else: 
        hear_us=hear_us[var]
    await hear_0.delete()
    experience_embed=discord.Embed(title="",description="How was your experience with Koders? Has any aspect of our company exceeded your expectations?",colour=0x11806a)
    exp=await ctx.send(embed=experience_embed,delete_after=60)
    experience = await embed.ctx_input(ctx, bot, exp)
    if not experience:
         return
     
    ratings={1:"😍 Excellent",2:"🙂 Satisfactory",3:"😑 Average",4:"😕 Bad",5:"😡 Worst"}
    rate_embed=discord.Embed(title="Rate us",description="😍 Excellent\n\n🙂 Satisfactory\n\n😑 Average\n\n😕 Bad\n\n😡 Worst",colour=0x11806a)
    rate_card=await ctx.send(embed=rate_embed,delete_after=60)
    
    communication_embed=discord.Embed(title="",description="Communication ?",colour=0x11806a)
    communication=await ctx.send(embed=communication_embed)
    var,communication_embed=await embed.take_reaction(ctx,5,communication,bot)
    communication_rating=ratings[var]
    await communication.delete()
    
    responsiveness_embed=discord.Embed(title="",description="Responsiveness ?",colour=0x11806a)
    responsiveness=await ctx.send(embed=responsiveness_embed)
    var,responsiveness_embed=await embed.take_reaction(ctx,5,responsiveness,bot)
    responsiveness_rating=ratings[var]
    await responsiveness.delete()
    
    costs_embed=discord.Embed(title="",description="Costs ?",colour=0x11806a)
    costs=await ctx.send(embed=costs_embed)
    var,costs_embed=await embed.take_reaction(ctx,5,costs,bot)
    costs_rating=ratings[var]
    await costs.delete()
    
    overall_embed=discord.Embed(title="",description="Overall knowledge and understanding of the project ?",colour=0x11806a)
    overall=await ctx.send(embed=overall_embed)
    var,overall_embed=await embed.take_reaction(ctx,5,overall,bot)
    overall_rating=ratings[var]
    await overall.delete()
    await rate_card.delete() 
    
    next_embed=discord.Embed(title="If we could make something for you the next time, what would you like?",description="",colour=0x11806a)
    next_embed.set_footer(text="If you wanna skip this press ❌, if you wanna answer press ✅")
    next=await ctx.send(embed=next_embed)
    var,next_embed=await embed.take_reaction_NA(ctx,2,next,bot)
    if(var==1): 
         next_time="NA"
         await next.delete()
    elif(var==2):
      optional_embed=discord.Embed(title="",description="Type your response",colour=0x11806a)
      optional=await ctx.send(embed=optional_embed)
      next_time = await embed.ctx_input(ctx, bot,optional)
      await next.delete()
      if not next_time:
         return
    
    additional_embed=discord.Embed(title="Any additional feedback ",description="Based on your experience, please give brief suggestions(if any) on how the experience could have been better for both of us. It may be related to the tools and services we used, the timeline, cost, how we communicated throughout the project, etc. This would mean a lot to us and will try to incorporate the suggestions made by you.",colour=0x11806a)
    additional_embed.set_footer(text="If you wanna skip this press ❌, if you wanna answer press ✅")
    additional=await ctx.send(embed=additional_embed,delete_after=60)
    var,additional_embed=await embed.take_reaction_NA(ctx,2,additional,bot)
    if(var==1): 
         additional_feedback="NA"
         await additional.delete()
    elif(var==2):
     optional_embed=discord.Embed(title="",description="Type your response",colour=0x11806a)
     optional=await ctx.send(embed=optional_embed)
     additional_feedback = await embed.ctx_input(ctx, bot,optional)
     await additional.delete()
     if not additional_feedback:
         return
    
    thankyou_embed=embed.simple_embed(title="Thank You for the valuable feedback",description="We value your time and efforts!")
    await ctx.send(embed=thankyou_embed,delete_after=60)
    await front.delete()
    
    sendEmbed=embed.simple_embed(title="\nFEEDBACK REPORT",description="")
    sendEmbed.set_author(name = f'Feedback from : {ctx.message.author}', icon_url = f'{ctx.author.avatar_url}')
    sendEmbed.add_field(name='Project Name: ', value = str(project_name)+"\n\n\n", inline=False) 
    sendEmbed.add_field(name='How did you hear about us?', value = str(hear_us)+"\n\n", inline=False) 
    sendEmbed.add_field(name='How was your experience with Koders? Has any aspect of our company exceeded your expectations?', value = str(experience)+"\n\n\n", inline=False)
    sendEmbed.add_field(name='Rate us:', value ="Communication :  "+communication_rating+"\n\n Responsiveness :  "+responsiveness_rating+"\n\nCosts :  "+costs_rating+"\n\n Overall knowledge and understanding of the project :  "+overall_rating+"\n\n\n", inline=False)
    sendEmbed.add_field(name='If we could make something for you the next time, what would you like?', value = str(next_time)+"\n\n\n", inline=False)
    sendEmbed.add_field(name='Any additional feedback: ', value = str(additional_feedback)+"\n\n\n", inline=False)
        
    await channel.send(embed=sendEmbed)
        
    
    


# Events
@bot.event
async def on_ready():
    
    print('Ready is my Body')
    

bot.run('TOKEN')
