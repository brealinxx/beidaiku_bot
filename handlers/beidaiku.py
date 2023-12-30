import os
import re
from telebot import TeleBot
from telebot.types import Message

def info(message: Message, bot: TeleBot) -> None: 
    """info: 最伟大的背带裤"""
    try:
        with open("../beidaiku.png", "rb") as f:
            bot.send_photo(message.chat.id, photo=f, caption="这里是最伟大的背带裤！")
    except Exception as e:
        print(e) 
        bot.reply_to(message, "处理请求时发生错误。")
    

def help(message: Message,bot: TeleBot) -> None: 
    """help: 可用的指令集"""
    #todo describe command
    try:
        bot.reply_to(message, "可用的指令集:\n" + format("".join([f"/{command}\n" for command in GetCommands()])))
    except:
        bot.reply_to(
            message,
            "An error occurred while processing the request.",
        )
    

def extract_commands(filepath):
    commands = []
    with open(filepath, 'r') as file:
        content = file.read()
        matches = re.findall(r'commands=\[(.*?)\]', content)
        for match in matches:
            cmds = match.replace("'", '').replace('"', '').split(',')
            commands.extend(cmds)
    return commands

def GetCommands():
    commands = []
    handles_dir = 'handlers'  
    for filename in os.listdir(handles_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(handles_dir, filename)
            commands.extend(extract_commands(filepath))
    return commands

def register(bot: TeleBot) -> None:
    bot.register_message_handler(info, commands=["info"], pass_bot=True)
    bot.register_message_handler(help, commands=["help"], pass_bot=True)
