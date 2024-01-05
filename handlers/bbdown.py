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
     download_path = os.path.expanduser("~/videos")

     # output, error = DownloadBBDVideo(url, download_path,title)
     # if error:
     #    bot.reply_to(message, f"下载错误: {error}")
     #    return
     
     video_file = f"{download_path}/{translate_space(title)}.mp4" 

     try: 
          files = os.listdir(download_path)
          mp4_files = [file for file in files if file.endswith(".mp4")]
          latest_video = max(mp4_files, key=os.path.getmtime)
          print(translate_space(latest_video))
          if mp4_files:
               for mp4_file in mp4_files:
                    print(os.path.join(download_path, mp4_file))
                    with open(os.path.join(download_path, translate_space(latest_video)), 'rb') as video:
                         bot.send_video(message.chat.id, video)
          # print(j)
          # if os.path.exists(j):
          #      with open(j, 'rb') as video_file:
          #           bot.send_video(message.chat.id, video_file)
          # else:
          #      bot.reply_to(message,'Local video not found.')
          # file = InputMediaVideo(open(os.path.join(download_path, f"{title}.mp4"), 'rb'))
          # bot.send_video(message.chat.id, file)
              
          #asyncio.create_task(DeleteFolder(video_file))
     except Exception as e:
        bot.reply_to(
            message,
            f"发生错误: {str(e)}"
        )
     finally:
        bot.delete_message(message.chat.id, message.message_id)

def DownloadBBDVideo(url, download_path,title):
#     print(os.path.join(download_path, f"{title}.mp4"))
#     with open(os.path.join(download_path, f"{title}.mp4"), 'rb') as video:
#                #bot.send_video(message.chat.id, video)
#               print(video)
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

# def GetVideoID(URL):
#     BVGroup = re.search(r"BV[0-9a-zA-Z]+", URL)
#     BV = BVGroup.group()
#     return HexToDec(BV)

def extract_url_and_title(text):
    pattern = r'(https?://\S+)\s(.+)'
    match = re.match(pattern, text)
    if match:
        url = match.group(1)
        title = match.group(2)
        return url, title
    else:
        return None, None
    
def translate_space(title):
    return re.sub(r"\s", r"\\ ", title)

def register(bot: TeleBot) -> None:
    bot.register_message_handler(BBDown, commands=["bbdown"], pass_bot=True)
    bot.register_message_handler(BBDown, regexp="^bbdown:", pass_bot=True)