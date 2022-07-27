print('  ___  __    _______   ___      ___ ___  ________       ')
print(' |\  \|\  \ |\  ___ \ |\  \    /  /|\  \|\   ___  \     ')
print(' \ \  \/  /|\ \   __/|\ \  \  /  / | \  \ \  \\\ \  \    ')
print('  \ \   ___  \ \  \_|/_\ \  \/  / / \ \  \ \  \\\ \  \   ')
print('   \ \  \\\ \  \ \  \_|\ \ \    / /   \ \  \ \  \\\ \  \  ')
print('    \ \__\\\ \__\ \_______\ \__/ /     \ \__\ \__\\\ \__\ ')
print('     \|__| \|__|\|_______|\|__|/       \|__|\|__| \|__| ')
print()
print('原版由 HansHans135 製作。')
print('Github:  https://github.com/HansHans135/ticket')
print()
print('此改版由 Krick#9685 所設計。')
print()


from discord_components import *
import discord
from datetime import datetime,timezone,timedelta
import os
import json
import threading
from flask import Flask, request
from flask import render_template

######
#設定#
#####

with open('Setting.json',mode='r',encoding='utf8') as jfile:
    jdata = json.load(jfile)
Prefix = jdata["Prefix"]
Token = jdata["Token"]

bot = commands.Bot(commands.when_mentioned_or(Prefix), intents=discord.Intents.all(), help_command=None)

ULR = "http://backupmode.xyz/" #!! 請自行設定
#線上看網址


def startweb():
    app = Flask(__name__)
    @app.route("/", methods=['GET'])
    def hello():
        id = request.args.get('id')
        r=open(f"web/{id}.txt","r")
        s = r.read()
        new_s = s.replace('\n','<br>')
        print(new_s)
        return new_s
    app.run(host="0.0.0.0",port=25596)
t = threading.Thread(target=startweb)  #建立執行緒
t.start()


@bot.event
async def on_ready():
    print(f"機器人 {bot.user} 已上線!")
    web_newpath = r'\web' 
    if not os.path.exists(web_newpath):
      print("未偵測到web資料夾，系統自動創建中...")
      os.makedirs(web_newpath)
      print("創建資料夾web完成~")
    else:
      print("偵測到web資料夾，繼續下一步啟動作業。")
    data_newpath = r'\data' 
    if not os.path.exists(data_newpath):
      print("未偵測到data資料夾，系統自動創建中...")
      os.makedirs(data_newpath)
      print("創建資料夾data完成~")
    else:
      print("偵測到data資料夾，繼續下一步啟動作業。")


@bot.command()
async def ticket(ctx):
  if ctx.author.guild_permissions.manage_messages:
    await ctx.send(jdata["Ticket_msg"],components = [Button(label = "開啟客服單", custom_id = "open",style=ButtonStyle.green)])
  else:
    await ctx.send("抱歉，您沒有權限進行此操作。")

@bot.event
async def on_button_click(interaction):
    def check(m):
        return m.author == interaction.author and m.channel == interaction.channel
    if interaction.component.custom_id == "open":
      overwrites = {
          interaction.author: discord.PermissionOverwrite(read_messages=True),
          interaction.guild.me: discord.PermissionOverwrite(read_messages=True),
          interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)
  }
      channel = discord.utils.get(interaction.guild.categories, name='客服單')
      客服單 = await interaction.guild.create_text_channel(name=f"ticket-{interaction.author.name}-hbot", category=channel, overwrites=overwrites)
      dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
      dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
      now = dt2.strftime("%Y-%m-%d %H:%M:%S")
      with open(f"data/{客服單.id}.txt", 'a') as filt:
        filt.write(f'客服單系統by Hbot\n\n創建時間:{now}\n頻道名稱:{客服單.name}\n創建人:{interaction.author}\n以下為詳細的對話紀錄:\n\n\n')
      await interaction.send(f'開了一張ticket在 <#{客服單.id}>')
      await 客服單.send(f'<@{interaction.author.id}>\n歡迎來到你的客服單\n請說明你的問題以便我們處理',components = [Button(label = "關閉客服單", custom_id = "close",style=ButtonStyle.red)])

    if interaction.component.custom_id == "close":
        if "ticket" in interaction.channel.name:
          dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
          dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
          now = dt2.strftime("%Y-%m-%d %H:%M:%S")
          txt =f"data/{interaction.channel.id}.txt"
          webid=interaction.channel.id
          with open(f"data/{interaction.channel.id}.txt", 'a') as filt:
            filt.write(f'\n\n關閉人:{interaction.author}\n關閉時間:{now}')
          await interaction.channel.delete()
          await interaction.author.send(f'你在**{interaction.guild.name}**的客服單已經關閉摟\n以下是對話紀錄:\n或是你要線上看? {ULR}?id={webid}', file=discord.File(txt))
          src=f'data/{webid}.txt'
          des=f'web/{webid}.txt'
          os.rename(src,des)

@bot.event
async def on_message(message):
  filepath = f"data/{message.channel.id}.txt"
  if os.path.isfile(filepath):
     with open(f"data/{message.channel.id}.txt", 'a') as filt:
      dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
      dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
      now = dt2.strftime("%Y-%m-%d %H:%M:%S")
      filt.write(f'{now}|{message.author}:{message.content}\n')

bot.run(Token)
