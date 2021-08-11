import requests
import json
import datetime
import os
import embeds
import redmine_api
import discord
logger = embeds.Logger("kourage-operations")
get_json = lambda _url, _hdr : requests.get(_url, headers = _hdr)

webpage = "http://sumyak.m.redmine.org/"


header = {
  'X-Redmine-API-Key': os.environ.get('REDMINE_KEY'),
 'Content-Type': 'application/json',
  
   }

def new_project(name,identifier):
   url = "http://sumyak.m.redmine.org/projects.json"

   
   payload = json.dumps({
   "project": {
    "name": name,
    "identifier": identifier,
    "enabled_module_names": "issue_tracking"
    }
    })
  
   
   response = requests.request("POST", url, headers=header, data=payload)
  
   if(str(response)== "<Response [201]>"): 
      logger.info("project: "+str(name+" created ")+str(response))
      return("CONGRATS 🤩"+"\nProject created successfully!")
      
   else:
    logger.error("error occured"+str(response))
    return(str(response)+ "\nSorry error occured!")
    

def project_list():
     logger.info("project list function called")
     #url="http://sumyak.m.redmine.org/projects.json"
     url = "https://www.kore.koders.in/projects.json"
     try:
      projects = get_json(url, header).json()
      project_list =""
      project_dict={}
      project_id_dict={}
     
      j=0;
      for i in projects["projects"]:
          j=j+1
          project_id_dict[j]=str((i["id"]))
          project_dict[j]=str((i["name"])).replace(" ","-")
          project_list=project_list+str(j)+") "+str((i["name"]))+"\n"
     except Exception as e: 
          logger.error("error getting project list: "+str(e))    
     return project_dict,project_list,project_id_dict;

async def add_person(ctx,bot, project_id,project_name):
    ''''
    if not 'REDMINE_KEY' in os.environ:
        logger.error("'REDMINE_KEY' doesn't exist in the environment variables")
        return
    logger.info("~add_person called for " + os.environ.get('REDMINE_KEY'))
    '''
    udict = dict()
    ujson_data = redmine_api.get_json(webpage + 'users.json', header)
    desc = ""
    for i in ujson_data['users']:
        udict[i['id']] = i['firstname'] + " " + i['lastname']
        desc += str(i['id']) + ") " + str(udict[i['id']]) + "\n"

    ujson_embed = embeds.simple_embed(
            title = "Enter user ID (space sperated) to add user in project: "+str(project_name),
            description = desc
            )

    sent = await ctx.send(embed = ujson_embed)
    ulist = await embeds.ctx_input(ctx, bot, sent)
    if not ulist:
        logger.error("User List input timed out.")
        return
    logger.info("Ulist : " + ulist)

    ulist = list(map(int, ulist.split()))
    for i in ulist:
        if not i in udict:
            logger.error("ID " + str(i) + " not in user dict.")
            return

    rset = set()
    rjson_data = redmine_api.get_json(webpage + 'roles.json', header)
    desc = ""
    for i in rjson_data['roles']:
        rset.add(i['id'])
        desc += str(i['id']) + ") " + i['name'] + '\n'
    rjson_embed = embeds.simple_embed(
            title = 'Select the role',
            description = desc
            )

    sent = await ctx.send(embed = rjson_embed)
    rlist = await embeds.ctx_input(ctx, bot, sent)
    if not rlist:
        logger.error("Role input timed out.")
        return
    logger.info("Rlist : " + rlist)

    rlist = list(map(int, rlist.split()))
    
    for i in rlist:
        if not i in rset:
            logger.error("Role " + str(i) + "not in role set.")
            return
    
    for uid in ulist:
        payload = json.dumps({
            "membership": {
                "user_id": uid,
                "role_ids": rlist
            }
        })
        print("Payload", payload)
        try:
         preq = redmine_api.post_data(webpage + "projects/" + str(project_id) + "/memberships.json", payload,header)
         if(str(preq)=="<Response [422]>"):
             logger.info("user already added : "+ str(preq))
             member_add_embed=discord.Embed(title="Member already added to project: "+project_name+"\n User ID: "+str(uid),description=preq,colour=0x11806a)
             await ctx.send(embed=member_add_embed,delete_after=15)
             await ctx.message.delete()
         
         else:
          logger.info("send req : "+ str(preq))
          member_add_embed=discord.Embed(title="Member added to project: "+project_name+"\nUser ID: "+str(uid),description=preq,colour=0x11806a)
          await ctx.send(embed=member_add_embed,delete_after=15)
          await ctx.message.delete()
        except Exception as e: 
          logger.error("error adding member "+str(e))
        
async def remove_mem(ctx,bot, project_id,project_name):
    logger.info("remove_user1 function called")
    '''
    if not 'REDMINE_KEY' in os.environ:
        logger.error("'REDMINE_KEY' doesn't exist in the environment variables")
        return
    logger.info("~remove_person called for " + os.environ.get('REDMINE_KEY'))
     '''
    
    desc = ""
    udict = dict()
    mjson = redmine_api.get_json(webpage + "projects/" + project_id + "/memberships.json", header)
    for i in mjson['memberships']:
        udict[i['user']['id']] = i['id']
        desc += str(i['user']['id']) + ") " + i['user']['name'] + "\n"

    mjson_embed = embeds.simple_embed(
            title = "Enter user ID (space sperated) to remove user from project: "+str(project_name),
            description = desc
            )

    sent = await ctx.send(embed = mjson_embed)
    mlist = await embeds.ctx_input(ctx, bot, sent)
    if not mlist:
        logger.error("Member input timed out.")
        return
    logger.info("Mlist : " + mlist)

    mlist = set(map(int, mlist.split()))
    for i in mlist:
        if not i in udict:
            await ctx.message.delete()
            logger.error("Member " + str(i) + "not in member set.")
            return
        else:
            try:
             ecode = requests.delete(webpage + "memberships/" + str(udict[i]) + ".json", headers = header)
             print(ecode)
             if(str(ecode)=="<Response [200]>"):
              logger.info("Removed user ID: " + str(i) + "\n")
              member_add_embed=discord.Embed(title="Removed user from project: "+project_name+"\nUser ID: "+str(i),description=ecode,colour=0x11806a)
              await ctx.send(embed=member_add_embed,delete_after=15)
              await ctx.message.delete()
             else:
              logger.error("error removing member "+str(e)+" "+str(ecode))
              await ctx.message.delete()
            except Exception as e: 
             logger.error("error removing member "+str(e))
             await ctx.message.delete()

def issues(project_name):
     logger.info("issues function called")
     ctime = datetime.datetime.now()
     name=str(project_name)
     issue_url = "https://www.kore.koders.in/projects/"+name+"/issues.json?set_filter=1"
     
     try:
      issues = get_json(issue_url, header).json()
      list =""
      for i in issues["issues"]:
          
          due=i["due_date"]
          if not due: 
               due="Null"
          else:
           due += " 23:59:59"
           due = datetime.datetime.strptime(due, '%Y-%m-%d %H:%M:%S')
           delta = due - ctime
          
           if( delta.days <0  ):
                if "assigned_to" not in i:
                    list=list+("Issue #"+str(i["id"])+" ( 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 ) "+"\nStatus: "+str(i["status"]["name"])+"\nAssigned by: "+str(i["author"]["name"])+"\nAssigned to: NULL"+"\nSubject: "+str(i["subject"])+"\nDue Date was: "+str(due)+"\n\n")  
                else:
                   list=list+("Issue #"+str(i["id"])+" ( 𝗘𝗫𝗣𝗜𝗥𝗘𝗗 ) "+"\nStatus: "+str(i["status"]["name"])+"\nAssigned by: "+str(i["author"]["name"])+"\nAssigned to: "+str(i["assigned_to"]["name"])+"\nSubject: "+str(i["subject"])+"\nDue Date was: "+str(due)+"\n\n")
           else:
               if "assigned_to" not in i:
                    list=list+("Issue #"+str(i["id"])+" ( Expires in "+str(delta.days)+" days )"+"\nStatus: "+str(i["status"]["name"])+"\nAssigned by: "+str(i["author"]["name"])+"\nAssigned to: NULL"+"\nSubject: "+str(i["subject"])+"\nDue Date is: "+str(due)+"\n\n")
               else:
                 list=list+("Issue #"+str(i["id"])+" ( Expires in "+str(delta.days)+" days )"+"\nStatus: "+str(i["status"]["name"])+"\nAssigned by: "+str(i["author"]["name"])+"\nAssigned to: "+str(i["assigned_to"]["name"])+"\nSubject: "+str(i["subject"])+"\nDue Date is: "+str(due)+"\n\n")
     except Exception as e: 
          logger.error("error getting issue list"+str(e))         
                
     return list
     

