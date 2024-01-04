import requests
import os
from os import *
from telebot import TeleBot
from telebot.types import Message
import subprocess
import re
import asyncio

def BBDown(message: Message, bot: TeleBot) -> None:  
     """BBDown : /bbdown <bilibili URL>"""
     url = message.text
     print(url)
     folder = os.listdir("~/videos")

     output, error = DownloadBBDVideo(url, folder)
     if error:
        bot.reply_to(message, f"下载错误: {error}")
        return
     
     video_folder = f"~/videos/{GetVideoID(url)}" 

     try: 
          files = os.listdir(video_folder)
          mp4_files = [file for file in files if file.endswith(".mp4")]
          if mp4_files:
               for mp4_file in mp4_files:
                    with open(os.path.join(video_folder, mp4_file), 'rb') as video_file:
                         bot.send_video(message.chat.id, video_file)
          asyncio.create_task(DeleteFolder(video_folder))
     except Exception as e:
        bot.reply_to(
            message,
            f"发生错误: {str(e)}"
        )
     finally:
        bot.delete_message(message.chat.id, message.message_id)

def DownloadBBDVideo(url, download_path):
    process = subprocess.Popen(['BBDown', '--work-dir', download_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        return None, error.decode('utf-8')
    return output.decode('utf-8'), None

async def DeleteFolder(path):
    await asyncio.sleep(7200) 
    os.rmdir(path)

def HexToDec(hex_str: str) -> int:
    dec_num = 0
    for i, c in enumerate(hex_str):
        dec_num += (16 ** (len(hex_str) - i - 1)) * ord(c) - ord('0')
    return dec_num

def GetVideoID(URL):
    BVGroup = re.search(r"BV[0-9a-zA-Z]+", URL)
    BV = BVGroup.group()
    return HexToDec(BV)

print(HexToDec("1qW411e7hV"))

def register(bot: TeleBot) -> None:
    bot.register_message_handler(BBDown, commands=["bbdown"], pass_bot=True)
    bot.register_message_handler(BBDown, regexp="^bbdown:", pass_bot=True)