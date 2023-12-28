import os
import importlib
from os import environ
from telebot import TeleBot
from telebot.types import Message

def info(message: Message, bot: TeleBot) -> None: 
     """info: 最伟大的背带裤"""
     try:
          bot.reply_to(
               message,
               "这里是最伟大背带裤🤖！" 
          )
     except:
          bot.reply_to(
               message,
               "An error occurred while processing the request.",
          )

def help(message: Message, bot: TeleBot) -> None: 
     """info: 最伟大的背带裤"""
     try:
          bot.reply_to(
               message,
               "指令集:\n" + GetCommands() 
          )
     except:
          bot.reply_to(
               message,
               "An error occurred while processing the request.",
          )

def GetCommands(bot: TeleBot) -> list:
    commands = []
    for path in os.listdir("handles"):
        if path.endswith(".py"):
            module_name = path[:-3]
            module = importlib.import_module(module_name)
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and isinstance(obj, str):
                    for command in obj.commands:
                        if isinstance(command, str):
                            commands.append(command)
    return commands

def register(bot: TeleBot) -> None:
    bot.register_message_handler(info, commands=["info"], pass_bot=True)
    bot.register_message_handler(help, commands=["help"], pass_bot=True)
