import requests
import os
from os import *
from telebot import TeleBot
from telebot.types import Message
import subprocess
import re
import asyncio

def BBDown(message: Message, bot: TeleBot) -> None:  
     """BBDown : /bbdown <bilibili URL> <title>"""
     url, title = extract_url_and_title(message.text)
     print((url,title))
     download_path = os.path.expanduser("~/videos")

     output, error = DownloadBBDVideo(url, download_path)
     if error:
        bot.reply_to(message, f"下载错误: {error}")
        return
     
     video_file = f"{download_path}/{title}.mp4" 

     try: 
          # files = os.listdir(video_folder)
          # mp4_files = [file for file in files if file.endswith(".mp4")]
          # if mp4_files:
          #      for mp4_file in mp4_files:
          #           with open(os.path.join(video_folder, mp4_file), 'rb') as video_file:
          #                bot.send_video(message.chat.id, video_file)
          if video_file:
            with open(f"{download_path}/{title}.mp4", 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            asyncio.create_task(DeleteFolder(video_file))
          
     except Exception as e:
        bot.reply_to(
            message,
            f"发生错误: {str(e)}"
        )
     finally:
        bot.delete_message(message.chat.id, message.message_id)

def DownloadBBDVideo(url, download_path):
    process = subprocess.Popen(['/root/DEV/BBDown', '--work-dir', download_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        return None, error.decode('utf-8')
    return output.decode('utf-8'), None

async def DeleteFolder(path):
    await asyncio.sleep(7200) 
    os.remove(path)

def HexToDec(hex_str: str) -> int:
    dec_num = 0
    for i, c in enumerate(hex_str):
        dec_num += (16 ** (len(hex_str) - i - 1)) * ord(c) - ord('0')
    return dec_num

def GetVideoID(URL):
    BVGroup = re.search(r"BV[0-9a-zA-Z]+", URL)
    BV = BVGroup.group()
    return HexToDec(BV)

def extract_url_and_title(text):
    pattern = r'(https?://\S+)\s(.+)'
    match = re.match(pattern, text)
    if match:
        url = match.group(1)
        title = match.group(2)
        return url, title
    else:
        return None, None

def register(bot: TeleBot) -> None:
    bot.register_message_handler(BBDown, commands=["bbdown"], pass_bot=True)
    bot.register_message_handler(BBDown, regexp="^bbdown:", pass_bot=True)